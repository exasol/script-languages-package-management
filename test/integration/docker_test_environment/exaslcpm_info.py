from dataclasses import dataclass
from pathlib import Path


@dataclass
class ExaslcpmInfo:
    executable_name = "exaslcpm"
    path_in_container = Path("/")

    @property
    def exaslcpm_path_in_container(self) -> Path:
        return self.path_in_container / self.executable_name
