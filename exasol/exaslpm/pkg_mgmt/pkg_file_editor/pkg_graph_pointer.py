from copy import copy
from pathlib import Path


class PackageGraphPointer:
    """
    Helper class to track position within the package file.
    Useful to print debug/exception info.
    Depending on position of occurred error creates a string of type:
    [Package-file = '...']
    or
    [Package-file = '...' -> Build-Step = '...']
    or
    [Package-file = '...' -> Build-Step = '...' -> Phase = '...']
    or
    [Package-file = '...' -> Build-Step = '...' -> Phase = '...' -> Pip]
    or
    [Package-file = '...' -> Build-Step = '...' -> Phase = '...' -> Apt]
    or
    [Package-file = '...' -> Build-Step = '...' -> Phase = '...' -> Conda]
    or
    [Package-file = '...' -> Build-Step = '...' -> Phase = '...' -> R]

    """

    def __init__(self, package_path: Path):
        self.package_path = package_path
        self.build_step: str | None = None
        self.phase: str | None = None
        self.package_mgr_name: str | None = None

    def new_instance_with_build_step(self, build_step: str) -> "PackageGraphPointer":
        assert self.build_step is None
        assert self.phase is None
        assert self.package_mgr_name is None
        new_instance = copy(self)
        new_instance.build_step = build_step
        return new_instance

    def new_instance_with_phase(self, phase: str) -> "PackageGraphPointer":
        assert self.build_step is not None
        assert self.phase is None
        assert self.package_mgr_name is None
        new_instance = copy(self)
        new_instance.phase = phase
        return new_instance

    def new_instance_with_package_apt_mgr(self) -> "PackageGraphPointer":
        assert self.build_step is not None
        assert self.phase is not None
        assert self.package_mgr_name is None
        new_instance = copy(self)
        new_instance.package_mgr_name = "Apt"
        return new_instance

    def new_instance_with_package_pip_mgr(self) -> "PackageGraphPointer":
        assert self.build_step is not None
        assert self.phase is not None
        assert self.package_mgr_name is None
        new_instance = copy(self)
        new_instance.package_mgr_name = "Pip"
        return new_instance

    def new_instance_with_package_conda_mgr(self) -> "PackageGraphPointer":
        assert self.build_step is not None
        assert self.phase is not None
        assert self.package_mgr_name is None
        new_instance = copy(self)
        new_instance.package_mgr_name = "Conda"
        return new_instance

    def new_instance_with_package_r_mgr(self) -> "PackageGraphPointer":
        assert self.build_step is not None
        assert self.phase is not None
        assert self.package_mgr_name is None
        new_instance = copy(self)
        new_instance.package_mgr_name = "R"
        return new_instance

    def to_string(self) -> str:

        items = [f"Package-file = '{self.package_path}'"]
        if self.build_step:
            items.append(f"Build-Step = '{self.build_step}'")

            if self.phase:
                items.append(f"Phase = '{self.phase}'")

                if self.package_mgr_name:
                    items.append(f"{self.package_mgr_name}")

        return "[{}]".format(" -> ".join(items))
