import click


def install(package_file):
    """
    Installs R packages using r_remote.
    :param package_file: The package file containing the CRAN package descriptions for R packages to install.
    """
    with open(package_file) as f:
        for line in f:
            print(line)
