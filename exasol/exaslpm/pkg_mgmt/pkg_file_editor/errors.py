from exasol.exaslpm.pkg_mgmt.pkg_file_editor.pkg_graph_pointer import (
    PackageGraphPointer,
)


class PackageMgrError(Exception):
    def __init__(
        self, package_graph_pointer: PackageGraphPointer, message: str
    ) -> None:
        self.package_graph_pointer = package_graph_pointer
        msg = message + " at " + package_graph_pointer.to_string()
        super().__init__(msg)


class DuplicateEntryError(PackageMgrError):
    """
    Exception raised when trying to add an item to a list, which already exists.
    """


class PhaseNotFoundError(PackageMgrError):
    """
    Exception raised when a phase cannot be found.
    """


class PackageNotFoundError(PackageMgrError):
    """
    Exception raised when a package cannot be found.
    """


class BuildStepNotFoundError(PackageMgrError):
    """
    Exception raised when a build step cannot be found.
    """


class ChannelNotFoundError(PackageMgrError):
    """
    Exception raised when a channel cannot be found.
    """
