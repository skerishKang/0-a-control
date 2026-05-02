# Format Sample: Pages 1-2

This file is the corrected sample output format for the flash workflow.
Use it as the formatting and tone baseline for future pages.

# Page 1

## Block 1
- type: other
- source_text: Speech and Language Processing. Daniel Jurafsky & James H. Martin. Copyright © 2021. All rights reserved. Draft of September 21, 2021.
- korean_translation: 음성 및 언어 처리. Daniel Jurafsky & James H. Martin. Copyright © 2021. All rights reserved. 2021년 9월 21일자 초안.
- study_note: 본 교재의 서지 정보와 판본 정보를 나타내는 헤더 블록입니다. 초안 날짜를 보면 아직 출판 전 원고 단계의 문서임을 알 수 있습니다.

## Block 2
- type: chapter_title
- source_text:
  CHAPTER
  2 Regular Expressions, Text Normalization, Edit Distance
- korean_translation:
  제2장
  정규 표현식, 텍스트 정규화, 편집 거리
- study_note: 이 장의 핵심 주제 세 가지를 한 번에 제시합니다. 자연어 처리의 가장 기본적인 전처리 개념들이 이 장에서 연결됩니다.

## Block 3
- type: dialogue
- source_text:
  User: I am unhappy.
  ELIZA: DO YOU THINK COMING HERE WILL HELP YOU NOT TO BE UNHAPPY
  User: I need some help, that much seems certain.
  ELIZA: WHAT WOULD IT MEAN TO YOU IF YOU GOT SOME HELP
  User: Perhaps I could learn to get along with my mother.
  ELIZA: TELL ME MORE ABOUT YOUR FAMILY
  User: My mother takes care of me.
  ELIZA: WHO ELSE IN YOU FAMILY TAKES CARE OF YOU
  User: My father.
  ELIZA: YOUR FATHER
  User: You are like my father in some ways.
- korean_translation:
  사용자: 저는 불행해요.
  ELIZA: 여기 오는 것이 당신이 더 이상 불행하지 않게 되는 데 도움이 될 것이라고 생각하나요?
  사용자: 도움이 좀 필요해요. 그건 분명한 것 같아요.
  ELIZA: 도움을 받는다는 것이 당신에게 어떤 의미일까요?
  사용자: 아마 어머니와 잘 지내는 법을 배울 수 있을지도 몰라요.
  ELIZA: 가족에 대해 좀 더 이야기해 주세요.
  사용자: 어머니가 저를 돌봐 주세요.
  ELIZA: 가족 중에 또 누가 당신을 돌봐 주나요?
  사용자: 아버지요.
  ELIZA: 당신의 아버지요?
  사용자: 당신은 어떤 면에서 제 아버지와 비슷해요.
- study_note: 초기 대화 시스템 ELIZA의 예시입니다. 사용자의 문장을 이해한다기보다 패턴을 감지해 반응을 생성한다는 점이 핵심입니다.

## Block 4
- type: reference
- source_text: Weizenbaum (1966)
- korean_translation: Weizenbaum (1966)
- study_note: ELIZA의 원전으로 연결되는 참고 표기입니다. 참고문헌형 표기는 원문 형태를 유지하는 것이 안전합니다.

## Block 5
- type: margin_note
- source_text: ELIZA
- korean_translation: ELIZA
- study_note: 본문 옆에서 현재 핵심 개념을 표시하는 여백 키워드입니다.

