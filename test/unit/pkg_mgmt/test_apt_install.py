import pytest

from exasol.exaslpm.model.package_file_config import (
    AptPackages,
    Package,
)
from exasol.exaslpm.pkg_mgmt.cmd_executor import CommandExecutor
from exasol.exaslpm.pkg_mgmt.install_apt import *

order_of_exec = ["update", "install", "clean", "remove", "locale", "ldconfig"]
call_count = 0


def mock_execute(_, cmd_strs):
    global call_count
    cmd_str = " ".join(cmd_strs)
    assert order_of_exec[call_count] in cmd_str
    call_count += 1


def test_install_via_apt_empty_packages(monkeypatch, capsys):
    monkeypatch.setattr(CommandExecutor, "execute", mock_execute)
    aptPackages = AptPackages(packages=[])
    install_via_apt(aptPackages, CommandExecutor())
    prints = capsys.readouterr()
    assert "empty list" in prints.out


def test_install_via_apt(monkeypatch):
    global call_count
    monkeypatch.setattr(CommandExecutor, "execute", mock_execute)

    pkgs = [
        Package(name="curl", version="7.68.0"),
        Package(name="requests", version="2.25.1"),
    ]
    aptPackages = AptPackages(packages=pkgs)
    install_via_apt(aptPackages, CommandExecutor())
    assert call_count == len(order_of_exec)
    call_count = 0


def test_prepare_update_command():
    cmd_strs = prepare_update_command()
    cmd_str = " ".join(cmd_strs)
    assert "apt-get" in cmd_str
    assert "update" in cmd_str


def test_prepare_clean_cmd():
    cmd_strs = prepare_clean_cmd()
    cmd_str = " ".join(cmd_strs)
    assert "apt-get" in cmd_str
    assert "clean" in cmd_str


def test_prepare_autoremove_cmd():
    cmd_strs = prepare_autoremove_cmd()
    cmd_str = " ".join(cmd_strs)
    assert "apt-get" in cmd_str
    assert "remove" in cmd_str


def test_prepare_locale_cmd():
    cmd_strs = prepare_locale_cmd()
    cmd_str = " ".join(cmd_strs)
    assert "locale" in cmd_str


def test_prepare_ldconfig_cmd():
    cmd_strs = prepare_ldconfig_cmd()
    cmd_str = " ".join(cmd_strs)
    assert "ldconfig" in cmd_str
