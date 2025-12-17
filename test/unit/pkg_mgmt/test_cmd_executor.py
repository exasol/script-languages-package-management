import subprocess
from unittest.mock import (
    MagicMock,
    Mock,
    call,
)

import pytest

from exasol.exaslpm.pkg_mgmt.cmd_executor import (
    CommandExecutor,
    CommandLogger,
    CommandResult,
    StdLogger,
)


def mock_command_result(logger: CommandLogger):
    fn_ret_code = lambda: 10
    stdout_iter = iter(["stdout line 1", "stdout line 2"])
    stderr_iter = iter(["stderr line 1", "stderr line 2", "stderr line 3"])
    return CommandResult(
        fn_ret_code=fn_ret_code,
        stdout=stdout_iter,
        stderr=stderr_iter,
        logger=logger,
    )


def test_command_executor(monkeypatch):
    mock_popen = MagicMock()
    monkeypatch.setattr(subprocess, "Popen", mock_popen)

    logger = MagicMock(spec=CommandLogger)
    executor = CommandExecutor(logger)
    result = executor.execute(["cmd1", "cmd2"])
    ret_code = result.return_code()
    assert mock_popen.mock_calls == [
        call(["cmd1", "cmd2"], stdout=-1, stderr=-1, text=True),
        call().stdout.__iter__(),
        call().stderr.__iter__(),
        call().wait(),
    ]
    assert ret_code == mock_popen.return_value.wait.return_value


def test_command_results(monkeypatch):
    call_counts = {"stdout": 0, "stderr": 0}
    logger = MagicMock(spec=CommandLogger)
    info_log = MagicMock()
    err_log = MagicMock()
    logger.info.side_effect = lambda msg: info_log.log(msg)
    logger.err.side_effect = lambda msg: err_log.log(msg)

    def mock_execute(cmd_strs):
        return mock_command_result(logger)

    def stdout_results(result_str: str):
        call_counts["stdout"] += 1
        expected = "stdout line " + str(call_counts["stdout"])
        assert expected == result_str

    def stderr_results(result_str: str):
        call_counts["stderr"] += 1
        expected = "stderr line " + str(call_counts["stderr"])
        assert expected == result_str

    cmd_executor = CommandExecutor(logger)
    monkeypatch.setattr(cmd_executor, "execute", mock_execute)
    result = cmd_executor.execute(["cmd1", "cmd2"])
    assert result.return_code() == 10
    return_code = result.consume_results(stdout_results, stderr_results)
    assert call_counts["stdout"] == 2
    assert call_counts["stderr"] == 3
    assert return_code == 10
    result.print_results()
    info_log.assert_called()
    err_log.assert_called()
