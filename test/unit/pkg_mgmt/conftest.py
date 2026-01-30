from pathlib import Path
from test.unit.pkg_mgmt.context import (
    FileDownloaderMock,
    HistoryFileManagerMock,
    TempFileProviderMock,
)
from unittest.mock import MagicMock

import pytest

from exasol.exaslpm.pkg_mgmt.context.binary_checker import BinaryChecker
from exasol.exaslpm.pkg_mgmt.context.cmd_executor import (
    CommandExecutor,
    CommandResult,
)
from exasol.exaslpm.pkg_mgmt.context.cmd_logger import CommandLogger
from exasol.exaslpm.pkg_mgmt.context.context import Context


@pytest.fixture
def context_mock():
    mock_logger = MagicMock(spec=CommandLogger)
    mock_executor = MagicMock(spec=CommandExecutor)
    mock_history_file_manager = HistoryFileManagerMock()
    mock_binary_checker = MagicMock(spec=BinaryChecker)
    mock_file_downloader = FileDownloaderMock(path=Path("path/to/file"))
    mock_temp_file_provider = TempFileProviderMock(path=Path("path/to/temp/file"))

    mock_command_result = MagicMock(spec=CommandResult)
    mock_command_result.return_code.return_value = 0
    mock_executor.execute.return_value = mock_command_result

    return Context(
        cmd_logger=mock_logger,
        cmd_executor=mock_executor,
        history_file_manager=mock_history_file_manager,
        binary_checker=mock_binary_checker,
        file_downloader=mock_file_downloader,
        temp_file_provider=mock_temp_file_provider,
    )
