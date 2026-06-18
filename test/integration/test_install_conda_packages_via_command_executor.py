from test.integration.docker_test_environment.docker_test_container import (
    DockerTestContainer,
)
from test.integration.docker_test_environment.test_logger import LogCollector
from test.integration.package_utils import ContainsCondaPackages

import pytest

pytestmark = pytest.mark.via_command_executor

from exasol.exaslpm.model.package_file_config import (
    CondaPackage,
    CondaPackages,
    Micromamba,
)
from exasol.exaslpm.model.serialization import to_yaml_str
from exasol.exaslpm.pkg_mgmt.constants import MICROMAMBA_PATH
from exasol.exaslpm.pkg_mgmt.context.cmd_executor import CommandFailedException
from exasol.exaslpm.pkg_mgmt.install_packages import package_install


def assert_packages_installed(
    docker_container: DockerTestContainer, conda: CondaPackages
) -> None:
    expected_packages = conda.packages
    pkgs_in_container = docker_container.list_conda_packages(MICROMAMBA_PATH)
    assert pkgs_in_container == ContainsCondaPackages(expected_packages)


def assert_packages_not_installed(
    docker_container: DockerTestContainer, conda: CondaPackages
) -> None:
    expected_packages = conda.packages
    pkgs_in_container = docker_container.list_conda_packages(MICROMAMBA_PATH)
    assert pkgs_in_container != ContainsCondaPackages(expected_packages)


@pytest.fixture
def prepare_micromamba_env(
    docker_container,
    micromamba_file_content,
    local_package_path,
    docker_executor_context,
) -> Micromamba:
    micromamba_package_file_yaml = to_yaml_str(micromamba_file_content)
    local_package_path.write_text(micromamba_package_file_yaml)

    package_install(
        package_file=local_package_path,
        build_step_name="build_step_1",
        context=docker_executor_context,
    )

    return (
        micromamba_file_content.find_build_step("build_step_1")
        .find_phase("phase_2")
        .tools.micromamba
    )


@pytest.fixture
def prepare_python(
    docker_container,
    local_package_path,
    conda_python_package_content,
    prepare_micromamba_env,
    docker_executor_context,
) -> None:
    micromamba_package_file_yaml = to_yaml_str(conda_python_package_content)
    local_package_path.write_text(micromamba_package_file_yaml)

    package_install(
        package_file=local_package_path,
        build_step_name="build_step_2",
        context=docker_executor_context,
    )
    return prepare_micromamba_env


def test_install_conda_packages(
    docker_container,
    conda_packages_file_content,
    docker_executor_context,
    local_package_path,
    prepare_micromamba_env,
):
    conda_packages_file_yaml = to_yaml_str(conda_packages_file_content)
    local_package_path.write_text(conda_packages_file_yaml)

    expected_packages = conda_packages_file_content.build_steps[0].phases[4].conda
    assert expected_packages

    assert_packages_not_installed(docker_container, expected_packages)

    package_install(
        package_file=local_package_path,
        build_step_name="build_step_2",
        context=docker_executor_context,
    )

    assert_packages_installed(docker_container, expected_packages)

    bazel_version_cmd_exit_code, _ = docker_container.run_in_login_shell(
        ["bazel", "--help"]
    )
    assert bazel_version_cmd_exit_code == 0


def test_install_pip_packages_in_conda(
    docker_container,
    conda_pip_packages_file_content,
    docker_executor_context,
    local_package_path,
    prepare_python,
):
    pip_packages_file_yaml = to_yaml_str(conda_pip_packages_file_content)
    local_package_path.write_text(pip_packages_file_yaml)

    expected_pip_packages = (
        conda_pip_packages_file_content.build_steps[0].phases[0].pip.packages
    )
    assert expected_pip_packages
    expected_conda_packages = CondaPackages(
        packages=[
            CondaPackage(name=pip_pkg.name, version=pip_pkg.version)
            for pip_pkg in expected_pip_packages
        ]
    )
    assert_packages_not_installed(docker_container, expected_conda_packages)

    log_collector = LogCollector()
    docker_executor_context.cmd_logger.error_callback = log_collector.log

    package_install(
        package_file=local_package_path,
        build_step_name="build_step_3",
        context=docker_executor_context,
    )

    assert_packages_installed(docker_container, expected_conda_packages)


def test_install_conda_packages_prints_requirements_file_if_exception(
    docker_container,
    incorrect_conda_packages_file_content,
    docker_executor_context,
    local_package_path,
    prepare_micromamba_env,
    python_version,
):
    conda_packages_file_yaml = to_yaml_str(incorrect_conda_packages_file_content)
    local_package_path.write_text(conda_packages_file_yaml)
    log_collector = LogCollector()
    docker_executor_context.cmd_logger.error_callback = log_collector.log

    with pytest.raises(CommandFailedException):
        package_install(
            package_file=local_package_path,
            build_step_name="build_step_2",
            context=docker_executor_context,
        )
    assert "invalid_conda_pkg=2.3.*" in log_collector.result
