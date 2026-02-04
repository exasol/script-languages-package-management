from pathlib import Path
from test.integration.docker_test_environment.docker_test_container import (
    DockerTestContainer,
)


class DockerFileAccess:
    def __init__(self, docker_test_container: DockerTestContainer):
        self.docker_test_container = docker_test_container

    def check_binary(self, binary_path: Path) -> Path:
        # Use 'stat' command to check file existence and permissions
        command = f"stat -c %a {binary_path}"
        # %a format specifier gives permissions in octal notation

        exit_code, output = self.docker_test_container.container.exec_run(command)

        if exit_code == 0:
            # File exists, now check executable permissions (any x bit set)
            permissions_octal_str = output.decode("utf-8").strip()
            try:
                permissions_octal = int(permissions_octal_str, 8)
                # Check if any executable bit is set (user, group, or others)
                # os.X_OK mode in os.access checks executable bit (value 1)
                # We use a custom check here as os.X_OK is for host system

                # Executable bits are 0o100 (user), 0o010 (group), 0o001 (others)
                is_exec = (permissions_octal & 0o111) > 0
                if not is_exec:
                    raise ValueError(f"Binary file {binary_path} is not executable")
            except ValueError as e:
                raise ValueError(
                    f"Failed to parse permissions: {permissions_octal_str}"
                ) from e
        else:
            raise ValueError(f"Failed to check if {binary_path} is executable")
        return binary_path

    def copy_file(self, source_path: Path, destination_path: Path) -> None:
        self.docker_test_container.run(["cp", str(source_path), str(destination_path)])
