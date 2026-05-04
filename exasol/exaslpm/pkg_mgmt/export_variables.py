import platform
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import (
    Any,
    TextIO,
)

from jinja2 import Template

from exasol.exaslpm.model.package_file_config import Tools
from exasol.exaslpm.pkg_mgmt.context.context import Context

PLATFORM_MACHINE_MAPPING = {
    "x86_64": "x86_64",
    "amd64": "x86_64",
    "aarch64": "arm64",
    "arm64": "arm64",
}


def _mapped_platform(machine_name: str) -> str:
    try:
        return PLATFORM_MACHINE_MAPPING[machine_name]
    except KeyError as error:
        raise ValueError(f"Unsupported platform machine '{machine_name}'.") from error


def _render_variable_value(variable_value: str) -> str:
    template = Template(variable_value)
    return template.render(platform=_mapped_platform(platform.machine()))


def _check_uniqueness_of_variables(
    build_step_name: str,
    phase_name: str,
    existing_variables: dict[str, str],
    variables: dict[str, str],
) -> None:
    for variable_key in variables.keys():
        if variable_key in existing_variables:
            raise ValueError(
                f"Variable {variable_key} in build-step={build_step_name}, phase={phase_name} was already defined."
            )


def _build_tools_key(key: str) -> str:
    PREFIX = "EXASLPM_TOOLS_"
    key = PREFIX + key.upper()
    return key


def _flatten(variables: dict[str, str], prefix: str, value: Any) -> dict[str, str]:

    if value is None:
        return {}

    # Nested dictionary
    if isinstance(value, dict):
        result = {}
        for k, v in value.items():
            new_prefix = f"{prefix}_{k}" if prefix else k
            result.update(_flatten(variables, new_prefix, v))
        return result

    # Convert Path → str
    if isinstance(value, Path):
        value = str(value)
    key = _build_tools_key(prefix)
    if key in variables:
        raise ValueError(f"Duplicated tools entry {key}")
    return {key: value}


def _update_tools(
    tools: Tools,
    variables: dict[str, str],
) -> dict[str, str]:

    for field, field_value in tools.model_dump().items():
        variables.update(_flatten(variables, field, field_value))

    return variables


def _variables(context: Context) -> Iterator[tuple[str, str]]:
    previous_build_steps = context.history_file_manager.get_all_previous_build_steps()
    variables: dict[str, str] = {}

    for build_step in previous_build_steps:
        for phase in build_step.phases:
            if phase.variables:
                _check_uniqueness_of_variables(
                    build_step.name, phase.name, variables, phase.variables
                )
                for variable_key, variable_value in phase.variables.items():
                    variables[variable_key] = _render_variable_value(variable_value)
            if phase.tools:
                _update_tools(phase.tools, variables)

    for variable_key, variable_value in variables.items():
        yield variable_key, variable_value


def _write_variables(context: Context, out_stream: TextIO) -> None:
    for variable_key, variable_value in _variables(context):
        print(f'export {variable_key}="{variable_value}"', file=out_stream)


def export_variables(
    output_file: Path | None,
    context: Context,
) -> None:

    if output_file is None:
        _write_variables(context, out_stream=sys.stdout)
    else:
        with open(output_file, "w") as out_stream:
            _write_variables(context, out_stream=out_stream)
