"""GitHub Issues webhook provider - auto-create issues from crashvault events."""

import json
import logging
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional

from .base import WebhookConfig, WebhookPayload, WebhookProvider
from .dispatcher import register_provider


logger = logging.getLogger("crashvault")


class GitHubIssue:
    """Represents a GitHub issue."""
    
    def __init__(self, number: int, title: str, html_url: str):
        self.number = number
        self.title = title
        self.html_url = html_url


class GitHubIssuesWebhook(WebhookProvider):
    """
    Automatically create GitHub issues from crashvault events.
    
    Configuration requires:
    - url: GitHub repository in format "https://api.github.com/repos/{owner}/{repo}"
    - secret: GitHub Personal Access Token (or can use token in URL)
    - name: Optional name for the webhook
    
    The provider will:
    1. Create a new issue for each crash event
    2. Optionally link to existing issue if issue_id matches
    3. Add labels based on severity level
    4. Include stacktrace and context in the issue body
    """
    
    # Map crashvault levels to GitHub labels
    LEVEL_LABELS = {
        "debug": ["priority/low", "crashvault/debug"],
        "info": ["priority/low", "crashvault/info"],
        "warning": ["priority/medium", "crashvault/warning"],
        "error": ["priority/high", "crashvault/error"],
        "critical": ["priority/critical", "crashvault/critical"],
    }
    
    # Severity to GitHub issue body template
    SEVERITY_EMOJI = {
        "debug": "🔍",
        "info": "ℹ️",
        "warning": "⚠️",
        "error": "❌",
        "critical": "🔥",
    }
    
    def __init__(self, config: WebhookConfig):
        super().__init__(config)
        self._token = config.secret or ""
        
    def send(self, payload: WebhookPayload) -> bool:
        """Create a GitHub issue from the payload."""
        try:
            # Parse the repository URL from config
            # Accept both full API URL and owner/repo format
            repo_url = self.config.url.rstrip("/")
            
            # Support both:
            # - https://api.github.com/repos/owner/repo
            # - https://github.com/owner/repo
            # - owner/repo (shorthand)
            if "/repos/" in repo_url:
                api_url = repo_url
            elif repo_url.startswith("http"):
                # Convert web URL to API URL
                # https://github.com/owner/repo -> https://api.github.com/repos/owner/repo
                parts = repo_url.replace("https://github.com/", "").split("/")
                if len(parts) >= 2:
                    owner, repo = parts[0], parts[1]
                    api_url = f"https://api.github.com/repos/{owner}/{repo}"
                else:
                    logger.error(f"Invalid GitHub URL: {repo_url}")
                    return False
            else:
                # Assume owner/repo format
                api_url = f"https://api.github.com/repos/{repo_url}"
            
            issue_data = self._build_issue_data(payload)
            
            # Make the API request
            data = json.dumps(issue_data).encode("utf-8")
            
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "CrashVault/1.0",
                "Accept": "application/vnd.github+json",
            }
            
            if self._token:
                headers["Authorization"] = f"Bearer {self._token}"
            
            # Determine if we're creating new or updating existing
            # For now, always create new issues
            # In the future, could check for existing issue by title/label
            url = f"{api_url}/issues"
            
            req = urllib.request.Request(
                url,
                data=data,
                headers=headers,
                method="POST",
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.status == 201:
                    result = json.loads(response.read().decode("utf-8"))
                    issue_url = result.get("html_url", "")
                    logger.info(f"GitHub issue created: {issue_url}")
                    return True
                else:
                    logger.error(f"GitHub API returned status: {response.status}")
                    return False
                    
        except urllib.error.HTTPError as e:
            try:
                error_body = e.read().decode("utf-8")
                error_data = json.loads(error_body)
                logger.error(f"GitHub API error: {error_data.get('message', str(e))}")
            except Exception:
                logger.error(f"GitHub webhook failed: {e}")
            return False
        except urllib.error.URLError as e:
            logger.error(f"GitHub webhook network error: {e}")
            return False
        except Exception as e:
            logger.error(f"GitHub webhook error: {e}")
            return False
    
    def _build_issue_data(self, payload: WebhookPayload) -> Dict[str, Any]:
        """Build the GitHub issue data from the payload."""
        emoji = self.SEVERITY_EMOJI.get(payload.level.lower(), "📌")
        
        # Build the issue body
        body_parts = []
        
        # Add crash details
        body_parts.append(f"## 🚨 CrashVault Event Details")
        body_parts.append(f"")
        body_parts.append(f"| Field | Value |")
        body_parts.append(f"|-------|-------|")
        body_parts.append(f"| **Event ID** | `{payload.event_id}` |")
        body_parts.append(f"| **Issue ID** | #{payload.issue_id} |")
        body_parts.append(f"| **Level** | {payload.level.upper()} |")
        body_parts.append(f"| **Timestamp** | {payload.timestamp or 'N/A'} |")
        body_parts.append(f"| **Host** | {payload.host or 'N/A'} |")
        
        if payload.tags:
            body_parts.append(f"| **Tags** | {', '.join(payload.tags)} |")
        
        body_parts.append(f"")
        
        # Add the error message
        body_parts.append(f"### 📝 Message")
        body_parts.append(f"")
        body_parts.append(f"```")
        body_parts.append(f"{payload.message}")
        body_parts.append(f"```")
        body_parts.append(f"")
        
        # Add stacktrace if available
        if payload.stacktrace:
            body_parts.append(f"### 🔧 Stacktrace")
            body_parts.append(f"")
            # Truncate if too long (GitHub has 65536 char limit)
            stack = payload.stacktrace[:15000]
            if len(payload.stacktrace) > 15000:
                stack += f"\n\n... (truncated, full stacktrace available in CrashVault)"
            body_parts.append(f"```")
            body_parts.append(f"{stack}")
            body_parts.append(f"```")
            body_parts.append(f"")
        
        # Add context if available
        if payload.context:
            body_parts.append(f"### 📋 Context")
            body_parts.append(f"")
            for key, value in payload.context.items():
                body_parts.append(f"- **{key}**: `{value}`")
            body_parts.append(f"")
        
        # Add footer
        body_parts.append(f"---")
        body_parts.append(f"*This issue was automatically created by CrashVault*")
        
        # Build labels
        labels = self.LEVEL_LABELS.get(payload.level.lower(), ["crashvault/unknown"])
        
        # Add custom tags as labels (sanitized)
        if payload.tags:
            for tag in payload.tags:
                # Sanitize tag to be GitHub label compatible
                safe_tag = "".join(c for c in tag.lower() if c.isalnum() or c in "-_").strip("-_")
                if safe_tag and len(safe_tag) < 50:
                    labels.append(f"crashvault:{safe_tag}")
        
        # Build the issue
        title = f"{emoji} [{payload.level.upper()}] #{payload.issue_id}: {payload.message[:60]}"
        if len(payload.message) > 60:
            title += "..."
        
        return {
            "title": title,
            "body": "\n".join(body_parts),
            "labels": labels,
        }
    
    def should_send(self, payload: WebhookPayload) -> bool:
        """Check if this webhook should receive this event."""
        if not self.config.enabled:
            return False
        
        # Only send error and critical levels to GitHub by default
        # (we don't want to spam with debug/info issues)
        if not self.config.events:
            return payload.level.lower() in ["error", "critical"]
        
        # Check if event level matches filter
        return payload.level.lower() in [e.lower() for e in self.config.events]


# Register the provider
register_provider("github", GitHubIssuesWebhook)
