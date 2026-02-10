from pathlib import Path

from exasol.exaslpm.model.serialization import to_yaml_str
from test.integration.validate_bazel import validate_bazel


def test_install_bazel(docker_container, bazel_file_content, cli_helper):
    bazel_file_yaml = to_yaml_str(bazel_file_content)

    bazel_package_file = docker_container.make_and_upload_file(
        Path("/"), "bazel_file_01", bazel_file_yaml.encode("utf-8")
    )

    ret, out = docker_container.run_exaslpm(
        cli_helper.install.package_file(bazel_package_file)
        .build_step("build_step_1")
        .args
    )
    assert ret == 0

    validate_bazel(docker_container)


def test_install_bazel_error(docker_container, bazel_file_content, cli_helper):
    bazel_file_content.find_build_step("build_step_1").find_phase(
        "phase_2"
    ).tools.bazel.version = "invalid_version"
    bazel_file_yaml = to_yaml_str(bazel_file_content)
    apt_invalid_pkg_file = docker_container.make_and_upload_file(
        Path("/"), "bazel_file_02", bazel_file_yaml.encode("utf-8")
    )

    ret, out = docker_container.run_exaslpm(
        cli_helper.install.package_file(apt_invalid_pkg_file)
        .build_step("build_step_1")
        .args,
        False,
    )
    assert ret != 0
    assert "404 Client Error: Not Found for url:" in out
