import argparse
import json
import os
import shutil
import stat
import subprocess
from argparse import ArgumentParser
from importlib.metadata import version
from inspect import cleandoc
from pathlib import Path
from tempfile import TemporaryDirectory

import PyInstaller.__main__
import docker
import nox
import requests
# imports all nox task provided by the toolbox
from nox import Session

from noxconfig import (
    PROJECT_CONFIG,
    PlatformConfig,
    PlatformConfigs, _INTEGRATION_TEST_RUNNER_VERSION,
)

# default actions to be run if nothing is explicitly specified with the -s option
nox.options.sessions = ["format:fix"]


def _current_platform_cfg(session: nox.Session) -> PlatformConfig:
    import platform

    supported_platforms = {
        "x86_64": PlatformConfigs.X86,
        "amd64": PlatformConfigs.X86,
        "aarch64": PlatformConfigs.ARM,
        "arm64": PlatformConfigs.ARM,
    }
    machine = platform.machine()
    session.log(f"Current platform: {machine}")
    return supported_platforms[machine].value


def _get_latest_gh_release(session: nox.Session) -> str:
    latest_release_url = "https://api.github.com/repos/exasol/script-languages-package-management/releases/latest"
    response = requests.get(latest_release_url)
    response.raise_for_status()
    response_json = response.json()
    latest_release = response_json["name"]
    session.log(f"Latest release: {latest_release}")
    return latest_release


def _build_binary(exe_name: str, clean_up, session: nox.Session):
    script_path = str(PROJECT_CONFIG.source_code_path / "main.py")
    old_cwd = os.getcwd()
    try:
        os.chdir(PROJECT_CONFIG.root_path)
        options = [
            script_path,
            "--onefile",  # As a single exe file
            f"--name={exe_name}",  # Name of the executable
        ]
        PyInstaller.__main__.run(options)
        print(f"PyInstaller completed building {exe_name}")

        if clean_up:
            spec_file_path = Path() / f"{exe_name}.spec"
            if spec_file_path.exists():
                spec_file_path.unlink()
            else:
                session.warn(f"Expected spec file '{spec_file_path}' doesn't exist")
            build_path = PROJECT_CONFIG.root_path / "build" / exe_name
            if build_path.exists():
                shutil.rmtree(str(build_path))
            else:
                session.warn(
                    f"Expected temporary build path '{build_path}' doesn't exist"
                )
    finally:
        os.chdir(old_cwd)


_BUILD_CONTAINER_IMAGE = "almalinux:8"
_BUILD_IMAGE_TAG = "exaslpm-binary-build:latest"


def _build_binary_build_image(session: nox.Session):
    with TemporaryDirectory() as tmp_dir:
        dockerfile_content = cleandoc(f"""
            FROM {_BUILD_CONTAINER_IMAGE}
            RUN dnf install -y -q epel-release && dnf install -y -q python3.12 python3.12-devel
            RUN python3.12 -m ensurepip --upgrade
            RUN python3.12 -m pip install --no-cache-dir poetry
        """)
        (Path(tmp_dir) / "Dockerfile").write_text(dockerfile_content)
        client = docker.from_env()
        _, build_logs = client.images.build(path=str(tmp_dir), tag=_BUILD_IMAGE_TAG)
        for log in build_logs:
            if isinstance(log, dict) and "stream" in log:
                print(log["stream"], end="", flush=True)


@nox.session(name="build-binary-build-image", python=False)
def build_binary_build_image(session: nox.Session):
    _build_binary_build_image(session)


def _build_binary_in_container(exe_name: str, clean_up: bool, session: nox.Session):
    client = docker.from_env()
    try:
        client.images.get(_BUILD_IMAGE_TAG)
    except docker.errors.ImageNotFound:
        _build_binary_build_image(session)

    script_relative = (PROJECT_CONFIG.source_code_path / "main.py").relative_to(
        PROJECT_CONFIG.root_path
    )
    script_path = f"/project/{script_relative}"
    install_cmd = "poetry config virtualenvs.in-project false && poetry install"
    pyinstaller_cmd = (
        f"poetry run python -m PyInstaller {script_path} "
        f"--onefile --name {exe_name}"
    )
    cleanup_cmd = (
        f"rm -f {exe_name}.spec; rm -rf build/{exe_name}; true" if clean_up else "true"
    )
    uid_gid = f"{os.getuid()}:{os.getgid()}"
    chown_cmd = (
        f"chown {uid_gid} dist/{exe_name}; "
        f"chown -R {uid_gid} build/{exe_name} 2>/dev/null; "
        f"chown {uid_gid} {exe_name}.spec 2>/dev/null; "
        f"true"
    )

    # Pre-create dist/ as the current user so we can move the root-owned binary out after the build.
    (PROJECT_CONFIG.root_path / "dist").mkdir(exist_ok=True)

    container = client.containers.run(
        image=_BUILD_IMAGE_TAG,
        command=[
            "sh",
            "-c",
            f"{install_cmd} && {pyinstaller_cmd} && {cleanup_cmd} && {chown_cmd}",
        ],
        volumes={str(PROJECT_CONFIG.root_path): {"bind": "/project", "mode": "rw"}},
        working_dir="/project",
        detach=True,
        stdout=True,
        stderr=True,
    )
    try:
        for chunk in container.logs(stream=True, follow=True):
            print(chunk.decode("utf-8"), end="", flush=True)
        result = container.wait()
        if result["StatusCode"] != 0:
            session.error(f"Build container exited with status {result['StatusCode']}")
    finally:
        container.remove(force=True)


