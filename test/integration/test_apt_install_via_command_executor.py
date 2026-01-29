from test.integration.docker_test_environment.test_logger import StringMatchCounter
from test.integration.package_fixtures import (  # noqa: F401, fixtures to be used
    apt_package_file_content,
)
from test.integration.package_utils import ContainsPackages

from exasol.exaslpm.model.serialization import to_yaml_str
from exasol.exaslpm.pkg_mgmt.install_packages import package_install


def test_apt_install(
    docker_container,
    apt_package_file_content,
    local_package_path,
    docker_executor_context,
):
    apt_package_file_yaml = to_yaml_str(apt_package_file_content)
    local_package_path.write_text(apt_package_file_yaml)

    expected_packages = apt_package_file_content.build_steps[0].phases[0].apt.packages

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
