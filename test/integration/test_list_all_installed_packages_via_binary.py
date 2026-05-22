from pathlib import Path

import pytest
import yaml

from exasol.exaslpm.model.serialization import to_yaml_str

pytestmark = pytest.mark.via_binary


EXPECTED_EMPTY_INSTALLED_PACKAGES_YAML = """
version: 1.0.0
apt: []
conda: []
pip: []
r: []

"""


def test_no_history_empty_lists_expected(docker_container):

    ret, out = docker_container.run_exaslpm(["list-all-installed-packages"])

    assert ret == 0
    assert yaml.safe_load(out) == yaml.safe_load(EXPECTED_EMPTY_INSTALLED_PACKAGES_YAML)


def test_out_file_parameter(docker_container):

    target_file = Path("/tmp/installed_packages.yml")
    ret, out = docker_container.run_exaslpm(
        ["list-all-installed-packages", "--out-file", str(target_file)]
    )
    assert ret == 0

    _, out_cat = docker_container.run(["cat", str(target_file)])
    assert yaml.safe_load(out_cat) == yaml.safe_load(
        EXPECTED_EMPTY_INSTALLED_PACKAGES_YAML
    )


def verify_package_exists_fail_otherwise(
    installed_packages,
    expected_package_name: str,
    expected_package_version: str,
    conda_channel: str | None = None,
) -> None:
    for package in installed_packages:
        if package["name"] == expected_package_name and package["version"].startswith(
            expected_package_version
        ):
            if conda_channel and package["channel"] != conda_channel:
                continue
            return
    pytest.fail(
        f"Package: '{expected_package_name}' with version: '{expected_package_version}' not in installed packages: {installed_packages}"
    )


def test_list_all_installed_packages(
    docker_container,
    list_all_installed_packages_file_content,
    cli_helper,
    python_version,
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
        installed_packages["apt"], "python3-dev", python_version[6:]
    )
    verify_package_exists_fail_otherwise(installed_packages["pip"], "Jinja2", "3")
    verify_package_exists_fail_otherwise(installed_packages["r"], "poorman", "0.2.7")
    verify_package_exists_fail_otherwise(
        installed_packages["conda"], "zstd", "1.5.7", "conda-forge"
    )
