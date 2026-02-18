from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock

from exasol.exaslpm.model.package_file_config import BuildStep, Phase
from exasol.exaslpm.pkg_mgmt.context.context import Context
from exasol.exaslpm.pkg_mgmt.export_variables import export_variables


def _make_context(build_steps: list[BuildStep]) -> Context:
    history_file_manager = MagicMock()
    history_file_manager.get_all_previous_build_steps.return_value = build_steps
    return Context(
        cmd_logger=MagicMock(),
        cmd_executor=MagicMock(),
        history_file_manager=history_file_manager,
        file_access=MagicMock(),
        file_downloader=MagicMock(),
        temp_file_provider=MagicMock(),
    )


def test_export_variables_to_stdout():
    context = _make_context(
        [
            BuildStep(
                name="build_step_1",
                phases=[
                    Phase(name="phase_1", variables={"B": "2"}),
                    Phase(name="phase_2", variables={"A": "1"}),
                ],
            )
        ]
    )

    output = StringIO()

    export_variables(context=context, output_stream=output)

    assert output.getvalue() == "export A=1\nexport B=2\n"


def test_export_variables_to_file(tmp_path: Path):
    context = _make_context(
        [
            BuildStep(
                name="build_step_1",
                phases=[
                    Phase(name="phase_1", variables={"A": "1"}),
                    Phase(name="phase_2", variables={"A": "2", "B": "3"}),
                ],
            )
        ]
    )

    output_file = tmp_path / "variables.sh"

    export_variables(context=context, output_file=output_file)

    assert output_file.read_text() == "export A=2\nexport B=3"
