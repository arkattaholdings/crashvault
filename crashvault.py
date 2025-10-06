"""Compatibility shim for legacy single-file CLI.

The actual CLI now lives in the package `crashvault`.
"""

from crashvault.cli import cli  # noqa: F401

if __name__ == "__main__":
    cli()
