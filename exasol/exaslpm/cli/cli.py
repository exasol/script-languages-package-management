import click


def install_packages(
    phase: str,
    package_file: click.Path,
    build_step: str,
    python_binary: click.Path,
    conda_binary: click.Path,
    r_binary: click.Path,
):
    click.echo(f"Option1: {phase}, Option2: {package_file}")


@click.group()
def cli():
    """
    EXASLPM - Exasol Script Languages Package Management

    Install Conda/Pip/R/APT packages

    Examples:

        Print this help message:

            $ exaslpm --help
    """
    pass


@cli.command()
@click.option("--phase", required=True, type=str, help="Name of the phase")
@click.option(
    "--package-file",
    type=click.Path(exists=True),
    required=True,
    help="Yaml file containing package details",
)
@click.option("--build-step", type=str, required=True, help="Name of the build deps")
@click.option(
    "--python-binary",
    required=True,
    type=click.Path(exists=True),
    help="Source channel for apt-get",
)
@click.option(
    "--conda-binary",
    required=True,
    type=click.Path(exists=True),
    help="Source channel for micromamba",
)
@click.option(
    "--r-binary",
    required=True,
    type=click.Path(exists=True),
    help="Source channel for r-remote",
)
def install(
    phase: str,
    package_file: click.Path,
    build_step: str,
    python_binary: click.Path,
    conda_binary: click.Path,
    r_binary: click.Path,
):
    """
    This command installs the specified package from the given binary path
    """
    install_packages(
        phase, package_file, build_step, python_binary, conda_binary, r_binary
    )
