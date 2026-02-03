class PackageFileValidationError(Exception):
    def __init__(self, package_file_graph: list[str], message: str) -> None:
        msg = message + " at " + "[{}]".format(" -> ".join(package_file_graph))
        super().__init__(msg)
