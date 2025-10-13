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
    click.echo(
        f"Phase: {phase}, \
        Package File: {package_file}, \
        Build Step: {build_step}, \
        Python Binary: {python_binary}, \
        Conda Binary: {conda_binary}, \
        R Binary: {r_binary}",
    )
