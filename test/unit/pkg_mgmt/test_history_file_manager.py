import contextlib
import re
from copy import deepcopy
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


def _resulting_files(history_file_manager) -> list[str]:
    result = [
        p.name for p in history_file_manager.history_path.iterdir() if p.is_file()
    ]
    result.sort()
    return result


def test_add_build_step_to_empty_history(history_file_manager):
    with history_file_manager([]) as hsm:
        hsm.add_build_step_to_history(TEST_BUILD_STEP)

        assert hsm.get_all_previous_build_steps() == [TEST_BUILD_STEP]

        assert _resulting_files(hsm) == [f"000_{TEST_BUILD_STEP.name}"]


def test_add_build_step_to_non_empty_history(history_file_manager):
    with history_file_manager([TEST_BUILD_STEP, TEST_BUILD_STEP_2]) as hsm:
        hsm.add_build_step_to_history(TEST_BUILD_STEP_3)

        sorted_result = hsm.get_all_previous_build_steps()
        assert sorted_result == [TEST_BUILD_STEP, TEST_BUILD_STEP_2, TEST_BUILD_STEP_3]

        assert _resulting_files(hsm) == [
            f"000_{TEST_BUILD_STEP.name}",
            f"001_{TEST_BUILD_STEP_2.name}",
            f"002_{TEST_BUILD_STEP_3.name}",
        ]


def test_fails_if_build_step_exists(history_file_manager):
    with history_file_manager([TEST_BUILD_STEP]) as hsm:
        with pytest.raises(
            ValueError,
            match=rf"Buildstep 'build_step_1' already exists in history path: '{hsm.history_path}'",
        ):
            hsm.add_build_step_to_history(TEST_BUILD_STEP)


def test_max_build_step_files(history_file_manager):
    def _make_build_step(index: int) -> BuildStep:
        build_step = deepcopy(TEST_BUILD_STEP)
        build_step.name = f"next_build_step_{index}"
        return build_step

    with history_file_manager([]) as hsm:
        for count in range(1000):
            hsm.add_build_step_to_history(_make_build_step(count))
        with pytest.raises(
            RuntimeError,
            match=re.escape("Maximum number of history files (999) exceeded."),
        ):
            hsm.add_build_step_to_history(_make_build_step(1000))
