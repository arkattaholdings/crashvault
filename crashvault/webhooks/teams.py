"""Microsoft Teams webhook provider."""

import json
import logging
import urllib.request
import urllib.error
from typing import Any, Dict, List

from .base import WebhookConfig, WebhookPayload, WebhookProvider
from .dispatcher import register_provider


logger = logging.getLogger("crashvault")


class TeamsWebhook(WebhookProvider):
    """Send notifications to Microsoft Teams via incoming webhooks."""

    def send(self, payload: WebhookPayload) -> bool:
        """Send a Teams notification."""
        try:
            teams_payload = self._build_teams_payload(payload)
            data = json.dumps(teams_payload).encode("utf-8")

            req = urllib.request.Request(
                self.config.url,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                return response.status == 200

        except urllib.error.URLError as e:
            logger.error(f"Teams webhook failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Teams webhook error: {e}")
            return False

    def _build_teams_payload(self, payload: WebhookPayload) -> Dict[str, Any]:
        """Build a Teams adaptive card message."""
        # Color based on level (Teams uses hex colors)
        level_colors = {
            "debug": "6B7280",    # Gray
            "info": "3B82F6",     # Blue
            "warning": "F59E0B",  # Amber
            "error": "EF4444",    # Red
            "critical": "7C2D12", # Dark red
        }
        color = level_colors.get(payload.level.lower(), "6B7280")

        level_emoji = {
            "debug": "🔍",
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "❌",
            "critical": "🔥",
        }
        emoji = level_emoji.get(payload.level.lower(), "📌")

        # Build facts list for the facts set
        facts: List[Dict[str, str]] = [
            {"name": "Level", "value": f"{emoji} {payload.level.upper()}"},
            {"name": "Issue", "value": f"#{payload.issue_id}"},
        ]

        if payload.host:
            facts.append({"name": "Host", "value": payload.host})

        if payload.tags:
            tags_str = ", ".join(payload.tags)
            facts.append({"name": "Tags", "value": tags_str})

        # Build the adaptive card
        card_body: List[Dict[str, Any]] = [
            {
                "type": "TextBlock",
                "text": "CrashVault Alert",
                "weight": "bolder",
                "size": "medium",
                "color": color,
            },
            {
                "type": "TextBlock",
                "text": payload.message[:500],
                "wrap": True,
                "spacing": "medium",
            },
            {
                "type": "FactSet",
                "facts": facts,
            },
        ]

        # Add stacktrace if available (truncated)
        if payload.stacktrace:
            stack = payload.stacktrace[:800]
            if len(payload.stacktrace) > 800:
                stack += "\n..."
            card_body.append({
                "type": "TextBlock",
                "text": f"```\n{stack}\n```",
                "wrap": True,
                "spacing": "medium",
                "isSubtle": True,
            })

        # Add timestamp if available
        if payload.timestamp:
            card_body.append({
                "type": "TextBlock",
                "text": f"Event: {payload.event_id} | {payload.timestamp}",
                "spacing": "medium",
                "isSubtle": True,
                "size": "small",
            })

        # Build the final adaptive card
        teams_payload = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": color,
            "summary": f"CrashVault Alert: {payload.level.upper()} - Issue #{payload.issue_id}",
            "sections": [
                {
                    "activityTitle": "CrashVault Alert",
                    "activitySubtitle": f"Level: {payload.level.upper()}",
                    "facts": facts,
                    "markdown": True,
                }
            ],
            "potentialAction": [
                {
                    "@type": "OpenUri",
                    "name": "View in CrashVault",
                    "targets": [
                        {"os": "default", "uri": f"crashvault://issue/{payload.issue_id}"}
                    ]
                }
            ]
        }

        # Add the message as a text block
        teams_payload["text"] = f"**CrashVault Alert** - {payload.level.upper()} - Issue #{payload.issue_id}\n\n{payload.message[:500]}"

        # Add stacktrace section if present
        if payload.stacktrace:
            stack = payload.stacktrace[:500]
            if len(payload.stacktrace) > 500:
                stack += "\n..."
            teams_payload["text"] += f"\n\n```\n{stack}\n```"

        return teams_payload


# Register the provider
register_provider("teams", TeamsWebhook)
