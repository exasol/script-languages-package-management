from pathlib import Path
from test.integration.package_utils import (
    ContainsCondaPackages,
    ContainsPackages,
    ContainsPipPackages,
)

import pytest
import yaml

from exasol.exaslpm.model.package_file_config import (
    AptPackage,
    CondaPackage,
    PipPackage,
    RPackage,
)
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

    installed_apt_packages = [
        AptPackage.model_validate(apt_package)
        for apt_package in installed_packages["apt"]
    ]
    assert installed_apt_packages == ContainsPackages(
        [AptPackage(name="python3-dev", version=f"{python_version[6:]}*")]
    )

    installed_pip_packages = [
        PipPackage.model_validate(pip_package)
        for pip_package in installed_packages["pip"]
    ]
    assert installed_pip_packages == ContainsPipPackages(
        [PipPackage(name="Jinja2", version=">=3.1.6, <4.0.0")]
    )

    installed_r_packages = [
        RPackage.model_validate(r_package) for r_package in installed_packages["r"]
    ]
    assert installed_r_packages == ContainsPackages(
        [RPackage(name="poorman", version="0.2.7")]
    )

    installed_conda_packages = [
        CondaPackage.model_validate(conda_package)
        for conda_package in installed_packages["conda"]
    ]
    assert installed_conda_packages == ContainsCondaPackages(
        [CondaPackage(name="zstd", version="=1.5.7", channel="conda-forge")]
    )
