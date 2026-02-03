import platform

from exasol.exaslpm.model.package_file_config import (
    Phase,
)
from exasol.exaslpm.pkg_mgmt.context.context import Context
from exasol.exaslpm.pkg_mgmt.install_common import (
    CommandExecInfo,
    run_cmd,
)
from exasol.exaslpm.pkg_mgmt.micromamba_env import micromamba_cmd_from_micromamba


def install_micromamba(phase: Phase, ctx: Context):
    if phase.tools and phase.tools.micromamba:
        micromamba = phase.tools.micromamba

        micromamba_machine_mapping = {"x86_64": "64", "aarch64": "aarch64"}

        micromamba_machine = micromamba_machine_mapping[platform.machine()]
        "https://github.com/mamba-org/micromamba-releases/releases/download/2.5.0-1/micromamba-linux-64.tar.bz2"

        download_url = f"https://github.com/mamba-org/micromamba-releases/releases/download/{micromamba.version}/micromamba-linux-{micromamba_machine}.tar.bz2"

        ctx.cmd_logger.info(f"Downloading {download_url}")
        with ctx.file_downloader.download_file_to_tmp(
            url=download_url, timeout_in_seconds=120
        ) as get_micromamba_tar:
            extract_cmd = CommandExecInfo(
                # Extract only "bin/micromamba" to target directory /
                cmd=[
                    "tar",
                    "-xvf",
                    str(get_micromamba_tar),
                    "-C",
                    "/",
                    "bin/micromamba",
                ],
                err="Failed while extracting micromamba",
            )
            run_cmd(extract_cmd, ctx)

        create_env_cmd = micromamba_cmd_from_micromamba(
            micromamba,
            params=["create", "-n", "base"],
            err="Create micromamba env failed",
        )
        run_cmd(create_env_cmd, ctx)
