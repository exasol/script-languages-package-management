import subprocess
import sys
from collections.abc import (
    Callable,
    Iterator,
)


class CommandResult:
    def __init__(
        self,
        fn_ret_code: Callable[[], int],
        stdout: Iterator[str],
        stderr: Iterator[str],
    ):
        self._fn_return_code = fn_ret_code  # a lambda to subprocess.open.wait
        self._stdout = stdout
        self._stderr = stderr

    def return_code(self):
        return self._fn_return_code()

    def itr_stdout(self) -> Iterator[str]:
        return self._stdout

    def itr_stderr(self) -> Iterator[str]:
        return self._stderr

    def consume_results(
        self,
        consume_stdout: Callable[[str | bytes, int], None],
        consume_stderr: Callable[[str | bytes, int], None],
    ):

        def pick_next(out_stream, count, callback) -> bool:
            try:
                _val = next(out_stream)
                callback(_val, count)
            except StopIteration:
                return -1
            return count + 1

        # Read from _stdout and _stderr simultaneously
        stdout_count = 1
        stderr_count = 1
        while stdout_count > 0 or stderr_count > 0:
            if stdout_count > 0:
                stdout_count = pick_next(self._stdout, stdout_count, consume_stdout)
            if stderr_count > 0:
                stderr_count = pick_next(self._stderr, stderr_count, consume_stderr)
        return self.return_code()

    def print_results(self):
        ret_code = self.consume_results(sys.stdout.write, sys.stderr.write)
        print(f"Return Code: {ret_code}")


class CommandExecutor:
    def execute(self, cmd_strs: list[str]) -> CommandResult:
        print(f"Executing: {cmd_strs}")

        sub_process = subprocess.Popen(
            cmd_strs, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return CommandResult(
            fn_ret_code=lambda: sub_process.wait(),
            stdout=iter(sub_process.stdout),
            stderr=iter(sub_process.stderr),
        )
