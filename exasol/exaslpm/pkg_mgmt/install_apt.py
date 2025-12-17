from exasol.exaslpm.model.package_file_config import AptPackages
from exasol.exaslpm.pkg_mgmt.cmd_executor import (
    CommandExecutor,
    CommandLogger,
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


def prepare_ldconfig_cmd() -> list[str]:
    ldconfig_cmd = ["ldconfig"]
    return ldconfig_cmd


def prepare_locale_cmd() -> list[str]:
    locale_cmd = ["locale-gen", "&&", "update-locale", "LANG=en_US.UTF8"]
    return locale_cmd


def prepare_install_cmd(apt_packages: AptPackages) -> list[str]:
    install_cmd = ["apt-get", "install", "-V", "-y", "--no-install-recommends"]
    if apt_packages.packages is not None:
        for package in apt_packages.packages:
            install_cmd.append(f"{package.name}={package.version}")
    return install_cmd


def install_via_apt(
    apt_packages: AptPackages, executor: CommandExecutor, log: CommandLogger
):
    if len(apt_packages.packages) > 0:
        update_cmd = prepare_update_command()
        cmd_res = executor.execute(update_cmd)
        cmd_res.print_results()
        #if cmd_res.return_code() != 0 :
            #log.err("Failed while updating apt cmd")

        install_cmd = prepare_install_cmd(apt_packages)
        cmd_res = executor.execute(install_cmd)
        cmd_res.print_results()
        # if cmd_res.return_code() != 0 :
        # log.err("Failed while installing apt cmd")

        clean_cmd = prepare_clean_cmd()
        cmd_res = executor.execute(clean_cmd)
        cmd_res.print_results()
        # if cmd_res.return_code() != 0 :
        # log.err("Failed while cleaning apt cmd")

        autoremove_cmd = prepare_autoremove_cmd()
        cmd_res = executor.execute(autoremove_cmd)
        cmd_res.print_results()
        # if cmd_res.return_code() != 0 :
        # log.err("Failed while autoremoving apt cmd")

        locale_cmd = prepare_locale_cmd()
        cmd_res = executor.execute(locale_cmd)
        cmd_res.print_results()

        ldconfig_cmd = prepare_ldconfig_cmd()
        cmd_res = executor.execute(ldconfig_cmd)
        cmd_res.print_results()
    else:
        log.error("Got an empty list of AptPackages")