## Block 6
- type: paragraph
- source_text: The dialogue above is from ELIZA, an early natural language processing system that could carry on a limited conversation with a user by imitating the responses of a Rogerian psychotherapist (Weizenbaum, 1966). ELIZA is a surprisingly simple program that uses pattern matching to recognize phrases like “I need X” and translate them into suitable outputs like “What would it mean to you if you got some help?”. This simple technique succeeds in this domain because ELIZA doesn’t actually need to know anything to mimic a Rogerian psychotherapist. As Weizenbaum notes, this is one of the few dialogue genres where listeners can act as if they know nothing of the world. Eliza’s mimicry of human conversation was remarkably successful: many people who interacted with ELIZA came to believe that it really understood them and their problems, many continued to believe in ELIZA’s abilities even after the program’s operation was explained to them (Weizenbaum, 1976), and even today such chatbots play a crucial role in natural language processing.
- korean_translation: 위 대화는 로저스 학파 심리치료사의 응답을 모방함으로써 사용자와 제한된 대화를 이어 갈 수 있었던 초기 자연어 처리 시스템 ELIZA의 사례입니다(Weizenbaum, 1966). ELIZA는 “I need X” 같은 구절을 인식하고 이를 “도움을 받는다면 그것이 당신에게 어떤 의미일까요?” 같은 적절한 출력으로 바꾸는 패턴 매칭 기반의 놀랄 만큼 단순한 프로그램입니다. 이 단순한 기법이 이 영역에서 성공한 이유는 ELIZA가 로저스 학파 심리치료사를 흉내 내는 데 실제 세계 지식을 거의 필요로 하지 않았기 때문입니다. Weizenbaum이 지적하듯, 이 대화 장르는 청자가 세상에 대해 아무것도 모르는 듯 행동해도 되는 몇 안 되는 경우 중 하나입니다. ELIZA의 인간 대화 모방은 매우 성공적이어서, 많은 사용자들이 ELIZA가 자신과 자신의 문제를 정말로 이해한다고 믿었고, 프로그램의 작동 원리를 설명받은 뒤에도 그 능력을 계속 믿었습니다(Weizenbaum, 1976). 오늘날에도 이런 챗봇은 자연어 처리에서 중요한 역할을 합니다.
- study_note: 이 문단은 ELIZA가 왜 단순한 기술로도 효과적으로 보였는지를 설명합니다. 핵심은 깊은 이해가 아니라 적절한 대화 장르와 패턴 반응의 조합입니다.

## Block 7
- type: margin_note
- source_text: chatbots
- korean_translation: 챗봇
- study_note: 대화형 인터페이스를 가진 프로그램을 가리키는 핵심 용어입니다.

## Block 8
- type: paragraph
- source_text: Of course modern conversational agents are much more than a diversion; they can answer questions, book flights, or find restaurants, functions for which they rely on a much more sophisticated understanding of the user’s intent, as we will see in Chapter 24. Nonetheless, the simple pattern-based methods that powered ELIZA and other chatbots play a crucial role in natural language processing.
- korean_translation: 물론 현대의 대화형 에이전트는 단순한 오락거리를 훨씬 넘어섭니다. 이들은 질문에 답하고, 항공편을 예약하고, 식당을 찾을 수 있으며, 이런 기능은 24장에서 보게 되듯 사용자의 의도를 훨씬 정교하게 이해하는 능력에 기대고 있습니다. 그럼에도 불구하고 ELIZA와 다른 챗봇을 움직였던 단순한 패턴 기반 방식은 자연어 처리에서 여전히 중요한 역할을 합니다.
- study_note: 현대 시스템은 훨씬 복잡하지만, 패턴 매칭 같은 기초 기술이 여전히 바탕을 이룬다는 연결을 만들어 주는 문단입니다.

## Block 9
- type: paragraph
- source_text: We’ll begin with the most important tool for describing text patterns: the regular expression. Regular expressions can be used to specify strings we might want to extract from a document, from transforming “I need X” in Eliza above, to defining strings like $199 or $24.99 for extracting tables of prices from a document.
- korean_translation: 이제 텍스트 패턴을 기술하는 가장 중요한 도구인 정규 표현식부터 시작하겠습니다. 정규 표현식은 위 ELIZA 예시의 “I need X”를 변환하는 일부터, 문서에서 가격표를 추출하기 위해 $199나 $24.99 같은 문자열을 정의하는 일까지, 우리가 추출하고 싶은 문자열을 지정하는 데 사용될 수 있습니다.
- study_note: 정규 표현식이 단순한 검색을 넘어서 텍스트 추출과 변환의 핵심 도구라는 점을 보여 줍니다.

## Block 10
- type: margin_note
- source_text: text normalization
- korean_translation: 텍스트 정규화
- study_note: 텍스트를 분석하기 쉬운 표준 형태로 바꾸는 과정 전체를 가리키는 용어입니다.

