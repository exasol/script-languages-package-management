import sys
from pathlib import Path
from typing import TextIO

from exasol.exaslpm.pkg_mgmt.context.context import Context


def _format_variable_exports(context: Context) -> str:
    previous_build_steps = context.history_file_manager.get_all_previous_build_steps()
    variables: dict[str, str] = {}

    for build_step in previous_build_steps:
        for phase in build_step.phases:
            if phase.variables:
                variables.update(phase.variables)

    lines = [f"export {name}={value}" for name, value in sorted(variables.items())]
    return "\n".join(lines)


def export_variables(
    context: Context,
    output_file: Path | None = None,
    output_stream: TextIO | None = None,
) -> None:
    rendered_variables = _format_variable_exports(context)

    if output_file is not None:
        output_file.write_text(rendered_variables)
        return

    if output_stream is None:
        output_stream = sys.stdout

    output_stream.write(rendered_variables)
    output_stream.write("\n")
