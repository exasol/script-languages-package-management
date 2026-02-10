from pathlib import Path

from exasol.exaslpm.model.serialization import to_yaml_str



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

    docker_container.run(["git", "clone", "https://github.com/bazelbuild/examples.git"], workdir="/tmp")
    docker_container.run(["bazel", "build", "//main:hello-world"], workdir="/tmp/examples/cpp-tutorial/stage1")
    ret, out = docker_container.run(["/tmp/examples/cpp-tutorial/stage1/bazel-bin/main/hello-world"])
    assert ret == 0
    assert "Hello world\n" in out

