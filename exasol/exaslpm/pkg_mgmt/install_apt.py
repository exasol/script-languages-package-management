from exasol.exaslpm.model.package_file_config import AptPackages
from exasol.exaslpm.pkg_mgmt.cmd_executor import (
    CommandExecutor,
    CommandFailedException,
    CommandLogger,
)
from exasol.exaslpm.pkg_mgmt.install_common import (
    CommandExecInfo,
    check_error,
)


def prepare_all_cmds(apt_packages: AptPackages) -> list[CommandExecInfo]:
    all_cmds = []

    all_cmds.append(
        CommandExecInfo(
            cmd=["apt-get", "-y", "update"], err="Failed while updating apt cmd"
        )
    )

    install_cmd = ["apt-get", "install", "-V", "-y", "--no-install-recommends"]
    if apt_packages.packages is None:
        raise ValueError("no apt packages defined")
    for package in apt_packages.packages:
        install_cmd.append(f"{package.name}={package.version}")
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


def install_via_apt(
    apt_packages: AptPackages, executor: CommandExecutor, log: CommandLogger
) -> int:
    if len(apt_packages.packages) > 0:
        cmd_n_errs = prepare_all_cmds(apt_packages)
        for cmd_n_err in cmd_n_errs:
            cmd_res = executor.execute(cmd_n_err.cmd)
            cmd_res.print_results()
            if not check_error(cmd_res.return_code(), cmd_n_err.err, log.err):
                raise CommandFailedException(cmd_n_err.err)
    else:
        log.warn("Got an empty list of AptPackages")
    return 0
