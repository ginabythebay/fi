from pathlib import Path

import pytest

import main


def verify_src_name(name: str, expected_year: int, expected_who: str) -> None:
    path = Path(name)
    p = main.is_src(path)
    assert p.year == expected_year
    assert p.sender == expected_who

def fail_src_name(name: str) -> None:
    assert not main.is_src(Path(name))

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
