from src.transforms.dates import parse_hackmageddon_date


def test_parse_explicit_ddmmyyyy_date():
    result = parse_hackmageddon_date("14/02/2024")
    assert result.parsed_iso == "2024-02-14"
    assert result.status == "parsed"


def test_keep_vague_dates_without_conversion():
    result = parse_hackmageddon_date("Recently")
    assert result.parsed_iso is None
    assert result.status == "vague"
