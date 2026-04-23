"""Tests for IndexNow submitter (unit tests)."""
from __future__ import annotations

import pytest

from tools.distribution.indexnow import submit_single


def test_indexnow_missing_key():
    with pytest.raises(RuntimeError, match="INDEXNOW_KEY"):
        submit_single("https://example.com/page", key=None)
