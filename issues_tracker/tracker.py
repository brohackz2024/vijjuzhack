"""Core issue tracker module."""
import json
import os
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import List, Optional


@dataclass
class Issue:
    """Represents a single issue."""
    title: str
    description: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "open"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Issue":
        return cls(**data)

    def __str__(self) -> str:
        return f"[{self.id[:8]}] ({self.status}) {self.title}"


class IssueTracker:
    """Manages a collection of issues stored in a JSON file."""

    def __init__(self, storage_path: str = "issues.json"):
        self.storage_path = storage_path
        self._issues: List[Issue] = []
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.storage_path):
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._issues = [Issue.from_dict(item) for item in data]

    def _save(self) -> None:
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump([issue.to_dict() for issue in self._issues], f, indent=2)

    def create_issue(self, title: str, description: str = "") -> Issue:
        """Create a new issue and persist it."""
        if not title or not title.strip():
            raise ValueError("Issue title cannot be empty.")
        issue = Issue(title=title.strip(), description=description)
        self._issues.append(issue)
        self._save()
        return issue

    def list_issues(self, status: Optional[str] = None) -> List[Issue]:
        """Return all issues, optionally filtered by status."""
        if status:
            return [i for i in self._issues if i.status == status]
        return list(self._issues)

    def get_issue(self, issue_id: str) -> Optional[Issue]:
        """Retrieve an issue by its full or partial ID."""
        for issue in self._issues:
            if issue.id.startswith(issue_id):
                return issue
        return None

    def close_issue(self, issue_id: str) -> Optional[Issue]:
        """Close an existing issue by ID."""
        issue = self.get_issue(issue_id)
        if issue:
            issue.status = "closed"
            issue.updated_at = datetime.now(timezone.utc).isoformat()
            self._save()
        return issue
