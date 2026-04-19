from src.utils.validation import (
    is_timeline_category_page_url,
    is_timeline_post_url,
    is_year_archive_page_url,
)


def test_timeline_post_url_accepts_dated_post():
    url = "https://www.hackmageddon.com/2024/11/21/16-31-august-2024-cyber-attacks-timeline"
    assert is_timeline_post_url(url)


def test_timeline_post_url_rejects_category_page():
    url = "https://www.hackmageddon.com/category/security/cyber-attacks-timeline"
    assert not is_timeline_post_url(url)
    assert is_timeline_category_page_url(url)


def test_year_archive_page_detection():
    assert is_year_archive_page_url("https://www.hackmageddon.com/2023/", year=2023)
    assert is_year_archive_page_url("https://www.hackmageddon.com/2023/page/2/", year=2023)
    assert not is_year_archive_page_url(
        "https://www.hackmageddon.com/2023/11/02/1-15-september-2023-cyber-attacks-timeline",
        year=2023,
    )
