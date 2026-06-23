from test.unit.cli.cli_runner import CliRunner

import pytest

import exasol.exaslpm.cli as cli
from exasol.exaslpm import __version__ as exaslpm_version


@pytest.fixture
def cli_runner():
    return CliRunner(cli.cli, True)


def test_root_help(cli_runner):
    ret = cli_runner.run("--help")
    assert ret.succeeded
    assert "EXASLPM - Exasol Script Languages Package Management" in ret.output
    assert "Commands:" in ret.output
    assert "install" in ret.output
    assert "export-variables" in ret.output
    assert "list-all-installed-packages" in ret.output


def test_root_version(cli_runner):
    ret = cli_runner.run("--version")
    assert ret.succeeded
    assert f"version {exaslpm_version}" in ret.output
