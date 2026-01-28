from pathlib import Path


class InstallCmd:
    def __init__(self):
        self._args = ["install"]

    @property
    def args(self) -> list[str]:
        return self._args

    def package_file(self, package_file: Path) -> "InstallCmd":
        self._args += ["--package-file", str(package_file)]
        return self

    def build_step(self, build_step: str) -> "InstallCmd":
        self._args += ["--build-step", build_step]
        return self

    def python_binary(self, python_binary: str) -> "InstallCmd":
        self._args += ["--python-binary", python_binary]
        return self

    def conda_binary(self, conda_binary: str) -> "InstallCmd":
        self._args += ["--conda-binary", conda_binary]
        return self

    def r_binary(self, r_binary: str) -> "InstallCmd":
        self._args += ["--r-binary", r_binary]
        return self


class CliHelper:
    def __init__(self):
        self._args: list[str] = list()

    @property
    def install(self):
        return InstallCmd()
