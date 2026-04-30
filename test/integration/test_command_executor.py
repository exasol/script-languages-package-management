import shutil

from exasol.exaslpm.pkg_mgmt.context.cmd_executor import CommandExecutor
from exasol.exaslpm.pkg_mgmt.context.cmd_logger import StdLogger


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


def test_env_variable():
    executor = CommandExecutor(StdLogger())
    result = executor.execute(["env"], env={"FOO": "bar"})
    stdout_lines = []
    stderr_lines = []

    def consume_stdout(line, **kwargs):
        stdout_lines.append(line)

    def consume_stderr(line, **kwargs):
        stderr_lines.append(line)

    ret_code = result.consume_results(consume_stdout, consume_stderr)
    assert ret_code == 0
    assert not stderr_lines
    assert "FOO=bar\n" in stdout_lines


def test_consume_results_callback_failure():
    # The following command produces a lot of stdout to fill the subprocess pipe.
    # Once the callback raises, the reader thread must keep draining stdout without
    # invoking the callback again, otherwise the subprocess causes a deadlock.
    if shutil.which("apt-cache") is None:
        pytest.skip("apt-cache is required for this integration test")

    executor = CommandExecutor(StdLogger())
    result = executor.execute(["apt-cache", "dumpavail"])
    stdout_lines = []
    stderr_lines = []

    def consume_stdout(line, **kwargs):
        stdout_lines.append(line)
        raise RuntimeError("apt stdout callback failed")

    def consume_stderr(line, **kwargs):
        stderr_lines.append(line)

    with pytest.raises(RuntimeError, match="Error while consuming stdout") as exc_info:
        result.consume_results(consume_stdout, consume_stderr)

    assert exc_info.value.__cause__ is not None
    assert str(exc_info.value.__cause__) == "apt stdout callback failed"
    assert len(stdout_lines) == 1
