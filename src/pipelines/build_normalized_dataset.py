from __future__ import annotations

from dataclasses import dataclass

from ..config import NORMALIZED_DATASET_PATH, RAW_DATASET_PATH
from ..transforms.normalize import build_normalized_dataframe
from ..utils.io import load_csv, save_csv


@dataclass
class NormalizeResult:
    total_raw_rows: int
    rows_after_dedup: int
    parseable_date_occurred_rows: int


def build_normalized_dataset() -> NormalizeResult:
    if not RAW_DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset raw não encontrado em {RAW_DATASET_PATH}. Rode o comando scrape primeiro."
        )

    raw_df = load_csv(RAW_DATASET_PATH)
    normalized_df = build_normalized_dataframe(raw_df)
    save_csv(normalized_df, NORMALIZED_DATASET_PATH)

    parseable = int((normalized_df["parse_status_date_occurred"] == "parsed").sum())

    return NormalizeResult(
        total_raw_rows=len(raw_df),
        rows_after_dedup=len(normalized_df),
        parseable_date_occurred_rows=parseable,
    )
