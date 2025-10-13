import pathlib
from test.unit.cli.cli_runner import CliRunner
from unittest import mock

# from click.testing import CliRunner
from unittest.mock import (
    MagicMock,
    call,
)

import pytest
from _pytest.monkeypatch import MonkeyPatch

from exasol.exaslpm.cli import cli
from exasol.exaslpm.cli.cli import install


@pytest.fixture
def cliRunner():
    return CliRunner(cli.install, True)


@pytest.fixture
def mock_install_packages(monkeypatch: MonkeyPatch) -> MagicMock:
    mock_function_to_mock = MagicMock()
    monkeypatch.setattr(cli, "package_install", mock_function_to_mock)
    return mock_function_to_mock


def test_mock_no_phase(cliRunner, mock_install_packages, some_package_file):
    ret = cliRunner.run("--package-file", some_package_file)
    assert ret.failed and "Missing option '--phase'" in ret.output


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
    python_package_file,
    conda_package_file,
    r_package_file,
):
    ret = cliRunner.run(
        "--phase",
        "Phase1",
        "--package-file",
        some_package_file,
        "--build-step",
        "udf_client",
        "--python-binary",
        python_package_file,
        "--conda-binary",
        conda_package_file,
        "--r-binary",
        r_package_file,
    )
    assert ret.succeeded

    assert mock_install_packages.mock_calls == [
        mock.call(
            "Phase1",
            pathlib.PosixPath(some_package_file),
            "udf_client",
            pathlib.PosixPath(python_package_file),
            pathlib.PosixPath(conda_package_file),
            pathlib.PosixPath(r_package_file),
        )
    ]
