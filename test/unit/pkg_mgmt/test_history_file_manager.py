import contextlib
from test.unit.test_data import (
    TEST_BUILD_STEP,
    TEST_BUILD_STEP_2,
    TEST_BUILD_STEP_3,
)

import pytest

from exasol.exaslpm.model.package_file_config import BuildStep
from exasol.exaslpm.pkg_mgmt.context.history_file_manager import HistoryFileManager


@pytest.fixture
def history_file_manager(tmp_path):
    history_path = tmp_path / "history"
    history_path.mkdir(parents=False, exist_ok=True)

    @contextlib.contextmanager
    def prepare(existing_build_steps: list[BuildStep]):
        hsm = HistoryFileManager(history_path=history_path)
        for existing_build_step in existing_build_steps:
            hsm.add_build_step_to_history(existing_build_step)
        yield hsm

    return prepare


def test_add_build_step_to_empty_history(history_file_manager):
    with history_file_manager([]) as hsm:
        hsm.add_build_step_to_history(TEST_BUILD_STEP)

        assert hsm.get_all_previous_build_steps() == [TEST_BUILD_STEP]


def test_add_build_step_to_non_empty_history(history_file_manager):
    with history_file_manager([TEST_BUILD_STEP, TEST_BUILD_STEP_2]) as hsm:
        hsm.add_build_step_to_history(TEST_BUILD_STEP_3)

        sorted_result = sorted(
            hsm.get_all_previous_build_steps(), key=lambda build_step: build_step.name
        )
        assert sorted_result == [TEST_BUILD_STEP, TEST_BUILD_STEP_2, TEST_BUILD_STEP_3]


def test_fails_if_build_step_exists(history_file_manager):
    with history_file_manager([TEST_BUILD_STEP]) as hsm:
        with pytest.raises(
            ValueError,
            match=rf"Buildstep 'build_step_1' already exists in history path: '{hsm.history_path}'",
        ):
            hsm.add_build_step_to_history(TEST_BUILD_STEP)
