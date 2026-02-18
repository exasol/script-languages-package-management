import sys
from collections.abc import Iterator
from io import TextIOBase
from pathlib import Path

from exasol.exaslpm.pkg_mgmt.context.context import Context


def _variables(context: Context) -> Iterator[tuple[str, str]]:
    previous_build_steps = context.history_file_manager.get_all_previous_build_steps()
    variables: dict[str, str] = {}

    for build_step in previous_build_steps:
        for phase in build_step.phases:
            if phase.variables:
                for variable_key, variable_value in phase.variables.items():
                    if variable_key in variables:
                        raise ValueError(
                            f"Variable {variable_key} in phase {build_step.name} already exists"
                        )
                variables.update(phase.variables)

    yield from variables.items()


def _write_variables(context: Context, out_stream: TextIOBase) -> None:
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
