import subprocess
import sys
from collections.abc import Iterator


class CommandResult:
    def __init__(self, ret_code: int, out_vals: list[str], err_vals: list[str]):
        self._return_code = ret_code
        self._stdout = out_vals
        self._stderr = err_vals

    def return_code(self):
        return self._return_code

    def itr_stdout(self) -> Iterator[str]:
        return iter(self._stdout)

    def itr_stderr(self) -> Iterator[str]:
        return iter(self._stderr)


class CommandExecutor:
    def execute(self, cmd_strs: list[str]) -> CommandResult:
        print(f"Executing: {cmd_strs}")
        sub_process = subprocess.Popen(
            cmd_strs, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        out_vals, err_vals = sub_process.communicate()

        out_lines = out_vals.splitlines() if out_vals else []
        for out_line in out_lines:
            sys.stdout.write(out_line)

        err_lines = err_vals.splitlines() if err_vals else []
        for err_line in err_lines:
            sys.stdout.write(err_line)

        return CommandResult(sub_process.returncode, out_lines, err_lines)
