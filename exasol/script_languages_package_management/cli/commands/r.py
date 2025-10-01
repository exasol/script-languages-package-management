from exasol.script_languages_package_management.cli.cli import cli
from exasol.script_languages_package_management.r.install import install as install_packages
import click

# R group
@cli.group()
def r():
    """R package operations"""
    pass

@r.command()
@click.option('--package-file', required=True, type=click.Path(), help='Path to the R package file')
def install(package_file):
    install_packages(package_file)
