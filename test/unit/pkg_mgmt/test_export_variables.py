from pathlib import Path

import pytest

from exasol.exaslpm.model.package_file_config import (
    Bazel,
    BuildStep,
    Micromamba,
    Phase,
    Pip,
    Tools,
)
from exasol.exaslpm.pkg_mgmt import export_variables as export_variables_module
from exasol.exaslpm.pkg_mgmt.export_variables import (
    _flatten,
    _mapped_platform,
    export_variables,
)

TEST_BUILD_STEP = BuildStep(
    name="build_step_1",
    phases=[
        Phase(name="phase_1", variables={"B": "2"}),
        Phase(name="phase_2", variables={"A": "1"}),
        Phase(
            name="phase_3",
            tools=Tools(
                pip=Pip(
                    version="1.2.3",
                    needs_break_system_packages=True,
                    comment="Latest Pip",
                ),
                micromamba=Micromamba(version="2.3"),
                bazel=Bazel(version="8.4.2"),
                python_binary_path=Path("/usr/bin/python3"),
                r_binary_path=Path("usr/bin/r"),
                conda_binary_path=Path("/usr/opt/conda/bin/conda"),
                mamba_binary_path=Path("/usr/opt/conda/bin/mamba"),
            ),
        ),
    ],
)

TEMPLATE_BUILD_STEP = BuildStep(
    name="build_step_template",
    phases=[
        Phase(
            name="phase_1",
            variables={
                "JAVA_HOME": "/usr/lib/jvm/java-1.17.0-openjdk-{% if platform == 'x86_64' %}amd64{% else %}arm64{% endif %}"
            },
        )
    ],
)


@pytest.mark.parametrize(
    "machine_name, expected_platform",
    [
        ("x86_64", "x86_64"),
        ("amd64", "x86_64"),
        ("aarch64", "arm64"),
        ("arm64", "arm64"),
    ],
)
def test_mapped_platform(machine_name: str, expected_platform: str):
    assert _mapped_platform(machine_name) == expected_platform


def test_mapped_platform_unsupported_platform():
    with pytest.raises(ValueError, match="Unsupported platform machine"):
        _mapped_platform("ppc64")


def test_export_variables_to_stdout(capsys, context_mock):
    context_mock.history_file_manager.build_steps = [TEST_BUILD_STEP]

    export_variables(None, context=context_mock)
    out = capsys.readouterr().out.splitlines()
    assert out == [
        'export B="2"',
        'export A="1"',
        'export EXASLPM_TOOLS_PIP_VERSION="1.2.3"',
        'export EXASLPM_TOOLS_PIP_NEEDS_BREAK_SYSTEM_PACKAGES="True"',
        'export EXASLPM_TOOLS_PIP_COMMENT="Latest Pip"',
        'export EXASLPM_TOOLS_MICROMAMBA_VERSION="2.3"',
        'export EXASLPM_TOOLS_MICROMAMBA_ROOT_PREFIX="/opt/conda"',
        'export EXASLPM_TOOLS_MICROMAMBA_ENV_NAME="base"',
        'export EXASLPM_TOOLS_BAZEL_VERSION="8.4.2"',
        'export EXASLPM_TOOLS_PYTHON_BINARY_PATH="/usr/bin/python3"',
        'export EXASLPM_TOOLS_R_BINARY_PATH="usr/bin/r"',
        'export EXASLPM_TOOLS_CONDA_BINARY_PATH="/usr/opt/conda/bin/conda"',
        'export EXASLPM_TOOLS_MAMBA_BINARY_PATH="/usr/opt/conda/bin/mamba"',
    ]


def test_export_variables_to_file(tmp_path: Path, context_mock):
    context_mock.history_file_manager.build_steps = [TEST_BUILD_STEP]

    output_file = tmp_path / "variables.sh"

    export_variables(output_file=output_file, context=context_mock)

    out = output_file.read_text().splitlines()
    assert out == [
        'export B="2"',
        'export A="1"',
        'export EXASLPM_TOOLS_PIP_VERSION="1.2.3"',
        'export EXASLPM_TOOLS_PIP_NEEDS_BREAK_SYSTEM_PACKAGES="True"',
        'export EXASLPM_TOOLS_PIP_COMMENT="Latest Pip"',
        'export EXASLPM_TOOLS_MICROMAMBA_VERSION="2.3"',
        'export EXASLPM_TOOLS_MICROMAMBA_ROOT_PREFIX="/opt/conda"',
        'export EXASLPM_TOOLS_MICROMAMBA_ENV_NAME="base"',
        'export EXASLPM_TOOLS_BAZEL_VERSION="8.4.2"',
        'export EXASLPM_TOOLS_PYTHON_BINARY_PATH="/usr/bin/python3"',
        'export EXASLPM_TOOLS_R_BINARY_PATH="usr/bin/r"',
        'export EXASLPM_TOOLS_CONDA_BINARY_PATH="/usr/opt/conda/bin/conda"',
        'export EXASLPM_TOOLS_MAMBA_BINARY_PATH="/usr/opt/conda/bin/mamba"',
    ]


@pytest.mark.parametrize(
    "platform, expected_variable_value",
    [
        ("aarch64", "/usr/lib/jvm/java-1.17.0-openjdk-arm64"),
        ("x86_64", "/usr/lib/jvm/java-1.17.0-openjdk-amd64"),
    ],
)
def test_export_variables_renders_jinja_template(
    capsys, context_mock, monkeypatch, platform, expected_variable_value
):
    monkeypatch.setattr(export_variables_module.platform, "machine", lambda: platform)
    context_mock.history_file_manager.build_steps = [TEMPLATE_BUILD_STEP]

    export_variables(None, context=context_mock)

    out = capsys.readouterr().out
    assert f'export JAVA_HOME="{expected_variable_value}"\n' in out


@pytest.mark.parametrize(
    "input_dict, expected_dict",
    [
        (
            {"A": 1, "B": 2},
            {"EXASLPM_TOOLS_SOME_PREFIX_A": 1, "EXASLPM_TOOLS_SOME_PREFIX_B": 2},
        ),
        (
            {"A": {"B": 2, "C": 3}},
            {"EXASLPM_TOOLS_SOME_PREFIX_A_B": 2, "EXASLPM_TOOLS_SOME_PREFIX_A_C": 3},
        ),
    ],
)
def test_flatten(input_dict, expected_dict):
    res = _flatten({}, "SOME_PREFIX", input_dict)
    assert res == expected_dict


def test_flatten_raises_for_duplicated():
    input_dict = {"A": 1, "B": 2}
    variables = {"EXASLPM_TOOLS_SOME_PREFIX_A": "5"}
    with pytest.raises(ValueError):
        _flatten(variables, "SOME_PREFIX", input_dict)
