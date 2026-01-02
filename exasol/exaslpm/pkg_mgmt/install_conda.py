import pathlib

from exasol.exaslpm.model.package_file_config import CondaPackages
from exasol.exaslpm.pkg_mgmt.cmd_executor import (
    CommandExecutor,
    CommandLogger,
)
from exasol.exaslpm.pkg_mgmt.install_utils import (
    prepare_ldconfig_cmd,
    prepare_locale_cmd,
)


def clear_cache_cmd(conda_binary: pathlib.Path):
    conda_binary_str = str(conda_binary)
    clean_cmd = [
        conda_binary_str,
        "clean",
        "--all",
        "--yes",
        "--index-cache",
        "-tarballs",
    ]
    return clean_cmd


def prepare_install_cmd(
    conda_packages: CondaPackages, conda_binary: pathlib.Path
) -> list[str]:
    conda_binary_str = str(conda_binary)
    install_cmd = [conda_binary_str, "install", "--no-install-recommends"]
    if conda_packages.channels:
        for channel in conda_packages.channels:
            install_cmd.append("-c")
            install_cmd.append(channel)
    if conda_packages.packages is not None:
        for package in conda_packages.packages:
            install_cmd.append(f"{package.name}={package.version}")
    return install_cmd


def check_error(ret_val, msg, log):
    if ret_val != 0:
        log(msg)
        return False
    return True


def install_via_conda(
    conda_packages: CondaPackages,
    conda_binary: pathlib.Path,
    executor: CommandExecutor,
    log: CommandLogger,
):
    if len(conda_packages.packages) > 0:
        clear_cache = clear_cache_cmd(conda_binary)
        cmd_res = executor.execute(clear_cache)
        cmd_res.print_results()
        if not check_error(
            cmd_res.return_code(), "Failed while updating clear cmd", log.err
        ):
            return

        install_cmd = prepare_install_cmd(conda_packages, conda_binary)
        cmd_res = executor.execute(install_cmd)
        cmd_res.print_results()
        if not check_error(
            cmd_res.return_code(), "Failed while installing conda cmd", log.err
        ):
            return

        locale_cmd = prepare_locale_cmd()
        cmd_res = executor.execute(locale_cmd)
        cmd_res.print_results()
        if not check_error(
            cmd_res.return_code(), "Failed while preparing conda cmd", log.err
        ):
            return

        ldconfig_cmd = prepare_ldconfig_cmd()
        cmd_res = executor.execute(ldconfig_cmd)
        cmd_res.print_results()
        if not check_error(
            cmd_res.return_code(), "Failed while ldconfig conda cmd", log.err
        ):
            return
    else:
        log.err("Got an empty list of CondaPackages")
