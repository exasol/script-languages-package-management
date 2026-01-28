import pathlib

import click

from exasol.exaslpm.pkg_mgmt.context.binary_checker import BinaryChecker
from exasol.exaslpm.pkg_mgmt.context.cmd_executor import (
    CommandExecutor,
)
from exasol.exaslpm.pkg_mgmt.context.cmd_logger import StdLogger
from exasol.exaslpm.pkg_mgmt.context.context import Context
from exasol.exaslpm.pkg_mgmt.context.history_file_manager import HistoryFileManager
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
        binary_checker=BinaryChecker(),
    )

    package_install(
        package_file,
        build_step,
        context,
    )
