from pathlib import Path

import pytest
import yaml

from exasol.exaslpm.model.serialization import to_yaml_str

pytestmark = pytest.mark.via_binary


def test_no_history_empty_lists_expected(docker_container):

    ret, out = docker_container.run_exaslpm(["list-all-installed-packages"])

    assert ret == 0
    expected_yaml = """
    version: 1.0.0
    apt: []
    conda: []
    pip: []
    r: []

    """
    assert yaml.safe_load(out) == yaml.safe_load(expected_yaml)


def verify_package_exists_fail_otherwise(
    installed_packages, expected_package_name: str, expected_package_version: str
) -> None:
    for package in installed_packages:
        if package["name"] == expected_package_name and package["version"].startswith(
            expected_package_version
        ):
            return
    pytest.fail(
        f"Package: '{expected_package_name}' with version: '{expected_package_version}' not in installed packages: {installed_packages}"
    )


def test_list_all_installed_packages(
    docker_container, list_all_installed_packages_file_content, cli_helper
):
    package_file_yaml = to_yaml_str(list_all_installed_packages_file_content)

    package_file = docker_container.make_and_upload_file(
        Path("/"), "package_file", package_file_yaml.encode("utf-8")
    )

    ret, _ = docker_container.run_exaslpm(
        cli_helper.install.package_file(package_file).build_step("build_step_1").args
    )
    assert ret == 0

    ret, out = docker_container.run_exaslpm(["list-all-installed-packages"])

    assert ret == 0
    installed_packages = yaml.safe_load(out)
    verify_package_exists_fail_otherwise(
        installed_packages["apt"], "python3-dev", "3.14.3"
    )
    verify_package_exists_fail_otherwise(installed_packages["pip"], "Jinja2", "3")
    verify_package_exists_fail_otherwise(installed_packages["r"], "poorman", "0.2.7")
    verify_package_exists_fail_otherwise(installed_packages["conda"], "zstd", "1.5.7")
