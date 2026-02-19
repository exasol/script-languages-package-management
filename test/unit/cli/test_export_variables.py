import pathlib
from test.unit.cli.cli_runner import CliRunner
from unittest import mock
from unittest.mock import MagicMock

import pytest
from _pytest.monkeypatch import MonkeyPatch

import exasol.exaslpm.cli as cli
import exasol.exaslpm.cli.export_variables as export_variables_mod


@pytest.fixture
def cli_runner():
    return CliRunner(cli.export_variables_command, True)


@pytest.fixture
def mock_export_variables(monkeypatch: MonkeyPatch) -> MagicMock:
    mocked = MagicMock()
    monkeypatch.setattr(export_variables_mod, "export_variables", mocked)
    return mocked


@pytest.fixture
def mock_context(monkeypatch: MonkeyPatch) -> MagicMock:
    context = MagicMock()
    mocked = MagicMock(return_value=context)
    monkeypatch.setattr(export_variables_mod, "make_context", mocked)
    return context


def test_export_variables_without_filename(
    cli_runner, mock_export_variables, mock_context
):
    ret = cli_runner.run()
    assert ret.succeeded

    assert mock_export_variables.mock_calls == [
        mock.call(context=mock_context, output_file=None)
    ]


def test_export_variables_with_filename(
    cli_runner, mock_export_variables, mock_context
):
    ret = cli_runner.run("--out-file", "variables.sh")
    assert ret.succeeded

    assert mock_export_variables.mock_calls == [
        mock.call(context=mock_context, output_file=pathlib.PosixPath("variables.sh"))
    ]
