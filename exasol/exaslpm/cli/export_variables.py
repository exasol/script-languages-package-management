import pathlib
from inspect import cleandoc

import click

from exasol.exaslpm.cli.cli import cli
from exasol.exaslpm.cli.make_context import make_context
from exasol.exaslpm.pkg_mgmt.export_variables import export_variables


@cli.command("export-variables")
@click.option(
    "--out-file",
    type=click.Path(path_type=pathlib.Path),
    required=False,
    help=cleandoc(
        """
    Optional outfile path. If given, the command prints the environment variables to this file. 
    Otherwise, it prints the environment variables to stdout.
    """
    ),
)
def export_variables_command(out_file: pathlib.Path | None):
    """Export all variables from build history as shell environment variables."""

    export_variables(output_file=out_file, context=make_context())
