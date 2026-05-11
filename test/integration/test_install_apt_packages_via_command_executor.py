from test.integration.docker_test_environment.test_logger import StringMatchCounter
from test.integration.package_utils import ContainsPackages

import pytest

from exasol.exaslpm.model.serialization import to_yaml_str
from exasol.exaslpm.pkg_mgmt.install_packages import package_install


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
    "no_doc_pkg_file", ["apt_pkg_file_no_doc_true", "apt_pkg_file_with_no_doc_default"]
)
def test_install_apt_no_doc(
    docker_container,
    no_doc_pkg_file,
    local_package_path,
    docker_executor_context,
    request,
):
    """Test: When no_doc is True or not specified, documentation is excluded."""
    no_doc_pkg_file = request.getfixturevalue(no_doc_pkg_file)
    apt_package_file_yaml = to_yaml_str(no_doc_pkg_file)
    local_package_path.write_text(apt_package_file_yaml)

    package_install(
        package_file=local_package_path,
        build_step_name="build_step_1",
        context=docker_executor_context,
    )

    # curl, locales shall not have documentation
    packages_to_check = ["locales", "curl"]
    excluded_paths = [
        "/usr/share/man",
        "/usr/share/info",
    ]

    for pkg in packages_to_check:
        for path in excluded_paths:
            _, output = docker_container.run(
                [
                    "sh",
                    "-c",
                    f"find {path} -type f -name '*{pkg}*' 2>/dev/null || true",
                ],
                check_exit_code=False,
            )
            assert (
                output.strip() == ""
            ), f"Expected no {pkg} documentation in {path}, but found: {output.strip()}"

    # Verify copyright files are present in /usr/share/doc
    for pkg in ["curl", "locales"]:
        _, output = docker_container.run(
            [
                "sh",
                "-c",
                f"find /usr/share/doc/{pkg}* -name 'copyright' -type f 2>/dev/null || true",
            ],
            check_exit_code=False,
        )
        assert (
            output.strip() != ""
        ), f"Expected copyright files for {pkg} in /usr/share/doc"


def test_install_apt_no_doc_to_false(
    docker_container,
    apt_pkg_file_with_no_doc_false,
    local_package_path,
    docker_executor_context,
):
    """Test: no_doc is explicitly False, documentation IS installed."""
    apt_package_file_yaml = to_yaml_str(apt_pkg_file_with_no_doc_false)
    local_package_path.write_text(apt_package_file_yaml)

    package_install(
        package_file=local_package_path,
        build_step_name="build_step_1",
        context=docker_executor_context,
    )

    # Check if documentation for both locales and binutils IS installed
    packages_to_check = ["locales", "binutils"]
    for pkg in packages_to_check:
        _, output = docker_container.run(
            [
                "sh",
                "-c",
                f"find /usr/share/doc/{pkg}* -type f ! -name 'copyright' 2>/dev/null | head -5 || true",
            ],
            check_exit_code=False,
        )
        assert (
            output.strip() != ""
        ), f"Expected {pkg} documentation files (other than copyright) in /usr/share/doc when no_doc=False"
