from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
RAW_HTML_DIR = RAW_DIR / "html"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"
LOG_DIR = DATA_DIR / "logs"

TIMELINE_URLS_PATH = INTERIM_DIR / "timeline_urls.csv"
SCRAPE_STATUS_PATH = INTERIM_DIR / "scrape_status.csv"
RAW_INCREMENTAL_PATH = INTERIM_DIR / "raw_events_incremental.csv"
RAW_DATASET_PATH = PROCESSED_DIR / "hackmageddon_raw.csv"
NORMALIZED_DATASET_PATH = PROCESSED_DIR / "hackmageddon_normalized.csv"
ANALYTIC_2023PLUS_PATH = PROCESSED_DIR / "hackmageddon_2023plus.csv"
DAILY_COUNTS_PATH = PROCESSED_DIR / "hackmageddon_daily_counts.csv"
LOG_FILE_PATH = LOG_DIR / "scrape.log"


@dataclass(frozen=True)
class Settings:
    base_url: str = "https://www.hackmageddon.com"
    user_agent: str = (
        "Mozilla/5.0 (compatible; HackmageddonScraper/1.0; +https://www.hackmageddon.com)"
    )
    timeout_seconds: float = 30.0
    min_sleep_seconds: float = 0.3
    max_sleep_seconds: float = 1.2
    retry_attempts: int = 4
    retry_backoff_min: float = 1.0
    retry_backoff_max: float = 8.0
    default_start_year: int = 2023
    default_end_year: int = datetime.utcnow().year
    discovery_max_pages_per_year: int = 80
    discovery_max_pages_category: int = 120

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            base_url=os.getenv("HACKMAGEDDON_BASE_URL", cls.base_url),
            user_agent=os.getenv("HACKMAGEDDON_USER_AGENT", cls.user_agent),
            timeout_seconds=float(
                os.getenv("HACKMAGEDDON_TIMEOUT_SECONDS", str(cls.timeout_seconds))
            ),
            min_sleep_seconds=float(
                os.getenv("HACKMAGEDDON_MIN_SLEEP_SECONDS", str(cls.min_sleep_seconds))
            ),
            max_sleep_seconds=float(
                os.getenv("HACKMAGEDDON_MAX_SLEEP_SECONDS", str(cls.max_sleep_seconds))
            ),
            retry_attempts=int(os.getenv("HACKMAGEDDON_RETRY_ATTEMPTS", str(cls.retry_attempts))),
            retry_backoff_min=float(
                os.getenv("HACKMAGEDDON_RETRY_BACKOFF_MIN", str(cls.retry_backoff_min))
            ),
            retry_backoff_max=float(
                os.getenv("HACKMAGEDDON_RETRY_BACKOFF_MAX", str(cls.retry_backoff_max))
            ),
            default_start_year=int(
                os.getenv("HACKMAGEDDON_DEFAULT_START_YEAR", str(cls.default_start_year))
            ),
            default_end_year=int(
                os.getenv("HACKMAGEDDON_DEFAULT_END_YEAR", str(cls.default_end_year))
            ),
            discovery_max_pages_per_year=int(
                os.getenv(
                    "HACKMAGEDDON_DISCOVERY_MAX_PAGES_PER_YEAR",
                    str(cls.discovery_max_pages_per_year),
                )
            ),
            discovery_max_pages_category=int(
                os.getenv(
                    "HACKMAGEDDON_DISCOVERY_MAX_PAGES_CATEGORY",
                    str(cls.discovery_max_pages_category),
                )
            ),
        )


settings = Settings.from_env()


def ensure_project_dirs() -> None:
    for path in [
        RAW_DIR,
        RAW_HTML_DIR,
        INTERIM_DIR,
        PROCESSED_DIR,
        LOG_DIR,
    ]:
        path.mkdir(parents=True, exist_ok=True)
