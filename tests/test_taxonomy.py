from src.transforms.taxonomy import normalize_attack_label


def test_cve_and_vulnerability_are_unified():
    assert normalize_attack_label("CVE-2024-1234 exploitation") == "vulnerability"
    assert normalize_attack_label("Vulnerabilities") == "vulnerability"


def test_unknown_maps_to_unknown():
    assert normalize_attack_label("Unknown") == "unknown"
