from unittest.mock import MagicMock

import pytest

from exasol.exaslpm.model.package_file_config import AptPackage
from exasol.exaslpm.pkg_mgmt.context.cmd_executor import CommandFailedException
from exasol.exaslpm.pkg_mgmt.context.context import Context
from exasol.exaslpm.pkg_mgmt.search.apt_madison_parser import (
    MadisonExecutor,
    MadisonParser,
)


def test_madison_executor_empty_list(context_mock: Context):
    madison_out = MadisonExecutor.execute_madison([], context_mock)
    assert madison_out == ""


def test_execute_madison_single_package(context_mock: Context):
    cmd_result = MagicMock()
    context_mock.cmd_executor.execute.return_value = cmd_result

    def consume_results_side_effect(stdout_cb, stderr_cb):
        stdout_cb(
            "gpg | 2.4.4-2ubuntu17.4 | http://archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages"
        )
        return 0

    cmd_result.consume_results.side_effect = consume_results_side_effect
    pkg_list = [AptPackage(name="gpg", version="2.4.4-2ubuntu17.4")]
    result = MadisonExecutor.execute_madison(pkg_list, context_mock)

    assert (
        result
        == "gpg | 2.4.4-2ubuntu17.4 | http://archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages"
    )
    context_mock.cmd_executor.execute.assert_called_once_with(
        ["apt-cache", "madison", "gpg"]
    )


def test_execute_madison_multiple_packages(context_mock: Context):
    cmd_result = MagicMock()
    context_mock.cmd_executor.execute.return_value = cmd_result

    def consume_results_side_effect(stdout_cb, stderr_cb):
        stdout_cb(
            "gpg | 2.4.4-2ubuntu17.4 | http://archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages"
        )
        stdout_cb(
            "vim | 2:9.1.0016-1ubuntu7.9 | http://archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages"
        )
        return 0

    cmd_result.consume_results.side_effect = consume_results_side_effect
    pkg_list = [
        AptPackage(name="gpg", version="2.4.4-2ubuntu17.4"),
        AptPackage(name="vim", version="2:9.1.0016-1ubuntu7.9"),
    ]

    result = MadisonExecutor.execute_madison(pkg_list, context_mock)
    assert "gpg | 2.4.4-2ubuntu17.4" in result
    assert "vim | 2:9.1.0016-1ubuntu7.9" in result
    context_mock.cmd_executor.execute.assert_called_once_with(
        ["apt-cache", "madison", "gpg", "vim"]
    )


def test_execute_madison_command_failure(context_mock: Context):
    cmd_result = MagicMock()
    context_mock.cmd_executor.execute.return_value = cmd_result

    cmd_result.consume_results.side_effect = lambda stdout_cb, stderr_cb: 1
    pkg_list = [AptPackage(name="gpg", version="2.4.4-2ubuntu17.4")]

    with pytest.raises(CommandFailedException) as exc_info:
        MadisonExecutor.execute_madison(pkg_list, context_mock)
    assert str(exc_info.value) == "Failed executing madison"


def test_execute_madison_empty_output(context_mock: Context):
    cmd_result = MagicMock()
    context_mock.cmd_executor.execute.return_value = cmd_result

    def consume_results_side_effect(stdout_cb, stderr_cb):
        return 0

    cmd_result.consume_results.side_effect = consume_results_side_effect
    pkg_list = [AptPackage(name="nonexistent", version="1.0")]

    result = MadisonExecutor.execute_madison(pkg_list, context_mock)
    assert result == ""


def test_parse_madison_output_empty_string(context_mock: Context):
    result = MadisonParser.parse_madison_output("", context_mock)
    assert result == {}


def test_parse_madison_output_none(context_mock: Context):
    result = MadisonParser.parse_madison_output(None, context_mock)
    assert result == {}


def test_parse_madison_output_with_whitespace(context_mock: Context):
    madison_out = "  gpg  |  2.4.4-2ubuntu17.4  |  http://archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages  "
    result = MadisonParser.parse_madison_output(madison_out, context_mock)
    assert "gpg" in result
    assert result["gpg"][0].version == "2.4.4-2ubuntu17.4"
    assert (
        result["gpg"][0].tail
        == "http://archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages"
    )
