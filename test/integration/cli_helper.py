from pathlib import Path


class RHelper:
    def __init__(self) -> None:
        self.args = ["r"]

    def install(self, package_file: Path) -> list[str]:
        return self.args + ["install", "--package-file", str(package_file)]


class AptHelper:
    def __init__(self) -> None:
        self.args = ["apt"]

    def install(self, package_file: Path) -> list[str]:
        return self.args + ["install", "--package-file", str(package_file)]


class CondaHelper:
    def __init__(self) -> None:
        self.args = ["conda"]

    def install(self, package_file: Path, channel_file: Path) -> list[str]:
        return self.args + ["install", "--package-file", str(package_file), "--channel-file", str(channel_file)]

class PipHelper:
    def __init__(self) -> None:
        self.args = ["pip"]

    def install(self, package_file: Path) -> list[str]:
        return self.args + ["install", "--package-file", str(package_file)]


class CliHelper:

    @property
    def r(self):
        return RHelper()

    @property
    def conda(self):
        return CondaHelper()

    @property
    def apt(self):
        return AptHelper()

    @property
    def pip(self):
        return PipHelper()

