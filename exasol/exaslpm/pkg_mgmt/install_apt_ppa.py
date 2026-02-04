from pathlib import Path

from exasol.exaslpm.model.package_file_config import (
    PPA,
    AptPackages,
)
from exasol.exaslpm.pkg_mgmt.context.context import Context
from exasol.exaslpm.pkg_mgmt.install_common import (
    CommandExecInfo,
    run_cmd,
)


def _run_apt_update(context: Context):
    apt_cmds = [
        CommandExecInfo(
            cmd=["apt-get", "-y", "update"], err="Failed while running apt-get update"
        ),
        CommandExecInfo(
            cmd=["apt-get", "-y", "clean"], err="Failed while running apt-get clean"
        ),
        CommandExecInfo(
            cmd=["apt-get", "-y", "autoremove"],
            err="Failed while running apt-get clean",
        ),
    ]
    for cmd in apt_cmds:
        run_cmd(cmd, context)


def _install_key(context: Context, ppa_name: str, ppa: PPA):
    with context.file_downloader.download_file_to_tmp(url=ppa.key_server) as tmp:
        key_file = f"/usr/share/keyrings/{ppa_name}.gpg"
        context.cmd_logger.info(f"Installing key of '{ppa_name}' to {key_file}")
        gpg_cmd = CommandExecInfo(
            cmd=["gpg", "--dearmor", "--yes", "-o", key_file, str(tmp)],
            err="Failed installing key",
        )
        run_cmd(gpg_cmd, context)


def _install_repository(context: Context, ppa_name: str, ppa: PPA):
    with context.temp_file_provider.create() as tmp:
        with tmp.open() as fp:
            print(ppa.ppa, file=fp)
        list_file_path = Path("/etc") / "apt" / "sources.list.d" / ppa.out_file
        context.cmd_logger.info(
            f"Installing ppa list file of '{ppa_name}' to {list_file_path}"
        )
        context.file_access.copy_file(tmp.path, list_file_path)


def install_ppas(apt_packages: AptPackages, context: Context):
    if apt_packages.ppas:
        for ppa_name, ppa in apt_packages.ppas.items():
            context.cmd_logger.info(f"Installing ppa '{ppa_name}'")
            _install_key(context, ppa_name, ppa)
            _install_repository(context, ppa_name, ppa)
        _run_apt_update(context)
