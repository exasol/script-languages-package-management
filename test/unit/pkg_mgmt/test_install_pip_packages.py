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


def test_install_apt_packages(context_with_python_env):
    tmp_file_provider = context_with_python_env.temp_file_provider

    pkgs = [
        PipPackage(name="numpy", version="1.2.3"),
        PipPackage(name="requests", version="2.25.1"),
    ]

    phase_one = Phase(name="phase-1", pip=PipPackages(packages=pkgs))
    build_step = BuildStep(name="build-step-1", phases=[phase_one])
    search_cache = SearchCache(build_step, phase_one, context_with_python_env)
    install_pip_packages(search_cache, phase_one, context_with_python_env)
    assert context_with_python_env.cmd_executor.mock_calls == [
        call.execute(
            [
                "/usr/bin/test-python",
                "-m",
                "pip",
                "install",
                "-r",
                str(tmp_file_provider.path),
            ]
        ),
        call.execute().print_results(),
        call.execute().return_code(),
    ]

    assert tmp_file_provider.result == "numpy==1.2.3\nrequests==2.25.1\n"
