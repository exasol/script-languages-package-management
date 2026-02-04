from pathlib import Path
from unittest.mock import (
    call,
)

from exasol.exaslpm.model.package_file_config import PPA
from exasol.exaslpm.pkg_mgmt.install_apt_packages import *
from exasol.exaslpm.pkg_mgmt.install_apt_ppa import install_ppas


def test_empty_packages(context_mock):
    aptPackages = AptPackages(packages=[])
    install_ppas(aptPackages, context_mock)


def test_install_ppas(context_mock):
    aptPackages = AptPackages(
        packages=[],
        ppas={
            "some_ppa": PPA(
                ppa="deb some_ppa",
                key_server="https://some.key.server",
                out_file="some_ppa.list",
            )
        },
    )

    install_ppas(aptPackages, context_mock)
    assert context_mock.cmd_executor.mock_calls == [
        call.execute(
            [
                "gpg",
                "--dearmor",
                "--yes",
                "-o",
                "/usr/share/keyrings/some_ppa.gpg",
                str(context_mock.file_downloader.mock_path),
            ],
            env=None,
        ),
        call.execute().print_results(),
        call.execute().return_code(),
        call.execute(["apt-get", "-y", "update"], env=None),
        call.execute().print_results(),
        call.execute().return_code(),
        call.execute(["apt-get", "-y", "clean"], env=None),
        call.execute().print_results(),
        call.execute().return_code(),
        call.execute(["apt-get", "-y", "autoremove"], env=None),
        call.execute().print_results(),
        call.execute().return_code(),
    ]

    assert context_mock.file_access.copy_file.mock_calls == [
        call(
            context_mock.temp_file_provider.path,
            Path("/etc") / "apt" / "sources.list.d" / "some_ppa.list",
        )
    ]
