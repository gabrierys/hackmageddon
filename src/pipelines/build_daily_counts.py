from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from ..config import ANALYTIC_2023PLUS_PATH, DAILY_COUNTS_PATH, NORMALIZED_DATASET_PATH
from ..transforms.taxonomy import collapse_unknown_and_rare
from ..utils.io import load_csv, save_csv


@dataclass
class DailyCountsResult:
    rows_2023plus: int
    daily_rows: int
    attack_distribution: dict[str, int]


def build_analytic_2023plus_and_daily_counts(start_date: str = "2023-01-01") -> DailyCountsResult:
    if not NORMALIZED_DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset normalized não encontrado em {NORMALIZED_DATASET_PATH}. Rode normalize primeiro."
        )

    normalized_df = load_csv(NORMALIZED_DATASET_PATH)

    cutoff = pd.Timestamp(start_date)
    working = normalized_df.copy()
    working["date_occurred_dt"] = pd.to_datetime(working["date_occurred"], errors="coerce")

    filtered = working[
        (working["parse_status_date_occurred"] == "parsed")
        & (working["date_occurred_dt"].notna())
        & (working["date_occurred_dt"] >= cutoff)
    ].copy()
    filtered["date_occurred"] = filtered["date_occurred_dt"].dt.date.astype(str)
    filtered = filtered.drop(columns=["date_occurred_dt"])

    filtered["attack_norm"] = collapse_unknown_and_rare(filtered["attack_norm"], rare_threshold=5)
    save_csv(filtered, ANALYTIC_2023PLUS_PATH)

    daily_counts = (
        filtered.groupby("date_occurred", dropna=False)
        .size()
        .reset_index(name="events_per_day")
        .rename(columns={"date_occurred": "date"})
        .sort_values("date")
        .reset_index(drop=True)
    )
    save_csv(daily_counts, DAILY_COUNTS_PATH)

    attack_distribution = filtered["attack_norm"].value_counts().to_dict()

    return DailyCountsResult(
        rows_2023plus=len(filtered),
        daily_rows=len(daily_counts),
        attack_distribution={str(k): int(v) for k, v in attack_distribution.items()},
    )
