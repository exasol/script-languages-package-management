import io
import json
import tarfile
from os import PathLike

from docker_test_environment_builder import *
from test.integration.cli_helper import CliHelper


def pytest_addoption(parser):
    parser.addoption("--test-image-ubuntu-version", action="store", help="Ubuntu version to use for testing", default="24.04")
    parser.addoption("--keep-docker-image", action="store_true", help="Runs the notebook test with a Docker-DB with a GPU device attached.",
                     default=False)


@pytest.fixture
def file_uploader(docker_container):
    def make_and_upload_file(target_path_in_container: PathLike, file_name: str,  content: str) -> None:
        tarstream = io.BytesIO()
        content_data = content.encode("utf-8")
        with tarfile.open(fileobj=tarstream, mode='w') as tar:
            tarinfo = tarfile.TarInfo(name=file_name)
            tarinfo.size = len(content_data)
            tar.addfile(tarinfo, io.BytesIO(content_data))
        tarstream.seek(0)
        res = docker_container.put_archive(str(target_path_in_container), tarstream.read())
        assert res
    return make_and_upload_file

@pytest.fixture
def cli_helper(exaslpm_executable):
    return CliHelper(f"/{exaslpm_executable}")

@pytest.fixture
def list_apt_package_factory(docker_runner):
    def list_apt():
        err, out = docker_runner(["bash", "-c", """dpkg-query -W -f='{"package":"${Package}","version":"${Version}"}\n'"""])
        assert err == 0, out
        output = out.decode("utf-8")
        packages = []
        for line in output.strip().splitlines():
            if line.strip():  # avoid empty lines
                packages.append(json.loads(line))
        return packages
    return list_apt