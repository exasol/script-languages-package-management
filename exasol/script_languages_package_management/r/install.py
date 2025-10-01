import click


def install(package_file):
    click.echo(f"Installing R packages from {package_file}")
