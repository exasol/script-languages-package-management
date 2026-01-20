from typing import (
    TYPE_CHECKING,
    Literal,
    Optional,
    overload,
)

if TYPE_CHECKING:
    from exasol.exaslpm.model.any_package import (
        PackageType,
    )
    from exasol.exaslpm.model.package_file_config import (
        BuildStep,
        PackageFile,
        Phase,
    )


@overload
def find_package(
    packages: list["PackageType"],
    pkg_name: str,
    raise_if_not_found: Literal[True] = True,
) -> "PackageType": ...


@overload
def find_package(
    packages: list["PackageType"], pkg_name: str, raise_if_not_found: Literal[False]
) -> Optional["PackageType"]: ...


def find_package(
    packages: list["PackageType"],
    pkg_name: str,
    raise_if_not_found: bool = True,
) -> Optional["PackageType"]:
    matched_pkgs = [package for package in packages if pkg_name == package.name]
    if len(matched_pkgs) > 1:
        raise ValueError(f"More than one package found for package name '{pkg_name}'")
    if not matched_pkgs:
        if raise_if_not_found:
            raise ValueError(f"Package '{pkg_name}' not found")
        else:
            return None
    return matched_pkgs[0]


@overload
def find_phase(
    build_step: "BuildStep", phase_name: str, raise_if_not_found: Literal[True] = True
) -> "Phase": ...


@overload
def find_phase(
    build_step: "BuildStep", phase_name: str, raise_if_not_found: Literal[False]
) -> Optional["Phase"]: ...


def find_phase(
    build_step: "BuildStep", phase_name: str, raise_if_not_found: bool = True
) -> Optional["Phase"]:
    found_phases = [phase for phase in build_step.phases if phase.name == phase_name]
    if len(found_phases) == 0:
        if raise_if_not_found:
            raise ValueError(f"Phase '{phase_name}' not found")
        else:
            return None
    if len(found_phases) > 1:
        raise ValueError(f"More than one phases found for phase name '{phase_name}'")
    return found_phases[0]


@overload
def find_build_step(
    pkg_file: "PackageFile",
    build_step_name: str,
    raise_if_not_found: Literal[True] = True,
) -> "BuildStep": ...


@overload
def find_build_step(
    pkg_file: "PackageFile", build_step_name: str, raise_if_not_found: Literal[False]
) -> Optional["BuildStep"]: ...


def find_build_step(
    pkg_file: "PackageFile",
    build_step_name: str,
    raise_if_not_found: bool = True,
) -> Optional["BuildStep"]:
    found_build_steps = [
        bs for bs in pkg_file.build_steps if bs.name == build_step_name
    ]
    if len(found_build_steps) == 0:
        if raise_if_not_found:
            raise ValueError(f"Build step '{build_step_name}' not found")
        else:
            return None
    if len(found_build_steps) > 1:
        raise ValueError(
            f"More than on build step for build step name '{build_step_name}'"
        )
    return found_build_steps[0]
