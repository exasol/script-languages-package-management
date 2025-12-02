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
        consume_stdout: Callable[[str | bytes], None],
        consume_stderr: Callable[[str | bytes], None],
    ):

        def pick_next(out_stream, callback) -> bool:
            try:
                _val = next(out_stream)
                callback(_val)
            except StopIteration:
                return False
            return True

        # Read from _stdout and _stderr simultaneously
        stdout_continue = True
        stderr_continue = True
        while stdout_continue or stderr_continue:
            if stdout_continue:
                stdout_continue = pick_next(self._stdout, consume_stdout)
            if stderr_continue:
                stderr_continue = pick_next(self._stderr, consume_stderr)
        return self.return_code()

    def print_results(self):
        ret_code = self.consume_results(sys.stdout.write, sys.stderr.write)
        print(f"Return Code: {ret_code}")


class CommandExecutor:
    def execute(self, cmd_strs: list[str]) -> CommandResult:
        cmd_str = " ".join(cmd_strs)
        print(f"Executing: {cmd_str}")

        sub_process = subprocess.Popen(
            cmd_strs, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return CommandResult(
            fn_ret_code=lambda: sub_process.wait(),
            stdout=iter(sub_process.stdout),
            stderr=iter(sub_process.stderr),
        )
