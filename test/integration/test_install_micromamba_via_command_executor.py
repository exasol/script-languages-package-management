from test.integration.docker_test_environment.test_logger import StringMatchCounter
from test.integration.package_fixtures import (  # noqa: F401, fixtures to be used
    micromamba_file_content,
)

from exasol.exaslpm.model.serialization import to_yaml_str
from exasol.exaslpm.pkg_mgmt.constants import MICROMAMBA_PATH
from exasol.exaslpm.pkg_mgmt.install_packages import package_install


def test_install_micromamba(
    docker_container,
    micromamba_file_content,
    cli_helper,
    docker_executor_context,
    local_package_path,
):
    micromamba_package_file_yaml = to_yaml_str(micromamba_file_content)
    local_package_path.write_text(micromamba_package_file_yaml)

    return_code_counter = StringMatchCounter("Return Code: 0")
    docker_executor_context.cmd_logger.info_callback = return_code_counter.log

    package_install(
        package_file=local_package_path,
        build_step_name="build_step_1",
        context=docker_executor_context,
    )

    # 7 (from apt install, see exasol.exaslpm.pkg_mgmt.install_apt) +
    # 2 (from install micromamba, see exasol.exaslpm.pkg_mgmt.install_micromamba)
    assert return_code_counter.result == 9

    micromamba = (
        micromamba_file_content.find_build_step("build_step_1")
        .find_phase("phase_2")
        .tools.micromamba
    )

    micromamba_cmd_result_exit_code, out = docker_container.run_in_mamba_env(
        [str(MICROMAMBA_PATH), "list"], micromamba
    )
    assert micromamba_cmd_result_exit_code == 0
    assert 'List of packages in environment: "/opt/conda"' in out
