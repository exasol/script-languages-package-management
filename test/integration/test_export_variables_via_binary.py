from pathlib import Path

from exasol.exaslpm.model.package_file_config import BuildStep, PackageFile, Phase
from exasol.exaslpm.model.serialization import to_yaml_str


HISTORY_PATH = Path("/build_info/packages/history")


def _add_history_build_step(docker_container, name: str, variables: dict[str, str]):
    content = to_yaml_str(
        PackageFile(
            build_steps=[BuildStep(name=name, phases=[Phase(name="phase_1", variables=variables)])]
        )
    )
    docker_container.make_and_upload_file(HISTORY_PATH, name, content.encode("utf-8"))


def test_export_variables_stdout(docker_container):
    docker_container.run(["mkdir", "-p", str(HISTORY_PATH)])
    _add_history_build_step(docker_container, "build_step_1", {"JAVA_HOME": "/usr/java"})
    _add_history_build_step(docker_container, "build_step_2", {"PROTOBUF_DIR": "/opt/protobuf"})

    ret, out = docker_container.run_exaslpm(["export-variables"])

    assert ret == 0
    assert "export JAVA_HOME=/usr/java" in out
    assert "export PROTOBUF_DIR=/opt/protobuf" in out


def test_export_variables_file(docker_container):
    docker_container.run(["mkdir", "-p", str(HISTORY_PATH)])
    _add_history_build_step(docker_container, "build_step_1", {"JAVA_HOME": "/usr/java"})

    target_file = Path("/tmp/variables.sh")
    ret, _ = docker_container.run_exaslpm(["export-variables", str(target_file)])

    assert ret == 0

    _, out = docker_container.run(["cat", str(target_file)])
    assert out.strip() == "export JAVA_HOME=/usr/java"
