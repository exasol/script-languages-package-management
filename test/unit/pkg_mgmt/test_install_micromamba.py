from pathlib import Path
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
    Tools,
)
from exasol.exaslpm.pkg_mgmt.constants import MICROMAMBA_PATH
from exasol.exaslpm.pkg_mgmt.install_micromamba import install_micromamba


def test_install_pip_empty_no_history(context_mock):
    phase = Phase(name="phase-1", apt=AptPackages(packages=[]))
    install_micromamba(phase, context_mock)

    assert context_mock.cmd_executor.mock_calls == []
    assert context_mock.file_downloader.mock.mock_calls == []


def _make_build_step(
    name: str,
    micromamba_version: str,
    root_prefix: Path | None,
) -> BuildStep:
    micromamba = (
        Micromamba(
            version=micromamba_version,
            root_prefix=root_prefix,
        )
        if root_prefix
        else Micromamba(version=micromamba_version)
    )

    phase = Phase(
        name="phase-1",
        tools=Tools(micromamba=micromamba),
    )
    phases = [phase]
    build_step = BuildStep(name=name, phases=phases)
    return build_step


@pytest.mark.parametrize(
    "root_prefix, expected_micromamba_path",
    [
        _named_params(root_prefix=None, expected_micromamba_path="/opt/conda"),
        _named_params(
            root_prefix=Path("/micromamba/path"),
            expected_micromamba_path="/micromamba/path",
        ),
    ],
)
def test_install_micromamba(
    root_prefix,
    expected_micromamba_path,
    context_mock,
):

    build_step = _make_build_step(
        "build-step-1",
        "2.5.0",
        root_prefix=root_prefix,
    )

    phase = build_step.find_phase("phase-1")
    install_micromamba(phase, context_mock)

    expected_micromamba_script_arguments = [
        "tar",
        "-xvf",
        str(context_mock.file_downloader.mock_path),
        "-C",
        "/",
        "bin/micromamba",
    ]

    expected_micromamba_create_env_arguments = [
        str(MICROMAMBA_PATH),
        "create",
        "-n",
        "base",
    ]

    assert context_mock.cmd_executor.mock_calls == [
        call.execute(
            expected_micromamba_script_arguments,
            None,
        ),
        call.execute().print_results(),
        call.execute().return_code(),
        call.execute(
            expected_micromamba_create_env_arguments,
            {"MAMBA_ROOT_PREFIX": expected_micromamba_path},
        ),
        call.execute().print_results(),
        call.execute().return_code(),
    ]

    assert context_mock.file_downloader.mock.mock_calls == [
        call(url="https://micro.mamba.pm/api/micromamba/linux-64/2.5.0")
    ]
