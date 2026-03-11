"""Tests for the issue tracker."""
import json
import os
import pytest

from issues_tracker.tracker import Issue, IssueTracker


@pytest.fixture
def storage(tmp_path):
    return str(tmp_path / "issues.json")


@pytest.fixture
def tracker(storage):
    return IssueTracker(storage_path=storage)


class TestIssueCreation:
    def test_create_issue_returns_issue(self, tracker):
        issue = tracker.create_issue("Fix login bug")
        assert isinstance(issue, Issue)

    def test_create_issue_sets_title(self, tracker):
        issue = tracker.create_issue("Fix login bug")
        assert issue.title == "Fix login bug"

    def test_create_issue_default_status_open(self, tracker):
        issue = tracker.create_issue("Fix login bug")
        assert issue.status == "open"

    def test_create_issue_strips_whitespace_from_title(self, tracker):
        issue = tracker.create_issue("  Fix login bug  ")
        assert issue.title == "Fix login bug"

    def test_create_issue_with_description(self, tracker):
        issue = tracker.create_issue("Fix login bug", description="Details here")
        assert issue.description == "Details here"

    def test_create_issue_assigns_unique_ids(self, tracker):
        issue1 = tracker.create_issue("Issue 1")
        issue2 = tracker.create_issue("Issue 2")
        assert issue1.id != issue2.id

    def test_create_issue_empty_title_raises(self, tracker):
        with pytest.raises(ValueError):
            tracker.create_issue("")

    def test_create_issue_blank_title_raises(self, tracker):
        with pytest.raises(ValueError):
            tracker.create_issue("   ")

    def test_create_issue_persists_to_file(self, storage):
        tracker = IssueTracker(storage_path=storage)
        tracker.create_issue("Persisted issue")
        assert os.path.exists(storage)
        with open(storage) as f:
            data = json.load(f)
        assert len(data) == 1
        assert data[0]["title"] == "Persisted issue"


class TestListIssues:
    def test_list_returns_all_issues(self, tracker):
        tracker.create_issue("Issue 1")
        tracker.create_issue("Issue 2")
        assert len(tracker.list_issues()) == 2

    def test_list_empty_when_no_issues(self, tracker):
        assert tracker.list_issues() == []

    def test_list_filter_by_status(self, tracker):
        issue = tracker.create_issue("Issue 1")
        tracker.create_issue("Issue 2")
        tracker.close_issue(issue.id)

        open_issues = tracker.list_issues(status="open")
        closed_issues = tracker.list_issues(status="closed")

        assert len(open_issues) == 1
        assert len(closed_issues) == 1


class TestCloseIssue:
    def test_close_issue_changes_status(self, tracker):
        issue = tracker.create_issue("Close me")
        tracker.close_issue(issue.id)
        updated = tracker.get_issue(issue.id)
        assert updated.status == "closed"

    def test_close_nonexistent_issue_returns_none(self, tracker):
        result = tracker.close_issue("nonexistent-id")
        assert result is None

    def test_close_issue_by_partial_id(self, tracker):
        issue = tracker.create_issue("Close me by prefix")
        tracker.close_issue(issue.id[:8])
        updated = tracker.get_issue(issue.id)
        assert updated.status == "closed"


class TestPersistence:
    def test_issues_reload_from_file(self, storage):
        tracker1 = IssueTracker(storage_path=storage)
        tracker1.create_issue("Reload me")

        tracker2 = IssueTracker(storage_path=storage)
        issues = tracker2.list_issues()
        assert len(issues) == 1
        assert issues[0].title == "Reload me"
