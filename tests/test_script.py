import pytest

import main


def verify_src_name(name: str, expected_year: int, expected_who: str) -> None:
    year, who = main.is_src_name(name)
    assert year == expected_year
    assert who == expected_who

def fail_src_name(name: str) -> None:
    year, who = main.is_src_name(name)
    assert not year
    assert not who

def test_is_src_name():
    verify_src_name('20251201_bigco', 2025, 'bigco')
    verify_src_name('20251201_bigco_foo', 2025, 'bigco')
    fail_src_name('2025120101_bigco_foo')
    fail_src_name('18991201_bigco')
    fail_src_name('20251a01_bigco')
    fail_src_name('20250001_bigco')
    fail_src_name('20250100_bigco')
    fail_src_name('20251303_bigco')
    fail_src_name('29251232_bigco')
