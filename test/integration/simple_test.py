import pytest

from exasol.exaslpm.pkg_mgmt.cmd_executor import (
    CommandExecutor,
    StdLogger,
)


@pytest.mark.parametrize(
    "is_positive",
    [True, False],
)
# Making "echo" cmd fail is tougher than making "cat" fail
# Hence, "cat"
def test_cat_command(tmp_path, is_positive: bool):
    test_file = tmp_path / "afile.txt"
    test_file.write_text("Some content")

    logger = StdLogger()
    executor = CommandExecutor(logger)
    str_file = str(test_file) if is_positive else "unknown"
    result = executor.execute(["cat", str_file])

    stdout_lines = []
    stderr_lines = []

    def consume_stdout(line):
        stdout_lines.append(line)

    def consume_stderr(line):
        stderr_lines.append(line)

    ret_code = result.consume_results(consume_stdout, consume_stderr)

    assert (ret_code == 0) if is_positive else (ret_code != 0)
    assert (
        any("Some content" in line for line in stdout_lines)
        if is_positive
        else any("No such file" in line for line in stderr_lines)
    )
    assert stdout_lines if is_positive else stderr_lines
