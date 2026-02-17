import pytest

from exasol.exaslpm.pkg_mgmt.search.apt_madison_parser import (
    MadisonData,
    MadisonParser,
)


def test_madison_parser_empty():
    madison_out = ""
    madison_dict = MadisonParser.parse_madison_output(madison_out)
    assert madison_dict == {}


def test_madision_proper_output():
    madison_out = """gpg | 2.4.3-2ubuntu17.4 | http://archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages
gpg | 2.4.4-2ubuntu17.4 | http://archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages
vim | 2:9.1.0015-1ubuntu7.9 | http://archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages
vim | 2:9.1.0016-1ubuntu7.9 | http://security.ubuntu.com/ubuntu noble-security/main amd64 Packages
"""
    madison_dict = MadisonParser.parse_madison_output(madison_out)
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


def test_madision_negative_output():
    # only 2 columns instead of 3, should raise ValueError
    madison_out = """gpg | 2.4.3-2ubuntu17.4 
gpg | 2.4.4-2ubuntu17.4 
"""
    with pytest.raises(ValueError):
        MadisonParser.parse_madison_output(madison_out)
