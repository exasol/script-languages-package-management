from unittest.mock import MagicMock

import pytest

from exasol.exaslpm.pkg_mgmt.context.binary_checker import BinaryChecker
from exasol.exaslpm.pkg_mgmt.context.cmd_executor import CommandExecutor
from exasol.exaslpm.pkg_mgmt.context.cmd_logger import CommandLogger
from exasol.exaslpm.pkg_mgmt.context.context import Context
from exasol.exaslpm.pkg_mgmt.context.history_file_manager import HistoryFileManager


@pytest.fixture
def context_mock():
    mock_logger = MagicMock(spec=CommandLogger)
    mock_executor = MagicMock(spec=CommandExecutor)
    mock_history_file_manager = MagicMock(spec=HistoryFileManager)
    mock_binary_checker = MagicMock(spec=BinaryChecker)
    return Context(
        cmd_logger=mock_logger,
        cmd_executor=mock_executor,
        history_file_manager=mock_history_file_manager,
        binary_checker=mock_binary_checker,
    )
