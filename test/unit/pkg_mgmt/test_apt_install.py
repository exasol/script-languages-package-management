from unittest.mock import (
    MagicMock,
    call,
    patch,
)

import pytest

from exasol.exaslpm.model.package_file_config import (
    AptPackages,
    Package,
)
from exasol.exaslpm.pkg_mgmt.cmd_executor import (
    CommandExecutor,
    CommandLogger,
    CommandResult,
    StdLogger,
)
from exasol.exaslpm.pkg_mgmt.install_apt import *


class CaptureLogger:
    def __init__(self):
        self.messages = []

    def info(self, msg: str, **kwargs):
        self.messages.append(msg)

    def warn(self, msg: str, **kwargs):
        self.messages.append(msg)

    def err(self, msg: str, **kwargs):
        self.messages.append(msg)


def test_install_via_apt_empty_packages():
    mock_logger = CaptureLogger()
    mock_executor = MagicMock(spec=CommandExecutor)
    aptPackages = AptPackages(packages=[])
    install_via_apt(aptPackages, mock_executor, mock_logger)

    assert any("empty list" in msg for msg in mock_logger.messages)


def test_install_via_apt_with_pkgs():
    mock_executor = MagicMock(spec=CommandExecutor)
    mock_command_result = MagicMock(spec=CommandResult)
    mock_executor.execute.return_value = mock_command_result
    mock_command_result.return_code.return_value = 0
    mock_logger = MagicMock(spec=CommandLogger)
    pkgs = [
        Package(name="curl", version="7.68.0"),
        Package(name="requests", version="2.25.1"),
    ]
    aptPackages = AptPackages(packages=pkgs)
    install_via_apt(aptPackages, mock_executor, mock_logger)
    assert mock_executor.mock_calls == [
        call.execute(["apt-get", "-y", "update"]),
        call.execute().print_results(),
        call.execute().return_code(),
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
        call.execute().return_code(),
        call.execute(["apt-get", "-y", "clean"]),
        call.execute().print_results(),
        call.execute().return_code(),
        call.execute(["apt-get", "-y", "autoremove"]),
        call.execute().print_results(),
        call.execute().return_code(),
        call.execute(["locale-gen", "&&", "update-locale", "LANG=en_US.UTF8"]),
        call.execute().print_results(),
        call.execute().return_code(),
        call.execute(["ldconfig"]),
        call.execute().print_results(),
        call.execute().return_code(),
    ]


class FailCommandResult:
    def __init__(self, ret_code):
        self._ret_code = ret_code

    def print_results(self):
        pass

    def return_code(self):
        return self._ret_code


class FailCommandExecutor:
    def __init__(self, fail_at_step):
        self.fail_step = fail_at_step
        self.count = 0

    def execute(self, cmd):
        self.count += 1
        step_index = self.count - 1
        if step_index == self.fail_step:
            return FailCommandResult(1)
        return FailCommandResult(0)


@pytest.mark.parametrize(
    "fail_step, expected_error",
    [
        (0, "Failed while updating apt cmd"),
        (1, "Failed while installing apt cmd"),
        (2, "Failed while cleaning apt cmd"),
        (3, "Failed while autoremoving apt cmd"),
        (4, "Failed while preparing apt cmd"),
        (5, "Failed while ldconfig apt cmd"),
    ],
)
def test_install_via_apt_negative_cases(fail_step, expected_error):
    logger = CaptureLogger()
    cmd_executor = FailCommandExecutor(fail_step)

    pkgs = [
        Package(name="curl", version="7.68.0"),
        Package(name="requests", version="2.25.1"),
    ]
    aptPackages = AptPackages(packages=pkgs)
    install_via_apt(aptPackages, cmd_executor, logger)
    assert any(expected_error in msg for msg in logger.messages)


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
