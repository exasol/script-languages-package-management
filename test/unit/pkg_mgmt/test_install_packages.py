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
    AptRepo,
    BuildStep,
    CondaPackage,
    CondaPackages,
    Micromamba,
    PackageFile,
    Phase,
    Pip,
    PipPackage,
    PipPackages,
    RPackage,
    RPackages,
    Tools, Bazel,
)
from exasol.exaslpm.model.serialization import to_yaml_str


@pytest.fixture
def mock_install_apt_packages(monkeypatch: MonkeyPatch) -> MagicMock:
    mock_function_to_mock = MagicMock()
    monkeypatch.setattr(install_packages, "install_apt_packages", mock_function_to_mock)
    return mock_function_to_mock


@pytest.fixture
def mock_install_apt_repos(monkeypatch: MonkeyPatch) -> MagicMock:
    mock_function_to_mock = MagicMock()
    monkeypatch.setattr(install_packages, "install_apt_repos", mock_function_to_mock)
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


@pytest.fixture
def mock_install_pip_packages(monkeypatch: MonkeyPatch) -> MagicMock:
    mock_function_to_mock = MagicMock()
    monkeypatch.setattr(install_packages, "install_pip_packages", mock_function_to_mock)
    return mock_function_to_mock


@pytest.fixture
def mock_install_micromamba(monkeypatch: MonkeyPatch) -> MagicMock:
    mock_function_to_mock = MagicMock()
    monkeypatch.setattr(install_packages, "install_micromamba", mock_function_to_mock)
    return mock_function_to_mock


@pytest.fixture
def mock_install_conda_packages(monkeypatch: MonkeyPatch) -> MagicMock:
    mock_function_to_mock = MagicMock()
    monkeypatch.setattr(
        install_packages, "install_conda_packages", mock_function_to_mock
    )
    return mock_function_to_mock


@pytest.fixture
def mock_install_r_packages(monkeypatch: MonkeyPatch) -> MagicMock:
    mock_function_to_mock = MagicMock()
    monkeypatch.setattr(install_packages, "install_r_packages", mock_function_to_mock)
    return mock_function_to_mock

@pytest.fixture
def mock_install_bazel(monkeypatch: MonkeyPatch) -> MagicMock:
    mock_function_to_mock = MagicMock()
    monkeypatch.setattr(install_packages, "install_bazel", mock_function_to_mock)
    return mock_function_to_mock


@dataclass
class ToolsSettings:
    python_binary_path: bool = False
    pip: Pip | None = None
    micromamba: Micromamba | None = None
    bazel: Bazel | None = None

    @staticmethod
    def disabled():
        return ToolsSettings()

    @property
    def is_disabled(self) -> bool:
        return not any([self.python_binary_path, self.pip, self.micromamba, self.bazel])


def _build_apt_package(
    enable_apt: bool = False, apt_package=AptPackage(name="curl", version="1.2.3")
) -> AptPackages | None:
    return AptPackages(packages=[apt_package]) if enable_apt else None


def _build_apt_rep_package(enable_apt_repo: bool = False) -> AptPackages | None:
    return (
        AptPackages(
            packages=[],
            repos={
                "some_ppa": AptRepo(
                    entry="deb some_ppa",
                    key_url="https://some.key.server",
                    out_file="some_ppa.list",
                )
            },
        )
        if enable_apt_repo
        else None
    )


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
            bazel=tools_settings.bazel,
        )
        if not tools_settings.is_disabled
        else None
    )


def _build_pip_packages(enable_pip_packages: bool = False) -> CondaPackages | None:
    return (
        PipPackages(packages=[PipPackage(name="numpy", version="1.2.3")])
        if enable_pip_packages
        else None
    )


def _build_conda_packages(enable_conda_packages: bool = False) -> CondaPackages | None:
    return (
        CondaPackages(packages=[CondaPackage(name="numpy", version="1.2.3")])
        if enable_conda_packages
        else None
    )


def _build_r_packages(enable_r_packages: bool = False) -> RPackages | None:
    return (
        RPackages(
            packages=[
                RPackage(name="tidyr", version="1.3.2"),
            ]
        )
        if enable_r_packages
        else None
    )


