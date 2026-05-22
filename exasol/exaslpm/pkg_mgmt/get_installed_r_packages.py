from exasol.exaslpm.model.package_file_config import RPackage
from exasol.exaslpm.pkg_mgmt.context.cmd_executor import CommandFailedException
from exasol.exaslpm.pkg_mgmt.context.context import Context
from exasol.exaslpm.pkg_mgmt.csv_installed_packages_parser import parse_csv_output


def get_installed_r_packages(context: Context) -> list[RPackage]:
    csv_output = RscriptExecutor.execute_rscript(context)
    return RscriptParser.parse_rscript_output(csv_output)


class RscriptExecutor:
    @staticmethod
    def execute_rscript(context: Context) -> list[str]:
        # Rscript -e 'write.table(installed.packages()[,c("Package","Version")], sep=",", row.names=FALSE, col.names=FALSE)'
        cmd = [
            "Rscript",
            "-e",
            'write.table(installed.packages()[,c("Package","Version")], sep=",", row.names=FALSE, col.names=FALSE)',
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
            raise CommandFailedException("Failed executing Rscript command")
        return stdout_lines


class RscriptParser:
    @staticmethod
    def parse_rscript_output(csv_output: list[str]) -> list[RPackage]:
        return [
            RPackage.model_validate(package.model_dump())
            for package in parse_csv_output(csv_output)
        ]
