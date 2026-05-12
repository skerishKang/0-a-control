"""Tests for runtime session id validation (Issue #170)."""

from __future__ import annotations

from pathlib import Path

from scripts.server import validate_session_id, _is_path_inside


class TestValidateSessionId:
    def test_valid_uuid_like(self):
        assert validate_session_id("a1b2c3d4-e5f6-7890-abcd-ef1234567890")

    def test_valid_hex(self):
        assert validate_session_id("deadbeef1234")

    def test_valid_with_underscore(self):
        assert validate_session_id("session_abc-123")

    def test_valid_short(self):
        assert validate_session_id("x")

    def test_valid_max_length(self):
        assert validate_session_id("a" * 128)

    def test_invalid_slash(self):
        assert not validate_session_id("../foo")

    def test_invalid_backslash(self):
        assert not validate_session_id("..\\foo")

    def test_invalid_dot_dot_plain(self):
        assert not validate_session_id("..")

    def test_invalid_null_byte(self):
        assert not validate_session_id("foo\x00bar")

    def test_invalid_colon(self):
        assert not validate_session_id("foo:bar")

    def test_invalid_absolute_style(self):
        assert not validate_session_id("/tmp/x")

    def test_invalid_too_long(self):
        assert not validate_session_id("a" * 129)

    def test_invalid_none(self):
        assert not validate_session_id(None)

    def test_invalid_empty(self):
        assert not validate_session_id("")

    def test_invalid_whitespace(self):
        assert not validate_session_id("valid valid")

    def test_invalid_rel_path_without_slash(self):
        assert not validate_session_id("foo/bar")


class TestIsPathInside:
    def test_child_inside(self, tmp_path: Path):
        parent = tmp_path.resolve()
        child = parent / "sub" / "file.json"
        assert _is_path_inside(child, parent)

    def test_equal_path(self, tmp_path: Path):
        parent = tmp_path.resolve()
        assert _is_path_inside(parent, parent)

    def test_outside_path(self, tmp_path: Path):
        parent = tmp_path.resolve()
        child = tmp_path.parent / "outside.json"
        assert not _is_path_inside(child, parent)

    def test_nonexistent_path(self, tmp_path: Path):
        parent = tmp_path.resolve()
        child = parent / "nonexistent" / "file.json"
        # resolve() works even for non-existent paths (as long as parent exists)
        assert _is_path_inside(child, parent)

    def test_absolute_outside(self, tmp_path: Path):
        parent = tmp_path.resolve()
        child = Path("/etc/passwd")
        assert not _is_path_inside(child, parent)
