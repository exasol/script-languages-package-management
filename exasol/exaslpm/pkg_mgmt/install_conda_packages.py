import pathlib
from io import TextIOBase

from exasol.exaslpm.model.package_file_config import (
    CondaBinary,
    CondaPackage,
    Phase,
)
from exasol.exaslpm.pkg_mgmt.context.context import Context
from exasol.exaslpm.pkg_mgmt.install_common import (
    CommandExecInfo,
    run_cmd,
)
from exasol.exaslpm.pkg_mgmt.micromamba_env import conda_cmd_from_history
from exasol.exaslpm.pkg_mgmt.search.package_collectors import (
    collect_conda_channels,
    collect_conda_packages,
)
from exasol.exaslpm.pkg_mgmt.search.search_cache import SearchCache


def _prepare_all_cmds(
    conda_package_file: pathlib.Path,
    all_channels: set[str],
    conda_binary: CondaBinary,
    search_cache: SearchCache,
) -> list[CommandExecInfo]:

    # create a list of kind ["-c", "conda-forge", "-c", "nvidia",...] from list ["conda-forge", "nvidia"]
    channel_args = [x for ch in all_channels for x in ("-c", ch)]

    install_cmd = conda_cmd_from_history(
        search_cache=search_cache,
        conda_binary=conda_binary,
        params=[
            "install",
            "--yes",
            "--file",
            str(conda_package_file),
        ]
        + channel_args,
        err="Failed while installing conda packages",
    )
    clean_cmd = conda_cmd_from_history(
        search_cache=search_cache,
        conda_binary=conda_binary,
        params=["clean", "--all", "--yes", "--index-cache", "--tarballs"],
        err="Failed while clearing cache - conda cmd",
    )

    ldconfig_cmd = CommandExecInfo(
        cmd=["ldconfig"], err="Failed while running ldconfig"
    )

    return [install_cmd, clean_cmd, ldconfig_cmd]


def _write_conda_spec(
    output_file: TextIOBase, all_packages: list[CondaPackage]
) -> None:
    for package in all_packages:
        channel_str = f"{package.channel}::" if package.channel else ""
        build_str = f"={package.build}" if package.build else ""
        print(
            f"{channel_str}{package.name}{package.version}{build_str}",
            file=output_file,
        )


def install_conda_packages(search_cache: SearchCache, phase: Phase, ctx: Context):
    if phase.conda and len(phase.conda.packages) > 0:
        all_packages = collect_conda_packages(search_cache.all_phases + [phase])
        all_channels = collect_conda_channels(search_cache.all_phases + [phase])
        with ctx.temp_file_provider.create() as temp_file:
            with temp_file.open() as f:
                _write_conda_spec(f, all_packages)
            cmds = _prepare_all_cmds(
                temp_file.path, all_channels, phase.conda.binary, search_cache
            )

            for cmd in cmds:
                run_cmd(cmd, ctx)
    else:
        ctx.cmd_logger.warn("Got an empty list of CondaPackages")
