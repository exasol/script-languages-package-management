def install(package_file):
    """
    Installs Debian packages using apt-get.
    :param package_file: The package file containing the apt package descriptions for apt packages to install.
    """
    with open(package_file) as f:
        for line in f:
            print(line)
