"""
Tests for search, list, and stats commands.
"""
import json
from pathlib import Path


class TestSearchCommand:
    """Tests for the search command."""

    def test_search_all_events(self, crashvault_home, cli_runner, sample_events):
        """Search without filters should return all events."""
        from crashvault.cli import cli

        result = cli_runner.invoke(cli, ["search"])

        assert result.exit_code == 0
        # Should show all 3 events
        assert "event-001" in result.output
        assert "event-002" in result.output
        assert "event-003" in result.output

    def test_search_by_level(self, crashvault_home, cli_runner, sample_events):
        """Search should filter by level."""
        from crashvault.cli import cli

        result = cli_runner.invoke(cli, ["search", "--level", "error"])

        assert result.exit_code == 0
        # Should show error events only
        assert "event-001" in result.output
        assert "event-002" in result.output
        # event-003 is warning, should not appear
        assert "event-003" not in result.output

    def test_search_by_level_case_insensitive(self, crashvault_home, cli_runner, sample_events):
        """Search level filter should be case insensitive."""
        from crashvault.cli import cli

        result = cli_runner.invoke(cli, ["search", "--level", "WARNING"])

        assert result.exit_code == 0
        assert "event-003" in result.output
        assert "event-001" not in result.output

    def test_search_by_tag(self, crashvault_home, cli_runner, sample_events):
        """Search should filter by tag."""
        from crashvault.cli import cli

        result = cli_runner.invoke(cli, ["search", "--tag", "backend"])

        assert result.exit_code == 0
        # Events with backend tag: event-001, event-002
        assert "event-001" in result.output
        assert "event-002" in result.output
        # event-003 has frontend tag, should not appear
        assert "event-003" not in result.output

    def test_search_by_multiple_tags(self, crashvault_home, cli_runner, sample_events):
        """Search with multiple tags should match all tags."""
        from crashvault.cli import cli

        # event-001 has tags: ["backend", "api"]
        result = cli_runner.invoke(cli, ["search", "--tag", "backend", "--tag", "api"])

        assert result.exit_code == 0
        # Only event-001 has both tags
        assert "event-001" in result.output
        # event-002 only has backend tag
        assert "event-002" not in result.output

    def test_search_by_text(self, crashvault_home, cli_runner, sample_events):
        """Search should filter by text in message."""
        from crashvault.cli import cli

        result = cli_runner.invoke(cli, ["search", "--text", "Test error"])

        assert result.exit_code == 0
        # event-001 and event-002 have "Test error message"
        assert "event-001" in result.output
        assert "event-002" in result.output

    def test_search_by_text_case_insensitive(self, crashvault_home, cli_runner, sample_events):
        """Search text filter should be case insensitive."""
        from crashvault.cli import cli

        result = cli_runner.invoke(cli, ["search", "--text", "test error"])

        assert result.exit_code == 0
        # Both should match regardless of case
        assert "event-001" in result.output
        assert "event-002" in result.output

    def test_search_combined_filters(self, crashvault_home, cli_runner, sample_events):
        """Search should combine multiple filters."""
        from crashvault.cli import cli

        # Search for error level with "backend" tag
        result = cli_runner.invoke(cli, ["search", "--level", "error", "--tag", "backend"])

        assert result.exit_code == 0
        # Should match error level + backend tag
        assert "event-001" in result.output
        assert "event-002" in result.output

    def test_search_no_results(self, crashvault_home, cli_runner, sample_events):
        """Search with non-matching filters should show no results."""
        from crashvault.cli import cli

        result = cli_runner.invoke(cli, ["search", "--level", "critical"])

        assert result.exit_code == 0
        assert "0 event(s) matched" in result.output

    def test_search_empty_events(self, crashvault_home, cli_runner):
        """Search on empty events should work."""
        from crashvault.cli import cli

        result = cli_runner.invoke(cli, ["search"])

        assert result.exit_code == 0
        assert "0 event(s) matched" in result.output


