import unittest
from datetime import datetime, timezone

from scripts import operational_state


class OperationalStateTests(unittest.TestCase):
    def test_closed_issue_is_done(self):
        result = operational_state.classify_issue({"state": "closed", "title": "Done"})

        self.assertEqual(result.status, operational_state.STATUS_DONE)
        self.assertEqual(result.priority, "P3")

    def test_blocked_issue_has_blocked_status(self):
        result = operational_state.classify_issue(
            {"state": "open", "title": "Blocked by missing config", "labels": []}
        )

        self.assertEqual(result.status, operational_state.STATUS_BLOCKED)
        self.assertIn(operational_state.GUARD_CONFIGURATION_MISSING, result.guards)

    def test_validation_issue_requires_validation(self):
        result = operational_state.classify_issue(
            {"state": "open", "title": "Run validation checklist", "labels": []}
        )

        self.assertEqual(result.status, operational_state.STATUS_NEEDS_VALIDATION)
        self.assertIn(operational_state.GUARD_VALIDATION_REQUIRED, result.guards)

    def test_stale_issue_requires_review(self):
        now = datetime(2026, 5, 4, tzinfo=timezone.utc)
        result = operational_state.classify_issue(
            {
                "state": "open",
                "title": "Old task",
                "labels": [],
                "updated_at": "2026-04-01T00:00:00Z",
            },
            now=now,
        )

        self.assertEqual(result.status, operational_state.STATUS_NEEDS_REVIEW)

    def test_open_unmarked_issue_needs_implementation(self):
        result = operational_state.classify_issue(
            {"state": "open", "title": "Add dashboard panel", "labels": []}
        )

        self.assertEqual(result.status, operational_state.STATUS_NEEDS_IMPLEMENTATION)

    def test_draft_pr_is_in_progress(self):
        result = operational_state.classify_pull_request(
            {"state": "open", "draft": True, "title": "feat: work in progress", "labels": []}
        )

        self.assertEqual(result.status, operational_state.STATUS_IN_PROGRESS)
        self.assertIn(operational_state.GUARD_VALIDATION_REQUIRED, result.guards)

    def test_docs_pr_needs_review(self):
        result = operational_state.classify_pull_request(
            {"state": "open", "draft": False, "title": "docs: update manual", "labels": []}
        )

        self.assertEqual(result.status, operational_state.STATUS_NEEDS_REVIEW)
        self.assertIn(operational_state.GUARD_REVIEW_REQUIRED, result.guards)

    def test_merged_pr_is_done(self):
        result = operational_state.classify_pull_request(
            {"state": "closed", "merged_at": "2026-05-04T00:00:00Z", "title": "merged"}
        )

        self.assertEqual(result.status, operational_state.STATUS_DONE)

    def test_summary_classification_adds_counts(self):
        summary = {
            "repository": {"full_name": "owner/example"},
            "counts": {"open_issues": 1, "open_pull_requests": 1},
            "open_issues": [
                {"state": "open", "title": "Blocked task", "labels": [], "number": 1}
            ],
            "open_pull_requests": [
                {"state": "open", "draft": False, "title": "docs: update", "labels": [], "number": 2}
            ],
            "recent_closed_pull_requests": [
                {"state": "closed", "merged_at": "2026-05-04T00:00:00Z", "title": "merged", "number": 3}
            ],
        }

        result = operational_state.classify_github_summary(summary)

        self.assertEqual(result["open_issues"][0]["classification"]["status"], operational_state.STATUS_BLOCKED)
        self.assertEqual(result["open_pull_requests"][0]["classification"]["status"], operational_state.STATUS_NEEDS_REVIEW)
        self.assertEqual(result["recent_closed_pull_requests"][0]["classification"]["status"], operational_state.STATUS_DONE)
        self.assertEqual(result["counts"]["classified_statuses"][operational_state.STATUS_BLOCKED], 1)
        self.assertEqual(result["counts"]["classified_statuses"][operational_state.STATUS_NEEDS_REVIEW], 1)
        self.assertEqual(result["counts"]["classified_statuses"][operational_state.STATUS_DONE], 1)


if __name__ == "__main__":
    unittest.main()