def _build_phase(
    phase_name: str = "phase-1",
    enable_apt: bool = False,
    enable_apt_repo: bool = False,
    tools_settings: ToolsSettings = ToolsSettings.disabled(),
    enable_pip_packages: bool = False,
    enable_conda_packages: bool = False,
    enable_r_packages: bool = False,
) -> Phase:
    return Phase(
        name=phase_name,
        apt=_build_apt_package(enable_apt=enable_apt)
        or _build_apt_rep_package(enable_apt_repo=enable_apt_repo),
        tools=_build_tools_package(tools_settings=tools_settings),
        pip=_build_pip_packages(enable_pip_packages=enable_pip_packages),
        conda=_build_conda_packages(enable_conda_packages=enable_conda_packages),
        r=_build_r_packages(enable_r_packages=enable_r_packages),
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


def test_install_packages_apt_repo(context_mock, mock_install_apt_repos, package_file):
    package_file_config = _build_package_config([_build_phase(enable_apt_repo=True)])
    with package_file(package_file_config) as package_file_path:
        install_packages.package_install(
            package_file=package_file_path,
            build_step_name="build-step-1",
            context=context_mock,
        )
    assert mock_install_apt_repos.mock_calls == [
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


def test_install_pip_packages(context_mock, mock_install_pip_packages, package_file):
    phase_conda_packages = _build_phase(
        phase_name="phase-1",
        enable_pip_packages=True,
    )
    package_file_config = _build_package_config([phase_conda_packages])
    with package_file(package_file_config) as package_file_path:
        install_packages.package_install(
            package_file=package_file_path,
            build_step_name="build-step-1",
            context=context_mock,
        )
    assert mock_install_pip_packages.mock_calls == [
        call(ANY, phase_conda_packages, context_mock)
    ]


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
    assert mock_install_micromamba.mock_calls == [call(phase_micromamba, context_mock)]


def test_install_conda_packages(
    context_mock, mock_install_conda_packages, package_file
):
    phase_conda_packages = _build_phase(
        phase_name="phase-1",
        enable_conda_packages=True,
    )
    package_file_config = _build_package_config([phase_conda_packages])
    with package_file(package_file_config) as package_file_path:
        install_packages.package_install(
            package_file=package_file_path,
            build_step_name="build-step-1",
            context=context_mock,
        )
    assert mock_install_conda_packages.mock_calls == [
        call(ANY, phase_conda_packages, context_mock)
    ]


def test_install_r_packages(context_mock, mock_install_r_packages, package_file):
    phase_r_packages = _build_phase(
        phase_name="phase-1",
        enable_r_packages=True,
    )
    package_file_config = _build_package_config([phase_r_packages])
    with package_file(package_file_config) as package_file_path:
        install_packages.package_install(
            package_file=package_file_path,
            build_step_name="build-step-1",
            context=context_mock,
        )
    assert mock_install_r_packages.mock_calls == [
        call(ANY, phase_r_packages, context_mock)
    ]



def test_install_bazel(context_mock, mock_install_bazel, package_file):
    phase_bazel = _build_phase(
        phase_name="phase-1",
        tools_settings=ToolsSettings(bazel=Bazel(version="2.5.0")),
    )
    package_file_config = _build_package_config([phase_bazel])
    with package_file(package_file_config) as package_file_path:
        install_packages.package_install(
            package_file=package_file_path,
            build_step_name="build-step-1",
            context=context_mock,
        )
    assert mock_install_bazel.mock_calls == [
        call(phase_bazel, context_mock)
    ]

def test_install_packages_multiple(
    context_mock,
    mock_install_apt_repos,
    mock_install_apt_packages,
    mock_install_pip,
    mock_install_micromamba,
    mock_install_pip_packages,
    mock_install_conda_packages,
    mock_install_r_packages,
    mock_install_bazel,
    package_file,
):
    phases = [
        Phase(
            name="phase-1",
            apt=_build_apt_rep_package(enable_apt_repo=True),
        ),
        Phase(
            name="phase-2",
            apt=_build_apt_package(enable_apt=True),
        ),
        Phase(
            name="phase-3",
            tools=_build_tools_package(
                tools_settings=ToolsSettings(python_binary_path=True)
            ),
        ),
        Phase(
            name="phase-4",
            tools=_build_tools_package(
                tools_settings=ToolsSettings(pip=Pip(version="25.5"))
            ),
        ),
        Phase(
            name="phase-5",
            apt=_build_apt_package(
                enable_apt=True, apt_package=AptPackage(name="wget", version="1.2.3")
            ),
        ),
        Phase(
            name="phase-6",
            tools=_build_tools_package(
                tools_settings=ToolsSettings(micromamba=Micromamba(version="2.5.0"))
            ),
        ),
        Phase(
            name="phase-7",
            pip=_build_pip_packages(enable_pip_packages=True),
        ),
        Phase(
            name="phase-8",
            conda=_build_conda_packages(enable_conda_packages=True),
        ),
        Phase(
            name="phase-9",
            r=_build_r_packages(enable_r_packages=True),
        ),
        Phase(
            name="phase-10",
            tools=_build_tools_package(tools_settings=ToolsSettings(bazel=Bazel(version="2.5.0"))),
        ),
    ]
    package_file_config = _build_package_config(phases)
    with package_file(package_file_config) as package_file_path:
        install_packages.package_install(
            package_file=package_file_path,
            build_step_name="build-step-1",
            context=context_mock,
        )
    assert mock_install_apt_repos.mock_calls == [
        call(
            phases[0].apt,
            context_mock,
        ),
    ]
    assert mock_install_apt_packages.mock_calls == [
        call(phases[1].apt, context_mock),
        call(phases[4].apt, context_mock),
    ]
    assert mock_install_pip.mock_calls == [call(ANY, phases[3], context_mock)]
    assert mock_install_micromamba.mock_calls == [call(phases[5], context_mock)]
    assert mock_install_pip_packages.mock_calls == [call(ANY, phases[6], context_mock)]
    assert mock_install_conda_packages.mock_calls == [
        call(ANY, phases[7], context_mock)
    ]
    assert mock_install_r_packages.mock_calls == [call(ANY, phases[8], context_mock)]
    assert mock_install_bazel.mock_calls == [
        call(phases[9], context_mock)
    ]
