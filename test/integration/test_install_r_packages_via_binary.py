from pathlib import Path
from test.integration.package_utils import ContainsPackages

import pytest

from exasol.exaslpm.model.serialization import to_yaml_str


@pytest.fixture
def prepare_gpg_env(docker_container, apt_gpg, apt_r_with_ppa, cli_helper):
    apt_gpg_package_file_yaml = to_yaml_str(apt_gpg)

    apt_gpg_package_file = docker_container.make_and_upload_file(
        Path("/"), "apt_gpg_file_01", apt_gpg_package_file_yaml.encode("utf-8")
    )

    ret, out = docker_container.run_exaslpm(
        cli_helper.install.package_file(apt_gpg_package_file)
        .build_step("build_step_1")
        .args
    )
    assert ret == 0


@pytest.fixture
def prepare_r_env(docker_container, prepare_gpg_env, apt_r_with_ppa, cli_helper):
    apt_r_package_file_yaml = to_yaml_str(apt_r_with_ppa)

    apt_gpg_package_file = docker_container.make_and_upload_file(
        Path("/"), "apt_r_file_01", apt_r_package_file_yaml.encode("utf-8")
    )

    ret, out = docker_container.run_exaslpm(
        cli_helper.install.package_file(apt_gpg_package_file)
        .build_step("build_step_2")
        .args
    )
    assert ret == 0


def test_install_r_packages(docker_container, packages_r, cli_helper, prepare_r_env):
    r_packages_file_yaml = to_yaml_str(packages_r)

    r_package_file = docker_container.make_and_upload_file(
        Path("/"), "r_file_01", r_packages_file_yaml.encode("utf-8")
    )

    expected_packages = packages_r.build_steps[0].phases[1].r.packages

    pkgs_before_install = docker_container.list_r()
    assert pkgs_before_install != ContainsPackages(expected_packages)

    ret, out = docker_container.run_exaslpm(
        cli_helper.install.package_file(r_package_file).build_step("build_step_3").args
    )
    assert ret == 0

    pkgs_after_install = docker_container.list_r()
    assert pkgs_after_install == ContainsPackages(expected_packages)


#
# def test_pip_packages_install_error(
#     docker_container, pip_packages_file_content, cli_helper, prepare_pip_env
# ):
#     pkg = (
#         pip_packages_file_content.find_build_step("build_step_2")
#         .find_phase("phase_1")
#         .pip.packages[0]
#     )
#     pkg.name = "unknowsoftware"
#     pkg.version = " == 0.0.0"
#     pip_package_file_content_yaml = to_yaml_str(pip_packages_file_content)
#     pip_invalid_pkg_file = docker_container.make_and_upload_file(
#         Path("/"), "pip_file_02", pip_package_file_content_yaml.encode("utf-8")
#     )
#
#     ret, out = docker_container.run_exaslpm(
#         cli_helper.install.package_file(pip_invalid_pkg_file)
#         .build_step("build_step_2")
#         .args,
#         False,
#     )
#     assert ret != 0
#     assert (
#         "Could not find a version that satisfies the requirement unknowsoftware==0.0.0"
#         in out
#     )
