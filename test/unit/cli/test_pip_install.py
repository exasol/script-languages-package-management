from test.unit.cli.cli_runner import CliRunner
from unittest.mock import (
    MagicMock,
    call,
)

import pytest
from _pytest.monkeypatch import MonkeyPatch

from exasol.script_languages_package_management.cli.commands import (
    r
)


@pytest.fixture
def cli():
    return CliRunner(r.install)


@pytest.fixture
def mock_install_packages(monkeypatch: MonkeyPatch) -> MagicMock:
    mock_function_to_mock = MagicMock()
    monkeypatch.setattr(
        r,
        "install_packages",
        mock_function_to_mock,
    )
    return mock_function_to_mock


def test_mock_deploy_ci_build_fail_without_package_file(cli, mock_install_packages):
    assert (
        cli.run().failed
        and "Missing option '--package-file'" in cli.output
    )

def test_mock_deploy_ci(cli, mock_install_packages, some_package_file):
    cli.run("--package-file", some_package_file)
    assert cli.succeeded

    # Validate the exact call using mock_calls and IsInstance matcher
    expected_call = call(some_package_file)
    assert mock_install_packages.mock_calls == [expected_call]
