from inspect import cleandoc
from pathlib import Path
from typing import Iterator

import pytest
import uuid
import subprocess
import shutil
import docker
from docker import DockerClient
from docker.models.containers import Container
from docker.models.images import Image


def _build(target_path: Path, target_exec_bin_name: str):
    result = subprocess.run(
        ["nox", "-s", "build-standalone-binary", "--", "--executable-name", target_exec_bin_name, "--cleanup"],
        capture_output=True,
        text=True,
        check=True
    )
    shutil.move(Path("dist") / target_exec_bin_name, target_path)

@pytest.fixture(scope="session")
def docker_client() -> DockerClient:
    return docker.from_env()

@pytest.fixture(scope="session")
def session_uuid() -> str:
    return str(uuid.uuid4())

@pytest.fixture(scope="session")
def target_exec_bin_name(session_uuid) -> str:
    target_exec_bin_name = f"exaslpm"
    return target_exec_bin_name

@pytest.fixture(scope="session")
def docker_build_dir(tmp_path_factory) -> Path:
    build_dir = tmp_path_factory.mktemp("docker_build")
    return build_dir

@pytest.fixture(scope='session')
def exaslpm_executable(docker_build_dir, target_exec_bin_name, session_uuid) -> str:
    target_exec_path = docker_build_dir / target_exec_bin_name
    tmp_exec_bin_name = f"exaslpm_{session_uuid}"
    _build(target_exec_path, tmp_exec_bin_name)
    return target_exec_bin_name

@pytest.fixture(scope='session')
def docker_img_tag(session_uuid):
    return f"exasol/script-languages-package-management-int-test:{session_uuid}"

@pytest.fixture(scope='session')
def keep_docker_image(request):
    return request.config.getoption("--keep-docker-image")

@pytest.fixture(scope='session')
def test_image_ubuntu_version(request):
    return request.config.getoption("--test-image-ubuntu-version")

@pytest.fixture(scope="session")
def test_dockerfile_content(test_image_ubuntu_version, target_exec_bin_name) -> str:
    return cleandoc(
        f"""
            FROM ubuntu:{test_image_ubuntu_version}
            ENV DEBIAN_FRONTEND=noninteractive
            
            COPY {target_exec_bin_name} /{target_exec_bin_name}
        """
    )

@pytest.fixture(scope='session')
def docker_img(docker_client, docker_build_dir, exaslpm_executable, docker_img_tag, keep_docker_image, test_dockerfile_content) -> Iterator[Image]:
    dockerfile_path = docker_build_dir / "Dockerfile"
    dockerfile_path.write_text(test_dockerfile_content)

    image, build_logs = docker_client.images.build(
        path=str(docker_build_dir),
        tag=docker_img_tag
    )
    yield image
    if not keep_docker_image:
        docker_client.images.remove(image.id)


@pytest.fixture(scope='function')
def docker_container(docker_img, docker_client, session_uuid) -> Iterator[Container]:
    container = docker_client.containers.run(
        docker_img.id,
        command="sleep infinity",
        detach=True,
        name=f"exaslpm_int_test_{session_uuid}",
    )
    yield container
    container.remove(force=True)

@pytest.fixture(scope='function')
def docker_runner(docker_container):
    def run(param_list: list[str]) -> tuple[int, str]:
        (exit_code, output) = docker_container.exec_run(param_list)
        return exit_code, output
    return run
