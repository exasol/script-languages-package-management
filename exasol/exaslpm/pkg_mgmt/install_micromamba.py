import platform
from inspect import cleandoc
from pathlib import Path

from exasol.exaslpm.model.package_file_config import (
    Micromamba,
    Phase,
)
from exasol.exaslpm.pkg_mgmt.context.context import Context
from exasol.exaslpm.pkg_mgmt.install_common import (
    CommandExecInfo,
    run_cmd,
)
from exasol.exaslpm.pkg_mgmt.micromamba_env import micromamba_cmd_from_micromamba

_MICROMAMBA_EXE = "bin/micromamba"
_ACTIVATION_SCRIPT_PATH = Path("/usr") / "local" / "bin" / "_activate_current_env.sh"


def _install_micromamba_exec(micromamba: Micromamba, ctx: Context):
    micromamba_machine_mapping = {"x86_64": "64", "aarch64": "aarch64"}

    micromamba_machine = micromamba_machine_mapping[platform.machine()]

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
                _MICROMAMBA_EXE,
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


def _install_activation_script(micromamba: Micromamba, ctx: Context) -> None:
    activation_script = cleandoc(f"""
        # shellcheck disable=SC2148
        
        # This script should never be called directly, only sourced:
        
        #     source _activate_current_env.sh
        export MAMBA_ROOT_PREFIX="{micromamba.root_prefix}"
        export MAMBA_DOCKERFILE_ACTIVATE=1
        
        if [[ "${{MAMBA_SKIP_ACTIVATE}}" == "1" ]]; then
          return
        fi
        
        # Initialize the current shell
        eval "$("/{_MICROMAMBA_EXE}" shell hook --shell=bash)" 2>/dev/null 1>2
        
        # For robustness, try all possible activate commands.
        conda activate "{micromamba.env_name}" 2>/dev/null 1>2 \
          || mamba activate "{micromamba.env_name}" 2>/dev/null 1>2 \
          || micromamba activate "{micromamba.env_name}" 2>/dev/null 1>2
    """)

    with ctx.temp_file_provider.create() as activation_script_temp_file:
        with activation_script_temp_file.open() as f:
            print(activation_script, file=f)
        ctx.file_access.copy_file(
            activation_script_temp_file.path, _ACTIVATION_SCRIPT_PATH
        )


def _run_setup_for_activation_script(micromamba: Micromamba, ctx: Context):
    install_activation_script = cleandoc(f"""
    #!/bin/bash

    set -e
    set -u
    set -o pipefail
    # Activate micromamba for the bash
    echo "source {_ACTIVATION_SCRIPT_PATH}" >> ~/.bashrc && \
    echo "source {_ACTIVATION_SCRIPT_PATH}" >> /etc/skel/.bashrc && \
    ln -s {_ACTIVATION_SCRIPT_PATH} /etc/profile.d/_activate_current_env.sh && \
    chmod -R a+rx {_ACTIVATION_SCRIPT_PATH}

    # Add conda lib directory to ld.so.conf
    echo "{micromamba.root_prefix}/lib" > /etc/ld.so.conf.d/conda.conf
    """)

    with ctx.temp_file_provider.create() as install_activation_script_temp_file:
        with install_activation_script_temp_file.open() as f:
            print(install_activation_script, file=f)
        err_msg = cleandoc(f"""
            Failed while installing conda activation script
            at {_ACTIVATION_SCRIPT_PATH}:
            {install_activation_script}
            """)
        cmd = CommandExecInfo(
            cmd=["bash", str(install_activation_script_temp_file.path)], err=err_msg
        )
        run_cmd(cmd, ctx)


def install_micromamba(phase: Phase, ctx: Context):
    if phase.tools and phase.tools.micromamba:
        micromamba = phase.tools.micromamba
        _install_micromamba_exec(micromamba, ctx)
        _install_activation_script(micromamba, ctx)
        _run_setup_for_activation_script(micromamba, ctx)
