from __future__ import annotations

import logging
from dataclasses import dataclass

import pandas as pd

from ..clients.http_client import HttpClient
from ..config import TIMELINE_URLS_PATH, settings
from ..utils.io import save_csv, utc_now_iso
from ..utils.validation import infer_year_from_url, validate_year_range
from .archive_discovery import (
    discover_timeline_links_from_archive,
    discover_timeline_links_from_category,
)

logger = logging.getLogger(__name__)


@dataclass
class DiscoveryResult:
    timeline_urls_df: pd.DataFrame
    total_urls: int


def discover_timeline_urls(
    client: HttpClient,
    base_url: str,
    start_year: int,
    end_year: int,
) -> DiscoveryResult:
    validate_year_range(start_year, end_year)

    rows: list[dict[str, object]] = []

    for year in range(start_year, end_year + 1):
        try:
            urls = discover_timeline_links_from_archive(
                client=client,
                base_url=base_url,
                year=year,
                max_pages=settings.discovery_max_pages_per_year,
            )
            for url in urls:
                url_year = infer_year_from_url(url) or year
                rows.append(
                    {
                        "timeline_url": url,
                        "source_year": url_year,
                        "discovered_from": f"{base_url.rstrip('/')}/{year}/",
                        "discovered_at": utc_now_iso(),
                    }
                )
            logger.info("Year %s -> %s timeline URLs", year, len(urls))
        except Exception as exc:
            logger.exception("Failed discovery for year %s: %s", year, exc)

    try:
        category_urls = discover_timeline_links_from_category(
            client=client,
            base_url=base_url,
            start_year=start_year,
            end_year=end_year,
            max_pages=settings.discovery_max_pages_category,
        )
        for url in category_urls:
            url_year = infer_year_from_url(url)
            if url_year is None:
                continue
            rows.append(
                {
                    "timeline_url": url,
                    "source_year": url_year,
                    "discovered_from": f"{base_url.rstrip('/')}/category/security/cyber-attacks-timeline/",
                    "discovered_at": utc_now_iso(),
                }
            )
        logger.info("Category crawl -> %s timeline URLs in range", len(category_urls))
    except Exception as exc:
        logger.exception("Failed discovery for category pages: %s", exc)

    if not rows:
        df = pd.DataFrame(columns=pd.Index(["timeline_url", "source_year", "discovered_from", "discovered_at"]))
    else:
        df = pd.DataFrame(rows)
        df = df.sort_values(["timeline_url", "discovered_from"]).drop_duplicates(
            subset=["timeline_url"], keep="first"
        )
        df = df.sort_values("timeline_url").reset_index(drop=True)

    save_csv(df, TIMELINE_URLS_PATH)
    logger.info("Saved %s discovered timeline URLs to %s", len(df), TIMELINE_URLS_PATH)

    return DiscoveryResult(timeline_urls_df=df, total_urls=len(df))
