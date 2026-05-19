from __future__ import annotations

import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from scripts import check_frontend_safety


class StaticAssetVersionGuardTests(unittest.TestCase):
    def _run_checker(self, html: str) -> int:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "index.html").write_text(html, encoding="utf-8")
            output = StringIO()
            with patch("sys.argv", ["check_frontend_safety.py", "--dir", str(root)]):
                with redirect_stdout(output):
                    return check_frontend_safety.main()

    def test_passes_local_assets_with_version_queries(self) -> None:
        status = self._run_checker(
            """
            <link rel="stylesheet" href="/app.css?v=20260519-281-1">
            <script src="/app.js?v=20260519-281-1"></script>
            """
        )
        self.assertEqual(status, 0)

    def test_fails_local_stylesheet_without_version_query(self) -> None:
        status = self._run_checker('<link rel="stylesheet" href="/app.css">')
        self.assertEqual(status, 1)

    def test_fails_local_script_without_version_query(self) -> None:
        status = self._run_checker('<script src="/app.js"></script>')
        self.assertEqual(status, 1)

    def test_ignores_external_assets(self) -> None:
        status = self._run_checker(
            """
            <link rel="stylesheet" href="https://cdn.example.com/app.css">
            <script src="https://cdn.example.com/app.js"></script>
            """
        )
        self.assertEqual(status, 0)

    def test_rejects_incorrect_version_format(self) -> None:
        status = self._run_checker('<script src="/app.js?v=1"></script>')
        self.assertEqual(status, 1)


if __name__ == "__main__":
    unittest.main()
