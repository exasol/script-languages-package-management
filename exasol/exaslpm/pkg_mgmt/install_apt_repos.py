from pathlib import Path

from exasol.exaslpm.model.package_file_config import (
    AptPackages,
    AptRepo,
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


def _install_key(context: Context, repo_name: str, repo: AptRepo):
    with context.file_downloader.download_file_to_tmp(url=str(repo.key_url)) as tmp:
        key_file = f"/usr/share/keyrings/{repo_name}.gpg"
        context.cmd_logger.info(f"Installing key of '{repo_name}' to {key_file}")
        gpg_cmd = CommandExecInfo(
            cmd=["gpg", "--dearmor", "--yes", "-o", key_file, str(tmp)],
            err="Failed installing key",
        )
        run_cmd(gpg_cmd, context)


def _install_repository(context: Context, repo_name: str, repo: AptRepo):
    with context.temp_file_provider.create() as tmp:
        with tmp.open() as fp:
            print(repo.entry, file=fp)
        list_file_path = Path("/etc") / "apt" / "sources.list.d" / repo.out_file
        context.cmd_logger.info(
            f"Installing APT repository list file of '{repo_name}' to {list_file_path}"
        )
        context.file_access.copy_file(tmp.path, list_file_path)


def install_apt_repos(apt_packages: AptPackages, context: Context):
    if apt_packages.repos:
        for repo_name, repo in apt_packages.repos.items():
            context.cmd_logger.info(f"Installing APT repository '{repo_name}'")
            _install_key(context, repo_name, repo)
            _install_repository(context, repo_name, repo)
        _run_apt_update(context)
