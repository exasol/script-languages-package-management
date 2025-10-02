from inspect import cleandoc

import pytest



@pytest.fixture
def apt_package_file_content():
    return cleandoc("""
    unzip|6.0-26ubuntu3.2
    git|1:2.34.1-1ubuntu1.15
    """)


@pytest.fixture
def apt_package_file(file_uploader, apt_package_file_content):
    file_uploader("/", "apt_package", apt_package_file_content)
    return "/apt_package"

def test_apt_install(docker_runner, apt_package_file, apt_package_file_content, cli_helper):
    exit_code, out = docker_runner(cli_helper.apt.install(apt_package_file))
    assert exit_code == 0, out
    output = out.decode("utf-8")
    for line in apt_package_file_content.splitlines():
        assert line in output, f"Line '{line}' is missing in output: \n{output}"


def test_apt_list(list_apt_package_factory):
    apt_packages = list_apt_package_factory()
    assert len(apt_packages) == 2, apt_packages