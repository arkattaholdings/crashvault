import click
from ..core import load_issues, save_issues
from ..rich_utils import get_console

console = get_console()


# Default severity levels - can be customized in config
DEFAULT_SEVERITY_LEVELS = ["low", "medium", "high", "critical"]


def get_severity_levels():
    """Get configured severity levels from config, or use defaults."""
    from ..core import get_config_value
    levels = get_config_value("severity_levels")
    if levels is None:
        levels = DEFAULT_SEVERITY_LEVELS
    return levels


def get_severity_choices():
    """Get click.Choice compatible tuple for severity levels."""
    levels = get_severity_levels()
    return tuple(levels)


@click.command(name="set-severity")
@click.argument("issue_id", type=int)
@click.argument("severity", type=click.Choice(get_severity_choices(), case_sensitive=False))
def set_severity(issue_id, severity):
    """Set severity level for an issue.
    
    Severity levels: low, medium, high, critical
    
    Example:
        crashvault set-severity 1 critical
    """
    issues = load_issues()
    issue = next((i for i in issues if i["id"] == issue_id), None)
    if not issue:
        console.print("[error]Issue not found[/error]")
        return
    
    issue["severity"] = severity.lower()
    save_issues(issues)
    
    # Style based on severity
    severity_styles = {
        "critical": "danger",
        "high": "warning", 
        "medium": "primary",
        "low": "secondary"
    }
    style = severity_styles.get(severity.lower(), "primary")
    
    console.print(f"[success]Issue[/success] [highlight]#{issue_id}[/highlight] [success]severity set to[/success] [{style}]{severity}[/{style}]")