## Block 11
- type: paragraph
- source_text: We’ll then turn to a set of tasks collectively called text normalization, in which regular expressions play an important part. Normalizing text means converting it to a more convenient, standard form. For example, most of what we are going to do with language relies on first separating out or tokenizing words from running text, the task of tokenization. English words are often separated from each other by whitespace, but whitespace is not always sufficient. New York and rock ’n’ roll are sometimes treated as large words despite the fact that they contain spaces, while sometimes we’ll need to separate I’m into the two words I and am. For processing tweets or texts we’ll need to tokenize emoticons like :) or hashtags like #nlproc.
- korean_translation: 다음으로는 정규 표현식이 중요한 역할을 하는 일련의 작업, 즉 텍스트 정규화를 살펴보겠습니다. 텍스트를 정규화한다는 것은 그것을 더 편리하고 표준적인 형태로 바꾸는 뜻입니다. 예를 들어, 우리가 언어를 다룰 때 하는 일의 대부분은 먼저 연속된 텍스트에서 단어를 분리해 내는 토큰화 작업에 의존합니다. 영어 단어는 흔히 공백으로 구분되지만 공백만으로는 충분하지 않을 때가 많습니다. New York이나 rock ’n’ roll은 공백을 포함해도 하나의 큰 단어처럼 다뤄지기도 하고, 반대로 I’m은 I와 am으로 나누어야 할 때도 있습니다. 트윗이나 문자 메시지를 처리할 때는 :) 같은 이모티콘이나 #nlproc 같은 해시태그도 토큰화해야 합니다.
- study_note: 토큰화가 왜 단순한 공백 분리가 아닌지를 보여 주는 대표 문단입니다. 실제 언어는 예외가 많기 때문에 규칙 설계가 중요합니다.

## Block 12
- type: margin_note
- source_text: tokenization
- korean_translation: 토큰화
- study_note: 텍스트를 분석 가능한 최소 단위인 토큰으로 분절하는 기초 작업입니다.

# Page 2

## Block 1
- type: other
- source_text: 2 CHAPTER 2 • REGULAR EXPRESSIONS, TEXT NORMALIZATION, EDIT DISTANCE
- korean_translation: 2 제2장 • 정규 표현식, 텍스트 정규화, 편집 거리
- study_note: 페이지 상단에 반복되는 장 제목과 페이지 번호입니다.

## Block 2
- type: paragraph
- source_text: Some languages, like Japanese, don’t have spaces between words, so word tokenization becomes more difficult.
- korean_translation: 일본어 같은 일부 언어는 단어 사이에 공백이 없기 때문에 단어 토큰화가 훨씬 더 어려워집니다.
- study_note: 공백이 없는 언어에서는 토큰화가 훨씬 복잡해진다는 점을 짚어 줍니다. 한국어도 완전히 같은 유형은 아니지만 비슷한 어려움이 있습니다.

## Block 3
- type: margin_note
- source_text: lemmatization
- korean_translation: 표제어 추출
- study_note: 다양한 활용형을 공통 기본형으로 돌리는 작업을 가리키는 용어입니다.

## Block 4
- type: paragraph
- source_text: Another part of text normalization is lemmatization, the task of determining that two words have the same root, despite their surface differences. For example, the words sang, sung, and sings are forms of the verb sing. The word sing is the common lemma of these words, and a lemmatizer maps from all of these to sing. Lemmatization is essential for processing morphologically complex languages like Arabic. Stemming refers to a simpler version of lemmatization in which we mainly just strip suffixes from the end of the word. Text normalization also includes sentence segmentation: breaking up a text into individual sentences, using cues like periods or exclamation points.
- korean_translation: 텍스트 정규화의 또 다른 부분은 표제어 추출입니다. 이는 표면 형태가 달라도 두 단어가 같은 어근을 가진다는 사실을 판별하는 작업입니다. 예를 들어 sang, sung, sings는 모두 동사 sing의 형태입니다. sing은 이 단어들의 공통 표제어이며, 표제어 추출기는 이 모든 단어를 sing으로 대응시킵니다. 표제어 추출은 아랍어처럼 형태론적으로 복잡한 언어를 처리할 때 특히 중요합니다. 어간 추출은 이보다 더 단순한 방식으로, 주로 단어 끝의 접미사를 잘라 내는 작업을 말합니다. 텍스트 정규화에는 문장 분리도 포함되며, 이는 마침표나 느낌표 같은 단서를 이용해 텍스트를 개별 문장으로 나누는 작업입니다.
- study_note: 표제어 추출, 어간 추출, 문장 분리를 한꺼번에 소개하는 문단입니다. 서로 비슷해 보이지만 정밀도와 목적이 다르다는 점을 구분해 두면 좋습니다.

