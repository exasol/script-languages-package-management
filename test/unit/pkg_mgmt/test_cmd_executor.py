import contextlib
import os
import subprocess
import sys
from test.unit.pkg_mgmt.utils import _named_params
from unittest.mock import (
    MagicMock,
    call,
)

import pytest

from exasol.exaslpm.pkg_mgmt.context.cmd_executor import (
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


@pytest.fixture
def mock_popen(monkeypatch):
    mock_popen = MagicMock()
    monkeypatch.setattr(subprocess, "Popen", mock_popen)
    return mock_popen


@pytest.mark.parametrize(
    "env_variables",
    [None, {"some": "value"}],
)
def test_command_executor(mock_popen, env_variables):
    logger = MagicMock(spec=CommandLogger)
    executor = CommandExecutor(logger)
    result = executor.execute(["cmd1", "cmd2"], env=env_variables)
    ret_code = result.return_code()
    assert mock_popen.mock_calls == [
        call(["cmd1", "cmd2"], stdout=-1, stderr=-1, text=True, env=env_variables),
        call().stdout.__iter__(),
        call().stderr.__iter__(),
        call().wait(),
    ]
    assert ret_code == mock_popen.return_value.wait.return_value


@contextlib.contextmanager
def set_meipass(new_value):
    assert not hasattr(sys, "_MEIPASS")
    sys._MEIPASS = new_value
    yield None
    del sys._MEIPASS


@pytest.fixture
def mock_os_env():
    @contextlib.contextmanager
    def patch_func(meipass: str, os_env: dict[str, str]):
        assert not hasattr(sys, "_MEIPASS")
        old_env = os.environ
        os.environ = os_env
        sys._MEIPASS = meipass
        yield None
        os.environ = old_env
        del sys._MEIPASS

    return patch_func


@pytest.mark.parametrize(
    "os_env_variables, input_env_variables, meipass, expected_env",
    [
        pytest.param(
            *_named_params(
                os_env_variables=None,
                input_env_variables=None,
                meipass="",
                expected_env=None,
            ),
            id="Nothing set",
        ),
        pytest.param(
            *_named_params(
                os_env_variables=None,
                input_env_variables={"some": "value"},
                meipass="",
                expected_env={"some": "value"},
            ),
            id="env_variable not LD_LIBRARY_PATH",
        ),
        pytest.param(
            *_named_params(
                os_env_variables={"LD_LIBRARY_PATH": "path_one:path_two"},
                input_env_variables=None,
                meipass="",
                expected_env=None,
            ),
            id="os env LD_LIBRARY_PATH, no MEIPASS",
        ),
        pytest.param(
            *_named_params(
                os_env_variables={"LD_LIBRARY_PATH": "path_one"},
                input_env_variables=None,
                meipass="path_one",
                expected_env={"LD_LIBRARY_PATH": ""},
            ),
            id="os env LD_LIBRARY_PATH single entry, MEIPASS matches",
        ),
        pytest.param(
            *_named_params(
                os_env_variables={"LD_LIBRARY_PATH": "path_one:path_two"},
                input_env_variables=None,
                meipass="path_one",
                expected_env={"LD_LIBRARY_PATH": "path_two"},
            ),
            id="os env LD_LIBRARY_PATH two entries, MEIPASS matches",
        ),
        pytest.param(
            *_named_params(
                os_env_variables={"LD_LIBRARY_PATH": "path_one:path_two:path_three"},
                input_env_variables=None,
                meipass="path_two",
                expected_env={"LD_LIBRARY_PATH": "path_one:path_three"},
            ),
            id="os env LD_LIBRARY_PATH three entries, MEIPASS matches",
        ),
        pytest.param(
            *_named_params(
                os_env_variables={"LD_LIBRARY_PATH": "path_one"},
                input_env_variables={"some": "value"},
                meipass="path_one",
                expected_env={"some": "value"},
            ),
            id="prefer given env, but no LD_LIBRARY_PATH",
        ),
        pytest.param(
            *_named_params(
                os_env_variables={"LD_LIBRARY_PATH": "path_one:path_two"},
                input_env_variables={"LD_LIBRARY_PATH": "path_one:path_three"},
                meipass="path_one",
                expected_env={"LD_LIBRARY_PATH": "path_three"},
            ),
            id="prefer given env with LD_LIBRARY_PATH",
        ),
    ],
)
def test_command_executor_ld_library_path(
    mock_popen,
    mock_os_env,
    os_env_variables,
    input_env_variables,
    meipass,
    expected_env,
):
    logger = MagicMock(spec=CommandLogger)
    executor = CommandExecutor(logger)
    with mock_os_env(meipass, os_env_variables):
        result = executor.execute(["cmd1"], env=input_env_variables)
        ret_code = result.return_code()
        assert mock_popen.mock_calls == [
            call(["cmd1"], stdout=-1, stderr=-1, text=True, env=expected_env),
            call().stdout.__iter__(),
            call().stderr.__iter__(),
            call().wait(),
        ]
        assert ret_code == mock_popen.return_value.wait.return_value


def test_command_results():
    cmd_result = mock_command_result(MagicMock(spec=CommandLogger))
    stdout_consumer = MagicMock()
    stderr_consumer = MagicMock()
    ret_code = cmd_result.consume_results(stdout_consumer, stderr_consumer)
    assert stdout_consumer.mock_calls == [
        call("stdout line 1"),
        call("stdout line 2"),
    ]
    assert stderr_consumer.mock_calls == [
        call("stderr line 1"),
        call("stderr line 2"),
        call("stderr line 3"),
    ]
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
