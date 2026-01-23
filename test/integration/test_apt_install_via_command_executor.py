from pathlib import Path
from test.integration.package_fixtures import (  # noqa: F401, fixtures to be used
    apt_invalid_package_file,
    apt_package_file_content,
)
from test.integration.package_utils import ContainsPackages

import yaml

from exasol.exaslpm.pkg_mgmt.install_packages import package_install


def test_apt_install(
    docker_container,
    apt_package_file_content,
    docker_command_executor,
    temp_history_file_manager,
    local_package_path,
    test_logger,
):
    apt_package_file_yaml = yaml.dump(apt_package_file_content.model_dump())
    local_package_path.write_text(apt_package_file_yaml)

    expected_packages = apt_package_file_content.build_steps[0].phases[0].apt.packages

    pkgs_before_install = docker_container.list_apt()
    assert pkgs_before_install != ContainsPackages(expected_packages)

    package_install(
        phase_name="phase_1",
        package_file=local_package_path,
        build_step_name="build_step_1",
        python_binary=Path(),
        conda_binary=Path(),
        r_binary=Path(),
        cmd_executor=docker_command_executor,
        logger=docker_command_executor._log,
        history_file_manager=temp_history_file_manager,
    )

    pkgs_after_install = docker_container.list_apt()
    assert pkgs_after_install == ContainsPackages(expected_packages)

    # Check that all 'install apt' commands (see install_apt.prepare_all_cmds() for list) succeeded
    assert test_logger.info_messages.count("Return Code: 0") == 7
