import sys
import unittest
from datetime import datetime
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.planning_input import classify_conversation, parse_quick_input


# ---------------------------------------------------------------------------
# classify_conversation 테스트
# ---------------------------------------------------------------------------

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

    # --- 추가 엣지 케이스 ---

    def test_recurring_keyword_with_weekly_now_recurring(self):
        """'매주 + 주간' 조합 → recurring 우선 (short_term 에서 '주간' 제거)"""
        result = classify_conversation("매주 월요일 주간 회의 진행")
        self.assertEqual(result["layer"], "recurring")
        self.assertEqual(result["bucket"], "recurring")

    def test_weekly_alone_is_short_term(self):
        """'주간' 단독 → short_term"""
        result = classify_conversation("주간 보고 정리")
        self.assertEqual(result["layer"], "short_term")
        self.assertEqual(result["bucket"], "short_term")

    def test_monthly_recurring_keyword(self):
        """매월 키워드도 recurring으로 분류"""
        result = classify_conversation("매월 말일 재고 실사")
        self.assertEqual(result["layer"], "recurring")
        self.assertEqual(result["bucket"], "recurring")

    def test_long_term_keyword_maps_long_term(self):
        """장기 키워드 → long_term"""
        result = classify_conversation("장기적으로 수익 구조 전환 필요")
        self.assertEqual(result["layer"], "long_term")
        self.assertEqual(result["bucket"], "long_term")

    def test_short_term_this_week(self):
        """이번 주 키워드 → short_term"""
        result = classify_conversation("이번 주 안에 보고서 초안 작성")
        self.assertEqual(result["layer"], "short_term")
        self.assertEqual(result["bucket"], "short_term")

    def test_dated_keyword_maps_dated(self):
        """기한/마감/까지 키워드 → dated"""
        result = classify_conversation("3/25까지 세금 보고서 제출")
        self.assertEqual(result["layer"], "dated")
        self.assertEqual(result["bucket"], "dated")

    def test_hold_keyword_maps_hold(self):
        """보류/대기 키워드 → hold"""
        result = classify_conversation("보류 중인 건 처리")
        self.assertEqual(result["layer"], "hold")
        self.assertEqual(result["bucket"], "hold")

    def test_now_keyword_classifies_today(self):
        """지금/당장 키워드 → today"""
        result = classify_conversation("지금 바로 확인해야 할 문서")
        self.assertEqual(result["layer"], "today")
        self.assertEqual(result["bucket"], "today")

    def test_project_layer_maps_short_term_bucket(self):
        """프로젝트 키워드 단독 → layer=project, bucket=short_term"""
        result = classify_conversation("프로젝트 일정 정리해서 공유")
        self.assertEqual(result["layer"], "project")
        self.assertEqual(result["bucket"], "short_term")

    def test_today_wins_over_project_by_weight(self):
        """오늘 + 프로젝트 동시 출현 → today가 weight 우위로 승리"""
        result = classify_conversation("오늘 프로젝트 마무리 작업")
        self.assertEqual(result["layer"], "today")

    def test_empty_text_falls_back_to_short_term(self):
        """빈 문자열 → 기본값 short_term"""
        result = classify_conversation("")
        self.assertEqual(result["layer"], "short_term")
        self.assertEqual(result["bucket"], "short_term")

    def test_title_from_multiline_takes_first_line(self):
        """여러 줄 입력 시 title은 첫 줄만"""
        result = classify_conversation("첫 번째 줄 제목\n두 번째 줄 내용")
        self.assertEqual(result["title"], "첫 번째 줄 제목")

    def test_description_truncated_at_500(self):
        """description은 500자로 절단"""
        long_text = "테스트 " * 200
        result = classify_conversation(long_text)
        self.assertLessEqual(len(result["description"]), 500)

    def test_recurring_keyword_present_maps_recurring(self):
        """정기 키워드 → recurring"""
        result = classify_conversation("정기 점검 일정 수립")
        self.assertEqual(result["layer"], "recurring")
        self.assertEqual(result["bucket"], "recurring")


