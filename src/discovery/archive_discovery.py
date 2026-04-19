from __future__ import annotations

import logging
from collections import deque
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from ..clients.http_client import HttpClient
from ..utils.validation import (
    canonicalize_url,
    infer_year_from_url,
    is_timeline_category_page_url,
    is_timeline_post_url,
    is_year_archive_page_url,
)

logger = logging.getLogger(__name__)


def _extract_links(html: str, current_url: str) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    links: list[str] = []
    for anchor in soup.find_all("a", href=True):
        absolute = urljoin(current_url, anchor["href"])
        links.append(canonicalize_url(absolute))
    return links


def _crawl_listing_pages(
    client: HttpClient,
    start_url: str,
    can_enqueue,
    can_collect,
    max_pages: int,
) -> set[str]:
    queue: deque[str] = deque([canonicalize_url(start_url)])
    visited: set[str] = set()
    collected: set[str] = set()

    while queue and len(visited) < max_pages:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)
        try:
            html = client.get_text(current)
        except Exception as exc:
            logger.warning("Failed discovery page: %s (%s)", current, exc)
            continue

        for link in _extract_links(html, current_url=current):
            if can_collect(link):
                collected.add(canonicalize_url(link))
            if link not in visited and can_enqueue(link):
                queue.append(link)

    return collected


def discover_timeline_links_from_archive(
    client: HttpClient,
    base_url: str,
    year: int,
    max_pages: int = 80,
) -> list[str]:
    archive_url = f"{base_url.rstrip('/')}/{year}/"
    logger.info("Discovering timeline links from year archive: %s", archive_url)

    def _can_enqueue(url: str) -> bool:
        return is_year_archive_page_url(url, year=year)

    def _can_collect(url: str) -> bool:
        return is_timeline_post_url(url) and infer_year_from_url(url) == year

    discovered = _crawl_listing_pages(
        client=client,
        start_url=archive_url,
        can_enqueue=_can_enqueue,
        can_collect=_can_collect,
        max_pages=max_pages,
    )
    return sorted(discovered)


def discover_timeline_links_from_category(
    client: HttpClient,
    base_url: str,
    start_year: int,
    end_year: int,
    max_pages: int = 120,
) -> list[str]:
    category_url = f"{base_url.rstrip('/')}/category/security/cyber-attacks-timeline/"
    logger.info("Discovering timeline links from category pages: %s", category_url)

    def _can_enqueue(url: str) -> bool:
        return is_timeline_category_page_url(url)

    def _can_collect(url: str) -> bool:
        if not is_timeline_post_url(url):
            return False
        year = infer_year_from_url(url)
        return year is not None and start_year <= year <= end_year

    discovered = _crawl_listing_pages(
        client=client,
        start_url=category_url,
        can_enqueue=_can_enqueue,
        can_collect=_can_collect,
        max_pages=max_pages,
    )
    return sorted(discovered)
