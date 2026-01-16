import pathlib

from exasol.exaslpm.model.package_file_config import CondaPackages
from exasol.exaslpm.pkg_mgmt.cmd_executor import (
    CommandExecutor,
    CommandFailedException,
    CommandLogger,
)
from exasol.exaslpm.pkg_mgmt.install_common import (
    CommandExecInfo,
    check_error,
)


def prepare_all_cmds(
    conda_packages: CondaPackages, conda_binary: pathlib.Path
) -> list[CommandExecInfo]:
    all_cmds = []

    all_cmds.append(
        CommandExecInfo(
            cmd=[
                str(conda_binary),
                "clean",
                "--all",
                "--yes",
                "--index-cache",
                "-tarballs",
            ],
            err="Failed while clearing cache - conda cmd",
        )
    )

    install_cmd = [str(conda_binary), "install", "--no-install-recommends"]
    if conda_packages.channels:
        for channel in conda_packages.channels:
            install_cmd.append("-c")
            install_cmd.append(channel)
    if conda_packages.packages:
        for package in conda_packages.packages:
            install_cmd.append(f"{package.name}={package.version}")
    all_cmds.append(
        CommandExecInfo(cmd=install_cmd, err="Failed while installing conda cmd")
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


def install_via_conda(
    conda_packages: CondaPackages,
    conda_binary: pathlib.Path,
    executor: CommandExecutor,
    log: CommandLogger,
) -> int:
    if len(conda_packages.packages) > 0:
        cmd_n_errs = prepare_all_cmds(conda_packages, conda_binary)
        for cmd_n_err in cmd_n_errs:
            cmd_res = executor.execute(cmd_n_err.cmd)
            cmd_res.print_results()
            if not check_error(cmd_res.return_code(), cmd_n_err.err, log.err):
                raise CommandFailedException(cmd_n_err.err)
    else:
        log.warn("Got an empty list of CondaPackages")
    return 0