@nox.session(name="build-binary-in-container", python=False)
def build_binary_in_container(session: nox.Session):
    p = ArgumentParser(
        usage='nox -s build-binary-in-container -- --executable-name "exaslpm"',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--executable-name")
    p.add_argument("--cleanup", action="store_true", help="Remove temporary files")
    args = p.parse_args(session.posargs)
    exe_name = args.executable_name
    cleanup = args.cleanup

    if not bool(exe_name):
        session.error("PyInstaller needs a valid executable-name")
    else:
        _build_binary_in_container(exe_name, cleanup, session)


@nox.session(name="build-standalone-binary", python=False)
def build_standalone_binary(session: nox.Session):
    p = ArgumentParser(
        usage='nox -s build-standalone-binary -- --executable-name "exaslpm"',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--executable-name")
    p.add_argument("--cleanup", action="store_true", help="Remove temporary files")
    args = p.parse_args(session.posargs)
    exe_name = args.executable_name
    cleanup = args.cleanup

    if not bool(exe_name):
        session.error("PyInstaller needs a valid executable-name")
    else:
        _build_binary(exe_name, cleanup, session)


def _build_docker_prefix_tag():
    __version__ = version("exasol-script-languages-package-management")

    return f"exaslpm-{__version__}-ubuntu"


def _build_docker_img_tag(ubuntu_version: str, docker_tag_suffix: str):
    return f"{_build_docker_prefix_tag()}-{ubuntu_version}-{docker_tag_suffix}"


@nox.session(name="matrix:docker-image-config", python=False)
def docker_image_config(_):
    """
    Returns configuration for the GitHub runner which builds the Docker images.
    Each entry consists of "runner" (e.g. ubuntu-24.04), "base_img" (e.g. ubuntu:24.04)
    and "complete_docker_tag" (e.g. "exaslpm-ubuntu-24.04-x86_64").
    Thus, there will be one configuration per supported ubuntu version and supported platform.
    """
    runner_ubuntu = min(PROJECT_CONFIG.supported_ubuntu_versions)

    def _build_docker_build_image_config(
            runner_suffix: str, ubuntu_version: str, docker_tag_suffix: str
    ):
        return {
            "runner": f"ubuntu-{runner_ubuntu}{runner_suffix}",
            "base_img": f"ubuntu:{ubuntu_version}",
            "complete_docker_tag": _build_docker_img_tag(
                ubuntu_version, docker_tag_suffix
            ),
        }

    docker_image_config = [
        _build_docker_build_image_config(
            runner_suffix=platform.runner_suffix,
            ubuntu_version=ubuntu_version,
            docker_tag_suffix=platform.docker_tag_suffix,
        )
        for platform in PROJECT_CONFIG.supported_platforms
        for ubuntu_version in PROJECT_CONFIG.supported_ubuntu_versions
    ]

    print(json.dumps({"include": docker_image_config}))


def _push_image_safe(client, repository, tag, auth_config):
    # Use decode=True to get dictionary objects instead of raw bytes
    push_logs = client.images.push(
        f"{repository}:{tag}", stream=True, decode=True, auth_config=auth_config
    )

    for log in push_logs:
        if "error" in log:
            error_msg = log["error"]
            raise RuntimeError(f"Docker push failed: {error_msg}")
        # Optional: print progress
        if "status" in log:
            print(log["status"])


def _get_docker_credentials_from_env() -> tuple[str, str]:
    if "DOCKER_USERNAME" not in os.environ or "DOCKER_PASSWORD" not in os.environ:
        raise ValueError(
            "Need to have set environment variable DOCKER_USERNAME and DOCKER_PASSWORD!"
        )
    return os.environ["DOCKER_USERNAME"], os.environ["DOCKER_PASSWORD"]


@nox.session(name="build-docker-image-from-latest-gh-release", python=False)
def build_docker_image_from_latest_gh_release(session: nox.Session):
    """
    Builds a docker image for given Docker repository, docker tag (including the architecture)
    and base image name of the Ubuntu image (e.g. ubuntu:24.04)
    After building the image. the nox task verifies that `exaslpm` can be executed within the image
    and then pushes the image to DockerHub.
    """
    p = ArgumentParser(
        usage='nox -s build-docker-image-from-latest-gh-release -- --base-img "ubuntu:24.04" --repository "exasol/slc_base --complete-docker-tag "24.04-arm"',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--base-img")
    p.add_argument("--repository")
    p.add_argument("--complete-docker-tag")

    args = p.parse_args(session.posargs)
    base_img = args.base_img
    complete_docker_tag = args.complete_docker_tag
    repository = args.repository

    docker_client = docker.from_env()
    current_platform = _current_platform_cfg(session)
    latest_release = _get_latest_gh_release(session)

    with TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        binary_name = f"exaslpm_linux_{current_platform.docker_tag_suffix}"
        url = f"https://github.com/exasol/script-languages-package-management/releases/download/{latest_release}/{binary_name}"
        # Read the binary all at once. Size is ~25MB, which is not an issue.
        response = requests.get(url)
        response.raise_for_status()

        exaslpm_path = tmp_path / "exaslpm"

        if response.status_code == 200:
            with open(exaslpm_path, "wb") as f:
                f.write(response.content)
        exaslpm_path.chmod(exaslpm_path.stat().st_mode | stat.S_IEXEC)
        dockerfile_path = tmp_path / "Dockerfile"

        exaslpm_target_path = "/opt/bin"

        dockerfile_content = cleandoc(f"""
        FROM {base_img}
        COPY exaslpm {exaslpm_target_path}/
        ENV PATH="${{PATH}}:{exaslpm_target_path}"
        ENV EXASLPM={exaslpm_target_path}/exaslpm
        """)

        dockerfile_path.write_text(dockerfile_content)

        docker_client.images.build(
            path=str(tmp_dir), tag=f"{repository}:{complete_docker_tag}"
        )
    # Test exaslpm before we push the image to DockerHub
    session.log("Checking exaslpm in new docker image.")
    _run_exaslpm_in_docker_container(
        "Running exaslpm with absolute path using new docker image",
        [f"{exaslpm_target_path}/exaslpm", "--help"],
        complete_docker_tag,
        repository,
        session,
    )
    _run_exaslpm_in_docker_container(
        "Running exaslpm with env variable using new docker image",
        ["bash", "-c", "$EXASLPM --help"],
        complete_docker_tag,
        repository,
        session,
    )
    _run_exaslpm_in_docker_container(
        "Running exaslpm using $PATH in bash using new docker image",
        ["bash", "-c", "exaslpm --help"],
        complete_docker_tag,
        repository,
        session,
    )

    docker_user, docker_pwd = _get_docker_credentials_from_env()
    auth_config = {
        "username": docker_user,
        "password": docker_pwd,
    }
    session.log("Pushing new image to Docker Hub.")
    _push_image_safe(
        docker_client, repository, complete_docker_tag, auth_config=auth_config
    )


def _run_exaslpm_in_docker_container(
        run_message: str,
        docker_args: list[str],
        complete_docker_tag,
        repository,
        session: Session,
):
    # Test exaslpm env variable before we push the image to DockerHub
    session.log(run_message)
    exaslpm_help_string = session.run(
        "docker",
        "run",
        f"{repository}:{complete_docker_tag}",
        *docker_args,
        silent=True,
    )
    if (
            not exaslpm_help_string
            or "EXASLPM - Exasol Script Languages Package Management"
            not in exaslpm_help_string
    ):
        session.error(
            f"{run_message} did not succeed. \noutput:\n'{exaslpm_help_string}'"
        )

    session.log(f"{run_message} succeeded.\noutput:\n'{exaslpm_help_string}'")


@nox.session(name="build-docker-manifests", python=False)
def build_docker_manifests(session: nox.Session):
    """
    Creates a docker manifest which includes all supported architectures.
    With that, a client can pull the architecture agnostic docker tag (e.g. exaslpm-ubuntu-22.04) and DockerHub
    will return the correct image for the architecture, the client runs on.
    """

    p = ArgumentParser(
        usage='nox -s build-docker-manifests -- --repository "exasol/slc_base"',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--repository")
    args = p.parse_args(session.posargs)
    repository = args.repository

    if "DOCKER_USERNAME" not in os.environ or "DOCKER_PASSWORD" not in os.environ:
        raise ValueError(
            "Need to have set environment variable DOCKER_USERNAME and DOCKER_PASSWORD!"
        )
    user, password = _get_docker_credentials_from_env()
    subprocess.run(
        ["docker", "login", "-u", user, "--password-stdin"],
        input=(password + "\n").encode(),
        check=True,
    )

    # Create a manifest for every supported Ubuntu version, e.g.
    #           docker manifest create exasol/script-languages-container:exaslpm-ubuntu-22.04 \
    #             --amend exasol/script-languages-container:exaslpm-ubuntu-22.04-arm64 \
    #             --amend exasol/script-languages-container:exaslpm-ubuntu-22.04-x86_64
    #           docker manifest push exasol/script-languages-container:exaslpm-ubuntu-22.04
    for ubuntu_version in PROJECT_CONFIG.supported_ubuntu_versions:
        manifest_tag = f"{_build_docker_prefix_tag()}-{ubuntu_version}"
        cmd = ["docker", "manifest", "create", f"{repository}:{manifest_tag}"]

        for platform in PROJECT_CONFIG.supported_platforms:
            complete_docker_tag = _build_docker_img_tag(
                ubuntu_version, platform.docker_tag_suffix
            )
            cmd.extend(["--amend", f"{repository}:{complete_docker_tag}"])

        session.run(*cmd)
        session.run("docker", "manifest", "push", f"{repository}:{manifest_tag}")
