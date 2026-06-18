from pathlib import Path
from test.integration.package_utils import ContainsCondaPackages

import pytest

pytestmark = pytest.mark.via_binary

from exasol.exaslpm.model.package_file_config import (
    CondaPackage,
    Micromamba,
)
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


@pytest.fixture
def prepare_python(
    docker_container, conda_python_package_content, prepare_micromamba_env, cli_helper
) -> None:
    python_conda_package_file_yaml = to_yaml_str(conda_python_package_content)

    conda_package_file = docker_container.make_and_upload_file(
        Path("/"),
        "python_conda_package_file_01",
        python_conda_package_file_yaml.encode("utf-8"),
    )

    ret, out = docker_container.run_exaslpm(
        cli_helper.install.package_file(conda_package_file)
        .build_step("build_step_2")
        .args
    )
    assert ret == 0
    return prepare_micromamba_env


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

    pkgs_before_install = docker_container.list_conda_packages(MICROMAMBA_PATH)
    assert pkgs_before_install != ContainsCondaPackages(expected_packages)

    ret, out = docker_container.run_exaslpm(
        cli_helper.install.package_file(conda_package_file)
        .build_step("build_step_2")
        .args
    )
    assert ret == 0

    pkgs_after_install = docker_container.list_conda_packages(MICROMAMBA_PATH)
    assert pkgs_after_install == ContainsCondaPackages(expected_packages)

    bazel_version_cmd_exit_code, _ = docker_container.run_in_login_shell(
        ["bazel", "--help"]
    )
    assert bazel_version_cmd_exit_code == 0


def test_install_pip_packages_in_conda(
    docker_container,
    conda_pip_packages_file_content,
    python_version,
    cli_helper,
    prepare_python,
):
    pip_packages_file_yaml = to_yaml_str(conda_pip_packages_file_content)

    pip_package_file = docker_container.make_and_upload_file(
        Path("/"), "pip_file_01", pip_packages_file_yaml.encode("utf-8")
    )

    expected_pip_packages = (
        conda_pip_packages_file_content.build_steps[0].phases[0].pip.packages
    )
    expected_pip_packages_as_conda_packages = [
        CondaPackage(name=pip_pkg.name, version=pip_pkg.version)
        for pip_pkg in expected_pip_packages
    ]

    # `micromamba list` also shows installed pip packages
    conda_pkgs_before_install = docker_container.list_conda_packages(MICROMAMBA_PATH)
    assert conda_pkgs_before_install != ContainsCondaPackages(
        expected_pip_packages_as_conda_packages
    )

    ret, out = docker_container.run_exaslpm(
        cli_helper.install.package_file(pip_package_file)
        .build_step("build_step_3")
        .args
    )
    assert ret == 0

    conda_pkgs_after_install = docker_container.list_conda_packages(MICROMAMBA_PATH)
    assert conda_pkgs_after_install == ContainsCondaPackages(
        expected_pip_packages_as_conda_packages
    )


def test_conda_packages_install_error(
    docker_container, conda_packages_file_content, cli_helper, prepare_micromamba_env
):
    pkg = (
        conda_packages_file_content.find_build_step("build_step_2")
        .find_phase("phase_1")
        .conda.packages[0]
    )
    pkg.name = "unknownsoftware"
    pkg.version = "=0.0.0"
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
    assert "unknownsoftware =0.0.0 * does not exist" in out


def test_install_cuda_conda_packages(
    docker_container, cuda_packages_file_content, cli_helper, prepare_micromamba_env
):
    cuda_packages_file_yaml = to_yaml_str(cuda_packages_file_content)

    cuda_package_file = docker_container.make_and_upload_file(
        Path("/"), "cuda_file_01", cuda_packages_file_yaml.encode("utf-8")
    )

    expected_packages = (
        cuda_packages_file_content.build_steps[0].phases[2].conda.packages
    )

    pkgs_before_install = docker_container.list_conda_packages(MICROMAMBA_PATH)
    assert pkgs_before_install != ContainsCondaPackages(expected_packages)

    ret, out = docker_container.run_exaslpm(
        cli_helper.install.package_file(cuda_package_file)
        .build_step("build_step_2")
        .args
    )
    assert ret == 0

    pkgs_after_install = docker_container.list_conda_packages(MICROMAMBA_PATH)
    assert pkgs_after_install == ContainsCondaPackages(expected_packages)
