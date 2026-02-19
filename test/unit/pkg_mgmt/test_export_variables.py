from pathlib import Path

import pytest

from exasol.exaslpm.model.package_file_config import (
    BuildStep,
    Phase,
)
from exasol.exaslpm.pkg_mgmt import export_variables as export_variables_module
from exasol.exaslpm.pkg_mgmt.export_variables import (
    _mapped_platform,
    export_variables,
)

TEST_BUILD_STEP = BuildStep(
    name="build_step_1",
    phases=[
        Phase(name="phase_1", variables={"B": "2"}),
        Phase(name="phase_2", variables={"A": "1"}),
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
    assert f"export JAVA_HOME={expected_variable_value}\n" in out
