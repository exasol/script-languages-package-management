import io
import json
import tarfile
from os import PathLike
from pathlib import Path
from test.integration.docker_test_environment.exaslpm_info import ExaslpmInfo

from docker.models.containers import Container

from exasol.exaslpm.model.package_file_config import (
    AptPackage,
    CondaPackage,
    Micromamba,
    PipPackage,
    RPackage,
)
from exasol.exaslpm.pkg_mgmt.micromamba_env import create_mamba_env_variables


class DockerTestContainer:
    def __init__(self, container: Container, exaslpm_info: ExaslpmInfo) -> None:
        self.container = container
        self.exaslpm_info = exaslpm_info

    def run(
        self,
        param_list: list[str],
        check_exit_code: bool = True,
        environment: dict[str, str] | None = None,
        workdir: str = None,
    ) -> tuple[int, str]:
        (exit_code, output) = self.container.exec_run(
            param_list, environment=environment, workdir=workdir
        )
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
        self, target_path_in_container: PathLike, file_name: str, content: bytes
    ) -> Path:
        tarstream = io.BytesIO()
        with tarfile.open(fileobj=tarstream, mode="w") as tar:
            tarinfo = tarfile.TarInfo(name=file_name)
            tarinfo.size = len(content)
            tar.addfile(tarinfo, io.BytesIO(content))
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
                "--disable-pip-version-check",
                "--format=json",
            ]
        )
        packages = json.loads(out.strip())
        return [
            PipPackage(name=pkg["name"], version=pkg["version"]) for pkg in packages
        ]

    def run_in_mamba_env(
        self,
        param_list: list[str],
        micromamba: Micromamba,
        check_exit_code: bool = True,
    ) -> tuple[int, str]:
        return self.run(
            param_list,
            check_exit_code=check_exit_code,
            environment=create_mamba_env_variables(micromamba),
        )

    def list_conda_packages(
        self, binary: Path, micromamba: Micromamba
    ) -> list[CondaPackage]:
        _, out = self.run_in_mamba_env(
            [
                str(binary),
                "list",
                "--json",
            ],
            micromamba,
        )
        packages = json.loads(out.strip())
        return [
            CondaPackage(
                name=pkg["name"],
                version=pkg["version"],
                channel=pkg["channel"],
                build=pkg["build_string"],
            )
            for pkg in packages
        ]

    def list_r(self) -> list[RPackage]:
        r_cmd = (
            r"""ip <- installed.packages()[,c("Package","Version")];"""
            + r"""cat("[", paste(apply(ip,1,function(x) sprintf("{\"Package\":\"%s\",\"Version\":\"%s\"}", """
            + r"""x[1], x[2])), collapse=","), "]", sep="")"""
        )
        _, out = self.run(
            [
                "Rscript",
                "-e",
                r_cmd,
            ]
        )
        packages = json.loads(out.strip())
        return [
            RPackage(name=pkg["Package"], version=pkg["Version"]) for pkg in packages
        ]
