import click


def install(package_file: str, channel_file: str):
    """
    Install conda packages using micromamba.
    :param package_file: The package file containing the conda package descriptions for conda packages to install.
    :param channel_file: The channel file containing the conda channels to use.
    """
