from test.integration.docker_test_environment.test_logger import StringMatchCounter
from test.integration.package_fixtures import (  # noqa: F401, fixtures to be used
    pip_package_file_content,
)

from exasol.exaslpm.model.serialization import to_yaml_str
from exasol.exaslpm.pkg_mgmt.install_packages import package_install


def test_install_pip(
    docker_container,
    pip_package_file_content,
    local_package_path,
    docker_executor_context,
):
    apt_package_file_yaml = to_yaml_str(pip_package_file_content)
    local_package_path.write_text(apt_package_file_yaml)

    return_code_counter = StringMatchCounter("Return Code: 0")
    docker_executor_context.cmd_logger.info_callback = return_code_counter.log

    package_install(
        package_file=local_package_path,
        build_step_name="build_step_1",
        context=docker_executor_context,
    )

    pip_cmd_result_exit_code, _ = docker_container.run(
        ["python3.12", "-m", "pip", "list"]
    )
    assert pip_cmd_result_exit_code == 0

    # 7 (from apt install, see exasol.exaslpm.pkg_mgmt.install_apt) +
    # 2 (from install pip, see exasol.exaslpm.pkg_mgmt.install_pip)
    assert return_code_counter.result == 9
