from exasol.exaslpm.model.package_file_config import (
    Phase,
)
from exasol.exaslpm.pkg_mgmt.context.context import Context
from exasol.exaslpm.pkg_mgmt.install_common import (
    CommandExecInfo,
    run_cmd,
)
from exasol.exaslpm.pkg_mgmt.search.package_collectors import collect_pip_packages
from exasol.exaslpm.pkg_mgmt.search.search_cache import SearchCache


def _install_build_tools_ephemerally(ctx: Context):
    apt_update_cmd = CommandExecInfo(
        cmd=["apt-get", "-y", "update"], err="Failed while updating apt cmd"
    )
    run_cmd(apt_update_cmd, ctx)

    apt_install_cmd = CommandExecInfo(
        cmd=[
            "apt-get",
            "install",
            "-y",
            "--no-install-recommends",
            "build-essential",
            "pkg-config",
        ],
        err="Failed while installing build-essential and pkg-config",
    )
    run_cmd(apt_install_cmd, ctx)


def _uninstall_build_tools_ephemerally(ctx: Context):
    apt_purge_cmd = CommandExecInfo(
        cmd=["apt-get", "purge", "-y", "build-essential", "pkg-config"],
        err="Failed while running apt-get purge",
    )
    run_cmd(apt_purge_cmd, ctx)

    apt_purge_cmd = CommandExecInfo(
        cmd=["apt-get", "-y", "autoremove"],
        err="Failed while running apt-get autoremove",
    )
    run_cmd(apt_purge_cmd, ctx)


def install_pip_packages(search_cache: SearchCache, phase: Phase, ctx: Context):

    packages_to_install = collect_pip_packages(search_cache.all_phases + [phase])
    python_binary_path = search_cache.python_binary_path

    if not phase.pip or phase.pip.packages:
        ctx.cmd_logger.warn("Got an empty list of pip packages")
    else:
        if phase.pip.install_build_tools_ephemerally:
            _install_build_tools_ephemerally(ctx)
        with ctx.temp_file_provider.create() as temp_file:
            with temp_file.open() as f:
                for package in packages_to_install:
                    print(f"{package.name}=={package.version}", file=f)

            install_pip_cmd = CommandExecInfo(
                cmd=[
                    str(python_binary_path),
                    "-m",
                    "pip",
                    "install",
                    "-r",
                    str(temp_file.path),
                ],
                err="Failed while installing pip packages",
            )
            if search_cache.pip.needs_break_system_packages:
                install_pip_cmd.cmd.append("--break-system-packages")
            run_cmd(install_pip_cmd, ctx)
        if phase.pip.install_build_tools_ephemerally:
            _uninstall_build_tools_ephemerally(ctx)
