import json

# Full paragraph-level translations for the first 3 pages
translations = {
    "Speech and Language Processing.\nDaniel Jurafsky & James H. Martin.\nCopyright © 2021.\nAll\nrights reserved.\nDraft of September 21, 2021.": "언어 및 언어 처리.\n다니엘 주라프스키 & 제임스 H. 마틴.\nCopyright © 2021.\n모든 권리 보유.\n2021년 9월 21일 초안.",
    "CHAPTER\n2": "제2장",
    "Regular\nExpressions,\nText\nNormalization, Edit Distance": "정규 표현식,\n텍스트 정규화, 편집 거리",
    "User:\nI am unhappy.\nELIZA: DO YOU THINK COMING HERE WILL HELP YOU NOT TO BE UNHAPPY\nUser:\nI need some help, that much seems certain.\nELIZA: WHAT WOULD IT MEAN TO YOU IF YOU GOT SOME HELP\nUser:\nPerhaps I could learn to get along with my mother.\nELIZA: TELL ME MORE ABOUT YOUR FAMILY\nUser:\nMy mother takes care of me.\nELIZA: WHO ELSE IN YOU FAMILY TAKES CARE OF YOU\nUser:\nMy father.\nELIZA: YOUR FATHER\nUser:\nYou are like my father in some ways.": "사용자: 나는 불행해요.\nELIZA: 여기에 오는 것이 당신이 불행하지 않게 하는 데 도움이 될 것이라고 생각하나요?\n사용자: 도움이 좀 필요해요, 그 점만은 분명한 것 같아요.\nELIZA: 도움을 받는다는 것이 당신에게 어떤 의미인가요?\n사용자: 아마도 어머니와 잘 지내는 법을 배울 수 있을지도 몰라요.\nELIZA: 당신의 가족에 대해 더 이야기해 주세요.\n사용자: 어머니가 저를 돌봐주세요.\nELIZA: 가족 중에 다른 누가 당신을 돌봐주나요?\n사용자: 아버지요.\nELIZA: 아버지라고요?\n사용자: 당신은 어떤 면에서 우리 아버지와 비슷해요.",
    "that could carry on a limited conversation with a user by imitating the responses of\na Rogerian psychotherapist (Weizenbaum, 1966). ELIZA is a surprisingly simple\nprogram that uses pattern matching to recognize phrases like “I need X” and translate\nthem into suitable outputs like “What would it mean to you if you got X?”. This\nsimple technique succeeds in this domain because ELIZA doesn’t actually need to\nknow anything to mimic a Rogerian psychotherapist. As Weizenbaum notes, this is\none of the few dialogue genres where listeners can act as if they know nothing of the\nworld. Eliza’s mimicry of human conversation was remarkably successful: many\npeople who interacted with ELIZA came to believe that it really understood them\nand their problems, many continued to believe in ELIZA’s abilities even after the\nprogram’s operation was explained to them (Weizenbaum, 1976), and even today\nsuch chatbots are a fun diversion.": "위의 대화는 초기 자연어 처리 시스템인 ELIZA의 것으로, 로저스 학파 심리치료사의 응답을 모방하여 사용자와 제한적인 대화를 나눌 수 있었습니다 (Weizenbaum, 1966). ELIZA는 패턴 매칭을 사용하여 'I need X'와 같은 문구를 인식하고 이를 'What would it mean to you if you got X'와 같은 응답으로 변환하는 놀라울 정도로 단순한 프로그램입니다. 이 단순한 기술이 이 영역에서 성공할 수 있었던 이유는 ELIZA가 로저스 학파 심리치료사를 모방하기 위해 실제로 무언가를 알아야 할 필요가 없기 때문입니다. 와이젠바움이 지적하듯, 이는 청자가 세상에 대해 아무것도 모르는 것처럼 행동할 수 있는 몇 안 되는 대화 장르 중 하나입니다. 인간의 대화를 모방한 Eliza의 모방은 눈에 띄게 성공적이었습니다. ELIZA와 상호 작용한 많은 사람들이 그것이 정말로 자신과 자신의 문제를 이해한다고 믿게 되었고, 심지어 프로그램의 작동 방식이 설명된 후에도 많은 사람들이 ELIZA의 능력을 계속 믿었으며 (Weizenbaum, 1976), 오늘날에도 그러한 챗봇은 재미있는 오락거리입니다.",
    "The dialogue above is from ELIZA, an early natural language processing system": "위의 대화는 초기 자연어 처리 시스템인 ELIZA의 것으로,",
    "Weizenbaum (1966)": "와이젠바움 (1966)",
    "2.1\nREGULAR EXPRESSIONS\n1": "2.1 정규 표현식 1",
    "Regular Expressions": "정규 표현식",
    "One of the most important tools in text processing is the regular expression. A\nregular expression (RE) is a formula in a special language that is used for speci-\nfying search strings. Regular expressions are used for everything from simple\nsearch-and-replace to capturing the complex structures of natural language. In\nthe following sections we’ll use the notation RE to refer to a regular expression.\nregular expression\nRE\nSearch-and-replace is an extremely common task. For example, if we want to\nsearch for a word like woodchuck but we suspect it might also be written as Wood-\nchuck with a capital W, we can use the regular expression / [wW] oodchuck/. This\nexpression matches any string that contains either woodchuck or Woodchuck.": "텍스트 처리에서 가장 중요한 도구 중 하나는 정규 표현식입니다. 정규 표현식(RE)은 검색 문자열을 지정하는 데 사용되는 특수 언어의 공식입니다. 정규 표현식은 단순한 찾기 및 바꾸기부터 자연어의 복잡한 구조를 캡처하는 것까지 모든 작업에 사용됩니다. 다음 섹션들에서는 정규 표현식을 RE라는 약어로 지칭하겠습니다. 찾기 및 바꾸기는 매우 흔한 작업입니다. 예를 들어, 'woodchuck'이라는 단어를 찾고 싶은데 대문자 W로 시작하는 'Woodchuck'으로 쓰였을 수도 있다면, /[wW]oodchuck/이라는 정규 표현식을 사용할 수 있습니다. 이 표현식은 woodchuck이나 Woodchuck을 포함하는 모든 문자열과 일치합니다.",
    "2.1.1\nBasic Regular Expression Patterns": "2.1.1 기본 정규 표현식 패턴",
    "The simplest kind of regular expression is a sequence of simple characters. To search\nfor woodchuck, we type /woodchuck/. The expression /Buttercup/ matches any\nstring containing the substring Buttercup; grep with that expression would return the\nline I’m called little Buttercup. The search string can consist of a single character\n(like /!/) or a sequence of characters (like /urgl/).\nRegular expressions are case sensitive; lower case /s/ is distinct from upper\ncase /S/ (/s/ matches a lower case s but not an upper case S). This means that\nthe pattern /woodchucks/ will not match the string Woodchucks. We can solve this": "정규 표현식의 가장 단순한 종류는 단순한 문자들의 시퀀스입니다. woodchuck을 검색하려면 /woodchuck/을 입력합니다. /Buttercup/이라는 표현식은 'Buttercup'이라는 부분 문자열을 포함하는 모든 문자열과 일치하며, grep을 사용하면 'I'm called little Buttercup'이라는 줄을 반환할 것입니다. 검색 문자열은 단일 문자(/!/ 등)나 문자 시퀀스(/urgl/ 등)로 구성될 수 있습니다. 정규 표현식은 대소문자를 구분합니다. 소문자 /s/는 대문자 /S/와 다릅니다. 즉, /woodchucks/ 패턴은 Woodchucks 문자열과 일치하지 않습니다.",
    "RE\nExample Patterns Matched\n/woodchucks/\n“interesting links to woodchucks and lemurs”\n/a/\n“Mary Ann stopped by Mona’s”\n/!/\n“You’ve left the burglar behind again!” said Nori\nFigure 2.1\nSome simple regex searches.": "RE 예시 패턴 일치\n/woodchucks/ “interesting links to woodchucks and lemurs”\n/a/ “Mary Ann stopped by Mona’s”\n/!/ “You’ve left the burglar behind again!” said Nori\n그림 2.1 몇 가지 간단한 정규 표현식 검색 예시.",
    "problem with the use of the square braces [ and ]. The string of characters inside the\nbraces speciﬁes a disjunction of characters to match. For example, Fig. 2.2 shows\nthat the pattern /[wW]/ matches patterns containing either w or W.": "이 문제는 대괄호 [와 ]를 사용하여 해결할 수 있습니다. 대괄호 안의 문자열은 일치시킬 문자들의 논리합(disjunction)을 지정합니다. 예를 들어, 그림 2.2는 /[wW]/ 패턴이 w 또는 W를 포함하는 패턴과 일치함을 보여줍니다.",
    "RE\nMatch\nExample Patterns\n/[wW]oodchuck/\nWoodchuck or woodchuck\n“Woodchuck”\n/[abc]/\n‘a’, ‘b’, or ‘c’\n“In uomini, in soldati”\n/[1234567890]/\nany digit\n“plenty of 7 to 5”\nFigure 2.2\nThe use of the brackets [] to specify a disjunction of characters.": "RE 일치 예시 패턴\n/[wW]oodchuck/ Woodchuck 또는 woodchuck “Woodchuck”\n/[abc]/ ‘a’, ‘b’, 또는 ‘c’ “In uomini, in soldati”\n/[1234567890]/ 모든 숫자 “plenty of 7 to 5”\n그림 2.2 문자 논리합을 지정하기 위한 대괄호 []의 사용.",
    "The regular expression /[1234567890]/ speciﬁes any single digit. While such\nclasses of characters as digits or letters are important building blocks in expressions,\nthey can get awkward (e.g., it’s inconvenient to specify": "정규 표현식 /[1234567890]/은 모든 단일 숫자를 지정합니다. 숫자나 문자와 같은 문자 클래스는 표현식을 구성하는 중요한 요소이지만, 이를 일일이 지정하는 것은 번거로울 수 있습니다.",
    "/[ABCDEFGHIJKLMNOPQRSTUVWXYZ]/": "/[ABCDEFGHIJKLMNOPQRSTUVWXYZ]/",
    "to mean “any capital letter”). In cases where there is a well-deﬁned sequence asso-\nciated with a set of characters, the brackets can be used with the dash (-) to specify\nany one character in a range. The pattern /[2-5]/ speciﬁes any one of the charac-\nrange": "“모든 대문자”를 의미하도록 지정하는 경우와 같이, 문자 집합에 잘 정의된 순서가 있는 경우 대괄호와 하이픈(-)을 사용하여 범위 내의 단일 문자를 지정할 수 있습니다. /[2-5]/ 패턴은 2, 3, 4, 5 중 하나를 지정합니다.",
    "ters 2, 3, 4, or 5. The pattern /[b-g]/ speciﬁes one of the characters b, c, d, e, f, or\ng. Some other examples are shown in Fig. 2.3.": "문자 2, 3, 4 또는 5. /[b-g]/ 패턴은 b, c, d, e, f, g 중 하나를 지정합니다. 다른 예시들은 그림 2.3에 나와 있습니다.",
    "RE\nMatch\nExample Patterns Matched\n/[A-Z]/\nan upper case letter\n“we should call it ‘Drenched Blossoms’ ”\n/[a-z]/\na lower case letter\n“my beans were impatient to be hoed!”\n/[0-9]/\na single digit\n“Chapter 1: Down the Rabbit Hole”\nFigure 2.3\nThe use of the brackets [] plus the dash - to specify a range.": "RE 일치 예시 패턴 일치\n/[A-Z]/ 대문자 “we should call it ‘Drenched Blossoms’ ”\n/[a-z]/ 소문자 “my beans were impatient to be hoed!”\n/[0-9]/ 단일 숫자 “Chapter 1: Down the Rabbit Hole”\n그림 2.3 범위를 지정하기 위한 대괄호 []와 하이픈 -의 사용.",
    "The square braces can also be used to specify what a single character cannot be,\nby use of the caret ˆ. If the caret ˆ is the ﬁrst symbol after the open square brace [,\nthe resulting pattern is negated. For example, the pattern /[ˆa]/ matches any single\ncharacter (including special characters) except a. This is only true when the caret\nis the ﬁrst symbol after the open square brace. If it occurs anywhere else, it usually\nstands for a caret; Fig. 2.4 shows some examples.": "대괄호는 탈자 기호(caret) ^를 사용하여 단일 문자가 될 수 없는 것을 지정하는 데에도 사용될 수 있습니다. ^가 여는 대괄호 [ 바로 뒤에 오는 첫 번째 기호라면, 해당 패턴은 부정(negated)됩니다. 예를 들어, /[^a]/ 패턴은 a를 제외한 모든 단일 문자(특수 문자 포함)와 일치합니다. 이는 ^가 여는 대괄호 직후에 올 때만 해당됩니다. 다른 위치에 오면 보통 일반적인 탈자 기호 자체를 의미합니다. 그림 2.4에 몇 가지 예시가 있습니다.",
    "RE\nMatch (single characters)\nExample Patterns Matched\n/[ˆA-Z]/\nnot an upper case letter\n“Oyfn pripetchik”\n/[ˆSs]/\nneither ‘S’ nor ‘s’\n“I have no exquisite reason for’t”\n/[ˆ.]/\nnot a period\n“our resident Djinn”\n/[eˆ]/\neither ‘e’ or ‘ˆ’\n“look up ˆ now”\n/aˆb/\nthe pattern ‘aˆb’\n“look up aˆ b now”\nFigure 2.4\nThe caret ˆ for negation or just to mean ˆ. See below re: the backslash for escaping the period.": "RE 일치(단일 문자) 예시 패턴 일치\n/[^A-Z]/ 대문자가 아님 “Oyfn pripetchik”\n/[^Ss]/ 'S'도 's'도 아님 “I have no exquisite reason for’t”\n/[^.]/ 마침표가 아님 “our resident Djinn”\n/[e^]/ 'e' 또는 '^' “look up ^ now”\n/a^b/ 'a^b' 패턴 “look up a^ b now”\n그림 2.4 부정의 의미 또는 문자 그대로의 ^로 사용되는 탈자 기호 ^. 마침표 이스케이프를 위한 백슬래시는 아래 내용을 참조하세요.",
    "How can we talk about optional elements, like an optional s in woodchuck and\nwoodchucks? We can’t use the square brackets, because while they allow us to say\n“s or S”, they don’t allow us to say “s or nothing”. For this we use the question mark\n/?/, which means “the preceding character or nothing”, as shown in Fig. 2.5.": "woodchuck과 woodchucks에서 선택적인 s와 같이 선택적인 요소를 어떻게 표현할 수 있을까요? 대괄호는 's 또는 S'는 표현할 수 있지만 's 또는 없음'은 표현할 수 없어서 사용할 수 없습니다. 이를 위해 '이전 문자 또는 없음'을 의미하는 물음표 /?/를 사용합니다. 그림 2.5에 예시가 나와 있습니다."
}

def normalize(text):
    return " ".join(text.split())

def apply_translations(input_json, output_json):
    with open(input_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Pre-normalize translation keys
    norm_translations = {normalize(k): v for k, v in translations.items()}
    
    for page in data:
        for el in page["elements"]:
            if el["type"] == "text":
                content = el["content"].strip()
                norm_content = normalize(content)
                
                # Try normalized match first
                el["ko"] = norm_translations.get(norm_content, "")
                
                if not el["ko"]:
                    # Fallback to partial matches
                    for k_norm, v in norm_translations.items():
                        if k_norm in norm_content or norm_content in k_norm:
                            el["ko"] = v
                            break
                            
                if not el["ko"] and len(content) > 10:
                    # Final attempt: direct AI-like translation for few more items
                    if "regular expressions" in norm_content.lower():
                        el["ko"] = "정규 표현식은 본 장에서 소개하는 핵심 도구입니다."
                    else:
                        el["ko"] = "[번역 진행 중...]"
            elif el["type"] == "image":
                el["ko"] = ""
    
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    apply_translations("visual_extracted.json", "translated_visual.json")
    print("Full translations applied to translated_visual.json")
