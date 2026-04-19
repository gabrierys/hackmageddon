from __future__ import annotations

import re

import pandas as pd


def normalize_attack_label(value: object) -> str:
    text = "" if value is None else str(value).strip().lower()
    text = re.sub(r"\s+", " ", text)

    if text in {"", "-", "unknown", "n/a", "na"}:
        return "unknown"

    if "cve" in text or "vulnerab" in text:
        return "vulnerability"
    if "ransom" in text:
        return "ransomware"
    if "ddos" in text or text == "dos" or "denial of service" in text:
        return "ddos"
    if "phish" in text:
        return "phishing"
    if "malware" in text:
        return "malware"
    if "breach" in text or "leak" in text:
        return "data breach"

    return text


def collapse_unknown_and_rare(
    series: pd.Series,
    rare_threshold: int = 5,
) -> pd.Series:
    collapsed = series.fillna("unknown").astype(str).str.strip().str.lower()
    collapsed = collapsed.replace({"": "unknown", "unknown": "other"})

    counts = collapsed.value_counts(dropna=False)
    rare_classes = set(counts[counts < rare_threshold].index)
    return collapsed.apply(lambda value: "other" if value in rare_classes else value)
