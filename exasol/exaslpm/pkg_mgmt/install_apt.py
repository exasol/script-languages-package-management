# sgn

from collections.abc import Callable
from typing import (
    Any,
    TypedDict,
)

from exasol.exaslpm.model.package_file_config import AptPackages
from exasol.exaslpm.pkg_mgmt.cmd_executor import (
    CommandExecutor,
    CommandFailedException,
    CommandLogger,
)


class CmdNErr(TypedDict):
    cmd: list[str]
    err: str


def prepare_all_cmds(apt_packages: AptPackages) -> list[dict]:
    all_cmds = []

    cmd_n_err: dict[str, list[str] | str] = {}
    cmd_n_err["cmd"] = ["apt-get", "-y", "update"]
    cmd_n_err["err"] = "Failed while updating apt cmd"
    all_cmds.append(cmd_n_err)

    cmd_n_err = {}
    install_cmd = ["apt-get", "install", "-V", "-y", "--no-install-recommends"]
    if apt_packages.packages is not None:
        for package in apt_packages.packages:
            install_cmd.append(f"{package.name}={package.version}")
    cmd_n_err["cmd"] = install_cmd
    cmd_n_err["err"] = "Failed while installing apt cmd"
    all_cmds.append(cmd_n_err)

    cmd_n_err = {}
    cmd_n_err["cmd"] = ["apt-get", "-y", "clean"]
    cmd_n_err["err"] = "Failed while cleaning apt cmd"
    all_cmds.append(cmd_n_err)

    cmd_n_err = {}
    cmd_n_err["cmd"] = ["apt-get", "-y", "autoremove"]
    cmd_n_err["err"] = "Failed while autoremoving apt cmd"
    all_cmds.append(cmd_n_err)

    cmd_n_err = {}
    cmd_n_err["cmd"] = ["locale-gen", "en_US.UTF-8"]
    cmd_n_err["err"] = "Failed while preparing locale-gen cmd"
    all_cmds.append(cmd_n_err)

    cmd_n_err = {}
    cmd_n_err["cmd"] = ["update-locale", "LC_ALL=en_US.UTF-8"]
    cmd_n_err["err"] = "Failed while update-locale apt cmd"
    all_cmds.append(cmd_n_err)

    cmd_n_err = {}
    cmd_n_err["cmd"] = ["ldconfig"]
    cmd_n_err["err"] = "Failed while ldconfig apt cmd"
    all_cmds.append(cmd_n_err)

    return all_cmds


def check_error(ret_val: int, msg: str, log: Callable[[str], None]) -> bool:
    if ret_val != 0:
        log(msg)
        return False
    return True


def install_via_apt(
    apt_packages: AptPackages, executor: CommandExecutor, log: CommandLogger
) -> int:
    if len(apt_packages.packages) > 0:
        cmd_n_errs = prepare_all_cmds(apt_packages)
        for cmd_n_err in cmd_n_errs:
            cmd_res = executor.execute(cmd_n_err["cmd"])
            cmd_res.print_results()
            if not check_error(cmd_res.return_code(), cmd_n_err["err"], log.err):
                raise CommandFailedException(cmd_n_err["err"])
    else:
        log.warn("Got an empty list of AptPackages")
    return 0
