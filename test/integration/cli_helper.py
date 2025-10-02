from pathlib import Path


class RHelper:
    def __init__(self, exaslcpm_executable: str) -> None:
        self.args = [exaslcpm_executable, "r"]

    def install(self, package_file: Path) -> list[str]:
        return self.args + ["install", "--package-file", str(package_file)]


class AptHelper:
    def __init__(self, exaslcpm_executable: str) -> None:
        self.args = [exaslcpm_executable, "apt"]

    def install(self, package_file: Path) -> list[str]:
        return self.args + ["install", "--package-file", str(package_file)]


class CondaHelper:
    def __init__(self, exaslcpm_executable: str) -> None:
        self.args = [exaslcpm_executable, "conda"]

    def install(self, package_file: Path, channel_file: Path) -> list[str]:
        return self.args + ["install", "--package-file", str(package_file), "--channel-file", str(channel_file)]

class PipHelper:
    def __init__(self, exaslcpm_executable: str) -> None:
        self.args = [exaslcpm_executable, "pip"]

    def install(self, package_file: Path) -> list[str]:
        return self.args + ["install", "--package-file", str(package_file)]


class CliHelper:
    def __init__(self, exaslcpm_executable: str):
        self.exaslcpm_executable = exaslcpm_executable

    @property
    def r(self):
        return RHelper(self.exaslcpm_executable)

    @property
    def conda(self):
        return CondaHelper(self.exaslcpm_executable)

    @property
    def apt(self):
        return AptHelper(self.exaslcpm_executable)

    @property
    def pip(self):
        return PipHelper(self.exaslcpm_executable)

