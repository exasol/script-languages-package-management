from collections.abc import Iterator
from pathlib import Path

from exasol.exaslpm.pkg_mgmt.history_file_manager import HistoryFileManager
from test.integration.cli_helper import CliHelper
from test.integration.docker_test_environment.docker_command_executor import (
    DockerCommandExecutor,
)
from test.integration.docker_test_environment.docker_test_container import (
    DockerTestContainer,
)
from test.integration.docker_test_environment.docker_test_image import DockerTestImage
from test.integration.docker_test_environment.docker_test_image_builder import (
    DockerTestImageBuilder,
)
from test.integration.docker_test_environment.test_logger import TestLogger

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--test-image-ubuntu-version",
        action="store",
        help="Ubuntu version to use for testing",
        default="24.04",
    )
    parser.addoption(
        "--keep-docker-image",
        action="store_true",
        help="Keep docker image after testing.",
        default=False,
    )


@pytest.fixture(scope="session")
def docker_image(request, tmp_path_factory) -> Iterator[DockerTestImage]:
    keep_docker_image = request.config.getoption("--keep-docker-image")
    ubuntu_version = request.config.getoption("--test-image-ubuntu-version")
    image_builder = DockerTestImageBuilder(
        build_path=tmp_path_factory.mktemp("image"), ubuntu_version=ubuntu_version
    )
    image = image_builder.build()
    yield image
    if not keep_docker_image:
        image.remove()


@pytest.fixture(scope="function")
def docker_container(docker_image, request) -> Iterator[DockerTestContainer]:
    container = docker_image.start_container(request.node.name)
    yield container
    container.remove()

@pytest.fixture(scope="function")
def test_logger() -> TestLogger:
    return TestLogger()


@pytest.fixture(scope="function")
def docker_command_executor(docker_container: DockerTestContainer, test_logger: TestLogger) -> DockerCommandExecutor:
    return DockerCommandExecutor(logger=test_logger, test_container=docker_container)

@pytest.fixture(scope="function")
def local_package_path(tmp_path, request) -> Path:
    p = tmp_path / "packages" / request.node.name
    p.parent.mkdir(parents=True, exist_ok=True)
    return p



@pytest.fixture(scope="function")
def temp_history_file_manager(tmp_path) -> HistoryFileManager:
    return HistoryFileManager(history_path=tmp_path / "history")



@pytest.fixture
def cli_helper():
    return CliHelper()
