import json
from pathlib import Path

from exasol.exaslpm.model.package_file_config import PipPackage
from exasol.exaslpm.pkg_mgmt.context.cmd_executor import CommandFailedException
from exasol.exaslpm.pkg_mgmt.context.context import Context


def get_installed_pip_packages(context: Context, python_path: Path) -> list[PipPackage]:
    pip_output = PipExecutor.execute_pip(context, python_path)
    return PipParser.parse_pip_output(pip_output)


class PipExecutor:
    @staticmethod
    def execute_pip(context: Context, python_path: Path) -> str:
        # python3 -m pip list --format json --no-cache-dir
        cmd = [
            str(python_path),
            "-m",
            "pip",
            "list",
            "--format",
            "json",
            "--no-cache-dir",
        ]
        cmd_res = context.cmd_executor.execute(cmd)

        stdout_lines: list[str] = []

        def consume_stdout(line: str | bytes) -> None:
            if isinstance(line, bytes):
                line = line.decode()
            stdout_lines.append(line)

        def consume_stderr(line: str | bytes) -> None:
            if isinstance(line, bytes):
                line = line.decode()
            context.cmd_logger.warn(line)

        ret_code = cmd_res.consume_results(consume_stdout, consume_stderr)
        if ret_code != 0:
            raise CommandFailedException("Failed executing pip command")
        return "".join(stdout_lines)


class PipParser:
    @staticmethod
    def parse_pip_output(pip_output: str) -> list[PipPackage]:
        installed_packages: list[PipPackage] = []
        if pip_output:
            parsed_pip_out = json.loads(pip_output)
            for parsed_pip_out_item in parsed_pip_out:
                package = PipPackage(
                    name=parsed_pip_out_item["name"],
                    version=parsed_pip_out_item["version"],
                )
                installed_packages.append(package)
        return installed_packages
