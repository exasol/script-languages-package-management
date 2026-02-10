import stat
from pathlib import Path

from exasol.exaslpm.pkg_mgmt.install_bazel import install_bazel
from test.unit.pkg_mgmt.utils import _named_params
from unittest.mock import (
    call,
)

import pytest

from exasol.exaslpm.model.package_file_config import (
    AptPackages,
    BuildStep,
    Micromamba,
    Phase,
    Tools, Bazel,
)
from exasol.exaslpm.pkg_mgmt.constants import MICROMAMBA_PATH
from exasol.exaslpm.pkg_mgmt.install_micromamba import install_micromamba


def test_install_bazel_empty_no_history(context_mock):
    phase = Phase(name="phase-1", apt=AptPackages(packages=[]))
    install_bazel(phase, context_mock)

    assert context_mock.cmd_executor.mock_calls == []
    assert context_mock.file_downloader.mock.mock_calls == []


def _make_build_step(
    name: str,
    bazel_version: str,
) -> BuildStep:
    bazel = Bazel(
            version=bazel_version,
        )

    phase = Phase(
        name="phase-1",
        tools=Tools(bazel=bazel),
    )
    phases = [phase]
    build_step = BuildStep(name=name, phases=phases)
    return build_step

def test_install_micromamba(
    context_mock,
):

    build_step = _make_build_step(
        "build-step-1",
        "2.5.0",
    )

    phase = build_step.find_phase("phase-1")
    install_bazel(phase, context_mock)

    assert context_mock.file_downloader.mock.mock_calls == [
        call(
            url="https://github.com/bazelbuild/bazel/releases/download/2.5.0/bazel-2.5.0-linux-x86_64",
            timeout_in_seconds=120
        )
    ]

    assert context_mock.file_access.chmod.mock_calls == [
        call(Path("path/to/file"), stat.S_IXUSR)
    ]
