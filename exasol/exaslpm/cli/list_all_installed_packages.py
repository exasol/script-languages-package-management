from exasol.exaslpm.cli.cli import cli
from exasol.exaslpm.cli.make_context import make_context
from exasol.exaslpm.model.serialization import to_yaml_str
from exasol.exaslpm.pkg_mgmt.list_all_installed_packages import (
    list_all_installed_packages,
)


@cli.command()
def list_all_installed_packages_command():
    """
    This command outputs all installed packages for all supported package types.
    The currently used package types are taken from this build steps history.
    """
    installed_packages = list_all_installed_packages(
        make_context(),
    )
    print(to_yaml_str(installed_packages))
