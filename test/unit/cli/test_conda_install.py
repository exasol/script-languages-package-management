from test.unit.cli.cli_runner import CliRunner
from unittest.mock import (
    MagicMock,
    call,
)

import pytest
from _pytest.monkeypatch import MonkeyPatch

from exasol.script_languages_package_management.cli.commands import conda


@pytest.fixture
def cli():
    return CliRunner(conda.install)


@pytest.fixture
def mock_install_packages(monkeypatch: MonkeyPatch) -> MagicMock:
    mock_function_to_mock = MagicMock()
    monkeypatch.setattr(
        conda,
        "install_packages",
        mock_function_to_mock,
    )
    return mock_function_to_mock


def test_mock_deploy_ci_build_fail_without_package_file(cli, mock_install_packages):
    assert cli.run().failed and "Missing option '--package-file'" in cli.output


def test_mock_deploy_ci_build_fail_without_channel_file(
    cli, mock_install_packages, some_package_file
):
    assert (
        cli.run("--package-file", some_package_file).failed
        and "Missing option '--channel-file'" in cli.output
    )


def test_mock_deploy_ci(cli, mock_install_packages, some_package_file):
    cli.run("--package-file", some_package_file, "--channel-file", some_package_file)
    assert cli.succeeded

    # Validate the exact call using mock_calls and IsInstance matcher
    expected_call = call(some_package_file, some_package_file)
    assert mock_install_packages.mock_calls == [expected_call]
