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
