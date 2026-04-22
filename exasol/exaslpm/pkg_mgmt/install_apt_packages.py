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
    if not pkg.version:
        return ""
    elif pkg.version.find("*") == -1:
        return pkg.version
    elif pkg.name in madison_dict:
        madison_variants = madison_dict[pkg.name]
        filtered_versions = [
            variant.version
            for variant in madison_variants
            if pkg.version and MadisonData.is_match(variant.version, pkg.version)
        ]
        if not filtered_versions:
            raise ValueError(
                f"No matching version found for {pkg.name} with version {pkg.version} in {madison_variants}"
            )
        pkg_ver = filtered_versions[0]
        ctx.cmd_logger.info(
            f"Resolved version={pkg_ver} for {pkg.name} with wildcard: {pkg.version}"
        )
    else:
        raise ValueError(
            f"{pkg.name} with version {pkg.version} not found in madison output"
        )
    return pkg_ver


def update_cmd_and_err() -> CommandExecInfo:
    return CommandExecInfo(
        cmd=["apt-get", "-y", "update"], err="Failed while updating apt cmd"
    )


def clean_cmd_and_err() -> CommandExecInfo:
    return CommandExecInfo(
        cmd=["apt-get", "-y", "clean"], err="Failed while running apt clean"
    )


def autoremove_cmd_and_err() -> CommandExecInfo:
    return CommandExecInfo(
        cmd=["apt-get", "-y", "autoremove"],
        err="Failed while running apt autoremove",
    )


def locale_gen_cmd_and_err() -> CommandExecInfo:
    return CommandExecInfo(
        cmd=["locale-gen", "en_US.UTF-8"], err="Failed while running locale-gen cmd"
    )


def update_locale_cmd_and_err() -> CommandExecInfo:
    return CommandExecInfo(
        cmd=["update-locale", "LC_ALL=en_US.UTF-8"],
        err="Failed while running update-locale cmd",
    )


def load_config_and_err() -> CommandExecInfo:
    return CommandExecInfo(
        cmd=["ldconfig"],
        err="Failed while running ldconfig",
    )


def install_cmd_and_err(all_pkgs: list[AptPackage], ctx: Context) -> CommandExecInfo:
    if all_pkgs is None:
        raise ValueError("no apt packages defined")
    install_cmd = ["apt-get", "install", "-V", "-y", "--no-install-recommends"]

    wildcard_pkgs = [
        pkg for pkg in all_pkgs if pkg and pkg.version and "*" in pkg.version
    ]
    madison_out = MadisonExecutor.execute_madison(wildcard_pkgs, ctx)
    madison_dict = MadisonParser.parse_madison_output(madison_out, ctx)
    for pkg in all_pkgs:
        pkg_ver = get_package_version(pkg, ctx, madison_dict)
        apt_cmd = f"{pkg.name}={pkg_ver}" if pkg_ver else pkg.name
        install_cmd.append(apt_cmd)
    return CommandExecInfo(
        cmd=install_cmd,
        err="Failed while installing apt cmd",
    )


def install_apt_packages(apt_packages: AptPackages, ctx: Context) -> int:
    if len(apt_packages.packages) == 0:
        ctx.cmd_logger.warn("Got an empty list of AptPackages")
        return 1

    run_cmd(update_cmd_and_err(), ctx)

    run_cmd(install_cmd_and_err(apt_packages.packages, ctx), ctx)

    run_cmd(clean_cmd_and_err(), ctx)

    run_cmd(autoremove_cmd_and_err(), ctx)

    run_cmd(locale_gen_cmd_and_err(), ctx)

    run_cmd(update_locale_cmd_and_err(), ctx)

    run_cmd(load_config_and_err(), ctx)
    return 0
