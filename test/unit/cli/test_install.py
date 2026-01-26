import pathlib
from test.unit.cli.cli_runner import CliRunner
from unittest import mock
from unittest.mock import (
    MagicMock,
)

import pytest
from _pytest.monkeypatch import MonkeyPatch

from exasol.exaslpm.cli import cli


@pytest.fixture
def cliRunner():
    return CliRunner(cli.install, True)


@pytest.fixture
def mock_install_packages(monkeypatch: MonkeyPatch) -> MagicMock:
    mock_function_to_mock = MagicMock()
    monkeypatch.setattr(cli, "package_install", mock_function_to_mock)
    return mock_function_to_mock


@pytest.fixture
def mock_history_manager(monkeypatch: MonkeyPatch) -> MagicMock:
    return_mock = MagicMock()
    mock_function_to_mock = MagicMock(return_value=return_mock)
    monkeypatch.setattr(cli, "HistoryFileManager", mock_function_to_mock)
    return return_mock


@pytest.fixture
def mock_binary_finder(monkeypatch: MonkeyPatch) -> MagicMock:
    return_mock = MagicMock()
    mock_function_to_mock = MagicMock(return_value=return_mock)
    monkeypatch.setattr(cli, "BinaryFinder", mock_function_to_mock)
    return return_mock


def test_mock_no_phase(cliRunner, mock_install_packages, some_package_file):
    ret = cliRunner.run("--package-file", some_package_file)
    assert ret.failed and "Missing option '--build-step'" in ret.output


def test_mock_no_package(cliRunner, mock_install_packages, some_package_file):
    ret = cliRunner.run("--phase", "Phase1")
    assert ret.failed and "Missing option '--package-file'" in ret.output


def test_mock_no_build_step(cliRunner, mock_install_packages, some_package_file):
    ret = cliRunner.run("--phase", "Phase1", "--package-file", some_package_file)
    assert ret.failed and "Missing option '--build-step'" in ret.output


def test_mock_all_options(
    cliRunner,
    mock_install_packages,
    some_package_file,
    python_binary,
    conda_binary,
    r_binary,
    mock_history_manager,
    mock_binary_finder,
):
    ret = cliRunner.run(
        "--phase",
        "Phase1",
        "--package-file",
        some_package_file,
        "--build-step",
        "udf_client",
        "--python-binary",
        python_binary,
        "--conda-binary",
        conda_binary,
        "--r-binary",
        r_binary,
    )
    assert ret.succeeded

    assert mock_install_packages.mock_calls == [
        mock.call(
            "Phase1",
            pathlib.PosixPath(some_package_file),
            "udf_client",
            pathlib.PosixPath(python_binary),
            pathlib.PosixPath(conda_binary),
            pathlib.PosixPath(r_binary),
            mock.ANY,
            mock.ANY,
            history_file_manager=mock_history_manager,
            binary_finder=mock_binary_finder,
        )
    ]
