from pathlib import Path
from unittest.mock import (
    call,
)

import pytest

from exasol.exaslpm.model.package_file_config import (
    BuildStep,
    Phase,
    Pip,
    PipPackage,
    PipPackages,
    Tools,
)
from exasol.exaslpm.pkg_mgmt.install_pip_packages import install_pip_packages
from exasol.exaslpm.pkg_mgmt.search.search_cache import SearchCache


@pytest.fixture
def context_with_python_env(context_mock):
    phase_python_binary = Phase(
        name="phase-python-bin",
        tools=Tools(python_binary_path=Path("/usr/bin/test-python")),
    )
    phase_pip = Phase(name="phase-pip", tools=Tools(pip=Pip(version="25.5")))
    context_mock.history_file_manager.build_steps = [
        BuildStep(name="prev-build-step", phases=[phase_python_binary, phase_pip])
    ]
    return context_mock


def test_empty_packages(context_with_python_env):
    phase_one = Phase(name="phase-1", pip=PipPackages(packages=[]))
    build_step = BuildStep(name="build-step-1", phases=[phase_one])
    search_cache = SearchCache(build_step, phase_one, context_with_python_env)
    install_pip_packages(search_cache, phase_one, context_with_python_env)

    assert context_with_python_env.cmd_logger.mock_calls == [
        call.warn("Got an empty list of pip packages"),
    ]


def _build_calls_install_build_tools_ephemerally(
    with_install_build_tools_ephemerally: bool,
):
    if with_install_build_tools_ephemerally:

        return [
            call.execute(["apt-get", "-y", "update"], None),
            call.execute().print_results(),
            call.execute().return_code(),
            call.execute(
                [
                    "apt-get",
                    "install",
                    "-y",
                    "--no-install-recommends",
                    "build-essential",
                    "pkg-config",
                ],
                None,
            ),
            call.execute().print_results(),
            call.execute().return_code(),
        ]
    else:
        return []


def _build_calls_uninstall_build_tools_ephemerally(
    with_install_build_tools_ephemerally: bool,
):
    if with_install_build_tools_ephemerally:

        return [
            call.execute(
                ["apt-get", "purge", "-y", "build-essential", "pkg-config"], None
            ),
            call.execute().print_results(),
            call.execute().return_code(),
            call.execute(["apt-get", "-y", "autoremove"], None),
            call.execute().print_results(),
            call.execute().return_code(),
        ]
    else:
        return []


@pytest.mark.parametrize(
    "with_install_build_tools_ephemerally",
    [True, False],
)
def test_install_pip_packages(
    context_with_python_env, with_install_build_tools_ephemerally
):
    tmp_file_provider = context_with_python_env.temp_file_provider

    pkgs = [
        PipPackage(name="numpy", version="== 1.2.3"),
        PipPackage(name="requests", version="== 2.25.1"),
        PipPackage(name="exasol-db-api", url="https://exasol.org/exasol-db-api"),
    ]

    phase_one = Phase(
        name="phase-1",
        pip=PipPackages(
            packages=pkgs,
            install_build_tools_ephemerally=with_install_build_tools_ephemerally,
        ),
    )
    build_step = BuildStep(name="build-step-1", phases=[phase_one])
    search_cache = SearchCache(build_step, phase_one, context_with_python_env)
    install_pip_packages(search_cache, phase_one, context_with_python_env)
    expected_calls = (
        _build_calls_install_build_tools_ephemerally(
            with_install_build_tools_ephemerally
        )
        + [
            call.execute(
                [
                    "/usr/bin/test-python",
                    "-m",
                    "pip",
                    "install",
                    "-r",
                    str(tmp_file_provider.path),
                ],
                None,
            ),
            call.execute().print_results(),
            call.execute().return_code(),
        ]
        + _build_calls_uninstall_build_tools_ephemerally(
            with_install_build_tools_ephemerally
        )
    )
    assert context_with_python_env.cmd_executor.mock_calls == expected_calls

    assert (
        tmp_file_provider.result
        == "numpy == 1.2.3\nrequests == 2.25.1\nhttps://exasol.org/exasol-db-api\n"
    )
