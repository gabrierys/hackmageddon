from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from ..clients.http_client import HttpClient
from ..config import (
    RAW_DATASET_PATH,
    RAW_HTML_DIR,
    RAW_INCREMENTAL_PATH,
    SCRAPE_STATUS_PATH,
    TIMELINE_URLS_PATH,
    ensure_project_dirs,
)
from ..parsers.timeline_parser import parse_timeline_page
from ..utils.hashing import sha256_text
from ..utils.io import append_csv, load_csv_or_empty, save_csv, save_text, slugify_for_filename, utc_now_iso

logger = logging.getLogger(__name__)

SCRAPE_STATUS_COLUMNS = [
    "timeline_url",
    "source_year",
    "status",
    "rows_extracted",
    "error",
    "timestamp",
]


@dataclass
class RawBuildResult:
    total_urls: int
    success_urls: int
    failed_urls: int
    rows_extracted: int


def _reset_incremental_files() -> None:
    for path in [RAW_INCREMENTAL_PATH, SCRAPE_STATUS_PATH]:
        if path.exists():
            path.unlink()


def _load_timeline_urls() -> pd.DataFrame:
    if not TIMELINE_URLS_PATH.exists():
        raise FileNotFoundError(
            f"Arquivo de URLs não encontrado: {TIMELINE_URLS_PATH}. Rode o comando discover primeiro."
        )
    urls_df = pd.read_csv(TIMELINE_URLS_PATH)
    if "timeline_url" not in urls_df.columns:
        raise ValueError("timeline_urls.csv deve conter a coluna 'timeline_url'.")
    if "source_year" not in urls_df.columns:
        urls_df["source_year"] = pd.NA
    return urls_df


def _save_raw_html(url: str, source_year: int | None, html: str) -> Path:
    digest = sha256_text(url)[:12]
    slug = slugify_for_filename(url.split("/")[-1] or url)
    filename = f"{source_year or 'unknown'}_{slug}_{digest}.html"
    output_path = RAW_HTML_DIR / filename
    save_text(output_path, html)
    return output_path


def _append_status(
    timeline_url: str,
    source_year: int | None,
    status: str,
    rows_extracted: int,
    error: str = "",
) -> None:
    row = pd.DataFrame(
        [
            {
                "timeline_url": timeline_url,
                "source_year": source_year,
                "status": status,
                "rows_extracted": rows_extracted,
                "error": error,
                "timestamp": utc_now_iso(),
            }
        ]
    )
    append_csv(row, SCRAPE_STATUS_PATH)


def build_raw_dataset(client: HttpClient, resume: bool = True) -> RawBuildResult:
    ensure_project_dirs()

    if not resume:
        _reset_incremental_files()

    urls_df = _load_timeline_urls()
    status_df = load_csv_or_empty(SCRAPE_STATUS_PATH, columns=SCRAPE_STATUS_COLUMNS)

    success_already = set()
    if not status_df.empty:
        success_already = set(
            status_df.loc[status_df["status"] == "success", "timeline_url"].astype(str).tolist()
        )

    total_urls = len(urls_df)

    for _, row in urls_df.iterrows():
        timeline_url = str(row.get("timeline_url", "")).strip()
        source_year = row.get("source_year", None)
        if not timeline_url:
            continue

        if resume and timeline_url in success_already:
            logger.info("Skipping already scraped URL (resume): %s", timeline_url)
            continue

        try:
            source_year_int = int(source_year) if pd.notna(source_year) else None
            logger.info("Scraping timeline URL: %s", timeline_url)
            html = client.get_text(timeline_url)
            html_path = _save_raw_html(timeline_url, source_year_int, html)
            logger.info("Saved raw HTML: %s", html_path)

            parsed_df = parse_timeline_page(
                html=html,
                source_timeline_url=timeline_url,
                source_year=source_year_int,
            )

            rows_extracted = len(parsed_df)
            if rows_extracted > 0:
                append_csv(parsed_df, RAW_INCREMENTAL_PATH)
                _append_status(
                    timeline_url=timeline_url,
                    source_year=source_year,
                    status="success",
                    rows_extracted=rows_extracted,
                )
                logger.info("Success URL=%s rows=%s", timeline_url, rows_extracted)
            else:
                _append_status(
                    timeline_url=timeline_url,
                    source_year=source_year,
                    status="no_valid_table",
                    rows_extracted=0,
                )
                logger.warning("No valid event table found for URL=%s", timeline_url)
        except Exception as exc:
            logger.exception("Failed URL=%s error=%s", timeline_url, exc)
            _append_status(
                timeline_url=timeline_url,
                source_year=source_year,
                status="failed",
                rows_extracted=0,
                error=str(exc),
            )

    raw_df = load_csv_or_empty(RAW_INCREMENTAL_PATH)
    save_csv(raw_df, RAW_DATASET_PATH)
    final_status_df = load_csv_or_empty(SCRAPE_STATUS_PATH, columns=SCRAPE_STATUS_COLUMNS)
    success_urls = 0
    if not final_status_df.empty:
        success_urls = final_status_df.loc[
            final_status_df["status"] == "success", "timeline_url"
        ].nunique()
    failed_urls = max(total_urls - success_urls, 0)

    return RawBuildResult(
        total_urls=total_urls,
        success_urls=success_urls,
        failed_urls=failed_urls,
        rows_extracted=len(raw_df),
    )
