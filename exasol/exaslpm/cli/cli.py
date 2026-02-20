import click


@click.group()
def cli():
    """
    EXASLPM - Exasol Script Languages Package Management

    Install Conda/Pip/R/APT packages

    Examples:

        Print this help message:

            $ exaslpm --help
    """
