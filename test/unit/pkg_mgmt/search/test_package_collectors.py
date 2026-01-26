import pytest
import yaml

from exasol.exaslpm.model.package_file_config import (
    AptPackage,
    AptPackages,
    BuildStep,
    CondaPackage,
    CondaPackages,
    PackageFile,
    Phase,
    PipPackage,
    PipPackages,
    RPackage,
    RPackages,
)
from exasol.exaslpm.pkg_mgmt.search.package_collectors import (
    collect_conda_packages,
    collect_pip_packages,
)


def yaml_to_package_file_config(yml: str) -> PackageFile:
    yaml_dict = yaml.safe_load(yml)
    return PackageFile.model_validate(yaml_dict)


@pytest.mark.parametrize(
    "collector, package_variable, packages_model",
    [
        pytest.param(
            collect_conda_packages,
            "apt",
            AptPackages,
            id="empty apt-packages, conda collector",
        ),
        pytest.param(
            collect_pip_packages,
            "apt",
            AptPackages,
            id="empty apt-packages, pip collector",
        ),
        pytest.param(
            collect_conda_packages,
            "conda",
            CondaPackages,
            id="empty conda-packages, conda collector",
        ),
        pytest.param(
            collect_pip_packages,
            "pip",
            PipPackages,
            id="empty pip-packages, pip collector",
        ),
    ],
)
def test_collect_empty(collector, package_variable, packages_model):
    d = {package_variable: packages_model(packages=[])}
    tst_package_file_model = PackageFile(
        build_steps=[
            BuildStep(name="build_step_1", phases=[Phase(name="phase_one", **d)])
        ]
    )
    assert collector(tst_package_file_model.build_steps) == []


TEST_PACKAGE_APT = AptPackage(name="test_package_apt", version="1.0.0")
TEST_PACKAGE_PIP = PipPackage(name="test_package_pip", version="1.0.0")
TEST_PACKAGE_PIP_2 = PipPackage(name="test_package_pip_2", version="1.0.0")
TEST_PACKAGE_CONDA = CondaPackage(name="test_package_conda", version="1.0.0")
TEST_PACKAGE_CONDA_2 = CondaPackage(name="test_package_conda_2", version="1.0.0")
TEST_PACKAGE_R = RPackage(name="test_package_conda", version="1.0.0")


@pytest.mark.parametrize(
    "collector, package_variable, packages",
    [
        pytest.param(
            collect_conda_packages,
            "apt",
            AptPackages(packages=[TEST_PACKAGE_APT]),
            id="apt-packages, conda collector",
        ),
        pytest.param(
            collect_conda_packages,
            "r",
            RPackages(packages=[TEST_PACKAGE_R]),
            id="r-packages, conda collector",
        ),
        pytest.param(
            collect_pip_packages,
            "apt",
            AptPackages(packages=[TEST_PACKAGE_APT]),
            id="apt-packages, pip collector",
        ),
        pytest.param(
            collect_pip_packages,
            "r",
            RPackages(packages=[TEST_PACKAGE_R]),
            id="r-packages, pip collector",
        ),
    ],
)
def test_collect_ignore_other_packages(collector, package_variable, packages):
    d = {package_variable: packages}
    test_build_step = BuildStep(
        name="build_step_1", phases=[Phase(name="phase_one", **d)]
    )
    assert collector([test_build_step]) == []


@pytest.mark.parametrize(
    "collector, package_variable, packages_model, package",
    [
        pytest.param(
            collect_conda_packages,
            "conda",
            CondaPackages,
            TEST_PACKAGE_CONDA,
            id="conda collector",
        ),
        pytest.param(
            collect_pip_packages,
            "pip",
            PipPackages,
            TEST_PACKAGE_PIP,
            id="pip collector",
        ),
    ],
)
def test_collect_single_build_step_single_phase(
    collector, package_variable, packages_model, package
):
    d = {package_variable: packages_model(packages=[package])}
    test_build_step = BuildStep(
        name="build_step_1", phases=[Phase(name="phase_one", **d)]
    )
    assert collector([test_build_step]) == [package]


@pytest.mark.parametrize(
    "collector, package_variable, packages_model, packages",
    [
        pytest.param(
            collect_conda_packages,
            "conda",
            CondaPackages,
            [TEST_PACKAGE_CONDA, TEST_PACKAGE_CONDA_2],
            id="conda collector",
        ),
        pytest.param(
            collect_pip_packages,
            "pip",
            PipPackages,
            [TEST_PACKAGE_PIP, TEST_PACKAGE_PIP_2],
            id="pip collector",
        ),
    ],
)
def test_collect_multi_build_step_single_phase(
    collector, package_variable, packages_model, packages
):
    d_one = {package_variable: packages_model(packages=[packages[0]])}
    d_two = {package_variable: packages_model(packages=[packages[1]])}
    build_step_one = BuildStep(
        name="build_step_1", phases=[Phase(name="phase_one", **d_one)]
    )
    build_step_two = BuildStep(
        name="build_step_2", phases=[Phase(name="phase_one", **d_two)]
    )
    assert collector([build_step_one, build_step_two]) == packages


@pytest.mark.parametrize(
    "collector, package_variable, packages_model, packages",
    [
        pytest.param(
            collect_conda_packages,
            "conda",
            CondaPackages,
            [TEST_PACKAGE_CONDA, TEST_PACKAGE_CONDA_2],
            id="conda collector",
        ),
        pytest.param(
            collect_pip_packages,
            "pip",
            PipPackages,
            [TEST_PACKAGE_PIP, TEST_PACKAGE_PIP_2],
            id="pip collector",
        ),
    ],
)
def test_collect_single_build_step_multi_phase(
    collector, package_variable, packages_model, packages
):
    d_one = {package_variable: packages_model(packages=[packages[0]])}
    d_two = {package_variable: packages_model(packages=[packages[1]])}
    build_step_one = BuildStep(
        name="build_step_1",
        phases=[Phase(name="phase_one", **d_one), Phase(name="phase_two", **d_two)],
    )
    assert collector([build_step_one]) == packages
