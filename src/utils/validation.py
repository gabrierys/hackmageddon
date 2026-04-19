from __future__ import annotations

import re
from urllib.parse import urlsplit, urlunsplit


TIMELINE_KEYWORD = "cyber-attacks-timeline"
CATEGORY_TIMELINE_PATH = "/category/security/cyber-attacks-timeline"


def validate_year_range(start_year: int, end_year: int) -> None:
    if start_year > end_year:
        raise ValueError(f"start_year ({start_year}) deve ser <= end_year ({end_year})")


def canonicalize_url(url: str) -> str:
    parts = urlsplit(url.strip())
    scheme = parts.scheme or "https"
    netloc = parts.netloc.lower()
    path = parts.path.rstrip("/")
    canonical = urlunsplit((scheme, netloc, path, "", ""))
    return canonical


def is_timeline_url(url: str) -> bool:
    return TIMELINE_KEYWORD in url.lower()


def is_timeline_post_url(url: str) -> bool:
    parts = urlsplit(url.strip())
    path = parts.path.lower().rstrip("/")
    if TIMELINE_KEYWORD not in path:
        return False
    if "/category/" in path:
        return False
    return bool(re.search(r"/20\d{2}/\d{2}/\d{2}/", path + "/"))


def is_timeline_category_page_url(url: str) -> bool:
    parts = urlsplit(url.strip())
    path = parts.path.lower().rstrip("/")
    if path == CATEGORY_TIMELINE_PATH:
        return True
    return bool(re.fullmatch(r"/category/security/cyber-attacks-timeline/page/\d+", path))


def is_year_archive_page_url(url: str, year: int) -> bool:
    parts = urlsplit(url.strip())
    path = parts.path.rstrip("/")
    year_prefix = rf"/{year}"
    patterns = [
        rf"{year_prefix}",
        rf"{year_prefix}/page/\d+",
        rf"{year_prefix}/\d{{2}}",
        rf"{year_prefix}/\d{{2}}/page/\d+",
    ]
    return any(re.fullmatch(pattern, path) for pattern in patterns)


def infer_year_from_url(url: str) -> int | None:
    match = re.search(r"/(20\d{2})/", url)
    if match:
        return int(match.group(1))
    return None
