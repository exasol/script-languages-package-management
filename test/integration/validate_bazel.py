from test.integration.docker_test_environment.docker_test_container import (
    DockerTestContainer,
)


def validate_bazel(docker_container: DockerTestContainer):
    docker_container.run(
        ["git", "clone", "https://github.com/bazelbuild/examples.git"], workdir="/tmp"
    )
    docker_container.run(
        ["bazel", "build", "//main:hello-world"],
        workdir="/tmp/examples/cpp-tutorial/stage1",
    )
    ret, out = docker_container.run(
        ["/tmp/examples/cpp-tutorial/stage1/bazel-bin/main/hello-world"]
    )
    assert ret == 0
    assert "Hello world\n" in out
