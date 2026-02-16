from unittest.mock import MagicMock

import pytest

from exasol.exaslpm.model.package_file_config import AptPackage
from exasol.exaslpm.pkg_mgmt.context.cmd_executor import CommandFailedException
from exasol.exaslpm.pkg_mgmt.context.context import Context
from exasol.exaslpm.pkg_mgmt.search.apt_madison_parser import (
    MadisonData,
    MadisonExecutor,
    MadisonParser,
)


def test_madison_parser_empty():
    madison_out = ""
    madison_dict = MadisonParser.parse_madison_output(madison_out)
    assert madison_dict == {}


def test_madision_proper_output():
    madison_out = """gpg | 2.4.3-2ubuntu17.4 | http://archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages
gpg | 2.4.4-2ubuntu17.4 | http://archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages |
vim | 2:9.1.0015-1ubuntu7.9 | http://archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages |
vim | 2:9.1.0016-1ubuntu7.9 | http://security.ubuntu.com/ubuntu noble-security/main amd64 Packages |
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


# Madison Executor tests


def test_madison_executor_empty_list():
    ctx = MagicMock(spec=Context)
    madison_out = MadisonExecutor.execute_madison([], ctx)
    assert madison_out == ""


def test_execute_madison_empty_package_list():
    ctx = MagicMock()
    result = MadisonExecutor.execute_madison([], ctx)
    assert result == ""


def test_execute_madison_single_package():
    ctx = MagicMock()
    cmd_result = MagicMock()
    ctx.cmd_executor.execute.return_value = cmd_result

    def consume_results_side_effect(stdout_cb, stderr_cb):
        stdout_cb(
            "gpg | 2.4.4-2ubuntu17.4 | http://archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages",
            None,
        )
        return 0

    cmd_result.consume_results.side_effect = consume_results_side_effect
    pkg_list = [AptPackage(name="gpg", version="2.4.4-2ubuntu17.4")]
    result = MadisonExecutor.execute_madison(pkg_list, ctx)

    assert (
        result
        == "gpg | 2.4.4-2ubuntu17.4 | http://archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages"
    )
    ctx.cmd_executor.execute.assert_called_once_with(["apt-cache", "madison", "gpg"])


def test_execute_madison_multiple_packages():
    ctx = MagicMock()
    cmd_result = MagicMock()
    ctx.cmd_executor.execute.return_value = cmd_result

    def consume_results_side_effect(stdout_cb, stderr_cb):
        stdout_cb(
            "gpg | 2.4.4-2ubuntu17.4 | http://archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages",
            None,
        )
        stdout_cb(
            "vim | 2:9.1.0016-1ubuntu7.9 | http://archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages",
            None,
        )
        return 0

    cmd_result.consume_results.side_effect = consume_results_side_effect
    pkg_list = [
        AptPackage(name="gpg", version="2.4.4-2ubuntu17.4"),
        AptPackage(name="vim", version="2:9.1.0016-1ubuntu7.9"),
    ]

    result = MadisonExecutor.execute_madison(pkg_list, ctx)
    assert "gpg | 2.4.4-2ubuntu17.4" in result
    assert "vim | 2:9.1.0016-1ubuntu7.9" in result
    ctx.cmd_executor.execute.assert_called_once_with(
        ["apt-cache", "madison", "gpg", "vim"]
    )


def test_execute_madison_command_failure():
    ctx = MagicMock()
    cmd_result = MagicMock()
    ctx.cmd_executor.execute.return_value = cmd_result

    def consume_results_side_effect(stdout_cb, stderr_cb):
        return 1

    cmd_result.consume_results.side_effect = consume_results_side_effect
    pkg_list = [AptPackage(name="gpg", version="2.4.4-2ubuntu17.4")]

    with pytest.raises(CommandFailedException) as exc_info:
        MadisonExecutor.execute_madison(pkg_list, ctx)
    assert str(exc_info.value) == "Failed executing madison"


def test_execute_madison_stderr_ignored():
    ctx = MagicMock()
    cmd_result = MagicMock()
    ctx.cmd_executor.execute.return_value = cmd_result
    stderr_cb_called = False

    def consume_results_side_effect(stdout_cb, stderr_cb):
        nonlocal stderr_cb_called
        stdout_cb(
            "gpg | 2.4.4-2ubuntu17.4 | http://archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages",
            None,
        )
        stderr_cb("some warning", None)
        stderr_cb_called = True
        return 0

    cmd_result.consume_results.side_effect = consume_results_side_effect
    pkg_list = [AptPackage(name="gpg", version="2.4.4-2ubuntu17.4")]
    result = MadisonExecutor.execute_madison(pkg_list, ctx)

    assert stderr_cb_called is True
    assert (
        result
        == "gpg | 2.4.4-2ubuntu17.4 | http://archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages"
    )


def test_execute_madison_empty_output():
    ctx = MagicMock()
    cmd_result = MagicMock()
    ctx.cmd_executor.execute.return_value = cmd_result

    def consume_results_side_effect(stdout_cb, stderr_cb):
        return 0

    cmd_result.consume_results.side_effect = consume_results_side_effect
    pkg_list = [AptPackage(name="nonexistent", version="1.0")]

    result = MadisonExecutor.execute_madison(pkg_list, ctx)
    assert result == ""


def test_parse_madison_output_empty_string():
    result = MadisonParser.parse_madison_output("")
    assert result == {}


def test_parse_madison_output_none():
    result = MadisonParser.parse_madison_output(None)
    assert result == {}


def test_parse_madison_output_multiple_versions_same_package():
    madison_out = """gpg | 2.4.4-2ubuntu17.4 | http://archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages
gpg | 2.4.4-2ubuntu17 | http://archive.ubuntu.com/ubuntu noble/main amd64 Packages"""
    result = MadisonParser.parse_madison_output(madison_out)

    assert len(result["gpg"]) == 2
    assert result["gpg"][0].ver == "2.4.4-2ubuntu17.4"
    assert result["gpg"][1].ver == "2.4.4-2ubuntu17"


def test_parse_madison_output_with_whitespace():
    madison_out = "  gpg  |  2.4.4-2ubuntu17.4  |  http://archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages  "
    result = MadisonParser.parse_madison_output(madison_out)
    assert "gpg" in result
    assert result["gpg"][0].ver == "2.4.4-2ubuntu17.4"
    assert (
        result["gpg"][0].tail
        == "http://archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages"
    )
