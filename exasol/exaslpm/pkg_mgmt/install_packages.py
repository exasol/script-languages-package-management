import pathlib

from exasol.exaslpm.model.package_file_config import (
    BuildStep,
    Phase,
)
from exasol.exaslpm.pkg_mgmt.context.context import Context
from exasol.exaslpm.pkg_mgmt.install_apt import install_via_apt
from exasol.exaslpm.pkg_mgmt.install_pip import install_pip
from exasol.exaslpm.pkg_mgmt.package_file_session import PackageFileSession
from exasol.exaslpm.pkg_mgmt.search.search_cache import SearchCache


def _process_tools(context: Context, search_cache: SearchCache, phase: Phase):
    if phase.tools:
        tools = phase.tools
        if tools.pip:
            install_pip(search_cache, phase, context)


def _process_phase(context: Context, build_step: BuildStep, phase: Phase) -> None:
    search_cache = SearchCache(build_step, phase, context)
    if phase.apt is not None:
        install_via_apt(phase.apt, context)
    if phase.tools is not None:
        _process_tools(context, search_cache, phase)


def package_install(package_file: pathlib.Path, build_step_name: str, context: Context):
    logger = context.cmd_logger

    logger.info(f"Package File: {package_file}, Build Step: {build_step_name}")

    context.history_file_manager.raise_if_build_step_exists(build_step_name)

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

    except Exception as e:
        logger.err(
            "Build step not found.",
            package_file=package_file,
            build_step=build_step_name,
            exception=e,
        )
        raise
    for phase in build_step.phases:
        logger.info(f"Processing phase:'{phase.name}'")
        try:
            _process_phase(context, build_step, phase)
        except Exception as e:
            logger.err(
                "Failed to process phase.", package_file=package_file, exception=e
            )
            raise

    context.history_file_manager.add_build_step_to_history(build_step)
