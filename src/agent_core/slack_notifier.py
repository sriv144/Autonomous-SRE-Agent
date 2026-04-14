"""
Slack Notifier for KubeSentient.

Sends structured alert investigation results and remediation plans to a
configured Slack webhook URL. Supports both success and failure notifications.
"""

import logging
import os
from typing import Optional

import httpx

logger = logging.getLogger("kubesentient.slack")

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")


def _truncate(text: str, max_chars: int = 2900) -> str:
    """Truncate text to fit within Slack's block character limits."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n_[truncated — see logs for full output]_"


def notify_plan_ready(
    group_key: str,
    plan: str,
    alert_names: Optional[list[str]] = None,
    namespace: Optional[str] = None,
) -> bool:
    """
    Post a remediation plan to Slack.

    Args:
        group_key: AlertManager group key identifying this alert group.
        plan: Markdown-formatted remediation plan from the LangGraph planner.
        alert_names: Optional list of individual alert names in this group.
        namespace: Optional Kubernetes namespace affected.

    Returns:
        True if the message was sent successfully, False otherwise.
    """
    if not SLACK_WEBHOOK_URL:
        logger.warning("SLACK_WEBHOOK_URL is not set — skipping Slack notification.")
        return False

    alert_list = ""
    if alert_names:
        alert_list = "\n".join(f"• `{name}`" for name in alert_names[:10])
        if len(alert_names) > 10:
            alert_list += f"\n• _...and {len(alert_names) - 10} more_"

    ns_text = f"*Namespace:* `{namespace}`\n" if namespace else ""

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🔴 KubeSentient: Remediation Plan Ready",
                "emoji": True,
            },
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Alert Group:*\n`{group_key}`",
                },
                *(
                    [
                        {
                            "type": "mrkdwn",
                            "text": f"*Namespace:*\n`{namespace}`",
                        }
                    ]
                    if namespace
                    else []
                ),
            ],
        },
    ]

    if alert_list:
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Triggered Alerts:*\n{alert_list}",
                },
            }
        )

    blocks += [
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*📋 Remediation Plan:*\n{_truncate(plan)}",
            },
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "⚠️ _This plan requires human review before executing any kubectl commands._",
                }
            ],
        },
    ]

    payload = {"blocks": blocks}
    return _post_to_slack(payload, context=f"plan for {group_key}")


def notify_agent_error(group_key: str, error: str) -> bool:
    """
    Post an agent failure notification to Slack.

    Args:
        group_key: AlertManager group key that failed to process.
        error: Error message/traceback string.

    Returns:
        True if the message was sent successfully, False otherwise.
    """
    if not SLACK_WEBHOOK_URL:
        logger.warning("SLACK_WEBHOOK_URL is not set — skipping Slack notification.")
        return False

    payload = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "⚠️ KubeSentient: Agent Error",
                    "emoji": True,
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*Alert Group:* `{group_key}`\n\n"
                        f"The autonomous SRE agent encountered an error while investigating this alert. "
                        f"*Manual investigation is required.*"
                    ),
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Error Details:*\n```{_truncate(error, max_chars=1500)}```",
                },
            },
        ]
    }
    return _post_to_slack(payload, context=f"error for {group_key}")


def _post_to_slack(payload: dict, context: str = "") -> bool:
    """Send a payload to the configured Slack webhook URL."""
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(SLACK_WEBHOOK_URL, json=payload)
            response.raise_for_status()
            logger.info(f"Slack notification sent successfully ({context})")
            return True
    except httpx.HTTPStatusError as e:
        logger.error(
            f"Slack webhook returned HTTP {e.response.status_code} for {context}: {e.response.text}"
        )
    except httpx.RequestError as e:
        logger.error(f"Failed to reach Slack webhook for {context}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error sending Slack notification for {context}: {e}")
    return False
