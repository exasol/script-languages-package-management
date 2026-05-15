from test.integration.docker_test_environment.test_logger import StringMatchCounter
from test.integration.package_utils import ContainsPackages

import pytest

from exasol.exaslpm.model.package_file_config import DocOption
from exasol.exaslpm.model.serialization import to_yaml_str
from exasol.exaslpm.pkg_mgmt.install_packages import package_install

pytestmark = pytest.mark.via_command_executor


def test_apt_install(
    docker_container,
    apt_pkg_file_wildcard,
    local_package_path,
    docker_executor_context,
):
    apt_package_file_yaml = to_yaml_str(apt_pkg_file_wildcard)
    local_package_path.write_text(apt_package_file_yaml)

    expected_packages = apt_pkg_file_wildcard.build_steps[0].phases[0].apt.packages

    pkgs_before_install = docker_container.list_apt()
    assert pkgs_before_install != ContainsPackages(expected_packages)

    return_code_counter = StringMatchCounter("Return Code: 0")
    docker_executor_context.cmd_logger.info_callback = return_code_counter.log

    package_install(
        package_file=local_package_path,
        build_step_name="build_step_1",
        context=docker_executor_context,
    )

    pkgs_after_install = docker_container.list_apt()
    assert pkgs_after_install == ContainsPackages(expected_packages)

    # Check that all 'install apt' commands (see install_apt.prepare_all_cmds() for list) succeeded
    assert return_code_counter.result == 7


@pytest.mark.parametrize(
    "doc_option_param", [DocOption.MINIMIZE, DocOption.SYSTEM_DEFAULT]
)
def test_install_apt_no_doc(
    docker_container,
    doc_option_param,
    apt_pkg_file_no_doc,
    local_package_path,
    docker_executor_context,
):

    # Better to clear any existing dpkg cfg
    docker_container.run(
        [
            "sh",
            "-c",
            "rm -f /etc/dpkg/dpkg.cfg.d/*excludes*",
        ],
        check_exit_code=False,
    )

    # Update package cache after clearing dpkg config
    docker_container.run(
        ["apt-get", "update", "-y"],
        check_exit_code=False,
    )

    # For SYSTEM_DEFAULT, install man-db and unminimize
    if doc_option_param == DocOption.SYSTEM_DEFAULT:
        # Install man-db and unminimize
        docker_container.run(
            ["sh", "-c", "apt-get install -y man-db unminimize"],
            check_exit_code=False,
        )
        # Run unminimize to restore docs. time consuming
        docker_container.run(
            ["sh", "-c", "yes | unminimize"],
            check_exit_code=False,
        )

    apt_pkg_file_no_doc.build_steps[0].phases[0].apt.doc_option = doc_option_param
    apt_package_file_yaml = to_yaml_str(apt_pkg_file_no_doc)

    local_package_path.write_text(apt_package_file_yaml)

    package_install(
        package_file=local_package_path,
        build_step_name="build_step_1",
        context=docker_executor_context,
    )

    # Get the status of docs (search recursively for *curl* files)
    _, output = docker_container.run(
        [
            "sh",
            "-c",
            "find /usr/share/doc /usr/share/man* -name '*curl*' -type f 2>/dev/null | "
            "grep -v copyright | head -10",
        ],
        check_exit_code=False,
    )

    if doc_option_param == DocOption.MINIMIZE:
        assert (
            output.strip() == ""
        ), "When doc_option is MINIMIZE, there shall be no curl docs"
    if doc_option_param == DocOption.SYSTEM_DEFAULT:
        assert (
            output.strip() != ""
        ), "When doc_option is SYSTEM_DEFAULT, curl docs shall be installed"

    # Irrespective of what doc_option is, copyright files shall be present
    _, output = docker_container.run(
        [
            "sh",
            "-c",
            "find /usr/share/doc -path '*curl*' -name '*copyright*' -type f 2>/dev/null",
        ],
        check_exit_code=False,
    )
    assert (
        output.strip() != ""
    ), "copyright files for curl are missing in /usr/share/doc"
