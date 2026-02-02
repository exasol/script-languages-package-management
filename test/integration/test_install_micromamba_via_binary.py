from copy import deepcopy
from pathlib import Path
from test.integration.package_fixtures import (  # noqa: F401, fixtures to be used
    micromamba_file_content,
)

from exasol.exaslpm.model.serialization import to_yaml_str
from exasol.exaslpm.pkg_mgmt.constants import MICROMAMBA_PATH


def test_install_micromamba(docker_container, micromamba_file_content, cli_helper):
    micromamba_file_yaml = to_yaml_str(micromamba_file_content)

    micromamba_package_file = docker_container.make_and_upload_file(
        Path("/"), "micromamba_file_01", micromamba_file_yaml.encode("utf-8")
    )

    ret, out = docker_container.run_exaslpm(
        cli_helper.install.package_file(micromamba_package_file)
        .build_step("build_step_1")
        .args
    )
    assert ret == 0

    micromamba = (
        micromamba_file_content.find_build_step("build_step_1")
        .find_phase("phase_2")
        .tools.micromamba
    )
    micromamba_list_cmd_result_exit_code, _ = docker_container.run_in_mamba_env(
        [str(MICROMAMBA_PATH), "list"], micromamba
    )
    assert micromamba_list_cmd_result_exit_code == 0


def test_install_micromamba_error(
    docker_container, micromamba_file_content, cli_helper
):
    micromamba_package_file_content_invalid = deepcopy(micromamba_file_content)
    micromamba_package_file_content_invalid.find_build_step("build_step_1").find_phase(
        "phase_2"
    ).tools.micromamba.version = "invalid"
    micromamba_package_file_yaml = to_yaml_str(micromamba_package_file_content_invalid)

    micromamba_package_file = docker_container.make_and_upload_file(
        Path("/"), "micromamba_file_01", micromamba_package_file_yaml.encode("utf-8")
    )

    ret, out = docker_container.run_exaslpm(
        cli_helper.install.package_file(micromamba_package_file)
        .build_step("build_step_1")
        .args,
        check_exit_code=False,
    )
    assert ret != 0
    assert "bin/micromamba: Not found in archive" in out
