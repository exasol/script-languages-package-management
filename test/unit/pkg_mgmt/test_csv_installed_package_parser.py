from exasol.exaslpm.model.package_file_config import Package
from exasol.exaslpm.pkg_mgmt.cvs_installed_packages_parser import parse_csv_output


def test_parse_csv_output_success() -> None:
    cvs_output = ["zlib1g:amd64,1:1.3.dfsg-3.1ubuntu2.1", ""]
    packages = parse_csv_output(cvs_output)
    assert packages == [
        Package(name="zlib1g:amd64", version="1:1.3.dfsg-3.1ubuntu2.1"),
    ]
