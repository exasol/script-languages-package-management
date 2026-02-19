import pathlib

import click

from exasol.exaslpm.cli.cli import cli
from exasol.exaslpm.cli.make_context import make_context
from exasol.exaslpm.pkg_mgmt.install_packages import package_install


@cli.command()
@click.option(
    "--package-file",
    type=click.Path(exists=True, path_type=pathlib.Path),
    required=True,
    help="Yaml file containing package details",
)
@click.option("--build-step", type=str, required=True, help="Name of the build deps")
def install_command(
    package_file: pathlib.Path,
    build_step: str,
):
    """
    This command installs the specified packages described in the given package file.
    If the package file contains R- / Conda- or Pip-packages, then respective binaries
    must be set accordingly.
    """
    package_install(
        package_file,
        build_step,
        make_context(),
    )
