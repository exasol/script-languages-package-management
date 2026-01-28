from pathlib import Path
from test.integration.docker_test_environment.docker_test_container import (
    DockerTestContainer,
)
from test.integration.package_fixtures import (  # noqa: F401, fixtures to be used
    apt_invalid_package_file,
    apt_package_file_content,
)
from test.integration.package_utils import ContainsPackages

import yaml

from exasol.exaslpm.model.package_file_config import (
    BuildStep,
    PackageFile,
)


def test_apt_install(docker_container, apt_package_file_content, cli_helper):
    apt_package_file_yaml = yaml.dump(apt_package_file_content.model_dump())

    apt_package_file = docker_container.make_and_upload_file(
        Path("/"), "apt_file_01", apt_package_file_yaml
    )

    expected_packages = apt_package_file_content.build_steps[0].phases[0].apt.packages

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


def test_apt_install_error(docker_container, apt_invalid_package_file, cli_helper):
    apt_invalid_package_file_yaml = yaml.dump(apt_invalid_package_file.model_dump())
    apt_invalid_pkg_file = docker_container.make_and_upload_file(
        Path("/"), "apt_file_02", apt_invalid_package_file_yaml
    )

    ret, out = docker_container.run_exaslpm(
        cli_helper.install.package_file(apt_invalid_pkg_file)
        .build_step("build_step_1")
        .args,
        False,
    )
    assert ret != 0
    assert "Unable to locate package unknowsoftware" in out


def _validate_build_step_history_file(
    docker_container: DockerTestContainer,
    history_file_path: Path,
    expected_build_step: BuildStep,
) -> None:
    _, out = docker_container.run(["cat", str(history_file_path)])
    history_one_model = PackageFile.model_validate(yaml.safe_load(out))
    assert len(history_one_model.build_steps) == 1
    assert history_one_model.build_steps[0] == expected_build_step


def test_history(docker_container, apt_package_file_content, cli_helper):
    apt_package_file_yaml = yaml.dump(apt_package_file_content.model_dump())

    apt_package_file = docker_container.make_and_upload_file(
        Path("/"), "apt_file_01", apt_package_file_yaml
    )

    ret, out = docker_container.run_exaslpm(
        cli_helper.install.package_file(apt_package_file)
        .build_step("build_step_1")
        .args
    )
    assert ret == 0

    ret, out = docker_container.run_exaslpm(
        cli_helper.install.package_file(apt_package_file)
        .build_step("build_step_2")
        .args
    )
    assert ret == 0

    _, out = docker_container.run(["ls", "/build_info/packages/history"])
    history_files = [line.strip() for line in out.splitlines()]
    assert history_files == ["build_step_1", "build_step_2"]

    _validate_build_step_history_file(
        docker_container,
        Path("/build_info/packages/history/build_step_1"),
        apt_package_file_content.build_steps[0],
    )
    _validate_build_step_history_file(
        docker_container,
        Path("/build_info/packages/history/build_step_2"),
        apt_package_file_content.build_steps[1],
    )