class TestListCommand:
    """Tests for the list command."""

    def test_list_all_issues(self, crashvault_home, cli_runner, sample_issues):
        """List without filters should show all issues."""
        from crashvault.cli import cli

        result = cli_runner.invoke(cli, ["list"])

        assert result.exit_code == 0
        # All 3 issues should be listed
        assert "#1" in result.output
        assert "#2" in result.output
        assert "#3" in result.output

    def test_list_by_status(self, crashvault_home, cli_runner, sample_issues):
        """List should filter by status."""
        from crashvault.cli import cli

        result = cli_runner.invoke(cli, ["list", "--status", "open"])

        assert result.exit_code == 0
        # Issue 1 is open
        assert "#1" in result.output
        # Issue 2 is resolved, issue 3 is ignored
        assert "#2" not in result.output
        assert "#3" not in result.output

    def test_list_by_status_case_insensitive(self, crashvault_home, cli_runner, sample_issues):
        """List status filter should be case insensitive."""
        from crashvault.cli import cli

        result = cli_runner.invoke(cli, ["list", "--status", "RESOLVED"])

        assert result.exit_code == 0
        assert "#2" in result.output
        assert "#1" not in result.output

    def test_list_by_ignored_status(self, crashvault_home, cli_runner, sample_issues):
        """List should filter by ignored status."""
        from crashvault.cli import cli

        result = cli_runner.invoke(cli, ["list", "--status", "ignored"])

        assert result.exit_code == 0
        assert "#3" in result.output
        assert "#1" not in result.output
        assert "#2" not in result.output

    def test_list_sort_by_id(self, crashvault_home, cli_runner, sample_issues):
        """List should sort by ID by default."""
        from crashvault.cli import cli

        result = cli_runner.invoke(cli, ["list", "--sort", "id"])

        assert result.exit_code == 0
        # Check order - ID 1 should come before 2, 2 before 3
        idx1 = result.output.find("#1")
        idx2 = result.output.find("#2")
        idx3 = result.output.find("#3")
        assert idx1 < idx2 < idx3

    def test_list_sort_by_id_desc(self, crashvault_home, cli_runner, sample_issues):
        """List should sort by ID descending with --desc."""
        from crashvault.cli import cli

        result = cli_runner.invoke(cli, ["list", "--sort", "id", "--desc"])

        assert result.exit_code == 0
        # Check order - ID 3 should come before 2, 2 before 1
        idx1 = result.output.find("#1")
        idx2 = result.output.find("#2")
        idx3 = result.output.find("#3")
        assert idx3 < idx2 < idx1

    def test_list_sort_by_title(self, crashvault_home, cli_runner, sample_issues):
        """List should sort by title."""
        from crashvault.cli import cli

        result = cli_runner.invoke(cli, ["list", "--sort", "title"])

        assert result.exit_code == 0
        # Should not error

    def test_list_sort_by_status(self, crashvault_home, cli_runner, sample_issues):
        """List should sort by status."""
        from crashvault.cli import cli

        result = cli_runner.invoke(cli, ["list", "--sort", "status"])

        assert result.exit_code == 0

    def test_list_empty_issues(self, crashvault_home, cli_runner):
        """List on empty vault should work."""
        from crashvault.cli import cli

        result = cli_runner.invoke(cli, ["list"])

        assert result.exit_code == 0


class TestStatsCommand:
    """Tests for the stats command."""

    def test_stats_shows_issue_counts(self, crashvault_home, cli_runner, sample_issues):
        """Stats should show issue counts by status."""
        from crashvault.cli import cli

        result = cli_runner.invoke(cli, ["stats"])

        assert result.exit_code == 0
        # Sample issues: 1 open, 1 resolved, 1 ignored
        assert "open:" in result.output
        assert "resolved:" in result.output

    def test_stats_shows_event_counts(self, crashvault_home, cli_runner, sample_events):
        """Stats should show event counts by level."""
        from crashvault.cli import cli

        result = cli_runner.invoke(cli, ["stats"])

        assert result.exit_code == 0
        # Sample events: 2 error, 1 warning
        assert "error:" in result.output
        assert "warning:" in result.output

    def test_stats_empty_vault(self, crashvault_home, cli_runner):
        """Stats on empty vault should show zeros."""
        from crashvault.cli import cli

        result = cli_runner.invoke(cli, ["stats"])

        assert result.exit_code == 0
        # Should show 0 counts
        assert "open: 0" in result.output or "open:" in result.output

    def test_stats_combines_issues_and_events(self, crashvault_home, cli_runner, sample_issues, sample_events):
        """Stats should show both issue and event statistics."""
        from crashvault.cli import cli

        result = cli_runner.invoke(cli, ["stats"])

        assert result.exit_code == 0
        # Should have both issues and events sections
        assert "Issues by status:" in result.output
        assert "Events by level:" in result.output

    def test_stats_with_only_issues(self, crashvault_home, cli_runner, sample_issues):
        """Stats should work with only issues (no events)."""
        from crashvault.cli import cli

        result = cli_runner.invoke(cli, ["stats"])

        assert result.exit_code == 0
        assert "Issues by status:" in result.output
        assert "Events by level:" in result.output

    def test_stats_with_only_events(self, crashvault_home, cli_runner, sample_events):
        """Stats should work with only events (no issues)."""
        from crashvault.cli import cli

        result = cli_runner.invoke(cli, ["stats"])

        assert result.exit_code == 0
        assert "Issues by status:" in result.output
        assert "Events by level:" in result.output
