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
              version: "1.20"
            - name: curl
              version: "7.68"
    """
    )


def test_apt_install(docker_container, apt_package_file_content, cli_helper):
    apt_package_file = docker_container.make_and_upload_file(
        Path("/"), "apt_file", apt_package_file_content
    )

    _, out = docker_container.run_exaslpm(
        cli_helper.package_file(apt_package_file)
        .phase("phase_1")
        .build_step("build_step_1")
        .args
    )
    for line in apt_package_file_content.splitlines():
        assert line in out, f"Line '{line}' is missing in output: \n{out}"


def test_apt_list(docker_container):
    apt_packages = docker_container.list_apt()
    assert len(apt_packages) > 0, apt_packages
