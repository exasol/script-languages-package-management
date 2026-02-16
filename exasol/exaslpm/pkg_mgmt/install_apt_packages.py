from exasol.exaslpm.model.package_file_config import (
    AptPackage,
    AptPackages,
)
from exasol.exaslpm.pkg_mgmt.context.context import Context
from exasol.exaslpm.pkg_mgmt.install_common import (
    CommandExecInfo,
    run_cmd,
)
from exasol.exaslpm.pkg_mgmt.search.apt_madison_parser import (
    MadisonData,
    MadisonExecutor,
    MadisonParser,
)


def get_package_version(
    pkg: AptPackage, ctx: Context, madison_dict: dict[str, list[MadisonData]]
) -> str:
    if pkg and pkg.version and pkg.version.find("*") == -1:
        return pkg.version
    if pkg.name in madison_dict:
        madison_variants = madison_dict[pkg.name]
        pkg_ver = madison_variants[0].ver
        ctx.cmd_logger.info(f"Resolved version for {pkg.name} with wildcard: {pkg_ver}")
    else:
        raise ValueError(
            f"{pkg.name} with version {pkg.version} not found in madison output"
        )
    return pkg_ver


def prepare_all_cmds(apt_packages: AptPackages, ctx: Context) -> list[CommandExecInfo]:
    all_cmds = []

    all_cmds.append(
        CommandExecInfo(
            cmd=["apt-get", "-y", "update"], err="Failed while updating apt cmd"
        )
    )
    install_cmd = ["apt-get", "install", "-V", "-y", "--no-install-recommends"]
    if apt_packages.packages is None:
        raise ValueError("no apt packages defined")

    # If wildcards are present, parse those
    pkgs = [
        pkg
        for pkg in apt_packages.packages
        if pkg and pkg.version and "*" in pkg.version
    ]
    madison_out = MadisonExecutor.execute_madison(pkgs, ctx)
    madison_dict = MadisonParser.parse_madison_output(madison_out)

    for package in apt_packages.packages:
        pkg_ver = get_package_version(package, ctx, madison_dict)
        apt_cmd = f"{package.name}={pkg_ver}" if pkg_ver else package.name
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
