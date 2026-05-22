from exasol.exaslpm.model.installed_packages_config import InstalledPackages
from exasol.exaslpm.model.package_file_config import (
    BuildStep,
    Phase,
)
from exasol.exaslpm.pkg_mgmt.binary_types import BinaryType
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
from exasol.exaslpm.pkg_mgmt.get_installed_r_packages import (
    get_installed_r_packages,
)
from exasol.exaslpm.pkg_mgmt.search.find_in_build_steps import find_binary


def get_installed_packages(
    used_package_types: dict[str, bool], context: Context, phases: list[Phase]
) -> InstalledPackages:
    installed_packages: InstalledPackages = InstalledPackages()
    for key, value in used_package_types.items():
        if not value:
            continue
        match key:
            case "apt":
                installed_packages.apt = get_installed_apt_packages(context)
            case "conda":
                micromamba_path = find_binary(BinaryType.MICROMAMBA, phases)
                installed_packages.conda = get_installed_conda_packages(
                    context, micromamba_path
                )
            case "pip":
                python_path = find_binary(BinaryType.PYTHON, phases)
                installed_packages.pip = get_installed_pip_packages(
                    context, python_path
                )
            case "r":
                r_path = find_binary(BinaryType.R, phases)
                installed_packages.r = get_installed_r_packages(context, r_path)
    return installed_packages


def get_all_phases(context: Context) -> list[Phase]:
    build_steps: list[BuildStep] = (
        context.history_file_manager.get_all_previous_build_steps()
    )
    # collect all phases from all build steps known to the HistoryFileManager
    return [phase for build_step in build_steps for phase in build_step.phases]


def list_all_installed_packages(context: Context) -> InstalledPackages:
    context.history_file_manager.check_consistency()
    phases = get_all_phases(context)

    used_package_types: dict[str, bool] = get_used_package_types(phases)
    installed_packages: InstalledPackages = get_installed_packages(
        used_package_types, context, phases
    )
    return installed_packages


def get_used_package_types(phases: list[Phase]) -> dict[str, bool]:
    used_package_types: dict[str, bool] = {
        "apt": False,
        "conda": False,
        "pip": False,
        "r": False,
    }

    for phase in phases:
        for package_type in used_package_types.keys():
            if getattr(phase, package_type):
                used_package_types[package_type] = True

    return used_package_types
