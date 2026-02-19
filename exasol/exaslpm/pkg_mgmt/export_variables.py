import sys
from collections.abc import Iterator
from pathlib import Path
from typing import TextIO

from exasol.exaslpm.pkg_mgmt.context.context import Context


def _check_uniquess_of_variables(
    build_step_name: str,
    phase_name: str,
    existing_variables: dict[str, str],
    variables: dict[str, str],
) -> None:
    for variable_key, variable_value in variables.items():
        if variable_key in existing_variables:
            raise ValueError(
                f"Variable {variable_key} in build-step={build_step_name}, phase={phase_name} was already defined."
            )


def _variables(context: Context) -> Iterator[tuple[str, str]]:
    previous_build_steps = context.history_file_manager.get_all_previous_build_steps()
    variables: dict[str, str] = {}

    for build_step in previous_build_steps:
        for phase in build_step.phases:
            if phase.variables:
                _check_uniquess_of_variables(
                    build_step.name, phase.name, variables, phase.variables
                )
                variables.update(phase.variables)

    yield from variables.items()


def _write_variables(context: Context, out_stream: TextIO) -> None:
    for variable_key, variable_value in _variables(context):
        print(f"export {variable_key}={variable_value}", file=out_stream)


def export_variables(
    output_file: Path | None,
    context: Context,
) -> None:

    if output_file is None:
        _write_variables(context, out_stream=sys.stdout)
    else:
        with open(output_file, "w") as out_stream:
            _write_variables(context, out_stream=out_stream)
