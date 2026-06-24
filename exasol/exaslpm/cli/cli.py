from inspect import cleandoc

import click

from exasol.exaslpm import __version__ as exaslpm_version

HELP_MESSAGE = cleandoc(f"""
    EXASLPM - Exasol Script Languages Package Management Version: {exaslpm_version}
    
    Install Conda/Pip/R/APT packages
    
    Examples:
    
        Print this help message:
    
            $ exaslpm --help
    """)


@click.group(help=HELP_MESSAGE)
@click.version_option(version=exaslpm_version)
def cli():
    """
    CLI group for Exasol Script Languages Package Management
    """
