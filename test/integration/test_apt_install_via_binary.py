from inspect import cleandoc
from json import JSONDecodeError
from pathlib import Path
from typing import Any

import pytest
import yaml

from exasol.exaslpm.model.package_file_config import (
    AptPackages,
    BuildStep,
    Package,
    PackageFile,
    Phase,
)


@pytest.fixture
def apt_package_file_content() -> PackageFile:
    return PackageFile(
        build_steps={
            "build_step_1": BuildStep(
                phases={
                    "phase_1": Phase(
                        apt=AptPackages(
                            packages=[
                                Package(name="wget", version="1.21.4-1ubuntu4.1"),
                                Package(name="curl", version="8.5.0-2ubuntu10.6"),
                            ]
                        )
                    )
                }
            )
        }
    )


@pytest.fixture
def apt_invalid_package_file() -> PackageFile:
    return PackageFile(
        build_steps={
            "build_step_1": BuildStep(
                phases={
                    "phase_1": Phase(
                        apt=AptPackages(
                            packages=[
                                Package(
                                    name="unknowsoftware", version="1.21.4-1ubuntu4.1"
                                ),
                            ]
                        )
                    )
                }
            )
        }
    )


class ContainsPackages:
    """
    Matcher to check if a list of installed packages contains
    all expected packages (matching name and version).
    """

    def __init__(self, expected_packages: list[Package]):
        self.expected_packages = expected_packages

    @staticmethod
    def _compare_package(expected: Package, installed: Package) -> bool:
        return expected.name == installed.name and expected.version == installed.version

    def __eq__(self, installed_packages: Any) -> bool:
        if not isinstance(installed_packages, list):
            return False

        # Check that every expected package exists in the installed list
        return all(
            any(self._compare_package(exp, inst) for inst in installed_packages)
            for exp in self.expected_packages
        )

    def __repr__(self):
        # This is what shows up in the assertion failure message
        return f"{self.expected_packages}"


def test_apt_install(docker_container, apt_package_file_content, cli_helper):
    apt_package_file_yaml = yaml.dump(apt_package_file_content.model_dump())

    apt_package_file = docker_container.make_and_upload_file(
        Path("/"), "apt_file_01", apt_package_file_yaml
    )

    expected_packages = (
        apt_package_file_content.build_steps["build_step_1"]
        .phases["phase_1"]
        .apt.packages
    )

    pkgs_before_install = docker_container.list_apt()
    assert pkgs_before_install != ContainsPackages(expected_packages)

    ret, out = docker_container.run_exaslpm(
        cli_helper.install.package_file(apt_package_file)
        .phase("phase_1")
        .build_step("build_step_1")
        .args
    )
    assert ret == 0

    pkgs_after_install = docker_container.list_apt()
    assert pkgs_after_install == ContainsPackages(expected_packages)


def test_apt_install_error(docker_container, apt_invalid_package_file, cli_helper):
    apt_invalid_package_file_yaml = yaml.dump(apt_invalid_package_file.model_dump())
    apt_invalid_pkg_file = docker_container.make_and_upload_file(
        Path("/"), "apt_file_02", apt_invalid_package_file_yaml
    )

    ret, out = docker_container.run_exaslpm(
        cli_helper.install.package_file(apt_invalid_pkg_file)
        .phase("phase_1")
        .build_step("build_step_1")
        .args,
        False,
    )
    assert ret != 0
    assert "Unable to locate package unknowsoftware" in out
