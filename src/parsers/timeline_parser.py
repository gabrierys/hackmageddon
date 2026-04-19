from __future__ import annotations

import logging
from io import StringIO
from datetime import datetime, timezone

import pandas as pd
from bs4 import BeautifulSoup

from .html_utils import (
    extract_page_title,
    extract_table_headers,
    normalize_header,
    normalize_header_key,
    parse_table_to_dataframe,
    table_matches_required_headers,
)

logger = logging.getLogger(__name__)

REQUIRED_HEADERS = {"Date Reported", "Attack", "Target"}


def _match_required_with_pandas(df: pd.DataFrame) -> bool:
    headers = [normalize_header(col) for col in df.columns]
    required = {normalize_header_key(col) for col in REQUIRED_HEADERS}
    current = {normalize_header_key(col) for col in headers}
    return required.issubset(current)


def extract_valid_event_tables(html: str) -> list[pd.DataFrame]:
    soup = BeautifulSoup(html, "lxml")
    valid_tables: list[pd.DataFrame] = []

    for table in soup.find_all("table"):
        headers = extract_table_headers(table)
        if not headers:
            continue
        if table_matches_required_headers(headers, REQUIRED_HEADERS):
            df = parse_table_to_dataframe(table, headers)
            if not df.empty:
                valid_tables.append(df)

    if valid_tables:
        return valid_tables

    # Fallback para páginas com marcação irregular.
    try:
        pandas_tables = pd.read_html(StringIO(html), flavor="lxml")
        for df in pandas_tables:
            if _match_required_with_pandas(df):
                normalized_columns = [normalize_header(str(col)) for col in df.columns]
                df.columns = normalized_columns
                valid_tables.append(df)
    except (ValueError, ImportError):
        logger.debug("No HTML tables found by pandas.read_html")

    return valid_tables


def parse_timeline_page(
    html: str,
    source_timeline_url: str,
    source_year: int | None,
) -> pd.DataFrame:
    soup = BeautifulSoup(html, "lxml")
    page_title = extract_page_title(soup)
    scraped_at = datetime.now(timezone.utc).isoformat()

    tables = extract_valid_event_tables(html)
    if not tables:
        return pd.DataFrame()

    combined = pd.concat(tables, ignore_index=True)
    combined["source_timeline_url"] = source_timeline_url
    combined["source_year"] = source_year
    combined["scraped_at"] = scraped_at
    combined["page_title"] = page_title

    return combined
