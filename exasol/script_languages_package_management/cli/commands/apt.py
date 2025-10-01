from exasol.script_languages_package_management.cli.cli import cli
from exasol.script_languages_package_management.apt.install import install as install_packages
import click

# Apt group
@cli.group()
def apt():
    """Apt package operations"""
    pass

@apt.command()
@click.option('--package-file', required=True, type=click.Path(exists=True), help='Path to the apt package file')
def install(package_file):
    install_packages(package_file)