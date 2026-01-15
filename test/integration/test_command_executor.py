from exasol.exaslpm.pkg_mgmt.cmd_executor import CommandExecutor
from exasol.exaslpm.pkg_mgmt.cmd_logger import StdLogger


def test_cat_command_positive(tmp_path):
    test_file = tmp_path / "afile.txt"
    test_file.write_text("Some content")

    executor = CommandExecutor(StdLogger())
    result = executor.execute(["cat", str(test_file)])
    stdout_lines = []
    stderr_lines = []

    def consume_stdout(line, **kwargs):
        stdout_lines.append(line)

    def consume_stderr(line, **kwargs):
        stderr_lines.append(line)

    ret_code = result.consume_results(consume_stdout, consume_stderr)
    assert ret_code == 0
    assert stdout_lines
    assert any("Some content" in line for line in stdout_lines)


def test_cat_command_negative(tmp_path):
    executor = CommandExecutor(StdLogger())
    str_no_file = str(tmp_path / "non_existent_file")
    result = executor.execute(["cat", str_no_file])
    stdout_lines = []
    stderr_lines = []

    def consume_stdout(line, **kwargs):
        stdout_lines.append(line)

    def consume_stderr(line, **kwargs):
        stderr_lines.append(line)

    ret_code = result.consume_results(consume_stdout, consume_stderr)
    assert ret_code != 0
    assert stderr_lines
    assert any("No such file" in line for line in stderr_lines)
