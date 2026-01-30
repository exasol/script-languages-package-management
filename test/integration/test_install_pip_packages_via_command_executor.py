from copy import deepcopy
from test.integration.package_fixtures import (  # noqa: F401, fixtures to be used
    pip_package_file_content,
    pip_packages_file_content,
    pip_packages_file_content_which_needs_pkg_config,
)
from test.integration.package_utils import ContainsPipPackages

import pytest

from exasol.exaslpm.model.serialization import to_yaml_str
from exasol.exaslpm.pkg_mgmt.context.cmd_executor import CommandFailedException
from exasol.exaslpm.pkg_mgmt.install_packages import package_install


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

    expected_packages = pip_packages_file_content.build_steps[0].phases[0].pip.packages

    pkgs_before_install = docker_container.list_pip()
    assert pkgs_before_install != ContainsPipPackages(expected_packages)

    package_install(
        package_file=local_package_path,
        build_step_name="build_step_2",
        context=docker_executor_context,
    )

    pkgs_after_install = docker_container.list_pip()
    assert pkgs_after_install == ContainsPipPackages(expected_packages)


@pytest.mark.parametrize(
    "use_install_build_tools_ephemerally",
    [True, False],
)
def test_install_pip_packages_with_install_build_tools_ephemerally(
    docker_container,
    pip_packages_file_content_which_needs_pkg_config,
    docker_executor_context,
    local_package_path,
    prepare_pip_env,
    use_install_build_tools_ephemerally,
):
    modified_pip_packages_file_content = deepcopy(
        pip_packages_file_content_which_needs_pkg_config
    )
    pip = (
        modified_pip_packages_file_content.find_build_step("build_step_2")
        .find_phase("phase_2")
        .pip
    )
    pip.install_build_tools_ephemerally = use_install_build_tools_ephemerally

    pip_packages_file_yaml = to_yaml_str(modified_pip_packages_file_content)
    local_package_path.write_text(pip_packages_file_yaml)

    expected_packages = pip.packages

    pkgs_before_install = docker_container.list_pip()
    assert pkgs_before_install != ContainsPipPackages(expected_packages)

    if use_install_build_tools_ephemerally:
        package_install(
            package_file=local_package_path,
            build_step_name="build_step_2",
            context=docker_executor_context,
        )

        pkgs_after_install = docker_container.list_pip()
        assert pkgs_after_install == ContainsPipPackages(expected_packages)
    else:
        with pytest.raises(CommandFailedException):
            package_install(
                package_file=local_package_path,
                build_step_name="build_step_2",
                context=docker_executor_context,
            )
