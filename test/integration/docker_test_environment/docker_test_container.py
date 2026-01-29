import io
import json
import tarfile
from os import PathLike
from pathlib import Path
from test.integration.docker_test_environment.exaslpm_info import ExaslpmInfo

from docker.models.containers import Container

from exasol.exaslpm.model.package_file_config import AptPackage, PipPackage


class DockerTestContainer:
    def __init__(self, container: Container, exaslpm_info: ExaslpmInfo) -> None:
        self.container = container
        self.exaslpm_info = exaslpm_info

    def run(
        self, param_list: list[str], check_exit_code: bool = True
    ) -> tuple[int, str]:
        (exit_code, output) = self.container.exec_run(param_list)
        if check_exit_code:
            assert exit_code == 0, output.decode("utf-8")
        return exit_code, output.decode("utf-8")

    def run_exaslpm(
        self, param_list: list[str], check_exit_code: bool = True
    ) -> tuple[int, str]:
        (exit_code, output) = self.container.exec_run(
            [str(self.exaslpm_info.exaslpm_path_in_container)] + param_list
        )
        if check_exit_code:
            assert exit_code == 0, output.decode("utf-8")
        return exit_code, output.decode("utf-8")

    def remove(self) -> None:
        self.container.remove(force=True)

    def make_and_upload_file(
        self, target_path_in_container: PathLike, file_name: str, content: str
    ) -> Path:
        tarstream = io.BytesIO()
        content_data = content.encode("utf-8")
        with tarfile.open(fileobj=tarstream, mode="w") as tar:
            tarinfo = tarfile.TarInfo(name=file_name)
            tarinfo.size = len(content_data)
            tar.addfile(tarinfo, io.BytesIO(content_data))
        tarstream.seek(0)
        res = self.container.put_archive(
            str(target_path_in_container), tarstream.read()
        )
        assert res
        return Path(target_path_in_container) / file_name

    def list_apt(self) -> list[AptPackage]:
        _, out = self.run(
            [
                "bash",
                "-c",
                """dpkg-query -W -f='{"package":"${Package}","version":"${Version}"}\n'""",
            ]
        )
        packages = []
        for line in out.strip().splitlines():
            if line.strip():  # avoid empty lines
                packages.append(json.loads(line))
        return [
            AptPackage(name=pkg["package"], version=pkg["version"]) for pkg in packages
        ]


    def list_pip(self) -> list[PipPackage]:
        _, out = self.run(
            [
                "python3.12",
                "-m",
                "pip",
                "list",
                "--format=json"
            ]
        )
        packages = json.loads(out.strip())
        return [
            PipPackage(name=pkg["name"], version=pkg["version"]) for pkg in packages
        ]
