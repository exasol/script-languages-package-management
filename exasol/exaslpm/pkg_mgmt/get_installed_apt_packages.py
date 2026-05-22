from exasol.exaslpm.model.package_file_config import AptPackage
from exasol.exaslpm.pkg_mgmt.context.cmd_executor import CommandFailedException
from exasol.exaslpm.pkg_mgmt.context.context import Context
from exasol.exaslpm.pkg_mgmt.cvs_installed_packages_parser import parse_csv_output


def get_installed_apt_packages(context: Context) -> list[AptPackage]:
    csv_output = AptExecutor.execute_apt(context)
    return AptParser.parse_csv_output(csv_output)


class AptExecutor:
    @staticmethod
    def execute_apt(context: Context) -> list[str]:
        # dpkg-query -W -f=${Package},${Version}\n
        cmd = ["dpkg-query", "-W", "-f=${Package},${Version}\n"]
        cmd_res = context.cmd_executor.execute(cmd)

        stdout_lines: list[str] = []

        def consume_stdout(line: str | bytes) -> None:
            if isinstance(line, bytes):
                line = line.decode()
            stdout_lines.append(line.strip())

        def consume_stderr(line: str | bytes) -> None:
            if isinstance(line, bytes):
                line = line.decode()
            context.cmd_logger.warn(line)

        ret_code = cmd_res.consume_results(consume_stdout, consume_stderr)
        if ret_code != 0:
            raise CommandFailedException("Failed executing dpkg-query command")
        return stdout_lines


class AptParser:
    @staticmethod
    def parse_csv_output(csv_output: list[str]) -> list[AptPackage]:
        return [
            AptPackage.model_validate(package.model_dump())
            for package in parse_csv_output(csv_output)
        ]
