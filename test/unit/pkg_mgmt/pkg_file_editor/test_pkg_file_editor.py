import re
from test.unit.pkg_mgmt.pkg_file_editor.constants import (
    TEST_BUILD_STEP_NAME,
    TEST_PHASE_NAME,
)
from test.unit.pkg_mgmt.pkg_file_editor.reload_package_file import reload_package_file

import pytest

from exasol.exaslpm.pkg_mgmt.pkg_file_editor.errors import (
    BuildStepNotFoundError,
    PhaseNotFoundError,
)


def test_commit(package_file_context, base_apt_package_file):
    """
    Test that commiting changes to the comment of the Package file works as expected.
    """
    with package_file_context(base_apt_package_file) as pkg_file_editor:
        pkg_file_editor.update_comment("Test comment")
        pkg_file_editor.commit()

        assert (
            reload_package_file(pkg_file_editor.package_file).comment == "Test comment"
        )


def test_build_step_editor(package_file_context, base_apt_package_file):
    """
    Test modifying build step name and comment works as expected
    """
    with package_file_context(base_apt_package_file) as pkg_file_editor:
        pkg_file_before = reload_package_file(pkg_file_editor.package_file)
        assert pkg_file_before.build_steps[0].name == TEST_BUILD_STEP_NAME
        assert pkg_file_before.build_steps[0].comment is None
        build_step_editor = pkg_file_editor.update_build_step(TEST_BUILD_STEP_NAME)
        build_step_editor.update_name("new build step name")
        build_step_editor.update_comment("Test comment")
        pkg_file_editor.commit()
        pkg_file_after = reload_package_file(pkg_file_editor.package_file)
        assert pkg_file_after.build_steps[0].name == "new build step name"
        assert pkg_file_after.build_steps[0].comment == "Test comment"


def test_pkg_editor_fail_on_wrong_build_step_name(
    package_file_context, base_apt_package_file
):
    """
    Test that trying to access an invalid build step name raises BuildStepNotFoundError.
    """
    with package_file_context(base_apt_package_file) as pkg_file_editor:
        expected_err_msg = f"'Invalid build step name' build step not found at [Package-file = '{pkg_file_editor.package_file}']"
        with pytest.raises(BuildStepNotFoundError, match=re.escape(expected_err_msg)):
            pkg_file_editor.update_build_step("Invalid build step name")


def test_phase_editor(package_file_context, base_apt_package_file):
    """
    Test that trying to modifying phase name and comment works as expected.
    """

    with package_file_context(base_apt_package_file) as pkg_file_editor:
        pkg_file_before = reload_package_file(pkg_file_editor.package_file)
        assert pkg_file_before.build_steps[0].phases[0].name == TEST_PHASE_NAME
        assert pkg_file_before.build_steps[0].phases[0].comment is None
        phase_editor = pkg_file_editor.update_build_step(
            TEST_BUILD_STEP_NAME
        ).update_phase(TEST_PHASE_NAME)
        phase_editor.update_name("new phase name")
        phase_editor.update_comment("Test comment")
        pkg_file_editor.commit()
        pkg_file_after = reload_package_file(pkg_file_editor.package_file)
        assert pkg_file_after.build_steps[0].phases[0].name == "new phase name"
        assert pkg_file_after.build_steps[0].phases[0].comment == "Test comment"


def test_build_step_editor_fail_on_wrong_phase_name(
    package_file_context, base_apt_package_file
):
    """
    Test that trying to access an invalid phase name raises expected PhaseNotFoundError.
    """
    with package_file_context(base_apt_package_file) as pkg_file_editor:
        expected_err_msg = f"'Invalid phase name' phase not found at [Package-file = '{pkg_file_editor.package_file}' -> Build-Step = 'test build step']"
        with pytest.raises(PhaseNotFoundError, match=re.escape(expected_err_msg)):
            pkg_file_editor.update_build_step(TEST_BUILD_STEP_NAME).update_phase(
                "Invalid phase name"
            )
