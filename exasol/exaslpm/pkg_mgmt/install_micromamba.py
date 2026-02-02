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

        download_url = (
            f"https://micro.mamba.pm/api/micromamba/linux-64/{micromamba.version}"
        )

        with ctx.file_downloader.download_file_to_tmp(
            url=download_url
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