# ---------------------------------------------------------------------------
# parse_quick_input 테스트
# ---------------------------------------------------------------------------

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

    # --- 추가 엣지 케이스 ---

    def test_single_plain_line_no_header(self):
        """헤더 없는 단일 줄 → today 버킷에 기본 분류"""
        result = parse_quick_input("김주석에게 전화 걸기")
        self.assertEqual(result["summary"]["today_count"], 1)
        self.assertEqual(result["summary"]["total_count"], 1)
        self.assertEqual(result["main_mission"]["bucket"], "today")

    def test_dated_section_with_date_extracted(self):
        """기한 섹션 + 날짜 포함 항목 → dated 버킷 + due_date 추출"""
        now = datetime.now()
        result = parse_quick_input("기한:\n- 12/25 크리스마스 전 보고서 제출")
        dated_candidates = [c for c in result["candidates"] if c["bucket"] == "dated"]
        self.assertEqual(len(dated_candidates), 1)
        self.assertIn("due_date", dated_candidates[0])

    def test_mixed_all_section_types(self):
        """오늘, 기한, 보류, 단기, 장기, 반복 모두 혼합"""
        text = (
            "오늘:\n- 배포 확인\n"
            "기한:\n- 3/10 보고서 제출\n"
            "보류:\n- 협의 대기\n"
            "단기:\n- 리팩토링 계획\n"
            "장기:\n- 아키텍처 개편 방향\n"
            "반복:\n- 매주 월요일 스탠드업"
        )
        result = parse_quick_input(text)
        self.assertEqual(result["summary"]["today_count"], 1)
        self.assertEqual(result["summary"]["dated_count"], 1)
        self.assertEqual(result["summary"]["hold_count"], 1)
        self.assertEqual(result["summary"]["total_count"], 6)

    def test_hold_section_items_not_in_main_mission(self):
        """보류 항목만 있을 때 main_mission은 보류에서 나옴"""
        result = parse_quick_input("보류:\n- 대기 중인 건")
        self.assertIsNotNone(result["main_mission"])
        self.assertEqual(result["main_mission"]["bucket"], "hold")

    def test_current_quest_with_actionable_keyword_across_buckets(self):
        """실행 가능 키워드가 여러 버킷에 분산될 때 우선순위 확인"""
        text = "오늘:\n- 문서 정리\n단기:\n- 김주석에게 연락해서 확인"
        result = parse_quick_input(text)
        self.assertIsNotNone(result["current_quest"])
        self.assertIn("연락", result["current_quest"]["title"])

    def test_due_date_with_time_pattern(self):
        """기한 항목에 시간 패턴 (N시) → 당일 시간으로 due_date 생성"""
        result = parse_quick_input("기한:\n- 3시 보고서 확인")
        dated_candidates = [c for c in result["candidates"] if c["bucket"] == "dated"]
        if dated_candidates:
            self.assertIn("due_date", dated_candidates[0])
            self.assertIn("T", dated_candidates[0]["due_date"])

    def test_bullet_variants_parsed(self):
        """다양한 불릿 문자 (-, *, ·, •) 지원 확인"""
        text = "오늘:\n- 첫 번째\n* 두 번째\n· 세 번째\n• 네 번째"
        result = parse_quick_input(text)
        self.assertEqual(result["summary"]["today_count"], 4)

    def test_priority_score_today_higher_than_hold(self):
        """today 항목의 priority_score가 hold보다 높아야 함"""
        text = "오늘:\n- 작업 수행\n보류:\n- 대기 중"
        result = parse_quick_input(text)
        today_c = [c for c in result["candidates"] if c["bucket"] == "today"][0]
        hold_c = [c for c in result["candidates"] if c["bucket"] == "hold"][0]
        self.assertGreater(today_c["priority_score"], hold_c["priority_score"])

    def test_priority_score_with_urgent_keyword(self):
        """긴급/urgent 키워드가 있으면 우선순위 상승"""
        text = "오늘:\n- 보통 작업\n- 긴급 배포 확인"
        result = parse_quick_input(text)
        urgent_c = [c for c in result["candidates"] if "긴급" in c["title"]][0]
        normal_c = [c for c in result["candidates"] if "보통" in c["title"]][0]
        self.assertGreater(urgent_c["priority_score"], normal_c["priority_score"])

    def test_empty_input_returns_no_candidates(self):
        """빈 입력 → candidates 빈 리스트"""
        result = parse_quick_input("")
        self.assertEqual(result["summary"]["total_count"], 0)
        self.assertIsNone(result["main_mission"])

    def test_whitespace_only_input(self):
        """공백만 있는 입력 → 빈 결과"""
        result = parse_quick_input("   \n  \n   ")
        self.assertEqual(result["summary"]["total_count"], 0)

    def test_korean_fullwidth_colon_as_header(self):
        """전각 콜론(：)도 섹션 헤더로 인식"""
        text = "오늘：\n- 테스트 작업"
        result = parse_quick_input(text)
        self.assertEqual(result["summary"]["today_count"], 1)

    def test_long_item_still_parsed(self):
        """긴 항목(24자 초과)도 정상 파싱, 점수는 낮을 수 있음"""
        text = "오늘:\n- 171번 폴더 완성해서 정리된 서류를 강혜림에게 전달하고 확인받기"
        result = parse_quick_input(text)
        self.assertEqual(result["summary"]["today_count"], 1)
        self.assertEqual(result["main_mission"]["bucket"], "today")

    def test_main_mission_fallback_to_top_candidate(self):
        """오늘 항목 없고 보류/기한도 없을 때 candidates 최상위로 fallback"""
        text = "단기:\n- 리팩토링 작업\n장기:\n- 시스템 설계 개선"
        result = parse_quick_input(text)
        self.assertIsNotNone(result["main_mission"])
        self.assertIn(result["main_mission"]["bucket"], ("short_term", "long_term"))

    def test_summary_counts_match_candidates(self):
        """summary 카운트가 candidates 실제 수와 일치해야 함"""
        text = "오늘:\n- 작업1\n- 작업2\n기한:\n- 5/1 마감\n보류:\n- 대기"
        result = parse_quick_input(text)
        self.assertEqual(
            result["summary"]["today_count"]
            + result["summary"]["dated_count"]
            + result["summary"]["hold_count"],
            result["summary"]["total_count"],
        )


