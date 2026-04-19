from __future__ import annotations

import pandas as pd

from ..utils.hashing import build_row_hash


HASH_FIELDS = [
    "source_timeline_url",
    "date_reported_raw",
    "target",
    "attack_raw",
    "description",
]


def add_row_hash(df: pd.DataFrame) -> pd.DataFrame:
    copy_df = df.copy()
    copy_df["row_hash"] = copy_df.apply(
        lambda row: build_row_hash([row.get(field, "") for field in HASH_FIELDS]),
        axis=1,
    )
    return copy_df


def deduplicate_rows(df: pd.DataFrame) -> pd.DataFrame:
    if "row_hash" not in df.columns:
        df = add_row_hash(df)
    return df.drop_duplicates(subset=["row_hash"]).reset_index(drop=True)
