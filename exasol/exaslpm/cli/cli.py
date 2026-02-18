import pathlib

import click

from exasol.exaslpm.pkg_mgmt.context.cmd_executor import (
    CommandExecutor,
)
from exasol.exaslpm.pkg_mgmt.context.cmd_logger import StdLogger
from exasol.exaslpm.pkg_mgmt.context.context import Context
from exasol.exaslpm.pkg_mgmt.context.file_access import FileAccess
from exasol.exaslpm.pkg_mgmt.context.file_downloader import FileDownloader
from exasol.exaslpm.pkg_mgmt.context.history_file_manager import HistoryFileManager
from exasol.exaslpm.pkg_mgmt.context.temp_file_provider import TempFileProvider
from exasol.exaslpm.pkg_mgmt.export_variables import export_variables
from exasol.exaslpm.pkg_mgmt.install_packages import package_install


@click.group()
def cli():
    """
    EXASLPM - Exasol Script Languages Package Management

    Install Conda/Pip/R/APT packages

    Examples:

        Print this help message:

            $ exaslpm --help
    """


@cli.command()
@click.option(
    "--package-file",
    type=click.Path(exists=True, path_type=pathlib.Path),
    required=True,
    help="Yaml file containing package details",
)
@click.option("--build-step", type=str, required=True, help="Name of the build deps")
def install(
    package_file: pathlib.Path,
    build_step: str,
):
    """
    This command installs the specified packages described in the given package file.
    If the package file contains R- / Conda- or Pip-packages, then respective binaries
    must be set accordingly.
    """

    logger = StdLogger()
    cmd_executor = CommandExecutor(logger)

    context = Context(
        cmd_logger=logger,
        cmd_executor=cmd_executor,
        history_file_manager=HistoryFileManager(),
        file_access=FileAccess(),
        file_downloader=FileDownloader(),
        temp_file_provider=TempFileProvider(),
    )

    package_install(
        package_file,
        build_step,
        context,
    )


@cli.command("export-variables")
@click.argument(
    "filename",
    type=click.Path(path_type=pathlib.Path),
    required=False,
)
def export_variables_command(filename: pathlib.Path | None):
    """Export all variables from build history as shell environment variables."""

    logger = StdLogger()
    cmd_executor = CommandExecutor(logger)

    context = Context(
        cmd_logger=logger,
        cmd_executor=cmd_executor,
        history_file_manager=HistoryFileManager(),
        file_access=FileAccess(),
        file_downloader=FileDownloader(),
        temp_file_provider=TempFileProvider(),
    )

    export_variables(context=context, output_file=filename)
