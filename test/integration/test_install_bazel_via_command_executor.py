from test.integration.validate_bazel import validate_bazel

from exasol.exaslpm.model.serialization import to_yaml_str
from exasol.exaslpm.pkg_mgmt.install_packages import package_install


def test_install_bazel(
    docker_container,
    bazel_file_content,
    local_package_path,
    docker_executor_context,
):
    bazel_package_file_yaml = to_yaml_str(bazel_file_content)
    local_package_path.write_text(bazel_package_file_yaml)

    package_install(
        package_file=local_package_path,
        build_step_name="build_step_1",
        context=docker_executor_context,
    )

    validate_bazel(docker_container)
