from packaging.version import Version
from exasol.exaslpm.model.package_file_config import (
    Phase,
)
from exasol.exaslpm.pkg_mgmt.context.context import Context
from exasol.exaslpm.pkg_mgmt.install_common import (
    CommandExecInfo,
    run_cmd,
)
from exasol.exaslpm.pkg_mgmt.search.package_collectors import collect_pip_packages
from exasol.exaslpm.pkg_mgmt.search.search_cache import SearchCache


def install_pip_packages(search_cache: SearchCache, phase: Phase, ctx: Context):

    packages_to_install = collect_pip_packages(search_cache.all_phases + [phase])
    python_binary_path = search_cache.python_binary_path

    if not phase.pip.packages:
        ctx.cmd_logger.warn("Got an empty list of pip packages")
    else:
        with ctx.temp_file_provider.create() as temp_file:
            with temp_file.open() as f:
                for package in packages_to_install:
                    print(f"{package.name}=={package.version}", file=f)

            install_pip_cmd = CommandExecInfo(
                cmd=[
                    str(python_binary_path),
                    "-m",
                    "pip",
                    "install",
                    "-r",
                    str(temp_file.path),
                ],
                err="Failed while installing pip packages",
            )
            if search_cache.pip.needs_break_system_packages:
                install_pip_cmd.cmd.append("--break-system-packages")
            run_cmd(install_pip_cmd, ctx)
