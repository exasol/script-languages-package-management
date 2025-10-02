from inspect import cleandoc
from pathlib import Path

import uuid
import subprocess
import shutil
import docker

from test.integration.docker_test_environment.docker_test_image import DockerTestImage
from test.integration.docker_test_environment.exaslcpm_info import ExaslcpmInfo


def _build(target_path: Path, target_exec_bin_name: str):
    result = subprocess.run(
        ["nox", "-s", "build-standalone-binary", "--", "--executable-name", target_exec_bin_name, "--cleanup"],
        capture_output=True,
        text=True,
        check=True
    )
    shutil.move(Path("dist") / target_exec_bin_name, target_path)

class DockerTestImageBuilder:
    def __init__(self, ubuntu_version: str, build_path: Path) -> None:
        self.ubuntu_version = ubuntu_version
        self.uuid = str(uuid.uuid4())
        self.build_path = build_path
        self.exaslpm_info = ExaslcpmInfo()
        self.docker_client = docker.from_env()

    def _build_exaslpm_executable(self) -> None:
        target_exec_path = self.build_path / self.exaslpm_info.executable_name
        tmp_exec_bin_name = f"exaslpm_{self.uuid}"
        _build(target_exec_path, tmp_exec_bin_name)

    @property
    def _docker_img_tag(self):
        return f"exasol/script-languages-package-management-int-test:{self.uuid}"

    @property
    def _test_dockerfile_content(self) -> str:
        return cleandoc(
            f"""
                FROM ubuntu:{self.ubuntu_version}
                ENV DEBIAN_FRONTEND=noninteractive

                COPY {self.exaslpm_info.executable_name} {self.exaslpm_info.exaslcpm_path_in_container} 
            """
        )

    def build(self):
        dockerfile_path = self.build_path / "Dockerfile"
        dockerfile_path.write_text(self._test_dockerfile_content)
        self._build_exaslpm_executable()

        image, build_logs = self.docker_client.images.build(
            path=str(self.build_path),
            tag=self._docker_img_tag
        )
        return DockerTestImage(image, self._docker_img_tag, self.exaslpm_info, self.docker_client)

