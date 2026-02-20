import pytest

from exasol.exaslpm.pkg_mgmt.context.context import Context
from exasol.exaslpm.pkg_mgmt.search.apt_madison_parser import (
    MadisonData,
    MadisonParser,
)


def test_madison_parser_empty(context_mock: Context):
    madison_out = ""
    madison_dict = MadisonParser.parse_madison_output(madison_out, context_mock)
    assert madison_dict == {}


def test_madision_proper_output(context_mock: Context):
    madison_out = """gpg | 2.4.3-2ubuntu17.4 | http://archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages
gpg | 2.4.4-2ubuntu17.4 | http://archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages
vim | 2:9.1.0015-1ubuntu7.9 | http://archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages
vim | 2:9.1.0016-1ubuntu7.9 | http://security.ubuntu.com/ubuntu noble-security/main amd64 Packages
"""
    madison_dict = MadisonParser.parse_madison_output(madison_out, context_mock)
    assert madison_dict == {
        "gpg": [
            MadisonData(
                "2.4.3-2ubuntu17.4",
                "http://archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages",
            ),
            MadisonData(
                "2.4.4-2ubuntu17.4",
                "http://archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages",
            ),
        ],
        "vim": [
            MadisonData(
                "2:9.1.0015-1ubuntu7.9",
                "http://archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages",
            ),
            MadisonData(
                "2:9.1.0016-1ubuntu7.9",
                "http://security.ubuntu.com/ubuntu noble-security/main amd64 Packages",
            ),
        ],
    }


def test_madision_missing_columns(context_mock: Context):
    madison_out = """gpg | 2.4.3-2ubuntu17.4 
gpg | 2.4.4-2ubuntu17.4 
"""
    with pytest.raises(ValueError):
        MadisonParser.parse_madison_output(madison_out, context_mock)


def test_parse_madison_output_invalid_line(context_mock: Context):
    madison_out = """gpg | 2.4.3-2ubuntu17.4 | http://archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages
invalid line without proper format
"""
    with pytest.raises(ValueError):
        MadisonParser.parse_madison_output(madison_out, context_mock)


def test_parse_madison_output_empty_lines(context_mock: Context):
    madison_out = """gpg | 2.4.3-2ubuntu17.4 | http://archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages

gpg | 2.4.4-2ubuntu17.4 | http://archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages
"""
    madison_dict = MadisonParser.parse_madison_output(madison_out, context_mock)
    assert madison_dict == {
        "gpg": [
            MadisonData(
                "2.4.3-2ubuntu17.4",
                "http://archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages",
            ),
            MadisonData(
                "2.4.4-2ubuntu17.4",
                "http://archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages",
            ),
        ]
    }


def test_madison_parser_output_with_extra_columns(context_mock: Context):
    madison_out = """gpg | 2.4.3-2ubuntu17.4 | http://archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages | extra column
gpg | 2.4.4-2ubuntu17.4 | http://archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages | extra column
"""
    with pytest.raises(ValueError):
        MadisonParser.parse_madison_output(madison_out, context_mock)


def test_madison_parser_output_with_empty_columns(context_mock: Context):
    madison_out = " | 2.4.3-2ubuntu17  | \n | | http://archive.ubuntu.com/ubuntu"
    with pytest.raises(ValueError):
        MadisonParser.parse_madison_output(madison_out, context_mock)


def test_madison_is_match():
    assert MadisonData.is_match("2.4.3-2ubuntu17.4", "2.4.3-2ubuntu17.4")
    assert not MadisonData.is_match("2.5.3-2ubuntu17.4", "2.4.*")
    assert MadisonData.is_match("2.4.3-2ubuntu17.4", "2.4.*")
    assert MadisonData.is_match("2.4.2-2ubuntu17.4", "2.4.*")
    assert MadisonData.is_match("2.4.3-2ubuntu17.4", "2.*-2ubuntu17.4")
    assert not MadisonData.is_match("2.4.3-2ubuntu17.4", "3.*")
    assert MadisonData.is_match("2.4.3-2ubuntu17.4", "")
