from exasol.script_languages_package_management.cli.cli import cli
from exasol.script_languages_package_management.pip import install as install_packages
import click


# Pip group
@cli.group()
def pip():
    """Pip package operations"""
    pass

@pip.command()
@click.option('--package-file', required=True, type=click.Path(exists=True), help='Path to the pip package file')
def install(package_file):
    install_packages(package_file)
