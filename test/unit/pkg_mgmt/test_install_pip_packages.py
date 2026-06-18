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
from exasol.exaslpm.pkg_mgmt.context.context import Context
from exasol.exaslpm.pkg_mgmt.context.temp_file_provider import TempFileProvider
from exasol.exaslpm.pkg_mgmt.install_pip_packages import install_pip_packages
from exasol.exaslpm.pkg_mgmt.search.search_cache import SearchCache


@pytest.fixture(params=[True, False], ids=["with_pip", "without_pip"])
def context_with_python_env(request, context_mock):
    with_pip = request.param
    phase_python_binary = Phase(
        name="phase-python-bin",
        tools=Tools(python_binary_path=Path("/usr/bin/test-python")),
    )
    phase_pip = Phase(name="phase-pip", tools=Tools(pip=Pip(version="25.5")))
    phases = [phase_python_binary, phase_pip] if with_pip else [phase_python_binary]
    context_mock.history_file_manager.build_steps = [
        BuildStep(name="prev-build-step", phases=phases)
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
            call.execute(["apt-get", "-y", "update"], env=None),
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
                env=None,
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
                ["apt-get", "purge", "-y", "build-essential", "pkg-config"], env=None
            ),
            call.execute().print_results(),
            call.execute().return_code(),
            call.execute(["apt-get", "-y", "autoremove"], env=None),
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
                env=None,
            ),
            call.execute().print_results(),
            call.execute().return_code(),
        ]
        + _build_calls_uninstall_build_tools_ephemerally(
            with_install_build_tools_ephemerally
        )
    )
    assert context_with_python_env.cmd_executor.mock_calls == expected_calls

    assert tmp_file_provider.result == (
        "numpy == 1.2.3\n" + "requests == 2.25.1\n"
        "exasol-db-api @ https://exasol.org/exasol-db-api\n"
    )

    assert context_with_python_env.file_access.check_binary.mock_calls == [
        call(Path("/usr/bin/test-python"))
    ]


@pytest.fixture
def context_with_python_env_and_temp_file(context_with_python_env):
    return Context(
        cmd_logger=context_with_python_env.cmd_logger,
        cmd_executor=context_with_python_env.cmd_executor,
        history_file_manager=context_with_python_env.history_file_manager,
        file_access=context_with_python_env.file_access,
        file_downloader=context_with_python_env.file_downloader,
        temp_file_provider=TempFileProvider(),
    )


def test_install_pip_packages_prints_package_file_if_exception(
    context_with_python_env_and_temp_file,
):

    context_with_python_env_and_temp_file.cmd_executor.execute.side_effect = Exception(
        "An error occurred"
    )

    pkgs = [
        PipPackage(name="numpy", version="== 1.2.3"),
    ]
    phase_one = Phase(
        name="phase-1",
        pip=PipPackages(
            packages=pkgs,
            install_build_tools_ephemerally=False,
        ),
    )
    build_step = BuildStep(name="build-step-1", phases=[phase_one])
    search_cache = SearchCache(
        build_step, phase_one, context_with_python_env_and_temp_file
    )
    with pytest.raises(Exception, match="An error occurred"):
        install_pip_packages(
            search_cache, phase_one, context_with_python_env_and_temp_file
        )
    assert context_with_python_env_and_temp_file.cmd_logger.err.mock_calls == [
        call("Failed while installing pip packages: \nnumpy == 1.2.3\n")
    ]
