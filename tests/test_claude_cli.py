import json
import subprocess
from unittest.mock import patch

import pytest

from aurealis_carousel.claude_cli import (
    ClaudeCLIError, ensure_available, query, query_json,
)


def _fake_proc(stdout: str, returncode: int = 0, stderr: str = ""):
    proc = subprocess.CompletedProcess(args=[], returncode=returncode)
    proc.stdout = stdout
    proc.stderr = stderr
    return proc


def test_ensure_available_raises_when_missing(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: None)
    with pytest.raises(ClaudeCLIError, match="not on PATH"):
        ensure_available()


def test_query_returns_result_text(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: "/fake/claude")
    envelope = json.dumps({"result": "hello", "is_error": False})
    monkeypatch.setattr("subprocess.run", lambda *a, **kw: _fake_proc(envelope))
    assert query("anything") == "hello"


def test_query_raises_on_nonzero_exit(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: "/fake/claude")
    monkeypatch.setattr(
        "subprocess.run", lambda *a, **kw: _fake_proc("", returncode=1, stderr="boom")
    )
    with pytest.raises(ClaudeCLIError, match="exited 1"):
        query("anything")


def test_query_raises_on_error_envelope(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: "/fake/claude")
    envelope = json.dumps({"result": "rate limited", "is_error": True})
    monkeypatch.setattr("subprocess.run", lambda *a, **kw: _fake_proc(envelope))
    with pytest.raises(ClaudeCLIError, match="reported error"):
        query("anything")


def test_query_json_strips_code_fences(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: "/fake/claude")
    inner = '```json\n{"ok": true, "n": 7}\n```'
    envelope = json.dumps({"result": inner, "is_error": False})
    monkeypatch.setattr("subprocess.run", lambda *a, **kw: _fake_proc(envelope))
    assert query_json("anything") == {"ok": True, "n": 7}


def test_query_json_extracts_object_from_prose(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: "/fake/claude")
    inner = 'Sure, here it is: {"ok": true} — let me know if more is needed.'
    envelope = json.dumps({"result": inner, "is_error": False})
    monkeypatch.setattr("subprocess.run", lambda *a, **kw: _fake_proc(envelope))
    assert query_json("anything") == {"ok": True}


def test_query_json_raises_claude_cli_error_on_unparseable_response(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: "/fake/claude")
    inner = 'First: {"a": 1}. Then unrelated text. Then: {"b": 2}'
    envelope = json.dumps({"result": inner, "is_error": False})
    monkeypatch.setattr("subprocess.run", lambda *a, **kw: _fake_proc(envelope))
    with pytest.raises(ClaudeCLIError, match="could not parse JSON"):
        query_json("anything")


@pytest.mark.live
def test_query_json_live_smoke():
    result = query_json('Return only the JSON object {"ok": true, "n": 42}.')
    assert result.get("ok") is True
    assert result.get("n") == 42
