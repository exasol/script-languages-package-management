from test.integration.docker_test_environment.test_logger import (
    LogCollector,
    StringMatchCounter,
)
from test.integration.package_utils import ContainsPackages

import pytest

from exasol.exaslpm.model.serialization import to_yaml_str
from exasol.exaslpm.pkg_mgmt.install_packages import package_install


@pytest.fixture
def prepare_gpg(docker_container, apt_gpg, local_package_path, docker_executor_context):
    gpg_package_file_yaml = to_yaml_str(apt_gpg)

    local_package_path.write_text(gpg_package_file_yaml)

    package_install(
        package_file=local_package_path,
        build_step_name="build_step_1",
        context=docker_executor_context,
    )


def test_install_trivy(
    docker_container,
    apt_trivy_with_ppa,
    docker_executor_context,
    prepare_gpg,
    local_package_path,
):
    ppa_packages_file_yaml = to_yaml_str(apt_trivy_with_ppa)
    local_package_path.write_text(ppa_packages_file_yaml)

    expected_packages = apt_trivy_with_ppa.build_steps[0].phases[0].apt.packages

    pkgs_before_install = docker_container.list_apt()
    assert pkgs_before_install != ContainsPackages(expected_packages)

    return_code_counter = StringMatchCounter("Return Code: 0")
    docker_executor_context.cmd_logger.info_callback = return_code_counter.log

    package_install(
        package_file=local_package_path,
        build_step_name="build_step_2",
        context=docker_executor_context,
    )

    pkgs_before_install = docker_container.list_apt()
    assert pkgs_before_install == ContainsPackages(expected_packages)

    pkgs_after_install = docker_container.list_apt()
    assert pkgs_after_install == ContainsPackages(expected_packages)
    ret, out = docker_container.run(["trivy", "--help"])

    assert ret == 0, out


def test_install_r(
    docker_container,
    apt_r_with_ppa,
    docker_executor_context,
    prepare_gpg,
    local_package_path,
):
    ppa_packages_file_yaml = to_yaml_str(apt_r_with_ppa)
    local_package_path.write_text(ppa_packages_file_yaml)

    expected_packages = apt_r_with_ppa.build_steps[0].phases[0].apt.packages

    pkgs_before_install = docker_container.list_apt()
    assert pkgs_before_install != ContainsPackages(expected_packages)

    return_code_counter = StringMatchCounter("Return Code: 0")
    docker_executor_context.cmd_logger.info_callback = return_code_counter.log

    log_collector = LogCollector()
    docker_executor_context.cmd_logger.err_callback = log_collector.log

    package_install(
        package_file=local_package_path,
        build_step_name="build_step_2",
        context=docker_executor_context,
    )

    pkgs_before_install = docker_container.list_apt()
    assert pkgs_before_install == ContainsPackages(expected_packages)

    pkgs_after_install = docker_container.list_apt()
    assert pkgs_after_install == ContainsPackages(expected_packages)
    ret, out = docker_container.run(["R", "--help"])

    assert ret == 0, out