## Block 5
- type: margin_note
- source_text: stemming
- korean_translation: 어간 추출
- study_note: 접미사를 잘라 단어를 더 단순한 형태로 만드는 비교적 거친 정규화 방식입니다.

## Block 6
- type: margin_note
- source_text: sentence segmentation
- korean_translation: 문장 분리
- study_note: 연속된 텍스트를 문장 단위로 끊는 과정입니다.

## Block 7
- type: paragraph
- source_text: Finally, we’ll need to compare words and other strings. We’ll introduce a metric called edit distance that measures how similar two strings are based on the number of edits (insertions, deletions, substitutions) it takes to change one string into the other. Edit distance is an algorithm with applications throughout language processing, from spelling correction to speech recognition to coreference resolution.
- korean_translation: 마지막으로 우리는 단어와 다른 문자열을 비교해야 합니다. 이를 위해 한 문자열을 다른 문자열로 바꾸는 데 필요한 편집 횟수, 즉 삽입, 삭제, 치환의 수를 바탕으로 두 문자열이 얼마나 비슷한지를 측정하는 편집 거리라는 척도를 도입하겠습니다. 편집 거리는 철자 교정부터 음성 인식, 상호 참조 해소에 이르기까지 언어 처리 전반에 활용되는 알고리즘입니다.
- study_note: 편집 거리는 두 문자열의 유사성을 수치로 다루게 해 주는 핵심 개념입니다. 이후 알고리즘 파트의 기반이 되므로 정의를 정확히 이해하는 것이 중요합니다.

## Block 8
- type: section_title
- source_text: 2.1 Regular Expressions
- korean_translation: 2.1 정규 표현식
- study_note: 이제 본격적으로 정규 표현식 자체를 다루는 본문 섹션에 들어갑니다.

## Block 9
- type: margin_note
- source_text: regular expression
- korean_translation: 정규 표현식
- study_note: 문자열 검색과 추출을 위한 패턴 기술 언어라는 점을 기억하면 됩니다.

## Block 10
- type: paragraph
- source_text: One of the unsung successes in standardization in computer science has been the regular expression (RE), a language for specifying text search strings. This practical language is used in every computer language, word processor, and text processing tools like the Unix tools grep or Emacs. Formally, a regular expression is an algebraic notation for characterizing a set of strings. They are particularly useful for searching in texts, when we have a pattern to search for and a corpus of texts to search through. A regular expression search function will search through the corpus, returning all texts that match the pattern. The corpus can be a single document or a collection. For example, the Unix command-line tool grep takes a regular expression and returns every line of the input document that matches the expression.
- korean_translation: 컴퓨터 과학의 표준화 과정에서 잘 알려지지 않은 성공 사례 중 하나가 정규 표현식(RE), 즉 텍스트 검색 문자열을 지정하는 언어입니다. 이 실용적인 언어는 거의 모든 프로그래밍 언어, 워드 프로세서, 그리고 grep이나 Emacs 같은 텍스트 처리 도구에서 사용됩니다. 형식적으로 정규 표현식은 문자열 집합을 특징짓는 대수적 표기법입니다. 정규 표현식은 검색할 패턴과 검색 대상이 되는 말뭉치가 있을 때 특히 유용합니다. 정규 표현식 검색 함수는 말뭉치를 탐색하여 패턴과 일치하는 모든 텍스트를 반환합니다. 말뭉치는 하나의 문서일 수도 있고 문서들의 집합일 수도 있습니다. 예를 들어 유닉스 명령줄 도구 grep은 정규 표현식을 받아 입력 문서에서 그 표현과 일치하는 모든 줄을 반환합니다.
- study_note: 정규 표현식이 왜 표준 도구로 자리 잡았는지 설명하는 문단입니다. 핵심은 패턴과 말뭉치라는 두 요소를 연결해 대량 텍스트 검색을 가능하게 한다는 점입니다.

## Block 11
- type: margin_note
- source_text: corpus
- korean_translation: 말뭉치(corpus)
- study_note: 언어 분석을 위해 모아 둔 텍스트 자료의 집합을 뜻합니다.

