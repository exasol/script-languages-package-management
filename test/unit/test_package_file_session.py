import pytest
import yaml

from exasol.exaslpm.model.package_file_config import PackageFile
from exasol.exaslpm.pkg_mgmt.package_file_session import PackageFileSession


def test_commit(tmp_path):
    yaml_file = """
    build_steps:
      - name: build_step_one
        phases:
          - name: phase_one
            apt:
                packages:
                - name: curl
                  version: 7.68.0
                  comment: install curl
          - name: phase_two
            tools:
              python_binary_path: /usr/bin/python3.12
    """
    package_file_path = tmp_path / "package.yaml"
    package_file_path.write_text(yaml_file)

    package_file_session = PackageFileSession(package_file=package_file_path)
    package_file_session.package_file_config.find_build_step(
        "build_step_one"
    ).comment = "Update"
    package_file_session.commit_changes()

    # Reload model from file and validate
    d = yaml.safe_load(package_file_path.read_text())
    assert (
        PackageFile.model_validate(d).find_build_step("build_step_one").comment
        == "Update"
    )


def test_raise_error_invalid_package_file(tmp_path):
    yaml_file = """
    invalid_somethong:
    """
    package_file_path = tmp_path / "package.yaml"
    package_file_path.write_text(yaml_file)

    with pytest.raises(ValueError, match=r"validation error for PackageFile"):
        PackageFileSession(package_file=package_file_path)
