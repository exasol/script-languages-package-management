import click


def install(package_file):
    click.echo(f"Installing PIP packages from {package_file}")