from exasol.exaslpm.model.any_package import (
    PackageType,
)
from exasol.exaslpm.model.package_file_config import AptPackage


def test_any_package_types():
    apt_package: PackageType = AptPackage(name="curl", version="1.2.3")
    assert isinstance(apt_package, AptPackage)
