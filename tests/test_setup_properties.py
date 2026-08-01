"""Tests for modules.setup.properties template-parent detection and stamping."""

import pytest

from modules.setup import properties as setup_props


def _template_lines() -> list[str]:
    return setup_props._build_initial_content().splitlines(keepends=True)  # pylint: disable=protected-access


def _stamp(lines, repo_local, monkeypatch, *, detected, confirm=False):
    monkeypatch.setattr(setup_props, "_detect_template_remote", lambda _remote: detected)
    monkeypatch.setattr(setup_props.cli, "confirm", lambda *_a, **_k: confirm)
    setup_props._stamp_template_parent(  # pylint: disable=protected-access
        lines, repo_local, "github.com/user/my_vault"
    )


class TestReadScalar:
    """Tests for _read_scalar()."""

    def test_reads_value_inside_section(self):
        lines = _template_lines()
        value = setup_props._read_scalar(lines, "template", "remote")  # pylint: disable=protected-access
        assert value == setup_props._TEMPLATE_REMOTE_PLACEHOLDER  # pylint: disable=protected-access

    def test_missing_key_returns_none(self):
        lines = _template_lines()
        assert setup_props._read_scalar(lines, "template", "nope") is None  # pylint: disable=protected-access

    def test_key_outside_section_not_matched(self):
        lines = _template_lines()
        assert setup_props._read_scalar(lines, "repos", "remote") is None  # pylint: disable=protected-access


class TestStampTemplateParent:
    """Tests for _stamp_template_parent()."""

    def test_detected_parent_stamped_with_sibling_local_guess(self, monkeypatch: pytest.MonkeyPatch):
        lines = _template_lines()
        _stamp(lines, "$HOME/Development/user/my_vault", monkeypatch, detected="github.com/user/template_my_vault")
        content = "".join(lines)
        assert 'remote: "github.com/user/template_my_vault"' in content
        assert 'local: "$HOME/Development/user/template_my_vault"' in content

    def test_hand_configured_parent_never_touched(self, monkeypatch: pytest.MonkeyPatch):
        lines = _template_lines()
        _stamp(lines, "$HOME/dev/my_vault", monkeypatch, detected="github.com/user/template_my_vault")
        before = "".join(lines)
        _stamp(lines, "$HOME/dev/my_vault", monkeypatch, detected="github.com/user/other_template")
        assert "".join(lines) == before

    def test_no_detection_and_declined_prompt_leaves_placeholder(self, monkeypatch: pytest.MonkeyPatch):
        lines = _template_lines()
        _stamp(lines, "$HOME/dev/my_vault", monkeypatch, detected=None, confirm=False)
        content = "".join(lines)
        assert setup_props._TEMPLATE_REMOTE_PLACEHOLDER in content  # pylint: disable=protected-access
        assert setup_props._TEMPLATE_LOCAL_PLACEHOLDER in content  # pylint: disable=protected-access

    def test_prompted_parent_stamped_when_confirmed(self, monkeypatch: pytest.MonkeyPatch):
        lines = _template_lines()
        monkeypatch.setattr(setup_props.cli, "prompt", lambda *_a, **_k: "github.com/user/template_my_vault")
        _stamp(lines, "$HOME/dev/my_vault", monkeypatch, detected=None, confirm=True)
        assert 'remote: "github.com/user/template_my_vault"' in "".join(lines)
