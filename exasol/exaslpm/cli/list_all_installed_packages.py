import pathlib
from inspect import cleandoc

import click

from exasol.exaslpm.cli.cli import cli
from exasol.exaslpm.cli.make_context import make_context
from exasol.exaslpm.model.serialization import to_yaml_str
from exasol.exaslpm.pkg_mgmt.list_all_installed_packages import (
    list_all_installed_packages,
)


@cli.command()
@click.option(
    "--out-file",
    type=click.Path(path_type=pathlib.Path),
    required=False,
    help=cleandoc("""
    Optional outfile path. If given, the command prints the installed packages to this file.
    Otherwise, it prints to stdout.
    """),
)
def list_all_installed_packages_command(out_file: pathlib.Path | None):
    """
    This command outputs all installed packages for all supported package types.
    The currently used package types are taken from this build steps history.
    """
    installed_packages = list_all_installed_packages(
        make_context(),
    )

    output_str = to_yaml_str(installed_packages)

    if out_file is None:
        print(output_str)
    else:
        with open(out_file, "w") as out_stream:
            out_stream.write(output_str)
