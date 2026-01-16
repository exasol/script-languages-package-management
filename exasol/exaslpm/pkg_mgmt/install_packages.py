import pathlib

import yaml

from exasol.exaslpm.model.package_file_config import (
    PackageFile,
    Phase,
)
from exasol.exaslpm.pkg_mgmt.cmd_executor import (
    CommandExecutor,
    CommandLogger,
)
from exasol.exaslpm.pkg_mgmt.install_apt import install_via_apt


def find_phase(
    package_file: PackageFile, phase_name: str, build_step_name: str
) -> Phase:
    matched_build_steps = [
        b for b in package_file.build_steps if b.name == build_step_name
    ]
    if len(matched_build_steps) != 1:
        raise ValueError(f"Build step name {build_step_name} does not match any build.")

    build_step = matched_build_steps[0]

    matched_phases = [phase for phase in build_step.phases if phase.name == phase_name]
    if len(matched_phases) != 1:
        raise ValueError(
            f"Phase name {phase_name} does not match any phase in build step {build_step_name}."
        )

    return matched_phases[0]


def package_install(
    phase: str,
    package_file: pathlib.Path,
    build_step: str,
    python_binary: pathlib.Path,
    conda_binary: pathlib.Path,
    r_binary: pathlib.Path,
    cmd_executor: CommandExecutor,
    logger: CommandLogger,
):
    logger.info(
        f"Phase: {phase}, \
        Package File: {package_file}, \
        Build Step: {build_step}, \
        Python Binary: {python_binary}, \
        Conda Binary: {conda_binary}, \
        R Binary: {r_binary}",
    )

    try:
        package_content = package_file.read_text()
    except Exception as e:
        logger.err(
            "Failed to read package file.", package_file=package_file, exception=e
        )
        raise
    try:
        yaml_data = yaml.safe_load(package_content)
        pkg_file = PackageFile.model_validate(yaml_data)
    except Exception as e:
        logger.err(
            "Failed to parse package file.", package_file=package_file, exception=e
        )
        raise
    try:
        single_phase = find_phase(pkg_file, phase, build_step)
    except Exception as e:
        logger.err(
            "Build step or phase not found.",
            package_file=package_file,
            build_step=build_step,
            phase=phase,
            exception=e,
        )
        raise
    try:
        if single_phase.apt is not None:
            install_via_apt(single_phase.apt, cmd_executor, logger)
    except Exception as e:
        logger.err(
            "Failed to install apt packages.", package_file=package_file, exception=e
        )
        raise
