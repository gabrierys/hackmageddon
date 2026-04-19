from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def save_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def save_csv(df: pd.DataFrame, path: Path, index: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=index)


def append_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    has_file = path.exists()
    df.to_csv(path, mode="a", index=False, header=not has_file)


def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def load_csv_or_empty(path: Path, columns: list[str] | None = None) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=columns or [])
    return pd.read_csv(path)


def slugify_for_filename(text: str, max_len: int = 80) -> str:
    cleaned = "".join(ch if ch.isalnum() else "-" for ch in text.lower())
    compact = "-".join(part for part in cleaned.split("-") if part)
    return compact[:max_len] or "page"
