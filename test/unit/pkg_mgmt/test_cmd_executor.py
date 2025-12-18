import subprocess
from unittest.mock import (
    MagicMock,
    call,
)

import pytest

from exasol.exaslpm.pkg_mgmt.cmd_executor import (
    CommandExecutor,
    CommandLogger,
    CommandResult,
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


def test_command_results():
    logger = MagicMock(spec=CommandLogger)
    cmd_result = mock_command_result(logger)
    ret_code = cmd_result.consume_results(logger.info, logger.err)
    assert logger.info.call_count == 2
    assert logger.err.call_count == 3
    assert ret_code == 10


def test_protocol_logger():
    logger = MagicMock(spec=CommandLogger)
    cmd_result = mock_command_result(logger)
    cmd_result.print_results()
    assert logger.info.mock_calls == [
        call("stdout line 1"),
        call("stdout line 2"),
        call("Return Code: 10"),
    ]
    assert logger.err.mock_calls == [
        call("stderr line 1"),
        call("stderr line 2"),
        call("stderr line 3"),
    ]
