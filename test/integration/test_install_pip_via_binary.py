from pathlib import Path
from test.integration.package_fixtures import (  # noqa: F401, fixtures to be used
    pip_package_file_content,
)

import yaml


def test_install_pip(docker_container, pip_package_file_content, cli_helper):
    pip_package_file_yaml = yaml.dump(pip_package_file_content.model_dump(mode="json"))

    pip_package_file = docker_container.make_and_upload_file(
        Path("/"), "pip_file_01", pip_package_file_yaml
    )

    ret, out = docker_container.run_exaslpm(
        cli_helper.install.package_file(pip_package_file)
        .build_step("build_step_1")
        .args
    )
    assert ret == 0

    pip_cmd_result_exit_code, _ = docker_container.run(
        ["python3.12", "-m", "pip", "list"]
    )
    assert pip_cmd_result_exit_code == 0


def test_install_pip_error(docker_container, pip_package_file_content, cli_helper):
    pip_package_file_content.find_build_step("build_step_1").find_phase(
        "phase_3"
    ).tools.pip.version = "invalid"
    pip_package_file_yaml = yaml.dump(pip_package_file_content.model_dump(mode="json"))

    pip_package_file = docker_container.make_and_upload_file(
        Path("/"), "pip_file_01", pip_package_file_yaml
    )

    ret, out = docker_container.run_exaslpm(
        cli_helper.install.package_file(pip_package_file)
        .build_step("build_step_1")
        .args,
        check_exit_code=False,
    )
    assert ret != 0
    assert "Invalid requirement: 'pip == invalid'" in out
