import pathlib

import click
import yaml

from exasol.exaslpm.model.package_file_config import (
    BuildStep,
    Package,
    PackageFile,
    Phase,
)
from exasol.exaslpm.pkg_mgmt.install_apt import install_via_apt


def parse_package_file(
    package_file: PackageFile, phase_name: str, build_step_name: str
) -> Phase:
    all_phases = []
    build_steps = package_file.build_steps
    for itr_step_name, itr_build_step in build_steps.items():
        if itr_step_name.lower() == build_step_name.lower():
            phases = itr_build_step.phases
            for itr_phase_name, itr_phase in phases.items():
                if itr_phase_name.lower() == phase_name.lower():
                    all_phases.append(itr_phase)
    return all_phases


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
        all_phases = parse_package_file(pkg_file, phase, build_step)
        for single_phase in all_phases:
            if single_phase.apt is not None:
                install_via_apt(single_phase.apt)
    except ValueError:
        print("Error parsing package file")
