import pytest

from exasol.exaslpm.model.serialization import to_yaml_str
from exasol.exaslpm.pkg_mgmt.export_variables import export_variables
from exasol.exaslpm.pkg_mgmt.install_packages import package_install


@pytest.fixture
def prepare_variables(
    docker_container,
    variables_file_content,
    local_package_path,
    docker_executor_context,
):
    variables_package_file_yaml = to_yaml_str(variables_file_content)
    local_package_path.write_text(variables_package_file_yaml)

    for build_step_name in ["build_step_1", "build_step_2"]:
        package_install(
            package_file=local_package_path,
            build_step_name=build_step_name,
            context=docker_executor_context,
        )


def test_export_variables_stdout(capsys, docker_executor_context, prepare_variables):

    export_variables(None, docker_executor_context)
    out = capsys.readouterr().out
    assert "export JAVA_HOME=/usr/java" in out
    assert "export PROTOBUF_DIR=/opt/protobuf" in out


def test_export_variables_file(tmp_path, docker_executor_context, prepare_variables):

    target_file = tmp_path / "variables.sh"
    export_variables(target_file, docker_executor_context)

    out = target_file.read_text()
    assert "export JAVA_HOME=/usr/java" in out
    assert "export PROTOBUF_DIR=/opt/protobuf" in out
