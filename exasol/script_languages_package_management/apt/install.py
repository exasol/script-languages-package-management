import click


def install(package_file):
    click.echo(f"Installing APT packages from {package_file}")