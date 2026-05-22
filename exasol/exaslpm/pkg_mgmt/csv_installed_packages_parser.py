import csv

from exasol.exaslpm.model.package_file_config import Package


def parse_csv_output(csv_output: list[str]) -> list[Package]:
    """
    This function only supports CSV output returned by:
    * RscriptExecutor.execute_rscript(context)
    * AptExecutor.execute_apt(context)
    The CSV output must be a list of strings.
    And each string of that list must follow the following format: package_name,package_version
    """
    installed_packages: list[Package] = []
    if csv_output:
        reader = csv.reader(csv_output)
        for row in reader:
            if not row:
                continue
            package = Package(name=row[0], version=row[1])
            installed_packages.append(package)
    return installed_packages
