from pathlib import Path
from unittest.mock import (
    call,
)

import pytest

from exasol.exaslpm.model.package_file_config import (
    BuildStep,
    CondaBinary,
    CondaPackage,
    CondaPackages,
    Micromamba,
    Phase,
    Tools,
)
from exasol.exaslpm.pkg_mgmt.constants import MICROMAMBA_PATH
from exasol.exaslpm.pkg_mgmt.install_conda_packages import install_conda_packages
from exasol.exaslpm.pkg_mgmt.search.search_cache import SearchCache

ROOT_PREFIX = Path("/some/root/prefix")
MAMBA_BIN_PATH = Path("/some/mamba/path")
CONDA_BIN_PATH = Path("/some/conda/path")


@pytest.fixture
def context_with_conda_env(context_mock):
    phase_micromamba = Phase(
        name="micromamba",
        tools=Tools(micromamba=Micromamba(version="2.5.0", root_prefix=ROOT_PREFIX)),
    )
    phase_mamba_binary = Phase(
        name="mamba-bin",
        tools=Tools(mamba_binary_path=MAMBA_BIN_PATH),
    )
    phase_conda_binary = Phase(
        name="conda-bin", tools=Tools(conda_binary_path=CONDA_BIN_PATH)
    )
    context_mock.history_file_manager.build_steps = [
        BuildStep(
            name="prev-build-step",
            phases=[phase_micromamba, phase_mamba_binary, phase_conda_binary],
        )
    ]
    return context_mock


@pytest.mark.parametrize(
    "conda_binary_type",
    [
        CondaBinary.Micromamba,
        CondaBinary.Mamba,
        CondaBinary.Conda,
    ],
)
def test_empty_packages(context_with_conda_env, conda_binary_type):
    phase_one = Phase(
        name="phase-1", conda=CondaPackages(packages=[], binary=conda_binary_type)
    )
    build_step = BuildStep(name="build-step-1", phases=[phase_one])
    search_cache = SearchCache(build_step, phase_one, context_with_conda_env)
    install_conda_packages(search_cache, phase_one, context_with_conda_env)

    assert context_with_conda_env.cmd_logger.mock_calls == [
        call.warn("Got an empty list of CondaPackages"),
    ]


@pytest.mark.parametrize(
    "conda_binary_type, expected_binary_path",
    [
        (CondaBinary.Micromamba, MICROMAMBA_PATH),
        (CondaBinary.Mamba, MAMBA_BIN_PATH),
        (CondaBinary.Conda, CONDA_BIN_PATH),
    ],
)
def test_install_conda_packages(
    context_with_conda_env, conda_binary_type, expected_binary_path
):
    tmp_file_provider = context_with_conda_env.temp_file_provider

    pkgs = [
        CondaPackage(name="numpy", version="1.2.3", channel="main"),
        CondaPackage(name="requests", version="2.25.*", build="something"),
    ]

    phase_one = Phase(
        name="phase-1",
        conda=CondaPackages(
            packages=pkgs,
            binary=conda_binary_type,
        ),
    )
    build_step = BuildStep(name="build-step-1", phases=[phase_one])
    search_cache = SearchCache(build_step, phase_one, context_with_conda_env)
    install_conda_packages(search_cache, phase_one, context_with_conda_env)
    expected_calls = [
        call.execute(
            [
                str(expected_binary_path),
                "install",
                "--yes",
                "--file",
                str(tmp_file_provider.path),
            ],
            {"MAMBA_ROOT_PREFIX": str(ROOT_PREFIX)},
        ),
        call.execute().print_results(),
        call.execute().return_code(),
        call.execute(
            [
                str(expected_binary_path),
                "clean",
                "--all",
                "--yes",
                "--index-cache",
                "--tarballs",
            ],
            {"MAMBA_ROOT_PREFIX": str(ROOT_PREFIX)},
        ),
        call.execute().print_results(),
        call.execute().return_code(),
        call.execute(["ldconfig"], None),
        call.execute().print_results(),
        call.execute().return_code(),
    ]
    assert context_with_conda_env.cmd_executor.mock_calls == expected_calls

    assert tmp_file_provider.result == (
        "main::numpy=1.2.3\n" "requests=2.25.*=something\n"
    )

    assert context_with_conda_env.binary_checker.check_binary.mock_calls == [
        call(expected_binary_path)
    ]
