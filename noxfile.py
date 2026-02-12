import argparse
import json
import os
import shutil
import subprocess
from argparse import ArgumentParser
from inspect import cleandoc
from pathlib import Path
from tempfile import TemporaryDirectory

import docker
import nox
import PyInstaller.__main__

# imports all nox task provided by the toolbox
from exasol.toolbox.nox.tasks import *

from noxconfig import (
    PROJECT_CONFIG,
)

# default actions to be run if nothing is explicitly specified with the -s option
nox.options.sessions = ["format:fix"]


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


@nox.session(name="matrix:runner", python=False)
def matrix_runner(session: nox.Session):
    runners = [
        f"ubuntu-{ubuntu_version}{platform.runner_suffix}"
        for platform in PROJECT_CONFIG.supported_platforms
        for ubuntu_version in PROJECT_CONFIG.supported_ubuntu_versions
    ]
    print(json.dumps(runners))


def _build_docker_tag(tag: str, docker_tag_suffix: str):
    return f"{tag}-{docker_tag_suffix}"


@nox.session(name="matrix:docker-image-config", python=False)
def docker_image_config(session: nox.Session):
    def _build_docker_build_image_config(
        runner_suffix: str, ubuntu_version: str, docker_tag_suffix: str
    ):
        return {
            "runner": f"ubuntu-{ubuntu_version}{runner_suffix}",
            "base_img": f"ubuntu:{ubuntu_version}",
            "complete_docker_tag": _build_docker_tag(ubuntu_version, docker_tag_suffix),
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


def push_image_safe(client, repository, tag, auth_config):
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


@nox.session(name="build-docker-image", python=False)
def build_docker_image(session: nox.Session):
    p = ArgumentParser(
        usage='nox -s build-docker-image -- --base-img "ubuntu:24.04" --repository "exasol/slc_base --complete-docker-tag "24.04-arm"',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--base-img")
    p.add_argument("--repository")
    p.add_argument("--complete-docker-tag")

    args = p.parse_args(session.posargs)
    base_img = args.base_img
    complete_docker_tag = args.complete_docker_tag
    repository = args.repository
    _build_binary("exaslpm", True, session)

    docker_client = docker.from_env()
    with TemporaryDirectory() as tmp_dir:
        shutil.copy(PROJECT_CONFIG.root_path / "dist" / "exaslpm", str(tmp_dir))
        dockerfile_path = Path(tmp_dir) / "Dockerfile"

        dockerfile_content = cleandoc(
            f"""
        FROM {base_img}
        COPY exaslpm /usr/local/bin/
        """
        )

        dockerfile_path.write_text(dockerfile_content)

        docker_client.images.build(
            path=str(tmp_dir), tag=f"{repository}:{complete_docker_tag}"
        )
    docker_user, docker_pwd = _get_docker_credentials_from_env()
    auth_config = {
        "username": docker_user,
        "password": docker_pwd,
    }
    # Test exaslpm before we push the image to Dockerhub
    session.log("Checking exaslpm in new docker image.")
    exaslpm_help_string = session.run(
        "docker",
        "run",
        f"{repository}:{complete_docker_tag}",
        "exaslpm",
        "--help",
        silent=True,
    )
    if (
        not exaslpm_help_string
        or "EXASLPM - Exasol Script Languages Package Management"
        not in exaslpm_help_string
    ):
        raise RuntimeError(
            f"Running exaslpm using new docker image did not succeed. \noutput:\n'{exaslpm_help_string}'"
        )
    session.log(f"Running exaslpm succeeded.\noutput:\n'{exaslpm_help_string}'")
    session.log(f"Pushing now new image to Docker Hub.")
    push_image_safe(
        docker_client, repository, complete_docker_tag, auth_config=auth_config
    )


@nox.session(name="build-docker-manifests", python=False)
def build_docker_manifests(session: nox.Session):

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
    #           docker manifest create exasol/script-languages-container:22.04 \
    #             --amend exasol/script-languages-container:22.04-aarch64 \
    #             --amend exasol/script-languages-container:22.04-x86_64
    #           docker manifest push exasol/script-languages-container:22.04
    for ubuntu_version in PROJECT_CONFIG.supported_ubuntu_versions:
        cmd = ["docker", "manifest", "create", f"{repository}:{ubuntu_version}"]

        for platform in PROJECT_CONFIG.supported_platforms:
            complete_docker_tag = _build_docker_tag(
                ubuntu_version, platform.docker_tag_suffix
            )
            cmd.extend(["--amend", f"{repository}:{complete_docker_tag}"])

        session.run(*cmd)
        session.run("docker", "manifest", "push", f"{repository}:{ubuntu_version}")
