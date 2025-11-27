import subprocess
from typing import List

from exasol.exaslpm.model.package_file_config import AptPackages


def prepare_update_command():
    update_cmd = ["apt-get", "-y", "update"]
    return update_cmd


def prepare_clean_cmd():
    clean_cmd = ["apt-get", "-y", "clean"]
    return clean_cmd


def prepare_autoremove_cmd():
    autoremove_cmd = ["apt-get", "-y", "autoremove"]
    return autoremove_cmd


def prepare_ldconfig_cmd():
    ldconfig_cmd = ["ldconfig"]
    return ldconfig_cmd


def prepare_locale_cmd():
    locale_cmd = ["locale-gen", "&&", "update-locale", "LANG=en_US.UTF8"]
    return locale_cmd


def prepare_install_cmd(apt_packages: AptPackages):
    install_cmd = ["apt-get", "install", "-V", "-y", "--no-install-recommends"]
    if apt_packages.packages is not None:
        for package in apt_packages.packages:
            install_cmd.append(f"{package.name}={package.version}")
    return install_cmd


class CommandExecutor:
  def execute(command: list[str]):
      print(f"Executing: {command}")
      result = subprocess.run(command, capture_output=True)
      print(
          "Success"
          if result.returncode == 0
          else f"Failed with exit code {result.returncode}"
      )


def install_via_apt(apt_packages: AptPackages):
    if apt_packages is not None:
        update_cmd = prepare_update_command()
        execute_cmd(update_cmd)

        install_cmd = prepare_install_cmd(apt_packages)
        execute_cmd(install_cmd)

        clean_cmd = prepare_clean_cmd()
        execute_cmd(clean_cmd)

        autoremove_cmd = prepare_autoremove_cmd()
        execute_cmd(autoremove_cmd)

        locale_cmd = prepare_locale_cmd()
        execute_cmd(locale_cmd)

        ldconfig_cmd = prepare_ldconfig_cmd()
        execute_cmd(ldconfig_cmd)
    else:
        print("Invalid AptPackagaes")
