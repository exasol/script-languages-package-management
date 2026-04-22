from exasol.exaslpm.cli.cli import cli
from exasol.exaslpm.cli.make_context import make_context
from exasol.exaslpm.pkg_mgmt.list_all_installed_packages import (
    list_all_installed_packages,
)


@cli.command()
def list_all_installed_packages_command():
    """
    This command outputs all installed packages for all supported package types.
    The currently used package types are taken from this build steps history.
    """
    list_all_installed_packages(
        make_context(),
    )
