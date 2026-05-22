import csv

from exasol.exaslpm.model.package_file_config import Package


def parse_csv_output(csv_output: list[str]) -> list[Package]:
    installed_packages: list[Package] = []
    if csv_output:
        reader = csv.reader(csv_output)
        for row in reader:
            if not row:
                continue
            package = Package(name=row[0], version=row[1])
            installed_packages.append(package)
    return installed_packages