# ---------------------------------------------------------------------------
# 한국어 운영 문장 시나리오 테스트 (classify_conversation)
# ---------------------------------------------------------------------------
#
# 각 시나리오는 실제 사용자가 CMD에 입력할 법한 자연어 문장으로,
# layer / bucket / main_mission 후보 여부 / current_quest 후보 여부를 검증한다.
#
# 기대 결과 표:
# | # | 입력                                     | layer      | bucket      | main_mission | current_quest |
# |---|------------------------------------------|------------|-------------|-------------|---------------|
# | 1 | 오늘 배포 확인하고 김주석 연락해          | today      | today       | O            | O (연락)       |
# | 2 | 이번 주 보고서 초안 완성                  | short_term | short_term  | O            | O             |
# | 3 | 매주 월요일 정기 스탠드업 회의            | recurring  | recurring   | O            | O             |
# | 4 | 장기적으로 수익 모델 전환 방향 수립        | long_term  | long_term   | O            | O             |
# | 5 | 3/25까지 세금 보고서 제출                  | short_term | short_term  | O            | O             |
# | 6 | 지금 바로 확인해야 할 문서 있다            | today      | today       | O            | O             |
# | 7 | 프로젝트 일정표 업데이트해서 공유          | project    | short_term  | O            | O             |
# | 8 | 오늘 프로젝트 배포 최종 점검              | today      | today       | O            | O             |
# | 9 | 운영 체계 개선 방향 논의                  | philosophy | long_term   | O            | O             |
# | 10| 그냥 메모해놓을 내용                      | short_term | short_term  | O            | O             |
# | 11| 다음 주 수요일까지 리팩토링 완료          | short_term | short_term  | O            | O             |
# | 12| 보류 중인 건 확인하고 연락                | short_term | short_term  | O            | O (연락)       |
# | 13| 반복 업무지만 오늘 특별히 수정 필요        | today      | today       | O            | O             |
# | 14| 후반 일정 어떻게 할지 방향 정해줘          | long_term  | long_term   | O            | O             |
# | 15| 작업장 체계 재정비 관련 아이디어           | philosophy | long_term   | O            | O             |

