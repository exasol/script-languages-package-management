from test.integration.package_utils import ContainsPackages

import pytest

from exasol.exaslpm.model.serialization import to_yaml_str
from exasol.exaslpm.pkg_mgmt.install_packages import package_install


@pytest.fixture
def prepare_gpg_env(
    docker_container,
    apt_gpg,
    apt_r_with_ppa,
    local_package_path,
    docker_executor_context,
):
    apt_gpg_package_file_yaml = to_yaml_str(apt_gpg)

    local_package_path.write_text(apt_gpg_package_file_yaml)

    package_install(
        package_file=local_package_path,
        build_step_name="build_step_1",
        context=docker_executor_context,
    )


@pytest.fixture
def prepare_r_env(
    docker_container,
    prepare_gpg_env,
    apt_r_with_ppa,
    local_package_path,
    docker_executor_context,
):
    apt_r_package_file_yaml = to_yaml_str(apt_r_with_ppa)

    local_package_path.write_text(apt_r_package_file_yaml)

    package_install(
        package_file=local_package_path,
        build_step_name="build_step_2",
        context=docker_executor_context,
    )


def test_install_pip_packages(
    docker_container,
    packages_r,
    docker_executor_context,
    local_package_path,
    prepare_r_env,
):
    r_packages_file_yaml = to_yaml_str(packages_r)
    local_package_path.write_text(r_packages_file_yaml)
    r = packages_r.build_steps[0].phases[2].r
    expected_packages = r.packages

    pkgs_before_install = docker_container.list_r()
    assert pkgs_before_install != ContainsPackages(expected_packages)

    package_install(
        package_file=local_package_path,
        build_step_name="build_step_3",
        context=docker_executor_context,
    )

    pkgs_after_install = docker_container.list_r()
    assert pkgs_after_install == ContainsPackages(expected_packages)
