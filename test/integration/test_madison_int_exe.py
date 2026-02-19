from pathlib import Path
from test.integration.docker_test_environment.docker_command_executor import (
    DockerCommandExecutor,
)
from test.integration.docker_test_environment.docker_test_container import (
    DockerTestContainer,
)
from test.integration.docker_test_environment.test_logger import TestLogger
from test.integration.package_utils import ContainsPackages

from exasol.exaslpm.model.package_file_config import AptPackage
from exasol.exaslpm.model.serialization import to_yaml_str
from exasol.exaslpm.pkg_mgmt.context.context import Context
from exasol.exaslpm.pkg_mgmt.search.apt_madison_parser import (
    MadisonExecutor,
    MadisonParser,
)


def test_apt_install_madison(docker_container, apt_pkg_file_wildcard, cli_helper):
    apt_package_file_yaml = to_yaml_str(apt_pkg_file_wildcard)

    apt_package_file = docker_container.make_and_upload_file(
        Path("/"), "apt_file_01", apt_package_file_yaml.encode("utf-8")
    )

    expected_packages = apt_pkg_file_wildcard.build_steps[0].phases[0].apt.packages

    pkgs_before_install = docker_container.list_apt()
    assert pkgs_before_install != ContainsPackages(expected_packages)

    ret, out = docker_container.run_exaslpm(
        cli_helper.install.package_file(apt_package_file)
        .build_step("build_step_1")
        .args
    )
    assert ret == 0

    pkgs_after_install = docker_container.list_apt()
    assert pkgs_after_install == ContainsPackages(expected_packages)


def test_madison_executor_basic_package(docker_container: DockerTestContainer):
    pkg_list = [AptPackage(name="bash")]
    logger = TestLogger()
    docker_cmd_executor = DockerCommandExecutor(
        logger=logger, test_container=docker_container
    )
    ctx = Context(
        cmd_logger=TestLogger(),
        cmd_executor=docker_cmd_executor,
        history_file_manager=None,
        file_access=None,
        file_downloader=None,
        temp_file_provider=None,
    )

    result = MadisonExecutor.execute_madison(pkg_list, ctx)
    assert result != ""
    assert "bash" in result


def test_madison_executor_nonexistent_package(docker_container: DockerTestContainer):
    pkg_list = [AptPackage(name="nonexistent-package")]

    logger = TestLogger()
    docker_cmd_executor = DockerCommandExecutor(
        logger=logger, test_container=docker_container
    )
    ctx = Context(
        cmd_logger=TestLogger(),
        cmd_executor=docker_cmd_executor,
        history_file_manager=None,
        file_access=None,
        file_downloader=None,
        temp_file_provider=None,
    )

    result = MadisonExecutor.execute_madison(pkg_list, ctx)
    assert isinstance(result, str)


def test_madison_mixed(docker_container: DockerTestContainer):
    pkg_list = [
        AptPackage(name="bash"),
        AptPackage(name="nonexistent-pkg-xyz"),
        AptPackage(name="grep"),
    ]

    logger = TestLogger()
    docker_cmd_executor = DockerCommandExecutor(
        logger=logger, test_container=docker_container
    )
    ctx = Context(
        cmd_logger=TestLogger(),
        cmd_executor=docker_cmd_executor,
        history_file_manager=None,
        file_access=None,
        file_downloader=None,
        temp_file_provider=None,
    )

    result = MadisonExecutor.execute_madison(pkg_list, ctx)
    parsed = MadisonParser.parse_madison_output(result, ctx)

    assert "bash" in parsed
    assert "grep" in parsed
