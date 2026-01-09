from inspect import cleandoc
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
              version: "1.21.4-1ubuntu4"
            - name: curl
              version: "6.0-26ubuntu3.2"
    """
    )


def test_apt_install(docker_container, apt_package_file_content, cli_helper):
    apt_package_file = docker_container.make_and_upload_file(
        Path("/"), "apt_file", apt_package_file_content
    )

    ret, out = docker_container.run_exaslpm(
        cli_helper.install.package_file(apt_package_file)
        .phase("phase_1")
        .build_step("build_step_1")
        .args
    )
    assert ret == 0


def test_apt_list(docker_container):
    apt_packages = docker_container.list_apt()
    assert len(apt_packages) > 0, apt_packages
    pkg_found = next(
        (
            pkg
            for pkg in apt_packages
            if pkg["package"] == "wget" and pkg["ver"] == "1.21.4-1ubuntu4"
        ),
        None,
    )
    assert pkg_found
