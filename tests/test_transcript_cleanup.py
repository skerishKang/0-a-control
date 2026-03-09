from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT_DIR / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from scripts.import_transcript import strip_ansi
from scripts.session_summary import summarize_transcript


class TranscriptCleanupTests(unittest.TestCase):
    def test_strip_ansi_removes_osc_sequences(self) -> None:
        raw = "Explain this codebase\x1b]10;?\x1b\\\x1b]11;?\x1b\\"
        self.assertEqual(strip_ansi(raw), "Explain this codebase")

    def test_summarize_transcript_ignores_launcher_noise(self) -> None:
        content = "\n".join(
            [
                "■ Conversation interrupted - tell the model what to do differently.",
                "Something went wrong? Hit `/feedback` to report the issue.",
                "Tip: NEW: Use ChatGPT Apps (Connectors) in Codex via $ mentions.",
                "gpt-5.4 medium · 100% left · /mnt/g/Ddrive/BatangD...",
                "현재 폴더와 파일 점검해주고 수정보완할거 찾아줘",
                "Resume work in project `0-a-control`.",
            ]
        )

        summary = summarize_transcript(content, project_key="0-a-control")

        self.assertNotIn("Conversation interrupted", summary)
        self.assertNotIn("ChatGPT Apps", summary)
        self.assertIn("현재 폴더와 파일 점검해주고 수정보완할거 찾아줘", summary)


if __name__ == "__main__":
    unittest.main()
