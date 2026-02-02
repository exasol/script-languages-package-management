from unittest.mock import (
    call,
)

import pytest

from exasol.exaslpm.model.package_file_config import (
    AptPackage,
)
from exasol.exaslpm.pkg_mgmt.context.cmd_executor import (
    CommandFailedException,
)
from exasol.exaslpm.pkg_mgmt.install_apt_packages import *


def test_empty_packages(context_mock):
    aptPackages = AptPackages(packages=[])
    install_apt_packages(aptPackages, context_mock)

    assert context_mock.cmd_logger.mock_calls == [
        call.warn("Got an empty list of AptPackages"),
    ]


def test_install_apt_packages(context_mock):
    pkgs = [
        AptPackage(name="curl", version="7.68.0"),
        AptPackage(name="requests", version="2.25.1"),
    ]
    aptPackages = AptPackages(packages=pkgs)
    install_apt_packages(aptPackages, context_mock)
    assert context_mock.cmd_executor.mock_calls == [
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
        call.execute(["locale-gen", "en_US.UTF-8"]),
        call.execute().print_results(),
        call.execute().return_code(),
        call.execute(["update-locale", "LC_ALL=en_US.UTF-8"]),
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


def build_context_with_fail_command_executor(ctx: Context, fail_step: int):
    fail_command_executor = FailCommandExecutor(fail_step)

    return Context(
        cmd_logger=ctx.cmd_logger,
        cmd_executor=fail_command_executor,
        history_file_manager=ctx.history_file_manager,
        binary_checker=ctx.binary_checker,
        file_downloader=ctx.file_downloader,
        temp_file_provider=ctx.temp_file_provider,
    )


@pytest.mark.parametrize(
    "fail_step, expected_error",
    [
        (0, "Failed while updating apt cmd"),
        (1, "Failed while installing apt cmd"),
        (2, "Failed while running apt clean"),
        (3, "Failed while running apt autoremove"),
        (4, "Failed while running locale-gen cmd"),
        (5, "Failed while running update-locale cmd"),
        (6, "Failed while running ldconfig"),
    ],
)
def test_install_apt_packages_negative_cases(context_mock, fail_step, expected_error):
    context = build_context_with_fail_command_executor(context_mock, fail_step)
    pkgs = [
        AptPackage(name="curl", version="7.68.0"),
        AptPackage(name="requests", version="2.25.1"),
    ]
    aptPackages = AptPackages(packages=pkgs)

    with pytest.raises(CommandFailedException):
        install_apt_packages(aptPackages, context)

    context.cmd_logger.err.assert_any_call(expected_error)
