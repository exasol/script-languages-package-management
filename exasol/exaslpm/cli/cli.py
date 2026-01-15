import pathlib

import click

from exasol.exaslpm.pkg_mgmt.cmd_executor import (
    CommandExecutor,
)
from exasol.exaslpm.pkg_mgmt.cmd_logger import StdLogger
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
@click.option("--phase", required=False, type=str, help="Name of the phase")
@click.option(
    "--package-file",
    type=click.Path(exists=True, path_type=pathlib.Path),
    required=True,
    help="Yaml file containing package details",
)
@click.option("--build-step", type=str, required=True, help="Name of the build deps")
@click.option(
    "--python-binary",
    required=False,
    default=None,
    type=click.Path(exists=True, path_type=pathlib.Path),
    help="Source channel for apt-get",
)
@click.option(
    "--conda-binary",
    required=False,
    default=None,
    type=click.Path(exists=True, path_type=pathlib.Path),
    help="Source channel for micromamba",
)
@click.option(
    "--r-binary",
    required=False,
    default=None,
    type=click.Path(exists=True, path_type=pathlib.Path),
    help="Source channel for r-remote",
)
def install(
    phase: str,
    package_file: pathlib.Path,
    build_step: str,
    python_binary: pathlib.Path,
    conda_binary: pathlib.Path,
    r_binary: pathlib.Path,
):
    """
    This command installs the specified packages described in the given package file.
    If the package file contains R- / Conda- or Pip-packages, then respective binaries
    must be set accordingly.
    """

    logger = StdLogger()
    cmd_executor = CommandExecutor(logger)

    package_install(
        phase,
        package_file,
        build_step,
        python_binary,
        conda_binary,
        r_binary,
        cmd_executor,
        logger,
    )
