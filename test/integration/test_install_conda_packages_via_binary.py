from pathlib import Path
from test.integration.package_utils import ContainsCondaPackages

import pytest

from exasol.exaslpm.model.package_file_config import Micromamba
from exasol.exaslpm.model.serialization import to_yaml_str
from exasol.exaslpm.pkg_mgmt.constants import MICROMAMBA_PATH


@pytest.fixture
def prepare_micromamba_env(
    docker_container, micromamba_file_content, cli_helper
) -> Micromamba:
    micromamba_package_file_yaml = to_yaml_str(micromamba_file_content)

    conda_package_file = docker_container.make_and_upload_file(
        Path("/"), "micromamba_file_01", micromamba_package_file_yaml.encode("utf-8")
    )

    ret, out = docker_container.run_exaslpm(
        cli_helper.install.package_file(conda_package_file)
        .build_step("build_step_1")
        .args
    )
    assert ret == 0

    return (
        micromamba_file_content.find_build_step("build_step_1")
        .find_phase("phase_2")
        .tools.micromamba
    )


def test_install_conda_packages(
    docker_container, conda_packages_file_content, cli_helper, prepare_micromamba_env
):
    conda_packages_file_yaml = to_yaml_str(conda_packages_file_content)

    conda_package_file = docker_container.make_and_upload_file(
        Path("/"), "conda_file_01", conda_packages_file_yaml.encode("utf-8")
    )

    expected_packages = (
        conda_packages_file_content.build_steps[0].phases[4].conda.packages
    )

    pkgs_before_install = docker_container.list_conda_packages(
        MICROMAMBA_PATH, prepare_micromamba_env
    )
    assert pkgs_before_install != ContainsCondaPackages(expected_packages)

    ret, out = docker_container.run_exaslpm(
        cli_helper.install.package_file(conda_package_file)
        .build_step("build_step_2")
        .args
    )
    assert ret == 0

    pkgs_after_install = docker_container.list_conda_packages(
        MICROMAMBA_PATH, prepare_micromamba_env
    )
    assert pkgs_after_install == ContainsCondaPackages(expected_packages)



def test_conda_packages_install_error(
    docker_container, conda_packages_file_content, cli_helper, prepare_micromamba_env
):
    pkg = (
        conda_packages_file_content.find_build_step("build_step_2")
        .find_phase("phase_1")
        .conda.packages[0]
    )
    pkg.name = "unknowsoftware"
    pkg.version = "0.0.0"
    conda_package_file_content_yaml = to_yaml_str(conda_packages_file_content)
    conda_invalid_pkg_file = docker_container.make_and_upload_file(
        Path("/"), "conda_file_02", conda_package_file_content_yaml.encode("utf-8")
    )

    ret, out = docker_container.run_exaslpm(
        cli_helper.install.package_file(conda_invalid_pkg_file)
        .build_step("build_step_2")
        .args,
        False,
    )
    assert ret != 0
    assert (
        "unknowsoftware =0.0.0 * does not exist"
        in out
    )
