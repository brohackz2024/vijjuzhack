"""Tests for the CLI interface."""
import json
import pytest

from issues_tracker.cli import main


@pytest.fixture
def storage(tmp_path):
    return str(tmp_path / "issues.json")


def test_create_issue_via_cli(storage):
    ret = main(["create", "CLI issue", "--storage", storage])
    assert ret == 0


def test_list_issues_via_cli_empty(storage, capsys):
    ret = main(["list", "--storage", storage])
    assert ret == 0
    out = capsys.readouterr().out
    assert "No issues found" in out


def test_list_issues_via_cli_after_create(storage, capsys):
    main(["create", "My issue", "--storage", storage])
    ret = main(["list", "--storage", storage])
    assert ret == 0
    out = capsys.readouterr().out
    assert "My issue" in out


def test_close_issue_via_cli(storage, capsys):
    main(["create", "Close via CLI", "--storage", storage])
    with open(storage) as f:
        data = json.load(f)
    issue_id = data[0]["id"]
    ret = main(["close", issue_id, "--storage", storage])
    assert ret == 0
    out = capsys.readouterr().out
    assert "Closed" in out


def test_close_nonexistent_issue_via_cli(storage, capsys):
    ret = main(["close", "nonexistent", "--storage", storage])
    assert ret == 1


def test_no_command_prints_help(capsys):
    ret = main([])
    assert ret == 1
