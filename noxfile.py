import argparse
import json
import os
import shutil
from argparse import ArgumentParser
from pathlib import Path

import nox
import PyInstaller.__main__

from noxconfig import (
    PROJECT_CONFIG,
)

# imports all nox task provided by the toolbox
from exasol.toolbox.nox.tasks import *


# default actions to be run if nothing is explicitly specified with the -s option
nox.options.sessions = ["project:fix"]

ROOT = Path(__file__).parent


@nox.session(name="build-standalone-binary", python=False)
def build_standalone_binary(session: nox.Session):
    script_path = str(ROOT / "exasol" / "exaslpm" / "main.py")

    p = ArgumentParser(
        usage='nox -s build-standalone-binary -- --executable-name "exaslpm"',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--executable-name")
    p.add_argument("--cleanup", action="store_true", help="Remove temporary files")
    args = p.parse_args(session.posargs)
    exe_name = args.executable_name

    if not bool(exe_name):
        session.error("PyInstaller needs a valid executable-name")
    else:
        old_cwd = os.getcwd()
        try:
            os.chdir(ROOT)
            options = [
                script_path,
                "--onefile",  # As a single exe file
                f"--name={exe_name}",  # Name of the executable
            ]
            PyInstaller.__main__.run(options)
            print(f"PyInstaller completed building {exe_name}")

            if args.cleanup:
                spec_file_path = Path() / f"{exe_name}.spec"
                if spec_file_path.exists():
                    spec_file_path.unlink()
                else:
                    session.warn(f"Expected spec file '{spec_file_path}' doesn't exist")
                build_path = ROOT / "build" / exe_name
                if build_path.exists():
                    shutil.rmtree(str(build_path))
                else:
                    session.warn(
                        f"Expected temporary build path '{build_path}' doesn't exist"
                    )
        finally:
            os.chdir(old_cwd)

@nox.session(name="matrix:python-platform", python=False)
def matrix_python_platform(session: nox.Session):
    from exasol.toolbox.nox._ci import _python_matrix
    d = _python_matrix(PROJECT_CONFIG)
    platforms = ["ubuntu-24.04", "ubuntu-24.04-arm"]
    d["platforms"] = platforms
    print(json.dumps(d))

