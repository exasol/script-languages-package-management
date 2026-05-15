from exasol.exaslpm.model.installed_packages_config import InstalledPackages
from exasol.exaslpm.model.package_file_config import BuildStep
from exasol.exaslpm.model.serialization import to_yaml_str
from exasol.exaslpm.pkg_mgmt.context.context import Context
from exasol.exaslpm.pkg_mgmt.get_installed_apt_packages import (
    get_installed_apt_packages,
)
from exasol.exaslpm.pkg_mgmt.get_installed_conda_packages import (
    get_installed_conda_packages,
)
from exasol.exaslpm.pkg_mgmt.get_installed_pip_packages import (
    get_installed_pip_packages,
)
from exasol.exaslpm.pkg_mgmt.get_installed_rscript_packages import (
    get_installed_r_packages,
)


def get_installed_packages(
    used_package_types: dict[str, bool], context: Context
) -> InstalledPackages:
    installed_packages: InstalledPackages = InstalledPackages()
    for key, value in used_package_types.items():
        if not value:
            continue
        match key:
            case "apt":
                installed_packages.apt = get_installed_apt_packages(context)
            case "conda":
                installed_packages.conda = get_installed_conda_packages(context)
            case "pip":
                installed_packages.pip = get_installed_pip_packages(context)
            case "r":
                installed_packages.r = get_installed_r_packages(context)
    return installed_packages


def list_all_installed_packages(context: Context) -> str:
    context.history_file_manager.check_consistency()
    used_package_types: dict[str, bool] = get_used_package_types(context)
    installed_packages: InstalledPackages = get_installed_packages(
        used_package_types, context
    )
    return to_yaml_str(installed_packages)


def get_used_package_types(context: Context) -> dict[str, bool]:
    used_package_types: dict[str, bool] = {
        "apt": False,
        "conda": False,
        "pip": False,
        "r": False,
    }
    build_steps: list[BuildStep] = (
        context.history_file_manager.get_all_previous_build_steps()
    )
    # iterate over all build steps known to the HistoryFileManager
    for build_step in build_steps:
        for phase in build_step.phases:
            for package_type in used_package_types.keys():
                if getattr(phase, package_type):
                    used_package_types[package_type] = True
                    # all package types needed, no need to look further
                    if all(used_package_types.values()):
                        return used_package_types
    return used_package_types
