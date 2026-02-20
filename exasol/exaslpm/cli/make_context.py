from exasol.exaslpm.pkg_mgmt.context.cmd_executor import CommandExecutor
from exasol.exaslpm.pkg_mgmt.context.cmd_logger import StdLogger
from exasol.exaslpm.pkg_mgmt.context.context import Context
from exasol.exaslpm.pkg_mgmt.context.file_access import FileAccess
from exasol.exaslpm.pkg_mgmt.context.file_downloader import FileDownloader
from exasol.exaslpm.pkg_mgmt.context.history_file_manager import HistoryFileManager
from exasol.exaslpm.pkg_mgmt.context.temp_file_provider import TempFileProvider


def make_context() -> Context:

    logger = StdLogger()
    cmd_executor = CommandExecutor(logger)

    return Context(
        cmd_logger=logger,
        cmd_executor=cmd_executor,
        history_file_manager=HistoryFileManager(),
        file_access=FileAccess(),
        file_downloader=FileDownloader(),
        temp_file_provider=TempFileProvider(),
    )
