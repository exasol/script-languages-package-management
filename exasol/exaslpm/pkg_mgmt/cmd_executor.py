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
        self.return_code()  # wait until child process complete
        return self._stdout

    def itr_stderr(self) -> Iterator[str]:
        self.return_code()  # wait until child process complete
        return self._stderr

    def print_result(self):
        self.return_code()  # wait until child process complete
        for out_line in self._stdout:
            sys.stdout.write(out_line + "\n")
        for err_line in self._stderr:
            sys.stderr.write(err_line + "\n")


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


class CommandResultPrinter:
    def __init__(self, cmd_res: CommandResult):
        self._cmd_res = cmd_res

    def print_result(self):
        self._cmd_res.print_result()
