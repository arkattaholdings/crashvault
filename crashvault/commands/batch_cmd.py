import click
from ..core import load_issues, save_issues
from ..rich_utils import get_console
from datetime import datetime, timezone

console = get_console()


@click.command(name="batch")
@click.option("--resolve", is_flag=True, help="Resolve the specified issues")
@click.option("--reopen", is_flag=True, help="Reopen the specified issues")
@click.option("--ignore", is_flag=True, help="Ignore the specified issues")
@click.option("--status", type=click.Choice(["open", "resolved", "ignored"], case_sensitive=False), help="Set status for issues")
@click.option("--severity", type=click.Choice(["low", "medium", "high", "critical"], case_sensitive=False), help="Set severity for issues")
@click.option("--tag", "tags", multiple=True, help="Add tag(s) to issues")
@click.option("--untag", "untags", multiple=True, help="Remove tag(s) from issues")
@click.argument("issue_ids", nargs=-1, type=int)
def batch_cmd(do_resolve, do_reopen, do_ignore, status, severity, tags, untags, issue_ids):
    """Perform batch operations on multiple issues.
    
    Examples:
        crashvault batch --resolve 1 2 3
        crashvault batch --status ignored 4 5
        crashvault batch --severity critical --tag urgent 1 2
        crashvault batch --untag old-tag --tag new-tag 1
    """
    if not issue_ids:
        console.print("[error]No issue IDs specified[/error]")
        raise click.Abort()
    
    issues = load_issues()
    found_issues = []
    not_found = []
    
    for issue_id in issue_ids:
        issue = next((i for i in issues if i["id"] == issue_id), None)
        if issue:
            found_issues.append((issue_id, issue))
        else:
            not_found.append(issue_id)
    
    if not_found:
        console.print(f"[warning]Issues not found: {', '.join(f'#{i}' for i in not_found)}[/warning]")
    
    if not found_issues:
        console.print("[error]No matching issues found[/error]")
        raise click.Abort()
    
    # Perform the actions
    changed = 0
    for issue_id, issue in found_issues:
        # Handle resolve flag
        if do_resolve:
            issue["status"] = "resolved"
            issue["resolved_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        
        # Handle reopen flag
        if do_reopen:
            issue["status"] = "open"
            issue["resolved_at"] = None
        
        # Handle ignore flag
        if do_ignore:
            issue["status"] = "ignored"
        
        # Handle explicit status (overrides flags)
        if status:
            issue["status"] = status.lower()
            if status.lower() == "resolved":
                issue["resolved_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            elif status.lower() == "open":
                issue["resolved_at"] = None
        
        # Handle severity
        if severity:
            issue["severity"] = severity.lower()
        
        # Handle tags
        if tags:
            if "tags" not in issue:
                issue["tags"] = []
            for tag in tags:
                if tag not in issue["tags"]:
                    issue["tags"].append(tag)
        
        # Handle untag
        if untags:
            if "tags" in issue:
                issue["tags"] = [t for t in issue["tags"] if t not in untags]
        
        changed += 1
    
    if changed > 0:
        save_issues(issues)
        
    # Report results
    console.print(f"[success]Updated[/success] [highlight]{changed}[/highlight] issue(s)")
    
    # Show what was done
    if do_resolve:
        console.print(f"  [success]Status:[/success] resolved")
    if do_reopen:
        console.print(f"  [success]Status:[/success] open (reopened)")
    if do_ignore:
        console.print(f"  [success]Status:[/success] ignored")
    if status:
        console.print(f"  [success]Status:[/success] {status}")
    if severity:
        console.print(f"  [success]Severity:[/success] {severity}")
    if tags:
        console.print(f"  [success]Added tags:[/success] {', '.join(tags)}")
    if untags:
        console.print(f"  [success]Removed tags:[/success] {', '.join(untags)}")
