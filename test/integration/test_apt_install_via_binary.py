from pathlib import Path
from typing import Any

import pytest
import yaml

from exasol.exaslpm.model.package_file_config import (
    AptPackage,
    AptPackages,
    BuildStep,
    PackageFile,
    Phase,
)


@pytest.fixture
def apt_package_file_content() -> PackageFile:
    return PackageFile(
        build_steps=[
            BuildStep(
                name="build_step_1",
                phases=[
                    Phase(
                        name="phase_1",
                        apt=AptPackages(
                            packages=[
                                AptPackage(name="wget", version="1.21.4-1ubuntu4.1"),
                                AptPackage(name="curl", version="8.5.0-2ubuntu10.6"),
                            ]
                        ),
                    )
                ],
            ),
            BuildStep(
                name="build_step_2",
                phases=[
                    Phase(
                        name="phase_1",
                        apt=AptPackages(
                            packages=[
                                AptPackage(name="coreutils", version="9.4-3ubuntu6.1"),
                            ]
                        ),
                    )
                ],
            ),
        ]
    )


@pytest.fixture
def apt_invalid_package_file() -> PackageFile:
    return PackageFile(
        build_steps=[
            BuildStep(
                name="build_step_1",
                phases=[
                    Phase(
                        name="phase_1",
                        apt=AptPackages(
                            packages=[
                                AptPackage(name="unknowsoftware", version="1.2.3"),
                            ]
                        ),
                    )
                ],
            )
        ]
    )


class ContainsPackages:
    """
    Matcher to check if a list of installed packages contains
    all expected packages (matching name and version).
    """

    def __init__(self, expected_packages: list[AptPackage]):
        self.expected_packages = expected_packages

    @staticmethod
    def _compare_package(expected: AptPackage, installed: AptPackage) -> bool:
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

    expected_packages = apt_package_file_content.build_steps[0].phases[0].apt.packages

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


def test_history(docker_container, apt_package_file_content, cli_helper):
    apt_package_file_yaml = yaml.dump(apt_package_file_content.model_dump())

    apt_package_file = docker_container.make_and_upload_file(
        Path("/"), "apt_file_01", apt_package_file_yaml
    )

    ret, out = docker_container.run_exaslpm(
        cli_helper.install.package_file(apt_package_file)
        .phase("phase_1")
        .build_step("build_step_1")
        .args
    )
    assert ret == 0

    ret, out = docker_container.run_exaslpm(
        cli_helper.install.package_file(apt_package_file)
        .phase("phase_1")
        .build_step("build_step_2")
        .args
    )
    assert ret == 0

    _, out = docker_container.run(["ls", "/build_info/packages/history"])
    history_files = [line.strip() for line in out.splitlines()]
    assert history_files == ["build_step_1", "build_step_2"]

    _, out = docker_container.run(["cat", "/build_info/packages/history/build_step_1"])
    history_one_model = PackageFile.model_validate(yaml.safe_load(out))
    assert len(history_one_model.build_steps) == 1
    assert history_one_model.build_steps[0] == apt_package_file_content.build_steps[0]

    _, out = docker_container.run(["cat", "/build_info/packages/history/build_step_2"])
    history_two_model = PackageFile.model_validate(yaml.safe_load(out))
    assert len(history_two_model.build_steps) == 1
    assert history_two_model.build_steps[0] == apt_package_file_content.build_steps[1]
