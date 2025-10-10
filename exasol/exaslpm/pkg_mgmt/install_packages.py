import pathlib

import click


def package_install(
    phase: str,
    package_file: pathlib.Path,
    build_step: str,
    python_binary: pathlib.Path,
    conda_binary: pathlib.Path,
    r_binary: pathlib.Path,
):
    click.echo(f"Option1: {phase}, Option2: {package_file}")
