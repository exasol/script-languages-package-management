import pathlib

from exasol.exaslpm.pkg_mgmt.binary_finder import BinaryFinder
from exasol.exaslpm.pkg_mgmt.cmd_executor import (
    CommandExecutor,
    CommandLogger,
)
from exasol.exaslpm.pkg_mgmt.history_file_manager import HistoryFileManager
from exasol.exaslpm.pkg_mgmt.install_apt import install_via_apt
from exasol.exaslpm.pkg_mgmt.package_file_session import PackageFileSession


def package_install(
    phase_name: str,
    package_file: pathlib.Path,
    build_step_name: str,
    python_binary: pathlib.Path,
    conda_binary: pathlib.Path,
    r_binary: pathlib.Path,
    cmd_executor: CommandExecutor,
    logger: CommandLogger,
    history_file_manager: HistoryFileManager,
    binary_finder: BinaryFinder,
):
    logger.info(
        f"Phase: {phase_name}, \
        Package File: {package_file}, \
        Build Step: {build_step_name}, \
        Python Binary: {python_binary}, \
        Conda Binary: {conda_binary}, \
        R Binary: {r_binary}",
    )

    history_file_manager.raise_if_build_step_exists(build_step_name)

    try:
        package_file_session = PackageFileSession(package_file=package_file)
    except Exception as e:
        logger.err(
            "Failed to read package file.", package_file=package_file, exception=e
        )
        raise
    try:
        build_step = package_file_session.package_file_config.find_build_step(
            build_step_name
        )
        single_phase = build_step.find_phase(phase_name)
    except Exception as e:
        logger.err(
            "Build step or phase not found.",
            package_file=package_file,
            build_step=build_step_name,
            phase=phase_name,
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

    history_file_manager.add_build_step_to_history(build_step)
