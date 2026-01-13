from inspect import cleandoc
from json import JSONDecodeError
from pathlib import Path

import pytest


@pytest.fixture
def apt_package_file_content():
    return cleandoc(
        """
build_steps:
  build_step_1:
    phases:
      phase_1:
        apt:
          packages:
            - name: wget
              version: "1.21.4-1ubuntu4.1"
            - name: curl
              version: "8.5.0-2ubuntu10.6"
    """
    )


def does_package_exist(installed_pkgs: list, pkgs_to_check: dict):
    pkgs_found = False
    for pkg_name, pkg_ver in pkgs_to_check.items():
        pkgs_found = next(
            (
                pkg
                for pkg in installed_pkgs
                if pkg["package"] == pkg_name and pkg["version"] == pkg_ver
            ),
            None,
        )
    return pkgs_found


def test_apt_install(docker_container, apt_package_file_content, cli_helper):
    apt_package_file = docker_container.make_and_upload_file(
        Path("/"), "apt_file", apt_package_file_content
    )

    pkgs_to_check = {"wget": "1.21.4-1ubuntu4.1", "curl": "8.5.0-2ubuntu10.6"}

    try:
        pkgs_before_install = docker_container.list_apt()
        assert not does_package_exist(pkgs_before_install, pkgs_to_check)
    except JSONDecodeError as jde:
        pass

    ret, out = docker_container.run_exaslpm(
        cli_helper.install.package_file(apt_package_file)
        .phase("phase_1")
        .build_step("build_step_1")
        .args
    )
    assert ret == 0

    pkgs_after_install = docker_container.list_apt()
    assert does_package_exist(pkgs_after_install, pkgs_to_check)

    # for pkg_name, pkg_ver in expected_pkgs.items():
    #     pkgs_found = next(
    #         (
    #             pkg
    #             for pkg in apt_packages
    #             if pkg["package"] == pkg_name and pkg["version"] == pkg_ver
    #         ),
    #         None,
    #     )
    #     assert pkgs_found
