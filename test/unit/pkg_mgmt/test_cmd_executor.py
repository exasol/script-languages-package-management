from unittest.mock import (
    MagicMock,
)

import pytest

from exasol.exaslpm.pkg_mgmt.cmd_executor import (
    CommandExecutor,
    CommandResult,
)

call_counts = {"stdout": 0, "stderr": 0}


@pytest.fixture
def mock_command_result():
    fn_ret_code = lambda: 10
    stdout_iter = iter(["stdout line 1", "stdout line 2"])
    stderr_iter = iter(["stderr line 1", "stderr line 2", "stderr line 3"])
    return CommandResult(
        fn_ret_code=fn_ret_code, stdout=stdout_iter, stderr=stderr_iter
    )


def stdout_results(result_str: str):
    global call_counts
    call_counts["stdout"] += 1
    expected = "stdout line " + str(call_counts["stdout"])
    assert expected == result_str


def stderr_results(result_str: str):
    global call_counts
    call_counts["stderr"] += 1
    expected = "stderr line " + str(call_counts["stderr"])
    assert expected == result_str


"""
def test_command_executor_01():
    cmd_exe = CommandExecutor()
    cmd_strs = ["ls", "-la"]
    cmd_res = cmd_exe.execute(cmd_strs)
    cmd_res.print_results()
"""


def test_command_executor_02(monkeypatch, mock_command_result):
    global call_counts

    def mock_execute(_, cmd_strs):
        return mock_command_result

    monkeypatch.setattr(CommandExecutor, "execute", mock_execute)
    executor = CommandExecutor()
    result = executor.execute(["cmd1", "cmd2"])
    assert result.return_code() == 10
    return_code = result.consume_results(stdout_results, stderr_results)
    assert call_counts["stdout"] == 2
    assert call_counts["stderr"] == 3
    assert return_code == 10
    result.print_results()
