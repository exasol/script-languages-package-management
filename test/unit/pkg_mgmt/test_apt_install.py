from unittest.mock import (
    MagicMock,
    Mock,
    patch,
)

import pytest

from exasol.exaslpm.pkg_mgmt.cmd_executor import (
    CommandExecutor,
    CommandResult,
)
from exasol.exaslpm.pkg_mgmt.install_apt import install_via_apt


def test_apt_install():
    assert True
