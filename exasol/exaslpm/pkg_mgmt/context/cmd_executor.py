import os
import subprocess  # nosec B404
import sys
import threading
from collections.abc import (
    Callable,
    Iterator,
)
from typing import (
    TextIO,
    cast,
)

from exasol.exaslpm.pkg_mgmt.context.cmd_logger import CommandLogger


class CommandFailedException(Exception):
    """
    Raised when command fails
    """


def stream_reader(
    pipe: Iterator[str],
    callback: Callable[[str | bytes], None],
    exception_list: list[BaseException] | None = None,
):
    invoke_callback = True
    while True:
        try:
            _val = next(pipe)
        except StopIteration:
            return
        try:
            if invoke_callback:
                callback(_val)
        # Skipping SonarQube's code-smell to not catch BaseException.
        # We need to catch all unknown exceptions here.
        except BaseException as exc:  # NOSONAR
            if exception_list is not None:
                exception_list.append(exc)
            invoke_callback = False


class CommandResult:
    def __init__(
        self,
        fn_ret_code: Callable[[], int],
        stdout: Iterator[str],
        stderr: Iterator[str],
        logger: CommandLogger,
    ):
        """
        :param fn_ret_code: a function that waits untils the process has stopped and returns the return code. For example, subprocess.open.wait.
        :param stdout: iterable stdout captures
        :param stderr: iterable stderr captures
        :param logger: a protocol that defines the log singatures
        """
        self._log = logger
        self._fn_return_code = fn_ret_code
        self._stdout = stdout
        self._stderr = stderr

    def return_code(self) -> int:
        return self._fn_return_code()

    def consume_results(
        self,
        consume_stdout: Callable[[str | bytes], None],
        consume_stderr: Callable[[str | bytes], None],
    ):
        exception_list_stdout: list[BaseException] = []
        exception_list_stderr: list[BaseException] = []

        read_out = threading.Thread(
            target=stream_reader,
            args=(
                self._stdout,
                consume_stdout,
                exception_list_stdout,
            ),
        )
        read_err = threading.Thread(
            target=stream_reader,
            args=(
                self._stderr,
                consume_stderr,
                exception_list_stderr,
            ),
        )

        read_out.start()
        read_err.start()
        return_code = self.return_code()
        read_out.join()
        read_err.join()

        # Skipping SonarQube. It says exception_list_stdout is always empty.
        # This is not true. They are populated inside the thread.
        if exception_list_stdout:  # NOSONAR
            raise RuntimeError(
                "Error while consuming stdout"
            ) from exception_list_stdout[0]
        if exception_list_stderr:  # NOSONAR
            raise RuntimeError(
                "Error while consuming stderr"
            ) from exception_list_stderr[0]

        return return_code

    def print_results(self):
        ret_code = self.consume_results(self._log.info, self._log.err)
        self._log.info(f"Return Code: {ret_code}")


class CommandExecutor:
    def __init__(self, logger: CommandLogger):
        self._log = logger

    @staticmethod
    def get_resource_path() -> str | None:
        return sys._MEIPASS if hasattr(sys, "_MEIPASS") else None

    def _cleanup_ld_library_path(
        self, env: dict[str, str] | None
    ) -> dict[str, str] | None:
        if res_path := self.get_resource_path():
            res_env = os.environ.copy() if env is None else env
            # Remove the PyInstaller-added path if it exists
            # This forces child processes to look at the SYSTEM libraries
            if "LD_LIBRARY_PATH" in res_env:
                # Filter out any path containing the temporary _MEI directory
                paths = res_env["LD_LIBRARY_PATH"].split(os.pathsep)
                paths = [p for p in paths if p != res_path]
                res_env["LD_LIBRARY_PATH"] = os.pathsep.join(paths)
            return res_env
        else:
            return env

    def execute(
        self, cmd_args: list[str], env: dict[str, str] | None = None
    ) -> CommandResult:
        """
        :param cmd_args: command with all its options as a list of individual str
        :return: The result that can be used to access the results
        :env: environment variables to be set during execution
        :rtype: CommandResult
        """
        cmd_str = " ".join(cmd_args)
        self._log.info(f"Executing: {cmd_str}")

        sub_process = subprocess.Popen(
            cmd_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=self._cleanup_ld_library_path(env),
        )  # nosec B603
        std_out = cast(TextIO, sub_process.stdout)
        std_err = cast(TextIO, sub_process.stderr)

        return CommandResult(
            fn_ret_code=sub_process.wait,
            stdout=iter(std_out),
            stderr=iter(std_err),
            logger=self._log,
        )
