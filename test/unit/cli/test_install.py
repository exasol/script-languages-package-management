from test.unit.cli.cli_runner import CliRunner

# from click.testing import CliRunner
from unittest.mock import (
    MagicMock,
    call,
)

import pytest
from _pytest.monkeypatch import MonkeyPatch

from exasol.exaslpm.cli import cli
from exasol.exaslpm.cli.cli import (
    install,
    install_packages,
)


@pytest.fixture
def cliRunner():
    return CliRunner(cli.install, True)


@pytest.fixture
def mock_install_packages(monkeypatch: MonkeyPatch) -> MagicMock:
    mock_function_to_mock = MagicMock()
    monkeypatch.setattr(cli, "install_packages", mock_function_to_mock)
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


def test_mock_no_python_binary(cliRunner, mock_install_packages, some_package_file):
    ret = cliRunner.run(
        "--phase",
        "Phase1",
        "--package-file",
        some_package_file,
        "--build-step",
        "udf_client",
    )
    assert ret.failed and "Missing option '--python-binary'" in ret.output


def test_mock_no_conda_binary(cliRunner, mock_install_packages, some_package_file):
    ret = cliRunner.run(
        "--phase",
        "Phase1",
        "--package-file",
        some_package_file,
        "--build-step",
        "udf_client",
        "--python-binary",
        some_package_file,
    )
    assert ret.failed and "Missing option '--conda-binary'" in ret.output


def test_mock_no_r_binary(cliRunner, mock_install_packages, some_package_file):
    ret = cliRunner.run(
        "--phase",
        "Phase1",
        "--package-file",
        some_package_file,
        "--build-step",
        "udf_client",
        "--python-binary",
        some_package_file,
        "--conda-binary",
        some_package_file,
    )
    assert ret.failed and "Missing option '--r-binary'" in ret.output


def test_mock_all_options(cliRunner, mock_install_packages, some_package_file):
    ret = cliRunner.run(
        "--phase",
        "Phase1",
        "--package-file",
        some_package_file,
        "--build-step",
        "udf_client",
        "--python-binary",
        some_package_file,
        "--conda-binary",
        some_package_file,
        "--r-binary",
        some_package_file,
    )
    assert ret.succeeded
