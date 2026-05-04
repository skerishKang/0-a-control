import os
import unittest
from unittest.mock import Mock, patch

from scripts import github_service


class GitHubServiceTests(unittest.TestCase):
    def test_get_github_config_uses_default_repository(self):
        with patch.dict(os.environ, {}, clear=True):
            config = github_service.get_github_config()

        self.assertEqual(config.repository, "skerishKang/0-a-control")
        self.assertFalse(config.token_configured)

    def test_get_github_config_uses_env_repository_and_token(self):
        with patch.dict(
            os.environ,
            {
                "CONTROL_TOWER_GITHUB_REPOSITORY": "owner/example",
                "CONTROL_TOWER_GITHUB_TOKEN": "token-value",
            },
            clear=True,
        ):
            config = github_service.get_github_config()

        self.assertEqual(config.repository, "owner/example")
        self.assertTrue(config.token_configured)

    def test_get_github_config_falls_back_on_invalid_repository(self):
        with patch.dict(os.environ, {"CONTROL_TOWER_GITHUB_REPOSITORY": "invalid"}, clear=True):
            config = github_service.get_github_config()

        self.assertEqual(config.repository, "skerishKang/0-a-control")

    def test_get_github_summary_normalizes_counts(self):
        responses = [
            {
                "full_name": "owner/example",
                "default_branch": "main",
                "html_url": "https://github.com/owner/example",
                "private": False,
                "updated_at": "2026-01-01T00:00:00Z",
                "pushed_at": "2026-01-01T00:00:00Z",
            },
            [
                {
                    "number": 1,
                    "title": "Issue one",
                    "state": "open",
                    "html_url": "https://github.com/owner/example/issues/1",
                    "created_at": "2026-01-01T00:00:00Z",
                    "updated_at": "2026-01-02T00:00:00Z",
                    "closed_at": None,
                    "comments": 2,
                    "labels": [{"name": "bug", "color": "ff0000", "description": "Bug"}],
                    "user": {"login": "alice", "avatar_url": "avatar", "html_url": "user-url"},
                },
                {
                    "number": 2,
                    "title": "PR masquerading as issue",
                    "state": "open",
                    "pull_request": {},
                },
            ],
            [
                {
                    "number": 3,
                    "title": "Open PR",
                    "state": "open",
                    "draft": True,
                    "html_url": "https://github.com/owner/example/pull/3",
                    "created_at": "2026-01-01T00:00:00Z",
                    "updated_at": "2026-01-02T00:00:00Z",
                    "closed_at": None,
                    "merged_at": None,
                    "base": {"ref": "main", "sha": "base-sha"},
                    "head": {"ref": "feature", "sha": "head-sha"},
                    "user": {"login": "bob", "avatar_url": "avatar", "html_url": "user-url"},
                }
            ],
            [
                {
                    "number": 4,
                    "title": "Closed PR",
                    "state": "closed",
                    "draft": False,
                    "html_url": "https://github.com/owner/example/pull/4",
                    "created_at": "2026-01-01T00:00:00Z",
                    "updated_at": "2026-01-02T00:00:00Z",
                    "closed_at": "2026-01-02T00:00:00Z",
                    "merged_at": "2026-01-02T00:00:00Z",
                    "base": {"ref": "main", "sha": "base-sha"},
                    "head": {"ref": "feature", "sha": "head-sha"},
                    "user": {"login": "carol", "avatar_url": "avatar", "html_url": "user-url"},
                }
            ],
        ]

        def fake_get(*args, **kwargs):
            response = Mock()
            response.status_code = 200
            response.headers = {
                "X-RateLimit-Limit": "60",
                "X-RateLimit-Remaining": "59",
                "X-RateLimit-Reset": "123",
            }
            response.json.return_value = responses.pop(0)
            return response

        with patch.dict(os.environ, {"CONTROL_TOWER_GITHUB_REPOSITORY": "owner/example"}, clear=True):
            with patch.object(github_service.requests, "get", side_effect=fake_get):
                summary = github_service.get_github_summary()

        self.assertEqual(summary["repository"]["full_name"], "owner/example")
        self.assertEqual(summary["counts"]["open_issues"], 1)
        self.assertEqual(summary["counts"]["open_pull_requests"], 1)
        self.assertEqual(summary["counts"]["draft_pull_requests"], 1)
        self.assertEqual(summary["counts"]["recent_closed_pull_requests"], 1)
        self.assertEqual(summary["open_issues"][0]["labels"][0]["name"], "bug")
        self.assertEqual(summary["open_pull_requests"][0]["head"]["sha"], "head-sha")


if __name__ == "__main__":
    unittest.main()
