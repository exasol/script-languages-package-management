from pathlib import Path

from exasol.exaslpm.model.package_file_config import (
    BuildStep,
    Phase,
)
from exasol.exaslpm.pkg_mgmt.export_variables import export_variables

TEST_BUILD_STEP = BuildStep(
    name="build_step_1",
    phases=[
        Phase(name="phase_1", variables={"B": "2"}),
        Phase(name="phase_2", variables={"A": "1"}),
    ],
)


def test_export_variables_to_stdout(capsys, context_mock):
    context_mock.history_file_manager.build_steps = [TEST_BUILD_STEP]

    export_variables(None, context=context_mock)
    out = capsys.readouterr().out
    assert "export A=1\n" in out
    assert "export B=2\n" in out


def test_export_variables_to_file(tmp_path: Path, context_mock):
    context_mock.history_file_manager.build_steps = [TEST_BUILD_STEP]

    output_file = tmp_path / "variables.sh"

    export_variables(output_file=output_file, context=context_mock)

    out = output_file.read_text()
    assert "export A=1\n" in out
    assert "export B=2\n" in out
