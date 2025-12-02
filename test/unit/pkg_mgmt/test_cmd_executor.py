import subprocess
from unittest.mock import (
    MagicMock,
    Mock,
    call,
)

import pytest

from exasol.exaslpm.pkg_mgmt.cmd_executor import (
    CommandExecutor,
    CommandResult,
    StdLogger,
)


@pytest.fixture
def mock_command_result():
    logger = StdLogger()
    fn_ret_code = lambda: 10
    stdout_iter = iter(["stdout line 1", "stdout line 2"])
    stderr_iter = iter(["stderr line 1", "stderr line 2", "stderr line 3"])
    return CommandResult(
        logger, fn_ret_code=fn_ret_code, stdout=stdout_iter, stderr=stderr_iter
    )


def test_command_executor(monkeypatch):
    mock_popen = MagicMock()
    monkeypatch.setattr(subprocess, "Popen", mock_popen)

    executor = CommandExecutor(StdLogger())
    result = executor.execute(["cmd1", "cmd2"])
    ret_code = result.return_code()
    assert mock_popen.mock_calls == [
        call(["cmd1", "cmd2"], stdout=-1, stderr=-1, text=True),
        call().stdout.__iter__(),
        call().stderr.__iter__(),
        call().wait(),
    ]
    assert ret_code == mock_popen.return_value.wait.return_value


def test_command_results(monkeypatch, mock_command_result):
    call_counts = {"stdout": 0, "stderr": 0}

    def mock_execute(_, cmd_strs):
        return mock_command_result

    def stdout_results(result_str: str):
        call_counts["stdout"] += 1
        expected = "stdout line " + str(call_counts["stdout"])
        assert expected == result_str

    def stderr_results(result_str: str):
        call_counts["stderr"] += 1
        expected = "stderr line " + str(call_counts["stderr"])
        assert expected == result_str

    monkeypatch.setattr(CommandExecutor, "execute", mock_execute)
    executor = CommandExecutor(StdLogger())
    result = executor.execute(["cmd1", "cmd2"])
    assert result.return_code() == 10
    return_code = result.consume_results(stdout_results, stderr_results)
    assert call_counts["stdout"] == 2
    assert call_counts["stderr"] == 3
    assert return_code == 10
    result.print_results()
