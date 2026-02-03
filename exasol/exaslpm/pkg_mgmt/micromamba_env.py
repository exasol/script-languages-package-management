from exasol.exaslpm.model.package_file_config import Micromamba
from exasol.exaslpm.pkg_mgmt.constants import MICROMAMBA_PATH
from exasol.exaslpm.pkg_mgmt.install_common import CommandExecInfo


def create_mamba_env_variables(micromamba: Micromamba) -> dict[str, str]:
    return {"MAMBA_ROOT_PREFIX": str(micromamba.root_prefix)}


def micromamba_cmd_from_micromamba(
    micromamba: Micromamba, params: list[str], err: str
) -> CommandExecInfo:
    return CommandExecInfo(
        cmd=[str(MICROMAMBA_PATH)] + params,
        err=err,
        env=create_mamba_env_variables(micromamba),
    )
