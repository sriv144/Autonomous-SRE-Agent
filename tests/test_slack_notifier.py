"""
Tests for the Slack notifier module.
Uses httpx mocking to avoid real network calls.
"""

import pytest
from unittest.mock import patch, MagicMock
import httpx

from src.agent_core.slack_notifier import (
    notify_plan_ready,
    notify_agent_error,
    _truncate,
)


class TestTruncate:
    def test_short_text_unchanged(self):
        text = "hello world"
        assert _truncate(text) == text

    def test_long_text_truncated(self):
        text = "x" * 3000
        result = _truncate(text, max_chars=2900)
        assert len(result) <= 2900 + 100  # allow for suffix
        assert "truncated" in result

    def test_exact_boundary_not_truncated(self):
        text = "y" * 2900
        result = _truncate(text, max_chars=2900)
        assert result == text


class TestNotifyPlanReady:
    def test_returns_false_when_no_webhook_url(self, monkeypatch):
        monkeypatch.setenv("SLACK_WEBHOOK_URL", "")
        import src.agent_core.slack_notifier as sn
        sn.SLACK_WEBHOOK_URL = ""
        result = notify_plan_ready("test-group", "some plan")
        assert result is False

    def test_sends_post_request_on_success(self, monkeypatch):
        monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.slack.com/test")
        import src.agent_core.slack_notifier as sn
        sn.SLACK_WEBHOOK_URL = "https://hooks.slack.com/test"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
            mock_client.post.return_value = mock_response

            result = notify_plan_ready(
                group_key="namespace/alert-group",
                plan="1. Check pod logs\n2. Restart deployment",
                alert_names=["PodCrashLoopBackOff", "HighMemoryUsage"],
                namespace="production",
            )

        assert result is True
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert call_args[0][0] == "https://hooks.slack.com/test"
        payload = call_args[1]["json"]
        assert "blocks" in payload

    def test_returns_false_on_http_error(self, monkeypatch):
        import src.agent_core.slack_notifier as sn
        sn.SLACK_WEBHOOK_URL = "https://hooks.slack.com/test"

        with patch("httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
            mock_response = MagicMock()
            mock_response.status_code = 403
            mock_response.text = "invalid_token"
            mock_client.post.return_value = mock_response
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "403", request=MagicMock(), response=mock_response
            )

            result = notify_plan_ready("group-key", "plan text")

        assert result is False

    def test_handles_many_alerts_truncated_in_message(self, monkeypatch):
        import src.agent_core.slack_notifier as sn
        sn.SLACK_WEBHOOK_URL = "https://hooks.slack.com/test"

        with patch("httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_client.post.return_value = mock_response

            # 15 alerts — only first 10 should appear explicitly
            alerts = [f"Alert{i}" for i in range(15)]
            notify_plan_ready("group", "plan", alert_names=alerts)

        call_args = mock_client.post.call_args
        payload_str = str(call_args[1]["json"])
        assert "and 5 more" in payload_str


class TestNotifyAgentError:
    def test_sends_error_notification(self, monkeypatch):
        import src.agent_core.slack_notifier as sn
        sn.SLACK_WEBHOOK_URL = "https://hooks.slack.com/test"

        with patch("httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_client.post.return_value = mock_response

            result = notify_agent_error(
                group_key="prod/critical-alert",
                error="ConnectionError: unable to reach Weaviate",
            )

        assert result is True
        call_args = mock_client.post.call_args
        payload = call_args[1]["json"]
        assert any(
            "Error" in str(block) for block in payload["blocks"]
        )
