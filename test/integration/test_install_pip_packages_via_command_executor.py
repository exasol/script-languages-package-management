from copy import deepcopy
from pathlib import Path
from test.integration.docker_test_environment.docker_test_container import (
    DockerTestContainer,
)
from test.integration.package_fixtures import (  # noqa: F401, fixtures to be used
    pip_package_file_content,
    pip_packages_file_content,
    pip_packages_file_content_which_needs_pkg_config,
)
from test.integration.package_utils import ContainsPipPackages

import pytest

from exasol.exaslpm.model.package_file_config import (
    PackageFile,
    PipPackages,
)
from exasol.exaslpm.model.serialization import to_yaml_str
from exasol.exaslpm.pkg_mgmt.context.cmd_executor import CommandFailedException
from exasol.exaslpm.pkg_mgmt.install_packages import package_install


def assert_packages_installed(
    docker_container: DockerTestContainer, pip: PipPackages
) -> None:
    expected_packages = pip.packages
    pkgs_in_container = docker_container.list_pip()
    assert pkgs_in_container == ContainsPipPackages(expected_packages)


def assert_packages_not_installed(
    docker_container: DockerTestContainer, pip: PipPackages
) -> None:
    expected_packages = pip.packages
    pkgs_in_container = docker_container.list_pip()
    assert pkgs_in_container != ContainsPipPackages(expected_packages)


@pytest.fixture
def prepare_pip_env(
    docker_container,
    pip_package_file_content,
    local_package_path,
    docker_executor_context,
):
    apt_package_file_yaml = to_yaml_str(pip_package_file_content)
    local_package_path.write_text(apt_package_file_yaml)

    package_install(
        package_file=local_package_path,
        build_step_name="build_step_1",
        context=docker_executor_context,
    )


def test_install_pip_packages(
    docker_container,
    pip_packages_file_content,
    docker_executor_context,
    local_package_path,
    prepare_pip_env,
):
    pip_packages_file_yaml = to_yaml_str(pip_packages_file_content)
    local_package_path.write_text(pip_packages_file_yaml)
    pip = pip_packages_file_content.build_steps[0].phases[0].pip

    assert_packages_not_installed(docker_container, pip)

    package_install(
        package_file=local_package_path,
        build_step_name="build_step_2",
        context=docker_executor_context,
    )

    assert_packages_installed(docker_container, pip)


def prepare_package_file_with_packages_which_needs_pkg_config(
    package_file: PackageFile,
    use_install_build_tools_ephemerally: bool,
    local_package_path: Path,
):
    modified_pip_packages_file_content = deepcopy(package_file)
    pip = (
        modified_pip_packages_file_content.find_build_step("build_step_2")
        .find_phase("phase_2")
        .pip
    )
    pip.install_build_tools_ephemerally = use_install_build_tools_ephemerally

    pip_packages_file_yaml = to_yaml_str(modified_pip_packages_file_content)
    local_package_path.write_text(pip_packages_file_yaml)


def test_install_pip_packages_with_install_build_tools_ephemerally(
    docker_container,
    pip_packages_file_content_which_needs_pkg_config,
    docker_executor_context,
    local_package_path,
    prepare_pip_env,
):
    prepare_package_file_with_packages_which_needs_pkg_config(
        package_file=pip_packages_file_content_which_needs_pkg_config,
        use_install_build_tools_ephemerally=True,
        local_package_path=local_package_path,
    )
    pip = pip_packages_file_content_which_needs_pkg_config.build_steps[0].phases[1].pip

    assert_packages_not_installed(docker_container, pip)

    package_install(
        package_file=local_package_path,
        build_step_name="build_step_2",
        context=docker_executor_context,
    )

    assert_packages_installed(docker_container, pip)


def test_install_pip_packages_without_install_build_tools_ephemerally_raises(
    docker_container,
    pip_packages_file_content_which_needs_pkg_config,
    docker_executor_context,
    local_package_path,
    prepare_pip_env,
):
    prepare_package_file_with_packages_which_needs_pkg_config(
        package_file=pip_packages_file_content_which_needs_pkg_config,
        use_install_build_tools_ephemerally=False,
        local_package_path=local_package_path,
    )
    pip = pip_packages_file_content_which_needs_pkg_config.build_steps[0].phases[1].pip
    assert_packages_not_installed(docker_container, pip)

    with pytest.raises(CommandFailedException):
        package_install(
            package_file=local_package_path,
            build_step_name="build_step_2",
            context=docker_executor_context,
        )
