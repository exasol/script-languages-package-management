import subprocess
import threading
from collections.abc import Callable
from typing import (
    IO,
    Any,
)

from exasol.exaslpm.pkg_mgmt.cmd_logger import CommandLogger


class CommandFailedException(Exception):
    """
    Raised when commands faile
    """

    pass


class CommandResult:
    def __init__(
        self,
        fn_ret_code: Callable[[], int],
        stdout: IO[str] | None,
        stderr: IO[str] | None,
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

    def return_code(self):
        return self._fn_return_code()

    def itr_stdout(self) -> Iterator[str]:
        return self._stdout

    def itr_stderr(self) -> Iterator[str]:
        return self._stderr

    def stream_reader(
        self,
        pipe: Iterator[str],
        callback: Callable[[str | bytes, Any], None],
    ):
        while True:
            try:
                _val = next(pipe)
                callback(_val)
            except StopIteration:
                return

    def consume_results(
        self,
        consume_stdout: Callable[[str | bytes, Any], None],
        consume_stderr: Callable[[str | bytes, Any], None],
    ):

        read_out = threading.Thread(
            target=self.stream_reader, args=(self._stdout, consume_stdout)
        )
        read_err = threading.Thread(
            target=self.stream_reader, args=(self._stderr, consume_stderr)
        )

        read_out.start()
        read_err.start()
        read_out.join()
        read_err.join()
        return self.return_code()

    def print_results(self):
        ret_code = self.consume_results(self._log.info, self._log.err)
        self._log.info(f"Return Code: {ret_code}")


class CommandExecutor:
    def __init__(self, logger: CommandLogger):
        self._log = logger

    def execute(self, cmd_strs: list[str]) -> CommandResult:
        """
        :param cmd_strs: command with all its options as a list of individual str
        :return: The result that can be used to access the results
        :rtype: CommandResult
        """
        cmd_str = " ".join(cmd_strs)
        self._log.info(f"Executing: {cmd_str}")

        sub_process = subprocess.Popen(
            cmd_strs, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return CommandResult(
            fn_ret_code=lambda: sub_process.wait(),
            stdout=sub_process.stdout,
            stderr=sub_process.stderr,
            logger=self._log,
        )
