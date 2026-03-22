import unittest

from scripts.server import classify_conversation, parse_quick_input


class ClassifyConversationTests(unittest.TestCase):
    def test_today_keyword_prefers_today_layer(self) -> None:
        result = classify_conversation("오늘 배포 확인")
        self.assertEqual(result["layer"], "today")
        self.assertEqual(result["bucket"], "today")

    def test_project_and_philosophy_prefers_philosophy_layer(self) -> None:
        result = classify_conversation("프로젝트 운영 철학 정리")
        self.assertEqual(result["layer"], "philosophy")
        self.assertEqual(result["bucket"], "long_term")

    def test_philosophy_without_project_maps_to_long_term(self) -> None:
        result = classify_conversation("운영 철학과 협업 원칙 정리")
        self.assertEqual(result["layer"], "philosophy")
        self.assertEqual(result["bucket"], "long_term")

    def test_quick_input_sections_keep_today_and_short_term(self) -> None:
        text = "오늘:\n- 배포 확인\n단기:\n- 리팩토링"
        result = parse_quick_input(text)
        buckets = [candidate["bucket"] for candidate in result["candidates"]]
        self.assertIn("today", buckets)
        self.assertIn("short_term", buckets)


if __name__ == "__main__":
    unittest.main()
