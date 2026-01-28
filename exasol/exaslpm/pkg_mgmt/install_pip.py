from packaging.version import Version

from exasol.exaslpm.model.package_file_config import (
    BuildStep,
    Phase,
)
from exasol.exaslpm.pkg_mgmt.binary_types import BinaryType
from exasol.exaslpm.pkg_mgmt.context.context import Context
from exasol.exaslpm.pkg_mgmt.install_common import (
    CommandExecInfo,
    run_cmd,
)
from exasol.exaslpm.pkg_mgmt.search.find_in_build_steps import (
    find_binary,
    find_phases_of_build_steps,
)


def install_pip(build_step: BuildStep, phase: Phase, ctx: Context):
    if phase.tools and phase.tools.pip:
        pip = phase.tools.pip
        with ctx.file_downloader.download_file_to_tmp(
            url="https://bootstrap.pypa.io/get-pip.py"
        ) as get_pip:

            previous_phases = find_phases_of_build_steps(
                ctx.history_file_manager.get_all_previous_build_steps(),
                build_step,
                phase.name,
            )
            python_binary_path = find_binary(BinaryType.PYTHON, previous_phases)
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
