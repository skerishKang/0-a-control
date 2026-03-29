import pytest
from longest_unique_substring import length_of_longest_substring


class TestLongestUniqueSubstring:
    """가장 긴 반복되지 않는 부분 문자열 길이 계산 테스트"""

    def test_example_cases(self):
        """예상 결과 테스트"""
        assert length_of_longest_substring("abcabcbb") == 3
        assert length_of_longest_substring("안녕안녕하세요") == 5
        assert length_of_longest_substring("") == 0
        assert length_of_longest_substring("   ") == 1

    def test_empty_string(self):
        """빈 문자열"""
        assert length_of_longest_substring("") == 0

    def test_whitespace_only(self):
        """공백만 있는 문자열"""
        assert length_of_longest_substring(" ") == 1
        assert length_of_longest_substring("   ") == 1
        assert length_of_longest_substring("\t\n\r") == 3  # tab, newline, carriage return은 모두 다른 문자

    def test_all_same_characters(self):
        """모든 문자가 동일한 경우"""
        assert length_of_longest_substring("aaaaa") == 1
        assert length_of_longest_substring("ㄱㄱㄱㄱㄱ") == 1
        assert length_of_longest_substring("😀😀😀") == 1

    def test_korean_mixed(self):
        """한글 혼합"""
        assert length_of_longest_substring("안녕안녕하세요") == 5  # "녕하세"
        assert length_of_longest_substring("가나다라가나다라") == 4
        assert length_of_longest_substring("한글한글테스트") == 5  # "글테스"
        assert length_of_longest_substring("ㅎㅏㄴㄱㅡㄹ") == 6  # 모든 자모음이 고유

    def test_unicode_emojis(self):
        """유니코드 이모지"""
        assert length_of_longest_substring("😀😁😂😀😁") == 3  # 최대 길이: "😀😁😂" or "😁😂😀" or "😂😀😁"
        assert length_of_longest_substring("👋🌍🎉👋🌍") == 3  # "👋🌍🎉" or "🌍🎉👋" or "🎉👋🌍"

    def test_english_alphabet(self):
        """영어 알파벳"""
        assert length_of_longest_substring("abcabcbb") == 3
        assert length_of_longest_substring("bbbbb") == 1
        assert length_of_longest_substring("pwwkew") == 3
        assert length_of_longest_substring("abcdef") == 6
        assert length_of_longest_substring("abba") == 2

    def test_case_sensitive(self):
        """대소문자 구분"""
        assert length_of_longest_substring("aA") == 2  # 'a'와 'A'는 다름
        assert length_of_longest_substring("AaAa") == 2

    def test_mixed_unicode(self):
        """혼합 유니코드 문자"""
        assert length_of_longest_substring("a한b글c") == 5
        assert length_of_longest_substring("😀ab한😀") == 4  # "ab한😀"

    def test_single_character(self):
        """단일 문자"""
        assert length_of_longest_substring("a") == 1
        assert length_of_longest_substring("한") == 1
        assert length_of_longest_substring("😀") == 1

    def test_long_string(self):
        """긴 문자열"""
        # 0-9 숫자 문자열을 반복 - 고유 숫자는 10개
        long_string = "0123456789" * 1000
        result = length_of_longest_substring(long_string)
        assert result == 10  # 10개의 고유 숫자

    def test_alternating_patterns(self):
        """번갈아出现 패턴"""
        assert length_of_longest_substring("ababab") == 2
        assert length_of_longest_substring("한영한영") == 2
        assert length_of_longest_substring("121212") == 2

    def test_with_newlines_and_tabs(self):
        """개행 및 탭 문자 포함"""
        assert length_of_longest_substring("a\nb\tc") == 5  # "a\nb\tc"
        assert length_of_longest_substring("a\na") == 2  # 개행 문자도 문자로 처리

    def test_zero_width_characters(self):
        """Zero-width 문자"""
        assert length_of_longest_substring("a\u200bb") == 3  # a, zero-width space, b
        assert length_of_longest_substring("\u200a\u200b\u200c") == 3

    def test_accents_and_diacritics(self):
        """악센트 및 발음 기호"""
        assert length_of_longest_substring("café") == 4  # 'é'는 'e'와 다름
        assert length_of_longest_substring("año") == 3

    def test_performance_stress(self):
        """성능 스트레스 테스트"""
        # 10,000자 길이의 모두 다른 문자 (알파벳 반복)
        stress = "".join(chr(ord('a') + i % 26) for i in range(10000))
        assert length_of_longest_substring(stress) == 26
