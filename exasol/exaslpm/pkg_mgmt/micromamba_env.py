from exasol.exaslpm.model.package_file_config import (
    CondaBinary,
    Micromamba,
)
from exasol.exaslpm.pkg_mgmt.constants import MICROMAMBA_PATH
from exasol.exaslpm.pkg_mgmt.install_common import CommandExecInfo
from exasol.exaslpm.pkg_mgmt.search.search_cache import SearchCache


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


def conda_cmd_from_history(
    search_cache: SearchCache, conda_binary: CondaBinary, params: list[str], err: str
) -> CommandExecInfo:
    # Use lazy loading here as searching for not declared binaries can raise an exception
    get_binary = {
        CondaBinary.Micromamba: lambda: search_cache.micro_mamba_binary_path,
        CondaBinary.Mamba: lambda: search_cache.mamba_binary_path,
        CondaBinary.Conda: lambda: search_cache.conda_binary_path,
    }
    binary_path = get_binary[conda_binary]()

    return CommandExecInfo(
        cmd=[str(binary_path)] + params,
        err=err,
        env=create_mamba_env_variables(search_cache.micromamba),
    )
