from test.integration.docker_test_environment.docker_command_executor import (
    DockerCommandExecutor,
)
from test.integration.docker_test_environment.docker_test_container import (
    DockerTestContainer,
)
from test.integration.docker_test_environment.test_logger import TestLogger

from exasol.exaslpm.model.package_file_config import AptPackage
from exasol.exaslpm.pkg_mgmt.context.context import Context
from exasol.exaslpm.pkg_mgmt.search.apt_madison_parser import (
    MadisonExecutor,
    MadisonParser,
)


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
