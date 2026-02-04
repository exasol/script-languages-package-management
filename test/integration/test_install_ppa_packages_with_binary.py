from pathlib import Path
from test.integration.package_fixtures import (  # noqa: F401, fixtures to be used
    apt_package_file_content,
)
from test.integration.package_utils import ContainsPackages

import pytest

from exasol.exaslpm.model.serialization import to_yaml_str


@pytest.fixture
def prepare_gpg(docker_container, apt_gpg, cli_helper):
    gpg_package_file_yaml = to_yaml_str(apt_gpg)

    gpg_package_file = docker_container.make_and_upload_file(
        Path("/"), "gpg_file_01", gpg_package_file_yaml.encode("utf-8")
    )

    ret, out = docker_container.run_exaslpm(
        cli_helper.install.package_file(gpg_package_file)
        .build_step("build_step_1")
        .args
    )
    assert ret == 0


def test_install_trivy(docker_container, prepare_gpg, apt_trivy_with_ppa, cli_helper):
    apt_package_file_yaml = to_yaml_str(apt_trivy_with_ppa)

    apt_package_file = docker_container.make_and_upload_file(
        Path("/"), "apt_file_01", apt_package_file_yaml.encode("utf-8")
    )

    expected_packages = apt_trivy_with_ppa.build_steps[0].phases[0].apt.packages

    pkgs_before_install = docker_container.list_apt()
    assert pkgs_before_install != ContainsPackages(expected_packages)

    ret, out = docker_container.run_exaslpm(
        cli_helper.install.package_file(apt_package_file)
        .build_step("build_step_2")
        .args
    )
    assert ret == 0, out

    pkgs_after_install = docker_container.list_apt()
    assert pkgs_after_install == ContainsPackages(expected_packages)
    ret, out = docker_container.run(["trivy", "--help"])

    assert ret == 0, out


def test_install_r(docker_container, prepare_gpg, apt_r_with_ppa, cli_helper):
    apt_package_file_yaml = to_yaml_str(apt_r_with_ppa)

    apt_package_file = docker_container.make_and_upload_file(
        Path("/"), "apt_file_01", apt_package_file_yaml.encode("utf-8")
    )

    expected_packages = apt_r_with_ppa.build_steps[0].phases[0].apt.packages

    pkgs_before_install = docker_container.list_apt()
    assert pkgs_before_install != ContainsPackages(expected_packages)

    ret, out = docker_container.run_exaslpm(
        cli_helper.install.package_file(apt_package_file)
        .build_step("build_step_2")
        .args
    )
    assert ret == 0, out

    pkgs_after_install = docker_container.list_apt()
    assert pkgs_after_install == ContainsPackages(expected_packages)
    ret, out = docker_container.run(["R", "--help"])

    assert ret == 0, out
