import argparse
import json
import os
import shutil
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
    print(json.dumps(PROJECT_CONFIG.runners))


@nox.session(name="matrix:docker-image-config", python=False)
def docker_image_config(session: nox.Session):
    print(json.dumps({"include": PROJECT_CONFIG.docker_image_config}))


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


@nox.session(name="build-docker-image", python=False)
def build_docker_image(session: nox.Session):
    p = ArgumentParser(
        usage='nox -s build-docker-image -- --base-img "ubuntu:24.04" --repository "exasol/slc_base --tag "24.04"',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--base-img")
    p.add_argument("--repository")
    p.add_argument("--tag")
    args = p.parse_args(session.posargs)
    base_img = args.base_img
    tag = args.tag
    repository = args.repository
    #    _build_binary("exaslpm", True, session)

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

        docker_client.images.build(path=str(tmp_dir), tag=f"{repository}:{tag}")
    if "DOCKER_USERNAME" not in os.environ or "DOCKER_PASSWORD" not in os.environ:
        raise ValueError(
            "Need to have set environment variable DOCKER_USERNAME and DOCKER_PASSWORD!"
        )
    auth_config = {
        "username": os.environ["DOCKER_USERNAME"],
        "password": os.environ["DOCKER_PASSWORD"],
    }
    push_image_safe(docker_client, repository, tag, auth_config=auth_config)
