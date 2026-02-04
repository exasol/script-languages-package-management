from test.integration.docker_test_environment.docker_test_container import (
    DockerTestContainer,
)
from test.integration.package_fixtures import (  # noqa: F401, fixtures to be used
    conda_packages_file_content,
    micromamba_file_content,
)
from test.integration.package_utils import ContainsCondaPackages

import pytest

from exasol.exaslpm.model.package_file_config import (
    CondaPackages,
    Micromamba,
)
from exasol.exaslpm.model.serialization import to_yaml_str
from exasol.exaslpm.pkg_mgmt.constants import MICROMAMBA_PATH
from exasol.exaslpm.pkg_mgmt.install_packages import package_install


def assert_packages_installed(
    docker_container: DockerTestContainer, conda: CondaPackages, micromamba: Micromamba
) -> None:
    expected_packages = conda.packages
    pkgs_in_container = docker_container.list_conda_packages(
        MICROMAMBA_PATH, micromamba
    )
    assert pkgs_in_container == ContainsCondaPackages(expected_packages)


def assert_packages_not_installed(
    docker_container: DockerTestContainer, conda: CondaPackages, micromamba: Micromamba
) -> None:
    expected_packages = conda.packages
    pkgs_in_container = docker_container.list_conda_packages(
        MICROMAMBA_PATH, micromamba
    )
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

    assert_packages_not_installed(
        docker_container, expected_packages, prepare_micromamba_env
    )

    package_install(
        package_file=local_package_path,
        build_step_name="build_step_2",
        context=docker_executor_context,
    )

    assert_packages_installed(
        docker_container, expected_packages, prepare_micromamba_env
    )
