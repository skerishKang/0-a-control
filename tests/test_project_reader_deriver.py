import os
import sys
import tempfile
import unittest
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
import shutil

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


class TestProjectReader(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_project = Path(self.temp_dir) / "test-project"
        self.test_project.mkdir()
        
        (self.test_project / ".git").mkdir()
        subprocess.run(["git", "init"], cwd=str(self.test_project), capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=str(self.test_project), capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=self.test_project, capture_output=True)
        
        self.test_file = self.test_project / "test.txt"
        self.test_file.write_text("test content")
        subprocess.run(["git", "add", "."], cwd=str(self.test_project), capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=str(self.test_project), capture_output=True)
        
        self.new_file = self.test_project / "new_file.py"
        self.new_file.write_text("# new file")
        
        import scripts.project_reader as project_reader
        self.original_config = project_reader.CONFIG_PATH
        self.original_output = project_reader.OUTPUT_PATH
        
        self.config_path = Path(self.temp_dir) / "tracked_projects.json"
        self.output_path = Path(self.temp_dir) / "project_context.json"
        
        self.config_path.write_text(json.dumps({
            "version": 1,
            "projects": [{
                "id": "test-proj",
                "name": "Test Project",
                "path": str(self.test_project),
                "enabled": True,
                "scan_rules": {
                    "recent_days": 7,
                    "max_recent_files": 5,
                    "ignore_patterns": [".git/"]
                },
                "entry_points": {
                    "session_file": ".session/current.md"
                }
            }]
        }))
        
        project_reader.CONFIG_PATH = self.config_path
        project_reader.OUTPUT_PATH = self.output_path

    def tearDown(self):
        shutil.rmtree(self.temp_dir)
        import scripts.project_reader as project_reader
        project_reader.CONFIG_PATH = self.original_config
        project_reader.OUTPUT_PATH = self.original_output

    def test_project_reader_scans_git_state(self):
        import scripts.project_reader as project_reader
        result = project_reader.scan_projects()
        
        self.assertEqual(len(result["projects"]), 1)
        proj = result["projects"][0]
        self.assertTrue(proj["exists"])
        self.assertEqual(proj["git"]["branch"], "master")
        self.assertEqual(proj["git"]["uncommitted_count"], 1)
        self.assertTrue(proj["git"]["has_uncommitted"])

    def test_project_reader_ignores_patterns(self):
        import scripts.project_reader as project_reader
        result = project_reader.scan_projects()
        
        proj = result["projects"][0]
        for f in proj.get("recent_files", []):
            self.assertNotIn(".git/", f["path"])

    def test_project_reader_nonexistent_project(self):
        import scripts.project_reader as project_reader
        
        config = json.loads(self.config_path.read_text())
        config["projects"].append({
            "id": "nonexistent",
            "name": "Nonexistent",
            "path": str(Path(self.temp_dir) / "does-not-exist"),
            "enabled": True
        })
        self.config_path.write_text(json.dumps(config))
        
        result = project_reader.scan_projects()
        
        self.assertEqual(len(result["projects"]), 2)
        nonex = [p for p in result["projects"] if p["id"] == "nonexistent"][0]
        self.assertFalse(nonex["exists"])


class TestQuestDeriver(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        
        self.context_path = Path(self.temp_dir) / "project_context.json"
        self.output_path = Path(self.temp_dir) / "quest_suggestions.json"
        
        import scripts.quest_deriver as quest_deriver
        self.original_context = quest_deriver.CONTEXT_PATH
        self.original_output = quest_deriver.OUTPUT_PATH
        
        quest_deriver.CONTEXT_PATH = self.context_path
        quest_deriver.OUTPUT_PATH = self.output_path

    def tearDown(self):
        import scripts.quest_deriver as quest_deriver
        quest_deriver.CONTEXT_PATH = self.original_context
        quest_deriver.OUTPUT_PATH = self.original_output
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_deriver_generates_uncommitted_suggestion(self):
        self.context_path.write_text(json.dumps({
            "scanned_at": datetime.now().isoformat(),
            "projects": [{
                "id": "test-proj",
                "name": "Test Project",
                "exists": True,
                "git": {
                    "branch": "feature/test",
                    "uncommitted_count": 3,
                    "has_uncommitted": True,
                    "recent_commits": []
                },
                "recent_files": [],
                "entry_point": {"exists": False}
            }]
        }))
        
        import scripts.quest_deriver as quest_deriver
        result = quest_deriver.derive_suggestions()
        
        self.assertEqual(len(result["suggestions"]), 1)
        s = result["suggestions"][0]
        self.assertEqual(s["signal"], "git_uncommitted")
        self.assertIn("3", s["title"])
        self.assertIn("source_project", s)
        self.assertIn("completion_criteria", s)

    def test_deriver_generates_session_resume_suggestion(self):
        self.context_path.write_text(json.dumps({
            "scanned_at": datetime.now().isoformat(),
            "projects": [{
                "id": "test-proj",
                "name": "Test Project",
                "exists": True,
                "git": {
                    "branch": "main",
                    "uncommitted_count": 0,
                    "has_uncommitted": False,
                    "recent_commits": []
                },
                "recent_files": [],
                "entry_point": {
                    "exists": True,
                    "type": "session",
                    "entry_text": "Continue implementing filter"
                }
            }]
        }))
        
        import scripts.quest_deriver as quest_deriver
        result = quest_deriver.derive_suggestions()
        
        self.assertEqual(len(result["suggestions"]), 1)
        s = result["suggestions"][0]
        self.assertEqual(s["signal"], "session_resume")
        self.assertIn("Continue implementing filter", s["title"])

    def test_deriver_empty_for_nonexistent_project(self):
        self.context_path.write_text(json.dumps({
            "scanned_at": datetime.now().isoformat(),
            "projects": [{
                "id": "test-proj",
                "name": "Test Project",
                "exists": False,
                "scan_error": "path not found"
            }]
        }))
        
        import scripts.quest_deriver as quest_deriver
        result = quest_deriver.derive_suggestions()
        
        self.assertEqual(len(result["suggestions"]), 0)

    def test_deriver_priority_ordering(self):
        self.context_path.write_text(json.dumps({
            "scanned_at": datetime.now().isoformat(),
            "projects": [
                {
                    "id": "stale-proj",
                    "name": "Stale Project",
                    "exists": True,
                    "git": {"branch": "feature/stale", "uncommitted_count": 0, "recent_commits": [{"date": (datetime.now() - timedelta(days=20)).isoformat()}]},
                    "recent_files": [],
                    "entry_point": {"exists": False}
                },
                {
                    "id": "active-proj",
                    "name": "Active Project",
                    "exists": True,
                    "git": {"branch": "main", "uncommitted_count": 2, "recent_commits": []},
                    "recent_files": [],
                    "entry_point": {"exists": False}
                },
                {
                    "id": "resume-proj",
                    "name": "Resume Project",
                    "exists": True,
                    "git": {"branch": "main", "uncommitted_count": 0, "recent_commits": []},
                    "recent_files": [],
                    "entry_point": {"exists": True, "type": "session", "entry_text": "Continue feature X"}
                }
            ]
        }))
        
        import scripts.quest_deriver as quest_deriver
        result = quest_deriver.derive_suggestions()
        
        self.assertEqual(len(result["suggestions"]), 3)
        self.assertEqual(result["suggestions"][0]["signal"], "session_resume")
        self.assertEqual(result["suggestions"][1]["signal"], "git_uncommitted")
        self.assertEqual(result["suggestions"][2]["signal"], "stale_branch")
        
        # Verify internal metadata is not exposed
        for s in result["suggestions"]:
            self.assertNotIn("_sort_priority", s)
            self.assertNotIn("rank", s)


if __name__ == "__main__":
    unittest.main()
