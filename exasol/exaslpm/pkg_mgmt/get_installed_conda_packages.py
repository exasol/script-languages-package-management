import json
from pathlib import Path

from exasol.exaslpm.model.package_file_config import CondaPackage
from exasol.exaslpm.pkg_mgmt.context.cmd_executor import CommandFailedException
from exasol.exaslpm.pkg_mgmt.context.context import Context


def get_installed_conda_packages(
    context: Context, micromamba_path: Path
) -> list[CondaPackage]:
    micromamba_output = MicromambaExecutor.execute_micromamba(context, micromamba_path)
    return MicromambaParser.parse_micromamba_output(micromamba_output)


class MicromambaExecutor:
    @staticmethod
    def execute_micromamba(context: Context, micromamba_path: Path) -> str:
        # micromamba list --json
        cmd = [str(micromamba_path), "list", "--json"]
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
            raise CommandFailedException("Failed executing micromamba command")
        return "".join(stdout_lines)


class MicromambaParser:
    @staticmethod
    def parse_micromamba_output(micromamba_output: str) -> list[CondaPackage]:
        installed_packages: list[CondaPackage] = []
        if micromamba_output:
            parsed_micromamba_output = json.loads(micromamba_output)
            for parsed_micromamba_out_item in parsed_micromamba_output:
                package = CondaPackage(
                    name=parsed_micromamba_out_item["name"],
                    version=parsed_micromamba_out_item["version"],
                    channel=parsed_micromamba_out_item["channel"],
                )
                installed_packages.append(package)
        return installed_packages
