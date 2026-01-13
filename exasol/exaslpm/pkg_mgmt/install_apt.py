from collections.abc import Callable
from typing import Any

from exasol.exaslpm.model.package_file_config import AptPackages
from exasol.exaslpm.pkg_mgmt.cmd_executor import (
    CommandExecutor,
    CommandFailedException,
    CommandLogger,
)
from exasol.exaslpm.pkg_mgmt.install_utils import (
    prepare_ldconfig_cmd,
    prepare_locale_cmd,
)


def prepare_update_command() -> list[str]:
    update_cmd = ["apt-get", "-y", "update"]
    return update_cmd


def prepare_clean_cmd() -> list[str]:
    clean_cmd = ["apt-get", "-y", "clean"]
    return clean_cmd


def prepare_autoremove_cmd() -> list[str]:
    autoremove_cmd = ["apt-get", "-y", "autoremove"]
    return autoremove_cmd


def prepare_install_cmd(apt_packages: AptPackages) -> list[str]:
    install_cmd = ["apt-get", "install", "-V", "-y", "--no-install-recommends"]
    if apt_packages.packages is not None:
        for package in apt_packages.packages:
            install_cmd.append(f"{package.name}={package.version}")
    return install_cmd


def check_error(ret_val: int, msg: str, log: Callable[[str], None]) -> bool:
    if ret_val != 0:
        log(msg)
        return False
    return True


def install_via_apt(
    apt_packages: AptPackages, executor: CommandExecutor, log: CommandLogger
) -> int:
    if len(apt_packages.packages) > 0:
        update_cmd = prepare_update_command()
        cmd_res = executor.execute(update_cmd)
        cmd_res.print_results()
        if not check_error(
            cmd_res.return_code(), "Failed while updating apt cmd", log.err
        ):
            raise CommandFailedException("Failed while updating apt cmd")

        install_cmd = prepare_install_cmd(apt_packages)
        cmd_res = executor.execute(install_cmd)
        cmd_res.print_results()
        if not check_error(
            cmd_res.return_code(), "Failed while installing apt cmd", log.err
        ):
            raise CommandFailedException("Failed while installing apt cmd")

        clean_cmd = prepare_clean_cmd()
        cmd_res = executor.execute(clean_cmd)
        cmd_res.print_results()
        if not check_error(
            cmd_res.return_code(), "Failed while cleaning apt cmd", log.err
        ):
            raise CommandFailedException("Failed while cleaning apt cmd")

        autoremove_cmd = prepare_autoremove_cmd()
        cmd_res = executor.execute(autoremove_cmd)
        cmd_res.print_results()
        if not check_error(
            cmd_res.return_code(), "Failed while autoremoving apt cmd", log.err
        ):
            raise CommandFailedException("Failed while autoremoving apt cmd")

        locale_cmd = ["locale-gen", "en_US.UTF-8"]
        cmd_res = executor.execute(locale_cmd)
        cmd_res.print_results()
        if not check_error(
            cmd_res.return_code(), "Failed while preparing locale cmd", log.err
        ):
            raise CommandFailedException("Failed while preparing locale apt cmd")

        locale_cmd = ["update-locale", "LC_ALL=en_US.UTF-8"]
        cmd_res = executor.execute(locale_cmd)
        cmd_res.print_results()
        if not check_error(
            cmd_res.return_code(), "Failed while update locale apt cmd", log.err
        ):
            raise CommandFailedException("Failed while update locale apt cmd")

        ldconfig_cmd = prepare_ldconfig_cmd()
        cmd_res = executor.execute(ldconfig_cmd)
        cmd_res.print_results()
        if not check_error(
            cmd_res.return_code(), "Failed while ldconfig apt cmd", log.err
        ):
            raise CommandFailedException("Failed while ldconfig apt cmd")
    else:
        log.warn("Got an empty list of AptPackages")
    return 0
