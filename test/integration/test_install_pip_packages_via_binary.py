from pathlib import Path

import pytest

from test.integration.package_fixtures import (  # noqa: F401, fixtures to be used
    pip_packages_file_content,pip_package_file_content
)
from test.integration.package_utils import ContainsPackages

from exasol.exaslpm.model.serialization import to_yaml_str

@pytest.fixture
def prepare_pip_env(docker_container, pip_package_file_content, cli_helper):
    pip_package_file_yaml = to_yaml_str(pip_package_file_content)

    pip_package_file = docker_container.make_and_upload_file(
        Path("/"), "pip_file_01", pip_package_file_yaml
    )

    ret, out = docker_container.run_exaslpm(
        cli_helper.install.package_file(pip_package_file)
        .build_step("build_step_1")
        .args
    )
    assert ret == 0



def test_install_pip_packages(docker_container, pip_packages_file_content, cli_helper, prepare_pip_env):
    pip_packages_file_yaml = to_yaml_str(pip_packages_file_content)

    pip_package_file = docker_container.make_and_upload_file(
        Path("/"), "pip_file_02", pip_packages_file_yaml
    )

    expected_packages = pip_packages_file_content.build_steps[0].phases[0].pip.packages

    pkgs_before_install = docker_container.list_pip()
    assert pkgs_before_install != ContainsPackages(expected_packages)

    ret, out = docker_container.run_exaslpm(
        cli_helper.install.package_file(pip_package_file)
        .build_step("build_step_2")
        .args
    )
    assert ret == 0

    pkgs_after_install = docker_container.list_pip()
    assert pkgs_after_install == ContainsPackages(expected_packages)
