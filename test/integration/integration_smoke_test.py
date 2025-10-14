from inspect import cleandoc
from pathlib import Path

import pytest


@pytest.fixture
def apt_package_file_content():
    return cleandoc(
        """
    unzip|6.0-26ubuntu3.2
    git|1:2.34.1-1ubuntu1.15
    """
    )


def test_apt_install(docker_container, apt_package_file_content, cli_helper):
    apt_package_file = docker_container.make_and_upload_file(
        Path("/"), "apt_file", apt_package_file_content
    )
    _, out = docker_container.run_exaslpm(
        cli_helper.install.package_file(apt_package_file).build_step("build").args
    )
    for line in apt_package_file_content.splitlines():
        assert line in out, f"Line '{line}' is missing in output: \n{out}"


def test_apt_list(docker_container):
    apt_packages = docker_container.list_apt()
    assert len(apt_packages) > 0, apt_packages
