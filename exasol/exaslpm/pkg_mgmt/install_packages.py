import pathlib

import yaml

from exasol.exaslpm.model.package_file_config import (
    PackageFile,
    Phase,
)
from exasol.exaslpm.pkg_mgmt.install_apt import (
    CommandExecutor,
    install_via_apt,
)


def parse_package_file(
    package_file: PackageFile, phase_name: str, build_step_name: str
) -> Phase:
    build_steps = package_file.build_steps
    build_step = build_steps[build_step_name]

    phases = build_step.phases
    phase = phases[phase_name]

    return phase


def package_install(
    phase: str,
    package_file: pathlib.Path,
    build_step: str,
    python_binary: pathlib.Path,
    conda_binary: pathlib.Path,
    r_binary: pathlib.Path,
):
    """
    click.echo(
        f"Phase: {phase}, \
        Package File: {package_file}, \
        Build Step: {build_step}, \
        Python Binary: {python_binary}, \
        Conda Binary: {conda_binary}, \
        R Binary: {r_binary}",
    )
    """

    package_content = package_file.read_text()
    try:
        yaml_data = yaml.safe_load(package_content)
        pkg_file = PackageFile.model_validate(yaml_data)
        single_phase = parse_package_file(pkg_file, phase, build_step)
        if single_phase.apt is not None:
            install_via_apt(single_phase.apt, CommandExecutor())
    except ValueError:
        print("Error parsing package file")
