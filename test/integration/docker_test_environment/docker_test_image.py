from pathlib import Path

import subprocess
import shutil
from docker.models.images import Image

from test.integration.docker_test_environment.docker_test_container import DockerTestContainer
from test.integration.docker_test_environment.exaslcpm_info import ExaslcpmInfo


def _build(target_path: Path, target_exec_bin_name: str):
    result = subprocess.run(
        ["nox", "-s", "build-standalone-binary", "--", "--executable-name", target_exec_bin_name, "--cleanup"],
        capture_output=True,
        text=True,
        check=True
    )
    shutil.move(Path("dist") / target_exec_bin_name, target_path)

class DockerTestImage:
    def __init__(self, image: Image, tag: str, exaslpm_info: ExaslcpmInfo, docker_client) -> None:
        self.image = image
        self.tag = tag
        self.exaslpm_info = exaslpm_info
        self.docker_client = docker_client

    def start_container(self, container_name_suffix: str):
        container = self.docker_client.containers.run(
            self.image.id,
            command="sleep infinity",
            detach=True,
            name=f"exaslpm_int_test_{container_name_suffix}",
        )
        return DockerTestContainer(container, self.exaslpm_info)


    def remove(self) -> None:
        self.docker_client.images.remove(self.image.id)
