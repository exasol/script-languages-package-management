import pathlib

from exasol.exaslpm.pkg_mgmt.cmd_executor import (
    CommandExecutor,
    CommandLogger,
)
from exasol.exaslpm.pkg_mgmt.install_apt import install_via_apt
from exasol.exaslpm.pkg_mgmt.package_file_session import PackageFileSession


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
        package_file_session = PackageFileSession(package_file=package_file)
    except Exception as e:
        logger.err(
            "Failed to read package file.", package_file=package_file, exception=e
        )
        raise
    try:
        found_build_step = package_file_session.package_file_config.find_build_step(
            build_step
        )
        assert (
            found_build_step is not None
        )  # Cannot happen as find_build_step must raise an exception if not found
        single_phase = found_build_step.find_phase(phase)
        assert (
            single_phase is not None
        )  # Cannot happen as find_phase must raise an exception if not found

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
