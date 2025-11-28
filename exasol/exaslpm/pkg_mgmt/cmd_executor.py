import subprocess
import sys
from collections.abc import Iterator


class CommandResult:
    def __init__(self, ret_code: int, stdout: Iterator[str], stderr: Iterator[str]):
        self._return_code = ret_code
        self._stdout = stdout
        self._stderr = stderr

    def return_code(self):
        return self._return_code

    def itr_stdout(self) -> Iterator[str]:
        return self._stdout

    def itr_stderr(self) -> Iterator[str]:
        return self._stderr

    def print_result(self):
        for out_line in self._stdout:
            sys.stdout.write(out_line)
        for err_line in self._stderr:
            sys.stderr.write(err_line)


class CommandExecutor:
    def execute(self, cmd_strs: list[str]) -> CommandResult:
        print(f"Executing: {cmd_strs}")
        sub_process = subprocess.Popen(
            cmd_strs, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        return CommandResult(
            ret_code=sub_process.wait(),
            stdout=iter(sub_process.stdout),
            stderr=iter(sub_process.stderr),
        )
