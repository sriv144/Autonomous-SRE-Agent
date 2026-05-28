"""Tests for the K8S_LOCAL_MODE environment toggle in agent_core.tools."""
from src.agent_core import tools


def test_local_mode_defaults_to_incluster(monkeypatch):
    monkeypatch.delenv("K8S_LOCAL_MODE", raising=False)
    assert tools._resolve_local_mode() is False


def test_local_mode_truthy_values(monkeypatch):
    for value in ("1", "true", "True", "YES", "on", " yes "):
        monkeypatch.setenv("K8S_LOCAL_MODE", value)
        assert tools._resolve_local_mode() is True


def test_local_mode_falsey_values(monkeypatch):
    for value in ("0", "false", "False", "no", "off", ""):
        monkeypatch.setenv("K8S_LOCAL_MODE", value)
        assert tools._resolve_local_mode() is False
