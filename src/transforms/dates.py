from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class DateParseResult:
    raw: str
    parsed_iso: str | None
    status: str


_SINGLE_SLASH_DATE = re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{4})$")
_SINGLE_ISO_DATE = re.compile(r"^(\d{4})-(\d{1,2})-(\d{1,2})$")


def _safe_iso(year: int, month: int, day: int) -> str | None:
    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return None


def parse_hackmageddon_date(value: object) -> DateParseResult:
    raw = "" if value is None else str(value).strip()
    if raw == "":
        return DateParseResult(raw=raw, parsed_iso=None, status="missing")

    lowered = raw.lower()
    if lowered in {"-", "unknown", "n/a", "na"}:
        return DateParseResult(raw=raw, parsed_iso=None, status="missing_or_unknown")

    if "recent" in lowered or "between" in lowered or "~" in lowered:
        return DateParseResult(raw=raw, parsed_iso=None, status="vague")

    slash_match = _SINGLE_SLASH_DATE.match(raw)
    if slash_match:
        day, month, year = map(int, slash_match.groups())
        parsed = _safe_iso(year, month, day)
        if parsed:
            return DateParseResult(raw=raw, parsed_iso=parsed, status="parsed")
        return DateParseResult(raw=raw, parsed_iso=None, status="invalid")

    iso_match = _SINGLE_ISO_DATE.match(raw)
    if iso_match:
        year, month, day = map(int, iso_match.groups())
        parsed = _safe_iso(year, month, day)
        if parsed:
            return DateParseResult(raw=raw, parsed_iso=parsed, status="parsed")
        return DateParseResult(raw=raw, parsed_iso=None, status="invalid")

    # Se existir texto ou intervalo, mantemos como vaga para evitar inferência indevida.
    if re.search(r"[a-zA-Z]", raw) or re.search(r"\d+\s*[-–]\s*\d+", raw):
        return DateParseResult(raw=raw, parsed_iso=None, status="vague")

    return DateParseResult(raw=raw, parsed_iso=None, status="invalid")
