from packaging.version import Version

from exasol.exaslpm.model.package_file_config import (
    Phase,
)
from exasol.exaslpm.pkg_mgmt.context.context import Context
from exasol.exaslpm.pkg_mgmt.install_common import (
    CommandExecInfo,
    run_cmd,
)
from exasol.exaslpm.pkg_mgmt.search.search_cache import SearchCache


def install_pip(search_cache: SearchCache, phase: Phase, ctx: Context):
    if phase.tools and phase.tools.pip:
        pip = phase.tools.pip
        with ctx.file_downloader.download_file_to_tmp(
            url="https://bootstrap.pypa.io/get-pip.py"
        ) as get_pip:
            python_binary_path = search_cache.python_binary_path
            install_pip_cmd = CommandExecInfo(
                cmd=[str(python_binary_path), str(get_pip), f"pip == {pip.version}"],
                err="Failed while installing pip",
            )

            if Version(pip.version) >= Version("23.1"):
                install_pip_cmd.cmd.append("--break-system-packages")

            run_cmd(install_pip_cmd, ctx)

            clean_pip_cache_cmd = CommandExecInfo(
                cmd=[
                    "bash",
                    "-c",
                    f'rm -rf "$({python_binary_path} -m pip cache dir)"',
                ],
                err="Failed while cleaning pip cache",
            )
            run_cmd(clean_pip_cache_cmd, ctx)
