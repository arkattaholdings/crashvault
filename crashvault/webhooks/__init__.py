"""Webhook providers for CrashVault."""

from .base import WebhookProvider
from .dispatcher import WebhookDispatcher, dispatch_webhooks
from .slack import SlackWebhook
from .discord import DiscordWebhook
from .teams import TeamsWebhook
from .http import HTTPWebhook
from .github import GitHubIssuesWebhook

# Import all providers to trigger registration
# The import side-effect registers each provider with the dispatcher
import crashvault.webhooks.teams  # noqa: F401
import crashvault.webhooks.github  # noqa: F401

__all__ = [
    "WebhookProvider",
    "WebhookDispatcher",
    "dispatch_webhooks",
    "SlackWebhook",
    "DiscordWebhook",
    "TeamsWebhook",
    "HTTPWebhook",
    "GitHubIssuesWebhook",
]
