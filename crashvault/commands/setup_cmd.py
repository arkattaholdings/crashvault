import click
from ..install_hook import create_user_config


@click.command(name="setup")
def setup_cmd():
    """Initialize or regenerate the .crashvault configuration directory."""
    config_dir = create_user_config()
    click.echo(f"Crashvault configuration initialized at {config_dir}")
    click.echo("Edit ~/.crashvault/config.json to customize:")
    click.echo("  - User information (name, email, team)")
    click.echo("  - AI settings (provider, model, API key)")
    click.echo("  - Notification preferences")
    click.echo("  - Storage settings")
