import unittest

from scripts import operations_summary


class OperationsSummaryTests(unittest.TestCase):
    def test_build_operations_summary_returns_classified_payload(self):
        github_summary = {
            "repository": {"full_name": "owner/example"},
            "counts": {"open_issues": 1},
            "open_issues": [{"number": 1, "state": "open", "title": "Blocked task", "labels": []}],
            "open_pull_requests": [],
            "recent_closed_pull_requests": [],
            "rate_limit": {"repo": {"remaining": "59"}},
        }

        result = operations_summary.build_operations_summary(
            github_summary_loader=lambda: github_summary
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["source_status"]["github"], "ok")
        self.assertEqual(result["source_status"]["classifier"], "ok")
        self.assertEqual(result["repository"]["full_name"], "owner/example")
        self.assertEqual(
            result["open_issues"][0]["classification"]["status"],
            "BLOCKED",
        )
        self.assertEqual(result["rate_limit"]["repo"]["remaining"], "59")
        self.assertIn("generated_at", result)

    def test_build_operations_summary_returns_structured_github_error(self):
        def broken_loader():
            raise RuntimeError("GitHub API error 403: rate limit")

        result = operations_summary.build_operations_summary(
            github_summary_loader=broken_loader
        )

        self.assertFalse(result["ok"])
        self.assertEqual(result["source_status"]["github"], "error")
        self.assertEqual(result["source_status"]["classifier"], "not_run")
        self.assertIn("rate limit", result["source_status"]["message"])
        self.assertEqual(result["open_issues"], [])

    def test_build_operations_summary_returns_structured_classifier_error(self):
        github_summary = {
            "repository": {"full_name": "owner/example"},
            "counts": {"open_issues": 1},
            "open_issues": [{"number": 1}],
            "open_pull_requests": [],
            "recent_closed_pull_requests": [],
            "rate_limit": {},
        }

        def broken_classifier(_summary):
            raise RuntimeError("classifier failed")

        result = operations_summary.build_operations_summary(
            github_summary_loader=lambda: github_summary,
            classifier=broken_classifier,
        )

        self.assertFalse(result["ok"])
        self.assertEqual(result["source_status"]["github"], "ok")
        self.assertEqual(result["source_status"]["classifier"], "error")
        self.assertEqual(result["repository"]["full_name"], "owner/example")
        self.assertEqual(result["open_issues"], [{"number": 1}])


if __name__ == "__main__":
    unittest.main()
