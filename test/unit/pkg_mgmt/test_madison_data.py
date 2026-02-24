import pytest

from exasol.exaslpm.pkg_mgmt.search.apt_madison_parser import MadisonData


@pytest.mark.parametrize(
    "text, pattern, expected",
    [
        ("2.4.3-2ubuntu17.4", "2.4.3-2ubuntu17.4", True),
        ("2.5.3-2ubuntu17.4", "2.4.*", False),
        ("2.4.3-2ubuntu17.4", "2.4.*", True),
        ("2.4.2-2ubuntu17.4", "2.4.*", True),
        ("2.4.3-2ubuntu17.4", "2.*-2ubuntu17.4", True),
        ("2.4.3-2ubuntu17.4", "3.*", False),
    ],
)
def test_madison_is_match(text, pattern, expected):
    assert MadisonData.is_match(text, pattern) == expected


@pytest.mark.parametrize(
    "text, pattern",
    [
        ("", "2.4.3-2ubuntu17.4"),
        ("2.4.3-2ubuntu17.4", ""),
    ],
)
def test_madison_is_match_raises(text, pattern):
    with pytest.raises(ValueError):
        MadisonData.is_match(text, pattern)
