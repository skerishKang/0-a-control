import sys
import unittest
from datetime import datetime
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.planning_input import classify_conversation, parse_quick_input


class ClassifyConversationTests(unittest.TestCase):
    def test_today_keyword_classifies_today(self):
        result = classify_conversation("오늘 배포 확인")
        self.assertEqual(result["layer"], "today")
        self.assertEqual(result["bucket"], "today")

    def test_project_philosophy_prefers_philosophy_when_hits_are_stronger(self):
        result = classify_conversation("프로젝트 운영 철학 정리")
        self.assertEqual(result["layer"], "philosophy")
        self.assertEqual(result["bucket"], "long_term")

    def test_philosophy_without_project_keywords_maps_long_term(self):
        result = classify_conversation("운영 철학과 협업 원칙 정리")
        self.assertEqual(result["layer"], "philosophy")
        self.assertEqual(result["bucket"], "long_term")

    def test_unmatched_text_falls_back_to_short_term(self):
        result = classify_conversation("별도 키워드 없는 일반 메모")
        self.assertEqual(result["layer"], "short_term")
        self.assertEqual(result["bucket"], "short_term")


class ParseQuickInputTests(unittest.TestCase):
    def test_parses_today_and_short_term_sections(self):
        text = "오늘:\n- 배포 확인\n단기:\n- 리팩토링"
        result = parse_quick_input(text)

        buckets = [candidate["bucket"] for candidate in result["candidates"]]
        self.assertIn("today", buckets)
        self.assertIn("short_term", buckets)
        self.assertEqual(result["summary"]["today_count"], 1)
        self.assertEqual(result["summary"]["total_count"], 2)

    def test_extracts_due_date_from_dated_bucket(self):
        now = datetime.now()
        expected_year = now.year if 3 >= now.month else now.year + 1
        result = parse_quick_input("기한:\n- 3/25 제출")
        dated = next(candidate for candidate in result["candidates"] if candidate["bucket"] == "dated")
        self.assertEqual(dated["due_date"], f"{expected_year}-03-25")

    def test_actionable_today_item_becomes_current_quest(self):
        result = parse_quick_input("오늘:\n- 10시 김주석 연락")
        today = next(candidate for candidate in result["candidates"] if candidate["bucket"] == "today")
        self.assertEqual(result["current_quest"]["title"], today["title"])
        self.assertEqual(result["current_quest"]["bucket"], "today")

    def test_defaults_to_today_when_no_headers_exist(self):
        result = parse_quick_input("김지혜 처리\n김주석 연락")
        self.assertEqual(result["summary"]["today_count"], 2)
        self.assertEqual(result["main_mission"]["bucket"], "today")

    def test_hold_bucket_is_preserved(self):
        result = parse_quick_input("보류:\n- 회신 대기")
        self.assertEqual(result["summary"]["hold_count"], 1)
        self.assertEqual(result["candidates"][0]["bucket"], "hold")

    def test_main_mission_prefers_first_today_item(self):
        result = parse_quick_input(
            "오늘:\n- 171번 폴더 완성해서 정리된 서류 강혜림에게 전달\n- 김주석 연락\n단기:\n- 24-1 폴더 해보면서 개발"
        )
        self.assertEqual(
            result["main_mission"]["title"],
            "171번 폴더 완성해서 정리된 서류 강혜림에게 전달",
        )
        self.assertEqual(result["main_mission"]["bucket"], "today")

    def test_current_quest_prefers_actionable_item(self):
        result = parse_quick_input(
            "오늘:\n- 171번 폴더 완성해서 정리된 서류 강혜림에게 전달\n- 김주석 연락\n단기:\n- 24-1 폴더 해보면서 개발"
        )
        self.assertEqual(result["current_quest"]["title"], "김주석 연락")
        self.assertEqual(result["current_quest"]["bucket"], "today")


if __name__ == "__main__":
    unittest.main()