## Block 12
- type: paragraph
- source_text: A search can be designed to return every match on a line, if there are more than one, or just the first match. In the following examples we generally underline the exact part of the pattern that matches the regular expression and show only the first match. We’ll show regular expressions delimited by slashes but note that slashes are not part of the regular expressions.
- korean_translation: 검색은 한 줄 안에 일치 항목이 여러 개 있을 경우 모든 항목을 돌려주도록 설계할 수도 있고, 첫 번째 항목만 돌려주도록 설계할 수도 있습니다. 이어지는 예시에서는 보통 정규 표현식과 일치하는 정확한 부분에 밑줄을 긋고 첫 번째 일치 결과만 보여 줄 것입니다. 우리는 정규 표현식을 슬래시(/)로 둘러싸 표시하겠지만, 슬래시 자체는 정규 표현식의 일부가 아니라는 점에 유의해야 합니다.
- study_note: 정규 표현식의 표기 관례와 검색 결과를 읽는 방식을 미리 설명해 주는 문단입니다. 이후 예시를 볼 때 슬래시를 실제 패턴의 일부로 오해하지 않도록 도와줍니다.

## Block 13
- type: paragraph
- source_text: Regular expressions come in many variants. We’ll be describing extended regular expressions; different regular expression parsers may only recognize subsets of these, or treat some expressions slightly differently. Using an online regular expression tester is a handy way to test out your expressions and explore these variations.
- korean_translation: 정규 표현식에는 여러 변형이 존재합니다. 여기서는 확장 정규 표현식을 설명할 것이며, 서로 다른 정규 표현식 파서는 그중 일부만 인식하거나 어떤 표현을 약간 다르게 처리할 수도 있습니다. 온라인 정규 표현식 테스트기를 사용하는 것은 여러분의 표현식을 시험해 보고 이런 차이를 살펴보는 편리한 방법입니다.
- study_note: 정규 표현식 문법이 환경마다 조금씩 다를 수 있다는 점을 경고합니다. 실제 실습에서는 사용하는 도구의 구현 차이를 항상 확인해야 합니다.

## Block 14
- type: subsection_title
- source_text: 2.1.1 Basic Regular Expression Patterns
- korean_translation: 2.1.1 기본 정규 표현식 패턴
- study_note: 정규 표현식의 가장 기본적인 요소와 패턴을 설명하는 하위 단원입니다.

## Block 15
- type: paragraph
- source_text: The simplest kind of regular expression is a sequence of simple characters. To search for woodchuck, we type /woodchuck/. The expression /Buttercup/ matches any string containing the substring Buttercup; grep with that expression would return the line I’m called little Buttercup. The search string can consist of a single character (like /!/) or a sequence of characters (like /urg1/).
- korean_translation: 가장 단순한 종류의 정규 표현식은 단순한 문자들의 나열입니다. woodchuck을 검색하려면 /woodchuck/이라고 입력합니다. /Buttercup/이라는 표현은 Buttercup이라는 부분 문자열을 포함하는 모든 문자열과 일치하며, 이 표현으로 grep을 수행하면 I’m called little Buttercup이라는 줄이 반환될 것입니다. 검색 문자열은 /!/처럼 문자 하나일 수도 있고, /urg1/처럼 여러 문자로 이루어진 열일 수도 있습니다.
- study_note: 가장 기초적인 리터럴 매칭을 설명합니다. 특별한 기호 없이도 정규 표현식은 그대로 문자열 검색에 사용할 수 있다는 점을 보여 줍니다.

## Block 16
- type: paragraph
- source_text: Regular expressions are case sensitive; lower case /s/ is distinct from upper case /S/ (/s/ matches a lower case s but not an upper case S). This means that the pattern /woodchucks/ will not match the string Woodchucks. We can solve this
- korean_translation: 정규 표현식은 대소문자를 구분합니다. 소문자 /s/는 대문자 /S/와 다르며, /s/는 소문자 s와는 일치하지만 대문자 S와는 일치하지 않습니다. 따라서 /woodchucks/ 패턴은 Woodchucks라는 문자열과 일치하지 않습니다. 우리는 이 문제를 다음과 같이 해결할 수 있습니다. [다음 페이지에서 계속]
- study_note: 정규 표현식의 대소문자 민감성은 초보자가 자주 놓치는 속성입니다. 다음 페이지에서 이를 해결하는 방법이 이어집니다.
