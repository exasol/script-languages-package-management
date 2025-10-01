import click


def install(package_file):
    click.echo(f"Installing Conda packages from {package_file}")