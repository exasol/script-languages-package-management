from pathlib import Path

import pytest

from exasol.exaslpm.model.serialization import to_yaml_str


@pytest.fixture
def prepare_variables(docker_container, cli_helper, variables_file_content):
    variables_package_file_yaml = to_yaml_str(variables_file_content)

    apt_package_file = docker_container.make_and_upload_file(
        Path("/"), "apt_file_01", variables_package_file_yaml.encode("utf-8")
    )
    ret, out = docker_container.run_exaslpm(
        cli_helper.install.package_file(apt_package_file)
        .build_step("build_step_1")
        .args
    )
    assert ret == 0

    ret, out = docker_container.run_exaslpm(
        cli_helper.install.package_file(apt_package_file)
        .build_step("build_step_2")
        .args
    )
    assert ret == 0


def test_export_variables_stdout(docker_container, prepare_variables):

    ret, out = docker_container.run_exaslpm(["export-variables"])

    assert ret == 0
    assert "export JAVA_HOME=/usr/java" in out
    assert "export PROTOBUF_DIR=/opt/protobuf" in out


def test_export_variables_file(docker_container, prepare_variables):

    target_file = Path("/tmp/variables.sh")
    ret, out = docker_container.run_exaslpm(
        ["export-variables", "--out-file", str(target_file)]
    )

    assert "export JAVA_HOME=/usr/java" not in out
    assert "export PROTOBUF_DIR=/opt/protobuf" not in out

    assert ret == 0

    _, out_cat = docker_container.run(["cat", str(target_file)])
    assert "export JAVA_HOME=/usr/java" in out_cat
    assert "export PROTOBUF_DIR=/opt/protobuf" in out_cat
