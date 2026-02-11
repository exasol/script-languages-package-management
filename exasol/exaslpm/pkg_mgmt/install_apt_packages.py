from exasol.exaslpm.model.package_file_config import AptPackages
from exasol.exaslpm.pkg_mgmt.context.context import Context
from exasol.exaslpm.pkg_mgmt.install_common import (
    CommandExecInfo,
    run_cmd,
)
from exasol.exaslpm.pkg_mgmt.search.apt_madison_parser import MadisonParser


def parse_wildcard(package: str, ctx: Context) -> list[str]:
    cmd_res = ctx.cmd_executor.execute(["apt-cache", "madison", package])
    stdout_lines = []

    def consume_stdout(line, **kwargs):
        str_line = str(line)
        stdout_lines.append(str_line.strip())

    def consume_stderr(line, **kwargs):
        pass

    ret_code = cmd_res.consume_results(consume_stdout, consume_stderr)
    if ret_code == 0:
        madison_out = " ".join(stdout_lines)
        trimmed_out = MadisonParser.split_n_trim_madison_out(madison_out)
        vers = MadisonParser.parse_version(trimmed_out, [package])
        return vers


def prepare_all_cmds(apt_packages: AptPackages, ctx: Context) -> list[CommandExecInfo]:
    all_cmds = []

    all_cmds.append(
        CommandExecInfo(
            cmd=["apt-get", "-y", "update"], err="Failed while updating apt cmd"
        )
    )
    # get list of all pkgs with wild-cards (use list comprehension)
    # https://www.w3schools.com/python/python_lists_comprehension.asp
    # call the apt-cache madison class where the cmd is executed with this pkg-list
    install_cmd = ["apt-get", "install", "-V", "-y", "--no-install-recommends"]
    if apt_packages.packages is None:
        raise ValueError("no apt packages defined")
    for package in apt_packages.packages:
        pkg_ver = package.version
        if pkg_ver and pkg_ver.find("*") != -1:
            vers = parse_wildcard(package.name, ctx)
            pkg_ver = vers[0] if vers else pkg_ver
        apt_cmd = f"{package.name}={pkg_ver}" if package.version else package.name
        install_cmd.append(apt_cmd)
    all_cmds.append(
        CommandExecInfo(cmd=install_cmd, err="Failed while installing apt cmd")
    )
    all_cmds.append(
        CommandExecInfo(
            cmd=["apt-get", "-y", "clean"], err="Failed while running apt clean"
        )
    )
    all_cmds.append(
        CommandExecInfo(
            cmd=["apt-get", "-y", "autoremove"],
            err="Failed while running apt autoremove",
        )
    )
    all_cmds.append(
        CommandExecInfo(
            cmd=["locale-gen", "en_US.UTF-8"], err="Failed while running locale-gen cmd"
        )
    )
    all_cmds.append(
        CommandExecInfo(
            cmd=["update-locale", "LC_ALL=en_US.UTF-8"],
            err="Failed while running update-locale cmd",
        )
    )
    all_cmds.append(
        CommandExecInfo(cmd=["ldconfig"], err="Failed while running ldconfig")
    )
    return all_cmds


def install_apt_packages(apt_packages: AptPackages, context: Context) -> int:
    if len(apt_packages.packages) > 0:
        cmd_n_errs = prepare_all_cmds(apt_packages, context)
        for cmd_n_err in cmd_n_errs:
            run_cmd(cmd_n_err, context)
    else:
        context.cmd_logger.warn("Got an empty list of AptPackages")
    return 0
