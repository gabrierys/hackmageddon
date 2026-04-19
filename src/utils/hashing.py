from __future__ import annotations

import hashlib


def normalize_for_hash(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip().lower()
    return " ".join(text.split())


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_row_hash(parts: list[object]) -> str:
    normalized = "||".join(normalize_for_hash(part) for part in parts)
    return sha256_text(normalized)
