from unittest.mock import (
    MagicMock,
    Mock,
    patch,
)

import pytest

from exasol.exaslpm.pkg_mgmt.cmd_executor import (
    CommandExecutor,
    CommandResult,
)


@pytest.fixture
def mock_command_result():
    fn_ret_code = lambda: 2
    stdout_iter = iter(["stdout line 1\n", "stdout line 2\n"])
    stderr_iter = iter(["stderr 1\n", "stderr 2\n", "stderr 3\n"])
    return CommandResult(
        fn_ret_code=fn_ret_code, stdout=stdout_iter, stderr=stderr_iter
    )


def stdout_results(result_str: str, count: int):
    assert "stdout" in result_str


def stderr_results(result_str: str, count: int):
    assert "stderr" in result_str


def test_command_executor(monkeypatch, mock_command_result):
    def mock_execute(self, cmd_strs):
        return mock_command_result

    monkeypatch.setattr(CommandExecutor, "execute", mock_execute)
    executor = CommandExecutor()
    result = executor.execute(["cmd1", "cmd2"])
    assert result.return_code() == 2
    result.consume_results(stdout_results, stderr_results)
    result.print_results()
