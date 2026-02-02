import contextlib
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import (
    ANY,
    MagicMock,
    call,
)

import pytest
from _pytest.monkeypatch import MonkeyPatch

import exasol.exaslpm.pkg_mgmt.install_packages as install_packages
from exasol.exaslpm.model.package_file_config import (
    AptPackage,
    AptPackages,
    BuildStep,
    Micromamba,
    PackageFile,
    Phase,
    Pip,
    Tools,
)
from exasol.exaslpm.model.serialization import to_yaml_str


@pytest.fixture
def mock_install_apt_packages(monkeypatch: MonkeyPatch) -> MagicMock:
    mock_function_to_mock = MagicMock()
    monkeypatch.setattr(install_packages, "install_apt_packages", mock_function_to_mock)
    return mock_function_to_mock


@pytest.fixture
def mock_install_pip(monkeypatch: MonkeyPatch) -> MagicMock:
    mock_function_to_mock = MagicMock()
    monkeypatch.setattr(install_packages, "install_pip", mock_function_to_mock)
    return mock_function_to_mock


@pytest.fixture
def mock_install_micromamba(monkeypatch: MonkeyPatch) -> MagicMock:
    mock_function_to_mock = MagicMock()
    monkeypatch.setattr(install_packages, "install_micromamba", mock_function_to_mock)
    return mock_function_to_mock


@dataclass
class ToolsSettings:
    python_binary_path: bool = False
    pip: Pip | None = None
    micromamba: Micromamba | None = None

    @staticmethod
    def disabled():
        return ToolsSettings()

    @property
    def is_disabled(self) -> bool:
        return not any([self.python_binary_path, self.pip, self.micromamba])


def _build_apt_package(
    enable_apt: bool = False, apt_package=AptPackage(name="curl", version="1.2.3")
) -> AptPackages | None:
    return AptPackages(packages=[apt_package]) if enable_apt else None


def _build_tools_package(
    tools_settings: ToolsSettings = ToolsSettings.disabled(),
) -> Tools | None:
    return (
        Tools(
            python_binary_path=(
                Path("/some/path") if tools_settings.python_binary_path else None
            ),
            pip=tools_settings.pip,
            micromamba=tools_settings.micromamba,
        )
        if not tools_settings.is_disabled
        else None
    )


def _build_phase(
    phase_name: str = "phase-1",
    enable_apt: bool = False,
    tools_settings: ToolsSettings = ToolsSettings.disabled(),
) -> Phase:
    return Phase(
        name=phase_name,
        apt=_build_apt_package(enable_apt=enable_apt),
        tools=_build_tools_package(tools_settings=tools_settings),
    )


def _build_package_config(phases: list[Phase]) -> PackageFile:
    return PackageFile(build_steps=[BuildStep(name="build-step-1", phases=phases)])


@pytest.fixture
def package_file(tmp_path):
    package_file_path = tmp_path / "package_file.yml"

    @contextlib.contextmanager
    def prepare(package_file: PackageFile):
        content = to_yaml_str(package_file)
        package_file_path.write_text(content)
        yield package_file_path

    return prepare


def test_install_packages_history_manager(
    context_mock, mock_install_apt_packages, package_file
):
    package_file_config = _build_package_config(
        [_build_phase(tools_settings=ToolsSettings(python_binary_path=True))]
    )

    with package_file(package_file_config) as package_file_path:
        install_packages.package_install(
            package_file=package_file_path,
            build_step_name="build-step-1",
            context=context_mock,
        )
    assert context_mock.history_file_manager.mock.mock_calls == [
        call.raise_if_build_step_exists("build-step-1"),
        call.add_build_step_to_history(
            package_file_config.find_build_step("build-step-1")
        ),
    ]


def test_install_packages_apt_empty(
    context_mock, mock_install_apt_packages, package_file
):
    package_file_config = _build_package_config(
        [_build_phase(tools_settings=ToolsSettings(python_binary_path=True))]
    )

    with package_file(package_file_config) as package_file_path:
        install_packages.package_install(
            package_file=package_file_path,
            build_step_name="build-step-1",
            context=context_mock,
        )
    assert mock_install_apt_packages.mock_calls == []


def test_install_packages_apt(context_mock, mock_install_apt_packages, package_file):
    package_file_config = _build_package_config([_build_phase(enable_apt=True)])
    with package_file(package_file_config) as package_file_path:
        install_packages.package_install(
            package_file=package_file_path,
            build_step_name="build-step-1",
            context=context_mock,
        )
    assert mock_install_apt_packages.mock_calls == [
        call(
            package_file_config.find_build_step("build-step-1")
            .find_phase("phase-1")
            .apt,
            context_mock,
        ),
    ]


def test_install_pip(context_mock, mock_install_pip, package_file):
    phase_python_binary = _build_phase(
        phase_name="phase-1", tools_settings=ToolsSettings(python_binary_path=True)
    )
    phase_pip = _build_phase(
        phase_name="phase-2", tools_settings=ToolsSettings(pip=Pip(version="25.5"))
    )
    package_file_config = _build_package_config([phase_python_binary, phase_pip])
    with package_file(package_file_config) as package_file_path:
        install_packages.package_install(
            package_file=package_file_path,
            build_step_name="build-step-1",
            context=context_mock,
        )
    assert mock_install_pip.mock_calls == [call(ANY, phase_pip, context_mock)]


def test_install_micromamba(context_mock, mock_install_micromamba, package_file):
    phase_micromamba = _build_phase(
        phase_name="phase-1",
        tools_settings=ToolsSettings(micromamba=Micromamba(version="2.5.0")),
    )
    package_file_config = _build_package_config([phase_micromamba])
    with package_file(package_file_config) as package_file_path:
        install_packages.package_install(
            package_file=package_file_path,
            build_step_name="build-step-1",
            context=context_mock,
        )
    assert mock_install_micromamba.mock_calls == [
        call(ANY, phase_micromamba, context_mock)
    ]


def test_install_packages_multiple(
    context_mock,
    mock_install_apt_packages,
    mock_install_pip,
    mock_install_micromamba,
    package_file,
):
    phases = [
        Phase(
            name="phase-1",
            apt=_build_apt_package(enable_apt=True),
        ),
        Phase(
            name="phase-2",
            tools=_build_tools_package(
                tools_settings=ToolsSettings(python_binary_path=True)
            ),
        ),
        Phase(
            name="phase-3",
            tools=_build_tools_package(
                tools_settings=ToolsSettings(pip=Pip(version="25.5"))
            ),
        ),
        Phase(
            name="phase-4",
            apt=_build_apt_package(
                enable_apt=True, apt_package=AptPackage(name="wget", version="1.2.3")
            ),
        ),
        Phase(
            name="phase-5",
            tools=_build_tools_package(
                tools_settings=ToolsSettings(micromamba=Micromamba(version="2.5.0"))
            ),
        ),
    ]
    package_file_config = _build_package_config(phases)
    with package_file(package_file_config) as package_file_path:
        install_packages.package_install(
            package_file=package_file_path,
            build_step_name="build-step-1",
            context=context_mock,
        )
    assert mock_install_apt_packages.mock_calls == [
        call(phases[0].apt, context_mock),
        call(phases[3].apt, context_mock),
    ]
    assert mock_install_pip.mock_calls == [call(ANY, phases[2], context_mock)]
    assert mock_install_micromamba.mock_calls == [call(ANY, phases[4], context_mock)]
