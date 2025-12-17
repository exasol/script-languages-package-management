from unittest.mock import (
    MagicMock,
    Mock,
    call,
)

import pytest

from exasol.exaslpm.model.package_file_config import (
    AptPackages,
    Package,
)
from exasol.exaslpm.pkg_mgmt.cmd_executor import (
    CommandExecutor,
    CommandResult,
    StdLogger,
)
from exasol.exaslpm.pkg_mgmt.install_apt import *

order_of_exec = ["update", "install", "clean", "remove", "locale", "ldconfig"]
call_count = 0


def mock_execute(_, cmd_strs):
    global call_count
    cmd_str = " ".join(cmd_strs)
    assert order_of_exec[call_count] in cmd_str
    call_count += 1
    return CommandResult(
        fn_ret_code=lambda: 0, stdout=iter([]), stderr=iter([]), logger=StdLogger()
    )


def test_install_via_apt_empty_packages():
    mock_logger = MagicMock()
    mock_executor = MagicMock(spec=CommandExecutor)
    aptPackages = AptPackages(packages=[])
    install_via_apt(aptPackages, mock_executor, mock_logger)

    found_log = False
    for call in mock_logger.mock_calls:
        args = call.args
        if args and "empty list" in str(args[0]):
            found_log = True
            break
    assert found_log


def test_install_via_apt_01():
    mock_executor = MagicMock(spec=CommandExecutor)
    pkgs = [
        Package(name="curl", version="7.68.0"),
        Package(name="requests", version="2.25.1"),
    ]
    aptPackages = AptPackages(packages=pkgs)
    install_via_apt(aptPackages, mock_executor, StdLogger())
    assert mock_executor.mock_calls == [
        call.execute(["apt-get", "-y", "update"]),
        call.execute().print_results(),
        call.execute(
            [
                "apt-get",
                "install",
                "-V",
                "-y",
                "--no-install-recommends",
                "curl=7.68.0",
                "requests=2.25.1",
            ]
        ),
        call.execute().print_results(),
        call.execute(["apt-get", "-y", "clean"]),
        call.execute().print_results(),
        call.execute(["apt-get", "-y", "autoremove"]),
        call.execute().print_results(),
        call.execute(["locale-gen", "&&", "update-locale", "LANG=en_US.UTF8"]),
        call.execute().print_results(),
        call.execute(["ldconfig"]),
        call.execute().print_results(),
    ]


# For Sonar Cube Code Coverage - ToDo: Check once if it complains
def test_prepare_update_command():
    cmd_strs = prepare_update_command()
    cmd_str = " ".join(cmd_strs)
    assert "apt-get" in cmd_str
    assert "update" in cmd_str


def test_prepare_clean_cmd():
    cmd_strs = prepare_clean_cmd()
    cmd_str = " ".join(cmd_strs)
    assert "apt-get" in cmd_str
    assert "clean" in cmd_str


def test_prepare_autoremove_cmd():
    cmd_strs = prepare_autoremove_cmd()
    cmd_str = " ".join(cmd_strs)
    assert "apt-get" in cmd_str
    assert "remove" in cmd_str


def test_prepare_locale_cmd():
    cmd_strs = prepare_locale_cmd()
    cmd_str = " ".join(cmd_strs)
    assert "locale" in cmd_str


def test_prepare_ldconfig_cmd():
    cmd_strs = prepare_ldconfig_cmd()
    cmd_str = " ".join(cmd_strs)
    assert "ldconfig" in cmd_str
