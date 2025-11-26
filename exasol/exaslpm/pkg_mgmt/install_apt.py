import subprocess

from exasol.exaslpm.model.package_file_config import AptPackages


def install_via_apt(apt_packages: AptPackages):
    if apt_packages is not None:
        for package in apt_packages.packages:
            command_01 = "apt-get -y update"    
            command_02 = "apt-get -y clean"
            command_03 = "apt-get -y autoremove"
            command_04 = f"apt-get install -V -y --dry-run --no-install-recommends {package.name}"
            command_05 = "key_servers"
            print(f"Installing - {command_04}")
            # result = subprocess.run(command, shell=True)
            # if result.returncode != 0:
            #    print(f"'{command}' failed with exit code {result.returncode}")
