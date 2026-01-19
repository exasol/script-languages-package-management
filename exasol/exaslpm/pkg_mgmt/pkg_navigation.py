from exasol.exaslpm.model.package_file_config import (
    AnyPackageList,
    BuildStep,
    PackageFile,
    PackageType,
    Phase,
)


def find_package(
    packages: AnyPackageList,
    pkg_name: str,
) -> None | PackageType:
    matched_pkgs = [package for package in packages if pkg_name == package.name]
    if not matched_pkgs:
        return None
    return matched_pkgs[0]


def find_phase(build_step: BuildStep, phase_name: str) -> Phase:
    found_phases = [phase for phase in build_step.phases if phase.name == phase_name]
    if len(found_phases) == 0:
        raise ValueError(f"Phase '{phase_name}' not found")
    if len(found_phases) > 1:
        raise ValueError(f"More than one phases found for phase name '{phase_name}'")
    return found_phases[0]


def find_build_step(pkg_file: PackageFile, build_step_name: str) -> BuildStep:
    found_build_steps = [
        bs for bs in pkg_file.build_steps if bs.name == build_step_name
    ]
    if len(found_build_steps) == 0:
        raise ValueError(f"Build step '{build_step_name}' not found")
    if len(found_build_steps) > 1:
        raise ValueError(
            f"More than on build step for build step name '{build_step_name}'"
        )
    return found_build_steps[0]
