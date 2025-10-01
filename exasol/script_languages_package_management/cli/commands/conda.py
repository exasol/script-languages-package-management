from exasol.script_languages_package_management.cli.cli import cli
from exasol.script_languages_package_management.conda.install import install as install_packages
import click

# Conda group
@cli.group()
def conda():
    """Conda package operations"""
    pass

@conda.command()
@click.option('--package-file', required=True, type=click.Path(exists=True), help='Path to the conda package file')
@click.option('--channel-file', required=False, type=click.Path(exists=True), help='Path to the conda channels file')
def install(package_file, channel_file):
    install_packages(package_file, channel_file)
