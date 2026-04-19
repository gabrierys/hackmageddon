from __future__ import annotations

import pandas as pd

from .dates import parse_hackmageddon_date
from .dedup import add_row_hash, deduplicate_rows
from .taxonomy import normalize_attack_label

RAW_COLUMN_ALIASES = {
    "id_raw": ["ID"],
    "date_reported_raw": ["Date Reported"],
    "date_occurred_raw": ["Date Occurred"],
    "date_discovered_raw": ["Date Discovered"],
    "author": ["Author"],
    "target": ["Target"],
    "description": ["Description"],
    "attack_raw": ["Attack"],
    "target_class": ["Target Class"],
    "attack_class": ["Attack Class"],
    "country": ["Country"],
    "link": ["Link"],
    "initial_access": ["Initial Access"],
    "source_timeline_url": ["source_timeline_url"],
    "source_year": ["source_year"],
}


def _find_first_existing_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    columns_lower = {col.lower(): col for col in df.columns}
    for candidate in candidates:
        exact = columns_lower.get(candidate.lower())
        if exact:
            return exact
    return None


def _map_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    for out_col, aliases in RAW_COLUMN_ALIASES.items():
        found = _find_first_existing_column(df, aliases)
        if found is None:
            out[out_col] = ""
        else:
            out[out_col] = df[found].fillna("").astype(str)
    return out


def _parse_date_series(series: pd.Series) -> tuple[pd.Series, pd.Series]:
    parsed_values: list[str | None] = []
    statuses: list[str] = []
    for value in series:
        result = parse_hackmageddon_date(value)
        parsed_values.append(result.parsed_iso)
        statuses.append(result.status)
    return pd.Series(parsed_values, index=series.index), pd.Series(statuses, index=series.index)


def build_normalized_dataframe(raw_df: pd.DataFrame) -> pd.DataFrame:
    base = _map_columns(raw_df)
    base["attack_norm"] = base["attack_raw"].apply(normalize_attack_label)

    for raw_col, parsed_col, status_col in [
        ("date_reported_raw", "date_reported", "parse_status_date_reported"),
        ("date_occurred_raw", "date_occurred", "parse_status_date_occurred"),
        ("date_discovered_raw", "date_discovered", "parse_status_date_discovered"),
    ]:
        parsed, status = _parse_date_series(base[raw_col])
        base[parsed_col] = parsed
        base[status_col] = status

    base = add_row_hash(base)
    base = deduplicate_rows(base)

    ordered_columns = [
        "id_raw",
        "date_reported_raw",
        "date_occurred_raw",
        "date_discovered_raw",
        "author",
        "target",
        "description",
        "attack_raw",
        "attack_norm",
        "target_class",
        "attack_class",
        "country",
        "link",
        "initial_access",
        "source_timeline_url",
        "source_year",
        "row_hash",
        "date_reported",
        "date_occurred",
        "date_discovered",
        "parse_status_date_reported",
        "parse_status_date_occurred",
        "parse_status_date_discovered",
    ]

    return base[ordered_columns]
