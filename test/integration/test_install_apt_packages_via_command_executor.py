from test.integration.docker_test_environment.test_logger import StringMatchCounter
from test.integration.package_utils import ContainsPackages

from exasol.exaslpm.model.serialization import to_yaml_str
from exasol.exaslpm.pkg_mgmt.context.context import Context
from exasol.exaslpm.pkg_mgmt.install_packages import package_install


class CommandExecuteRecorder:
    def __init__(self, delegate):
        self._delegate = delegate
        self.commands: list[list[str]] = []

    def execute(self, cmd_strs: list[str], env=None):
        self.commands.append(cmd_strs)
        return self._delegate.execute(cmd_strs, env=env)


def test_apt_install(
    docker_container,
    apt_pkg_file_wildcard,
    local_package_path,
    docker_executor_context,
):
    apt_package_file_yaml = to_yaml_str(apt_pkg_file_wildcard)
    local_package_path.write_text(apt_package_file_yaml)

    expected_packages = apt_pkg_file_wildcard.build_steps[0].phases[0].apt.packages

    pkgs_before_install = docker_container.list_apt()
    assert pkgs_before_install != ContainsPackages(expected_packages)

    return_code_counter = StringMatchCounter("Return Code: 0")
    docker_executor_context.cmd_logger.info_callback = return_code_counter.log

    package_install(
        package_file=local_package_path,
        build_step_name="build_step_1",
        context=docker_executor_context,
    )

    pkgs_after_install = docker_container.list_apt()
    assert pkgs_after_install == ContainsPackages(expected_packages)

    # Check that all 'install apt' commands (see install_apt.prepare_all_cmds() for list) succeeded
    assert return_code_counter.result == 7


def test_apt_install_updates_before_install(
    apt_pkg_file_wildcard,
    local_package_path,
    docker_executor_context,
):
    apt_package_file_yaml = to_yaml_str(apt_pkg_file_wildcard)
    local_package_path.write_text(apt_package_file_yaml)

    execute_recorder = CommandExecuteRecorder(docker_executor_context.cmd_executor)
    ctx_with_exe_recorder = Context(
        cmd_logger=docker_executor_context.cmd_logger,
        cmd_executor=execute_recorder,
        history_file_manager=docker_executor_context.history_file_manager,
        file_access=docker_executor_context.file_access,
        file_downloader=docker_executor_context.file_downloader,
        temp_file_provider=docker_executor_context.temp_file_provider,
    )

    package_install(
        package_file=local_package_path,
        build_step_name="build_step_1",
        context=ctx_with_exe_recorder,
    )

    update_index = next(
        index
        for index, command in enumerate(execute_recorder.commands)
        if command == ["apt-get", "-y", "update"]
    )
    install_index = next(
        index
        for index, command in enumerate(execute_recorder.commands)
        if command[:5] == ["apt-get", "install", "-V", "-y", "--no-install-recommends"]
    )

    assert update_index < install_index
