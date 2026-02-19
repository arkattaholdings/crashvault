# CrashVault - Promotional Materials

## Project Description

**CrashVault** is a lightweight, local-first crash/error vault with a simple CLI. Perfect for developers who want to track, organize, and analyze errors from their applications without relying on cloud services.

## Key Features

- 🖥️ **Simple CLI** - Intuitive command-line interface
- 🔌 **HTTP Server** - Receive errors in real-time from any application
- 🔔 **Webhooks** - Slack, Discord, and HTTP integrations
- 📊 **Rich Reports** - Markdown, HTML, and JSON export
- 🏷️ **Tagging & Filtering** - Organize errors by level, tags, and text search
- 📁 **Local Storage** - Your data stays on your machine
- 🧪 **Test Coverage** - Well-tested with pytest

## Target Audience

- Python developers
- CLI enthusiasts
- Developers who prefer local-first tools
- Teams wanting error tracking without cloud dependencies

---

## Draft Post: r/python

**Title:** I built a local error vault with a CLI - no cloud required

**Body:**

Hey r/python! 👋

I wanted to share **CrashVault**, a CLI tool I've been working on for tracking errors locally.

**Why?**
- You're tired of sending your errors to third-party services
- You want something simple that just works
- You prefer having full control of your data

**What it does:**
- Log errors via CLI or HTTP server
- Group errors into issues
- Search and filter by level, tags, text
- Export to Markdown, HTML, JSON
- Send notifications to Slack/Discord

**Quick demo:**
```bash
pip install crashvault
crashvault add "Database timeout" --level=error --tag=db
crashvault list --level=error
crashvault stats
```

It's open source (MIT licensed). Would love feedback!

🔗 https://github.com/Ak-dude/crashvault

---

## Draft Post: r/commandline

**Title:** CrashVault - A CLI-first error tracking tool

**Body:**

Sharing a tool I made for fellow CLI lovers: **CrashVault**

A local error vault that lives in your terminal:

```
$ crashvault add "Connection refused" --level=error --tag=network
$ crashvault list --status=open
$ crashvault generate-report --format html --output report.html
```

Features:
- Full CLI interface (no GUI needed)
- HTTP server for receiving errors from any app
- Webhook integrations (Slack, Discord)
- Export to Markdown/HTML/JSON
- Rich terminal output with colors

Install: `pip install crashvault`

GitHub: https://github.com/Ak-dude/crashvault

---

## Draft Post: r/opensource

**Title:** CrashVault - Local-first error tracking (MIT licensed)

**Body:**

I wanted to share my open-source project: **CrashVault**

A lightweight, local error vault for developers who:
- Want to track errors without cloud services
- Prefer CLI tools over GUIs
- Value data privacy

**Tech stack:** Python, Click, Rich

**Features:**
- CLI for logging, searching, and managing errors
- HTTP server to receive errors from any application
- Webhook notifications (Slack, Discord, HTTP)
- Export reports in multiple formats
- Tagging and filtering system

**Try it:**
```bash
pip install crashvault
crashvault setup
crashvault add "Something went wrong"
```

Would appreciate stars, contributions, and feedback!

🔗 https://github.com/Ak-dude/crashvault

---

## Draft Post: dev.to

**Title:** I Built a Local Error Tracking Tool Because I Wanted Privacy

**Body:**

I've been frustrated with sending all my application errors to third-party services. So I built **CrashVault** - a local-first error vault with a CLI.

## Why?

1. **Privacy** - Your error data stays on your machine
2. **Simplicity** - No complex setup or accounts
3. **Control** - Full ownership of your data

## Features

- **CLI Interface** - Full-featured command-line tool
- **HTTP Server** - Receive errors from any application in real-time
- **Webhooks** - Notify Slack, Discord, or any HTTP endpoint
- **Rich Reports** - Export to Markdown, HTML, or JSON
- **Tagging System** - Organize errors with tags and levels

## Quick Start

```bash
pip install crashvault
crashvault setup
crashvault add "Database timeout" --level=error --tag=db
crashvault list
```

## Example: Receiving Errors from a Python App

```python
import requests

def crashvault_excepthook(exc_type, exc_value, exc_tb):
    requests.post('http://localhost:5678/api/v1/events', json={
        'message': str(exc_value),
        'stacktrace': ''.join(traceback.format_exception(exc_type, exc_value, exc_tb)),
        'level': 'error'
    })

sys.excepthook = crashvault_excepthook
```

Check it out: https://github.com/Ak-dude/crashvault

---

## Draft Post: Hacker News (Show HN)

**Title:** Show HN: CrashVault - A local error vault with CLI

**Body:**

**CrashVault** (https://github.com/Ak-dude/crashvault) is a lightweight, local-first error tracking tool with a CLI interface.

Features:
- Log errors via CLI or HTTP API
- Group errors into issues with tags
- Search and filter by level, tags, text
- Export to Markdown, HTML, JSON
- Webhook notifications (Slack, Discord)
- Rich terminal output

Demo:
```
$ crashvault add "Connection timeout" --level=error --tag=network
$ crashvault list --level=error
$ crashvault stats
```

Built with Python, Click, and Rich. MIT licensed.

---

## Discord Servers to Consider

1. **Python Discord** - #showcase channel
2. **DevOps Discord** - #tools channel
3. **Software Development Discord** - Various channels

---

## Hashtags for Social Media

- #python
- #cli
- #developertools
- #opensource
- #errorhandling
- #devtools

---

*Last updated: February 2026*