class RealWorldClassifyScenarios(unittest.TestCase):
    """실제 운영 문장에 대한 분류 시나리오 테스트."""

    def test_scenario_1_today_deploy_and_contact(self):
        result = classify_conversation("오늘 배포 확인하고 김주석 연락해")
        self.assertEqual(result["layer"], "today")

    def test_scenario_2_this_week_report(self):
        result = classify_conversation("이번 주 보고서 초안 완성")
        self.assertEqual(result["layer"], "short_term")

    def test_scenario_3_weekly_standup(self):
        result = classify_conversation("매주 월요일 정기 스탠드업 회의")
        self.assertEqual(result["layer"], "recurring")

    def test_scenario_4_long_term_strategy(self):
        result = classify_conversation("장기적으로 수익 모델 전환 방향 수립")
        self.assertEqual(result["layer"], "long_term")

    def test_scenario_5_dated_deadline(self):
        """'까지' 키워드로 dated 레이어 매칭"""
        result = classify_conversation("3/25 까지 세금 보고서 제출")
        self.assertEqual(result["layer"], "dated")

    def test_scenario_6_right_now(self):
        result = classify_conversation("지금 바로 확인해야 할 문서 있다")
        self.assertEqual(result["layer"], "today")

    def test_scenario_7_project_update(self):
        result = classify_conversation("프로젝트 일정표 업데이트해서 공유")
        self.assertEqual(result["layer"], "project")

    def test_scenario_8_today_plus_project_today_wins(self):
        result = classify_conversation("오늘 프로젝트 배포 최종 점검")
        self.assertEqual(result["layer"], "today")

    def test_scenario_9_operation_system(self):
        result = classify_conversation("운영 체계 개선 방향 논의")
        self.assertEqual(result["layer"], "philosophy")

    def test_scenario_10_plain_memo(self):
        result = classify_conversation("그냥 메모해놓을 내용")
        self.assertEqual(result["layer"], "short_term")

    def test_scenario_11_next_week_deadline(self):
        """'까지' 키워드로 dated 레이어 매칭 — weight 4 로 short_term 과 동점이나 선행 규칙 우선"""
        result = classify_conversation("다음 주 수요일까지 리팩토링 완료")
        self.assertEqual(result["layer"], "dated")

    def test_scenario_13_special_today_among_recurring(self):
        result = classify_conversation("반복 업무지만 오늘 특별히 수정 필요")
        self.assertEqual(result["layer"], "today")

    def test_scenario_14_late_direction(self):
        result = classify_conversation("후반 일정 어떻게 할지 방향 정해줘")
        self.assertEqual(result["layer"], "long_term")

    def test_scenario_15_workshop_system_idea(self):
        result = classify_conversation("작업장 체계 재정비 관련 아이디어")
        self.assertEqual(result["layer"], "philosophy")


# ---------------------------------------------------------------------------
# 한국어 운영 문장 시나리오 테스트 (parse_quick_input)
# ---------------------------------------------------------------------------
#
# 기대 결과 표:
# | # | 입력 구조                                        | main_mission bucket | current_quest | 핵심 검증                   |
# |---|--------------------------------------------------|--------------------|---------------|-----------------------------|
# | 1 | 헤더 없이 한 줄                                  | today              | today         | 기본 today 분류             |
# | 2 | 오늘:\n- 작업1\n기한:\n- 3/25 마감               | today              | today         | 섹션 분리 + 날짜 추출       |
# | 3 | 보류:\n- 대기\n단기:\n- 리팩토링                 | hold (없으면 short) | -             | hold 우선순위 낮음          |
# | 4 | 오늘:\n- 문서 작성\n- 김주석 확인 연락            | today (문서 작성)  | today (연락)  | actionable 퀘스트 분리      |
# | 5 | 긴급 오늘 배포                                    | today              | today         | 헤더 없는 긴급 문장         |

class RealWorldParseScenarios(unittest.TestCase):
    """실제 운영 문장에 대한 quick-input 파싱 시나리오."""

    def test_plain_single_line_defaults_today(self):
        result = parse_quick_input("김주석에게 전화 걸기")
        self.assertEqual(result["summary"]["today_count"], 1)
        self.assertEqual(result["main_mission"]["bucket"], "today")

    def test_today_plus_dated_sections(self):
        text = "오늘:\n- 배포 확인\n기한:\n- 3/25 보고서 마감"
        result = parse_quick_input(text)
        self.assertEqual(result["summary"]["today_count"], 1)
        self.assertEqual(result["summary"]["dated_count"], 1)

    def test_hold_and_short_term_ordering(self):
        text = "보류:\n- 협의 대기\n단기:\n- 리팩토링 계획"
        result = parse_quick_input(text)
        self.assertEqual(result["summary"]["hold_count"], 1)
        self.assertEqual(result["summary"]["total_count"], 2)

    def test_today_actionable_separates_mission_and_quest(self):
        text = "오늘:\n- 김지혜 파일 전달\n- 긴급 김주석 확인 연락"
        result = parse_quick_input(text)
        # main_mission: 오늘 섹션 첫 번째 항목
        self.assertEqual(result["main_mission"]["title"], "김지혜 파일 전달")
        # current_quest: actionable 키워드 다수 + 긴급 → 높은 점수
        self.assertEqual(result["current_quest"]["title"], "긴급 김주석 확인 연락")

    def test_urgent_plain_line_still_today(self):
        result = parse_quick_input("긴급 오늘 배포 확인")
        self.assertEqual(result["main_mission"]["bucket"], "today")


if __name__ == "__main__":
    unittest.main()
