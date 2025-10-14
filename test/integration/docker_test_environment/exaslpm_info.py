from dataclasses import dataclass
from pathlib import Path


@dataclass
class ExaslpmInfo:
    executable_name = "exaslpm"
    path_in_container = Path("/")

    @property
    def exaslpm_path_in_container(self) -> Path:
        return self.path_in_container / self.executable_name
