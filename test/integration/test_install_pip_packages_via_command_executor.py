from pathlib import Path

import pytest

from exasol.exaslpm.pkg_mgmt.install_packages import package_install
from test.integration.package_fixtures import (  # noqa: F401, fixtures to be used
    pip_packages_file_content,pip_package_file_content
)
from test.integration.package_utils import ContainsPackages

from exasol.exaslpm.model.serialization import to_yaml_str

@pytest.fixture
def prepare_pip_env(docker_container,
                    pip_package_file_content,
                    local_package_path,
                    docker_executor_context):
    apt_package_file_yaml = to_yaml_str(pip_package_file_content)
    local_package_path.write_text(apt_package_file_yaml)

    package_install(
        package_file=local_package_path,
        build_step_name="build_step_1",
        context=docker_executor_context,
    )



def test_install_pip_packages(docker_container, pip_packages_file_content, docker_executor_context, local_package_path, prepare_pip_env):
    pip_packages_file_yaml = to_yaml_str(pip_packages_file_content)
    local_package_path.write_text(pip_packages_file_yaml)

    expected_packages = pip_packages_file_content.build_steps[0].phases[0].pip.packages

    pkgs_before_install = docker_container.list_pip()
    assert pkgs_before_install != ContainsPackages(expected_packages)

    package_install(
        package_file=local_package_path,
        build_step_name="build_step_2",
        context=docker_executor_context,
    )

    pkgs_after_install = docker_container.list_pip()
    assert pkgs_after_install == ContainsPackages(expected_packages)
