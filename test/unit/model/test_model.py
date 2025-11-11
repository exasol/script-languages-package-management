import pytest
from pydantic import ValidationError

from exasol.exaslpm.model.package_file_config import (
    AptPackages,
    BuildStep,
    CondaPackages,
    Package,
    PackageFile,
    Phase,
    PipPackages,
    RPackages,
)


def test_empty_package_file():
    """
    Atleast one Buildstep shall be there
    """
    with pytest.raises(ValueError) as excinfo:
        PackageFile(build_steps={})
    assert "atleast one Buildstep" in str(excinfo.value)


def test_empty_build_step():
    """
    Atleast one Phase shall be there
    """
    with pytest.raises(ValueError) as excinfo:
        BuildStep(phases={})
    assert "atleast one Phase" in str(excinfo.value)


def test_empty_package_installer():
    """
    Atleast one Phase shall be there
    """
    with pytest.raises(ValueError) as excinfo:
        phase = Phase(apt=None, pip=None, r=None, conda=None, comment=None)
    assert "atleast one Package" in str(excinfo.value)


def test_valid_package_installer_apt():
    """
    Create atleast one phase and see if works
    """
    pack = Package(name="curl", version="7.68.0", comment=None)
    aptPack = AptPackages(packages=[pack], comment=None)
    phase = Phase(apt=aptPack, pip=None, r=None, conda=None, comment=None)
    assert phase


def test_valid_package_installer_pip():
    """
    Create atleast one phase and see if works
    """
    pack = Package(name="requests", version="2.25.1", comment=None)
    pipPack = PipPackages(packages=[pack], comment=None)
    phase = Phase(apt=None, pip=pipPack, r=None, conda=None, comment=None)
    assert phase


def test_valid_package_installer_conda():
    """
    Create atleast one phase and see if works
    """
    pack = Package(name="numpy", version="1.19.2", comment=None)
    cndPack = CondaPackages(packages=[pack], channels=None, comment=None)
    phase = Phase(apt=None, pip=None, r=None, conda=cndPack, comment=None)
    assert phase


def test_valid_package_installer_r():
    """
    Create atleast one phase and see if works
    """
    pack = Package(name="ggplot2", version="3.3.5", comment=None)
    rPack = RPackages(packages=[pack], channels=None, comment=None)
    phase = Phase(apt=None, pip=None, r=rPack, conda=None, comment=None)
    assert phase


def test_valid_package_all_installers():
    """
    Create atleast one phase and see if works
    """

    pack_apt = Package(name="curl", version="7.68.0", comment=None)
    aptPack = AptPackages(packages=[pack_apt], comment=None)

    pack_pip = Package(name="requests", version="2.25.1", comment=None)
    pipPack = PipPackages(packages=[pack_pip], comment=None)

    pack_cnd = Package(name="numpy", version="1.19.2", comment=None)
    cndPack = CondaPackages(packages=[pack_cnd], channels=None, comment=None)

    pack_r = Package(name="ggplot2", version="3.3.5", comment=None)
    rPack = RPackages(packages=[pack_r], channels=None, comment=None)

    phase = Phase(apt=aptPack, pip=pipPack, r=rPack, conda=cndPack, comment=None)
    assert phase
