"""Tests for Google Indexing API submitter."""
from __future__ import annotations

import pytest

from tools.distribution.indexing_api import submit_url


def test_indexing_api_missing_creds():
    with pytest.raises(RuntimeError, match="GSC_CREDENTIALS_PATH"):
        submit_url("https://example.com/page")
