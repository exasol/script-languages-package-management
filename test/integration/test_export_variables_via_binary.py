from pathlib import Path

import pytest

from exasol.exaslpm.model.serialization import to_yaml_str


@pytest.fixture
def prepare_variables(
    docker_container, cli_helper, variables_file_content, micromamba_file_content
):
    micromamba_package_file_yaml = to_yaml_str(micromamba_file_content)
    micromamba_package_file = docker_container.make_and_upload_file(
        Path("/"), "micromamba_01", micromamba_package_file_yaml.encode("utf-8")
    )
    ret, out = docker_container.run_exaslpm(
        cli_helper.install.package_file(micromamba_package_file)
        .build_step("build_step_1")
        .args
    )
    assert ret == 0

    variables_file_content_package_file, prepared_variables = variables_file_content
    variables_package_file_yaml = to_yaml_str(variables_file_content_package_file)
    variables_package_file = docker_container.make_and_upload_file(
        Path("/"), "micromamba_01", variables_package_file_yaml.encode("utf-8")
    )

    ret, out = docker_container.run_exaslpm(
        cli_helper.install.package_file(variables_package_file)
        .build_step("build_step_2")
        .args
    )
    assert ret == 0

    ret, out = docker_container.run_exaslpm(
        cli_helper.install.package_file(variables_package_file)
        .build_step("build_step_3")
        .args
    )
    assert ret == 0

    return prepared_variables


def test_export_variables_stdout(docker_container, prepare_variables):

    ret, out = docker_container.run_exaslpm(["export-variables"])

    assert ret == 0

    assert prepare_variables.java_home in out
    assert 'export PROTOBUF_DIR="/opt/protobuf"' in out
    assert "{% if platform" not in out
    assert 'export EXASLPM_TOOLS_MICROMAMBA_VERSION="2.5.0-1"\n' in out
    assert 'export EXASLPM_TOOLS_MICROMAMBA_ROOT_PREFIX="/opt/conda"\n' in out


def test_export_variables_file(docker_container, prepare_variables):

    target_file = Path("/tmp/variables.sh")
    ret, out = docker_container.run_exaslpm(
        ["export-variables", "--out-file", str(target_file)]
    )

    assert "export JAVA_HOME" not in out
    assert 'export PROTOBUF_DIR="/opt/protobuf"' not in out
    assert 'export EXASLPM_TOOLS_MICROMAMBA_VERSION="2.3"\n' not in out
    assert 'export EXASLPM_TOOLS_MICROMAMBA_ROOT_PREFIX="/opt/conda"\n' not in out

    assert ret == 0

    _, out_cat = docker_container.run(["cat", str(target_file)])
    out_lines = out_cat.splitlines()
    assert out_lines == [
        'export EXASLPM_TOOLS_MICROMAMBA_VERSION="2.5.0-1"',
        'export EXASLPM_TOOLS_MICROMAMBA_ROOT_PREFIX="/opt/conda"',
        prepare_variables.java_home,
        'export PROTOBUF_DIR="/opt/protobuf"',
    ]
