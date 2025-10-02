import click


def install(package_file):
    """
    Installs Python packages using pip.
    :param package_file: The package file containing the PyPi package descriptions for Python packages to install.
    """
    with open(package_file) as f:
        for line in f:
            print(line)