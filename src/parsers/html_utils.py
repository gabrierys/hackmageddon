from __future__ import annotations

import re

import pandas as pd
from bs4 import BeautifulSoup, Tag


def clean_text(value: str | None) -> str:
    if value is None:
        return ""
    return " ".join(value.replace("\xa0", " ").split()).strip()


def normalize_header(header: str) -> str:
    text = clean_text(header)
    text = re.sub(r"\s+", " ", text)
    return text


def normalize_header_key(header: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", normalize_header(header).lower())


def extract_page_title(soup: BeautifulSoup) -> str:
    title_tag = soup.find("title")
    return clean_text(title_tag.get_text()) if title_tag else ""


def extract_table_headers(table_tag: Tag) -> list[str]:
    header_cells = table_tag.find_all("th")
    if header_cells:
        return [normalize_header(cell.get_text(" ", strip=True)) for cell in header_cells]

    first_row = table_tag.find("tr")
    if not first_row:
        return []
    cells = first_row.find_all(["td", "th"])
    return [normalize_header(cell.get_text(" ", strip=True)) for cell in cells]


def table_matches_required_headers(headers: list[str], required: set[str]) -> bool:
    normalized = {normalize_header_key(header) for header in headers}
    required_norm = {normalize_header_key(column) for column in required}
    return required_norm.issubset(normalized)


def parse_table_to_dataframe(table_tag: Tag, headers: list[str]) -> pd.DataFrame:
    if not headers:
        return pd.DataFrame()

    body_rows = table_tag.find_all("tr")
    records: list[dict[str, str]] = []

    for tr in body_rows:
        cells = tr.find_all("td")
        if not cells:
            continue

        row: dict[str, str] = {}
        for idx, cell in enumerate(cells):
            if idx >= len(headers):
                break
            header = headers[idx]

            link = cell.find("a", href=True)
            text = clean_text(cell.get_text(" ", strip=True))
            if normalize_header_key(header) == "link" and link:
                row[header] = clean_text(link.get("href", "")) or text
            else:
                row[header] = text

        if any(clean_text(v) for v in row.values()):
            records.append(row)

    if not records:
        return pd.DataFrame(columns=headers)

    df = pd.DataFrame(records)
    for col in headers:
        if col not in df.columns:
            df[col] = ""
    return df[headers]
