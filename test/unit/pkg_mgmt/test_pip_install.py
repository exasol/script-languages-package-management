from pathlib import Path
from test.unit.pkg_mgmt.utils import _named_params
from unittest.mock import (
    call,
)

import pytest

from exasol.exaslpm.model.package_file_config import (
    AptPackages,
    BuildStep,
    Phase,
    Pip,
    Tools,
)
from exasol.exaslpm.pkg_mgmt.install_pip import install_pip
from exasol.exaslpm.pkg_mgmt.search.search_cache import SearchCache


def test_install_pip_empty_no_history(context_mock):
    phase = Phase(name="phase-1", apt=AptPackages(packages=[]))
    build_step = BuildStep(name="build-step-1", phases=[phase])
    install_pip(build_step, phase, context_mock)

    assert context_mock.cmd_executor.mock_calls == []
    assert context_mock.file_downloader.mock.mock_calls == []


def _make_build_step(
    name: str,
    pip_version: str,
    needs_break_system_packages_option: bool,
    enable_binary: bool = False,
) -> BuildStep:
    phase_one = Phase(
        name="phase-1", tools=Tools(python_binary_path=Path("/some/path"))
    )
    phase_two = Phase(
        name="phase-2",
        tools=Tools(
            pip=Pip(
                version=pip_version,
                needs_break_system_packages=needs_break_system_packages_option,
            )
        ),
    )
    phases = []
    if enable_binary:
        phases.append(phase_one)
    phases.append(phase_two)
    build_step = BuildStep(name=name, phases=phases)
    return build_step


@pytest.mark.parametrize(
    "pip_version, needs_break_system_packages_option, python_binary_in_history",
    [
        pytest.param(
            *_named_params(
                pip_version="23.3",
                needs_break_system_packages_option=True,
                python_binary_in_history=True,
            ),
            id="New pip, Python binary in history",
        ),
        pytest.param(
            *_named_params(
                pip_version="23.3",
                needs_break_system_packages_option=True,
                python_binary_in_history=False,
            ),
            id="New pip, Python binary in current build-step",
        ),
        pytest.param(
            *_named_params(
                pip_version="25.5",
                needs_break_system_packages_option=False,
                python_binary_in_history=True,
            ),
            id="Old pip, Python binary in history",
        ),
        pytest.param(
            *_named_params(
                pip_version="25.5",
                needs_break_system_packages_option=False,
                python_binary_in_history=False,
            ),
            id="Old pip, Python binary in current build-step",
        ),
    ],
)
def test_install_pip(
    pip_version,
    needs_break_system_packages_option,
    python_binary_in_history,
    context_mock,
):

    context_mock.history_file_manager.build_steps = [
        _make_build_step(
            "build-step-1",
            pip_version,
            enable_binary=python_binary_in_history,
            needs_break_system_packages_option=needs_break_system_packages_option,
        )
    ]
    build_step = _make_build_step(
        "build-step-2",
        pip_version,
        enable_binary=not python_binary_in_history,
        needs_break_system_packages_option=needs_break_system_packages_option,
    )

    phase = build_step.find_phase("phase-2")
    search_cache = SearchCache(build_step, phase, context_mock)
    install_pip(search_cache, phase, context_mock)

    expected_pip_script_arguments = [
        "/some/path",
        str(context_mock.file_downloader.mock_path),
        f"pip == {pip_version}",
    ]
    if needs_break_system_packages_option:
        expected_pip_script_arguments.append("--break-system-packages")

    assert context_mock.cmd_executor.mock_calls == [
        call.execute(expected_pip_script_arguments),
        call.execute().print_results(),
        call.execute().return_code(),
        call.execute(["bash", "-c", 'rm -rf "$(/some/path -m pip cache dir)"']),
        call.execute().print_results(),
        call.execute().return_code(),
    ]

    assert context_mock.file_downloader.mock.mock_calls == [
        call(url="https://bootstrap.pypa.io/get-pip.py")
    ]
