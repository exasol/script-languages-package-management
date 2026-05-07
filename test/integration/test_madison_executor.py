from test.integration.docker_test_environment.docker_command_executor import (
    DockerCommandExecutor,
)
from test.integration.docker_test_environment.docker_test_container import (
    DockerTestContainer,
)
from test.integration.docker_test_environment.test_logger import (
    LogCollector,
    TestLogger,
)

from exasol.exaslpm.model.package_file_config import AptPackage
from exasol.exaslpm.pkg_mgmt.context.context import Context
from exasol.exaslpm.pkg_mgmt.search.apt_madison_parser import (
    MadisonExecutor,
    MadisonParser,
)


def _update_apt_metadata(docker_container: DockerTestContainer) -> None:
    docker_container.run(["apt-get", "-y", "update"])


def test_madison_executor_basic_package(
    docker_container: DockerTestContainer, docker_executor_context: Context
):
    pkg_list = [AptPackage(name="bash")]
    _update_apt_metadata(docker_container)

    result = MadisonExecutor.execute_madison(pkg_list, docker_executor_context)
    assert result != ""
    assert "bash" in result


def test_madison_executor_nonexistent_package(
    docker_container: DockerTestContainer,
    docker_executor_context: Context,
    test_logger: TestLogger,
):
    pkg_list = [AptPackage(name="nonexistent-package")]
    _update_apt_metadata(docker_container)
    warn_log = LogCollector()
    error_log = LogCollector()
    test_logger.warning_callback = warn_log.log
    test_logger.error_callback = error_log.log
    result = MadisonExecutor.execute_madison(pkg_list, docker_executor_context)
    assert isinstance(result, str)
    assert result == ""
    assert warn_log.result.strip() == "N: Unable to locate package nonexistent-package"
    assert error_log.result == ""


def test_madison_mixed(docker_container: DockerTestContainer):
    pkg_list = [
        AptPackage(name="bash"),
        AptPackage(name="nonexistent-pkg-xyz"),
        AptPackage(name="grep"),
    ]
    _update_apt_metadata(docker_container)

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
