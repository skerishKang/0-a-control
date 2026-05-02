# Pages 1-2

Source: `2. Regular Expressions, Text Normalization, Edit Distance.pdf`
Workflow: `html-codex-flash`
Status: accepted

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
# Pages 3-4

Source: `2. Regular Expressions, Text Normalization, Edit Distance.pdf`
Workflow: `html-codex-flash`
Status: accepted

# Page 3

## Block 1
- type: other
- source_text: 2.1 • REGULAR EXPRESSIONS 3
- korean_translation: 2.1 • 정규 표현식 3
- study_note: 페이지 상단의 섹션 번호와 제목, 그리고 페이지 번호를 나타내는 헤더입니다.

## Block 2
- type: table
- source_text:
  [table]
  row 1: RE | Example Patterns Matched
  row 2: /woodchucks/ | “interesting links to woodchucks and lemurs”
  row 3: /a/ | “Mary Ann stopped by Mona’s”
  row 4: /!/ | “You’ve left the burglar behind again!” said Nori
- korean_translation:
  [table]
  행 1: 정규 표현식 | 일치하는 패턴 예시
  행 2: /woodchucks/ | “interesting links to woodchucks and lemurs”
  행 3: /a/ | “Mary Ann stopped by Mona’s”
  행 4: /!/ | “You’ve left the burglar behind again!” said Nori
- study_note: 가장 기본적인 정규 표현식 매칭 사례를 보여 줍니다. 슬래시(/) 사이에 적힌 문자열이 대상 문장에서 그대로 발견되면 일치(match)로 간주합니다.

## Block 3
- type: figure_caption
- source_text: Figure 2.1 Some simple regex searches.
- korean_translation: 그림 2.1 몇 가지 간단한 정규 표현식 검색 예시.
- study_note: 위 표의 내용을 설명하는 캡션입니다. 정규 표현식(regex)을 이용한 기초적인 검색 시나리오를 정의합니다.

## Block 4
- type: paragraph
- source_text: problem with the use of the square braces [ and ]. The string of characters inside the braces specifies a disjunction of characters to match. For example, Fig. 2.2 shows that the pattern /[wW]/ matches patterns containing either w or W.
- korean_translation: 대괄호 [ 와 ] 사용 시의 문제입니다. 대괄호 안의 문자열은 일치시킬 문자들의 선택적 집합(disjunction)을 지정합니다. 예를 들어 그림 2.2는 /[wW]/ 패턴이 w 또는 W 중 하나를 포함하는 패턴과 일치함을 보여 줍니다.
- study_note: 대괄호([])는 여러 문자 중 하나와 일치시키는 '선택적 집합' 개념을 도입합니다. 앞 페이지에서 언급된 대소문자 구분 문제를 해결하는 유용한 도구입니다.

## Block 5
- type: table
- source_text:
  [table]
  row 1: RE | Match | Example Patterns
  row 2: /[wW]oodchuck/ | Woodchuck or woodchuck | “Woodchuck”
  row 3: /[abc]/ | ‘a’, ‘b’, or ‘c’ | “In uomini, in soldati”
  row 4: /[1234567890]/ | any digit | “plenty of 7 to 5”
- korean_translation:
  [table]
  행 1: 정규 표현식 | 일치 대상 | 패턴 예시
  행 2: /[wW]oodchuck/ | Woodchuck 또는 woodchuck | “Woodchuck”
  행 3: /[abc]/ | ‘a’, ‘b’, 또는 ‘c’ | “In uomini, in soldati”
  행 4: /[1234567890]/ | 임의의 한 자리 숫자 | “plenty of 7 to 5”
- study_note: 대괄호를 활용해 대소문자나 특정 문자 집합, 숫자를 찾아내는 구체적인 예시입니다. 대괄호 하나는 정확히 '문자 하나'의 자리에 대응하며, 그 자리에 올 수 있는 후보들을 나열하는 방식입니다.

## Block 6
- type: figure_caption
- source_text: Figure 2.2 The use of the brackets [] to specify a disjunction of characters.
- korean_translation: 그림 2.2 문자들의 선택적 집합을 지정하기 위한 대괄호 []의 사용.
- study_note: 대괄호가 정규 표현식에서 '여러 문자 중 하나'를 선택하는 기능을 수행함을 강조하는 캡션입니다.

## Block 7
- type: paragraph
- source_text: The regular expression /[1234567890]/ specifies any single digit. While such classes of characters as digits or letters are important building blocks in expressions, they can get awkward (e.g., it’s inconvenient to specify /[ABCDEFGHIJKLMNOPQRSTUVWXYZ]/ to mean “any capital letter”). In cases where there is a well-defined sequence associated with a set of characters, the brackets can be used with the dash (-) to specify any one character in a range. The pattern /[2-5]/ specifies any one of the characters 2, 3, 4, or 5. The pattern /[b-g]/ specifies one of the characters b, c, d, e, f, or g. Some other examples are shown in Fig. 2.3.
- korean_translation: 정규 표현식 /[1234567890]/은 임의의 한 자리 숫자를 지정합니다. 숫자나 문자와 같은 문자 클래스는 표현식을 구성하는 중요한 요소이지만, 때로는 작성하기 번거로울 수 있습니다. (예를 들어, "임의의 대문자 하나"를 나타내기 위해 /[ABCDEFGHIJKLMNOPQRSTUVWXYZ]/라고 일일이 쓰는 것은 불편합니다.) 문자 집합에 잘 정의된 순서가 있는 경우, 대괄호 안에 대시(-)를 사용하여 범위 내의 임의의 한 문자를 지정할 수 있습니다. /[2-5]/ 패턴은 2, 3, 4, 5 중 하나를 의미하며, /[b-g]/ 패턴은 b, c, d, e, f, g 중 하나를 의미합니다. 그림 2.3에서 다른 예시들을 볼 수 있습니다.
- study_note: 문자를 일일이 나열하는 대신 대시(-) 기호를 사용해 '범위(range)'를 지정하는 효율적인 문법을 소개합니다. 알파벳이나 숫자는 순서가 정해져 있어 이 방식이 특히 유용합니다.

## Block 8
- type: margin_note
- source_text: range
- korean_translation: 범위
- study_note: 대괄호 안에서 대시(-)를 사용해 지정하는 문자 범위를 가리키는 핵심 용어입니다.

## Block 9
- type: table
- source_text:
  [table]
  row 1: RE | Match | Example Patterns Matched
  row 2: /[A-Z]/ | an upper case letter | “we should call it ‘Drenched Blossoms’ ”
  row 3: /[a-z]/ | a lower case letter | “my beans were impatient to be hoed!”
  row 4: /[0-9]/ | a single digit | “Chapter 1: Down the Rabbit Hole”
- korean_translation:
  [table]
  행 1: 정규 표현식 | 일치 대상 | 일치하는 패턴 예시
  행 2: /[A-Z]/ | 대문자 하나 | “we should call it ‘Drenched Blossoms’ ”
  행 3: /[a-z]/ | 소문자 하나 | “my beans were impatient to be hoed!”
  행 4: /[0-9]/ | 임의의 한 자리 숫자 | “Chapter 1: Down the Rabbit Hole”
- study_note: 대문자 전체, 소문자 전체, 숫자 전체를 범위를 활용해 지정하는 가장 흔한 정규 표현식 패턴들입니다.

## Block 10
- type: figure_caption
- source_text: Figure 2.3 The use of the brackets [] plus the dash - to specify a range.
- korean_translation: 그림 2.3 범위를 지정하기 위한 대괄호 []와 대시 -의 사용.
- study_note: 대괄호와 대시의 조합을 통해 넓은 범위의 문자 집합을 간결하게 표현하는 원리를 설명합니다.

## Block 11
- type: paragraph
- source_text: The square braces can also be used to specify what a single character cannot be, by use of the caret ^. If the caret ^ is the first symbol after the open square brace [, the resulting character class is negated. For example, the pattern /[^a]/ matches any single character (including special characters) except a. This is only true when the caret is the first symbol after the open square brace. If it occurs anywhere else, it usually stands for a caret; Fig. 2.4 shows some examples.
- korean_translation: 대괄호는 캐럿(^) 기호를 사용하여 단일 문자가 될 수 없는 대상을 지정하는 데에도 쓰일 수 있습니다. 캐럿(^)이 여는 대괄호([) 바로 다음의 첫 번째 기호로 오면, 그 결과로 나타나는 문자 클래스는 부정(negated)됩니다. 예를 들어 /[^a]/ 패턴은 a를 제외한 모든 단일 문자(특수 문자 포함)와 일치합니다. 이는 오직 캐럿이 여는 대괄호 바로 다음의 첫 번째 기호일 때만 해당합니다. 그 외의 위치에 캐럿이 나타나면 대개 단순한 캐럿 기호 자체를 의미합니다. 그림 2.4에 몇 가지 예시가 나와 있습니다.
- study_note: 캐럿(^) 기호의 위치에 따른 중의적 의미를 설명합니다. 대괄호 시작 직후에 오면 '부정'의 의미를 갖지만, 다른 곳에서는 단순 문자로 취급된다는 점이 핵심입니다.

## Block 12
- type: table
- source_text:
  [table]
  row 1: RE | Match (single characters) | Example Patterns Matched
  row 2: /[^A-Z]/ | not an upper case letter | “Oyfn pripetchik”
  row 3: /[^Ss]/ | neither ‘S’ nor ‘s’ | “I have no exquisite reason for’t”
  row 4: /[^\.]/ | not a period | “our resident Djinn”
  row 5: /[e^]/ | either ‘e’ or ‘^’ | “look up ^ now”
  row 6: /a^b/ | the pattern ‘a^b’ | “look up a^b now”
- korean_translation:
  [table]
  행 1: 정규 표현식 | 일치 대상 (단일 문자) | 일치하는 패턴 예시
  행 2: /[^A-Z]/ | 대문자가 아님 | “Oyfn pripetchik”
  행 3: /[^Ss]/ | ‘S’도 ‘s’도 아님 | “I have no exquisite reason for’t”
  행 4: /[^\.]/ | 마침표가 아님 | “our resident Djinn”
  행 5: /[e^]/ | ‘e’ 또는 ‘^’ | “look up ^ now”
  행 6: /a^b/ | 패턴 ‘a^b’ | “look up a^b now”
- study_note: 부정(negation) 기법의 구체적인 매칭 사례를 보여 줍니다. 특히 마침표를 제외하거나, 캐럿 기호 자체가 문자로 쓰이는 경우의 차이를 확인해야 합니다.

## Block 13
- type: figure_caption
- source_text: Figure 2.4 The caret ^ for negation or just to mean ^. See below re: the backslash for escaping the period.
- korean_translation: 그림 2.4 부정을 의미하거나 단순한 ^를 의미하는 캐럿 ^. 마침표를 이스케이프하기 위한 백슬래시에 대해서는 아래를 참조하십시오.
- study_note: 캐럿 기호의 두 가지 용도를 정리한 캡션입니다. 마침표(.)를 일반 문자로 인식시키기 위한 백슬래시(\) 사용법을 예고하고 있습니다.

## Block 14
- type: paragraph
- source_text: How can we talk about optional elements, like an optional s in woodchuck and woodchucks? We can’t use the square brackets, because while they allow us to say “s or S”, they don’t allow us to say “s or nothing”. For this we use the question mark /?/, which means “the preceding character or nothing”, as shown in Fig. 2.5.
- korean_translation: woodchuck과 woodchucks의 사례처럼 선택적인 s와 같은 요소를 어떻게 표현할 수 있을까요? 대괄호는 "s 또는 S"는 표현할 수 있게 해 주지만 "s 또는 없음"을 표현할 수는 없기에 이 경우에는 사용할 수 없습니다. 이를 위해 "앞선 문자가 나타나거나 혹은 나타나지 않음"을 뜻하는 물음표 /?/를 사용하며, 그림 2.5에서 그 사례를 보여 줍니다.
- study_note: 선택성(optionality)을 다루는 메타 문자인 물음표(?)를 소개합니다. 대괄호로 해결할 수 없는 '존재하거나 존재하지 않음'의 문제를 해결하는 도구입니다.

# Page 4

## Block 1
- type: other
- source_text: 4 CHAPTER 2 • REGULAR EXPRESSIONS, TEXT NORMALIZATION, EDIT DISTANCE
- korean_translation: 4 제2장 • 정규 표현식, 텍스트 정규화, 편집 거리
- study_note: 페이지 상단의 장 제목과 페이지 번호 정보입니다.

## Block 2
- type: table
- source_text:
  [table]
  row 1: RE | Match | Example Patterns Matched
  row 2: /woodchucks?/ | woodchuck or woodchucks | “woodchuck”
  row 3: /colou?r/ | color or colour | “color”
- korean_translation:
  [table]
  행 1: 정규 표현식 | 일치 대상 | 일치하는 패턴 예시
  행 2: /woodchucks?/ | woodchuck 또는 woodchucks | “woodchuck”
  행 3: /colou?r/ | color 또는 colour | “color”
- study_note: 물음표(?)가 어떻게 바로 앞의 문자를 선택적으로 만드는지 보여 줍니다. 철자 차이를 하나의 패턴으로 처리하는 유용한 방식입니다.

## Block 3
- type: figure_caption
- source_text: Figure 2.5 The question mark ? marks optionality of the previous expression.
- korean_translation: 그림 2.5 물음표 ?는 앞선 표현의 선택성(optionality)을 표시합니다.
- study_note: 물음표의 주요 기능을 '선택성 표시'로 정의하고 있습니다.

## Block 4
- type: paragraph
- source_text: We can think of the question mark as meaning “zero or one instances of the previous character”. That is, it’s a way of specifying how many of something that we want, something that is very important in regular expressions. For example, consider the language of certain sheep, which consists of strings that look like the following:
- korean_translation: 우리는 물음표를 "앞선 문자가 0번 또는 1번 나타남"을 의미한다고 생각할 수 있습니다. 즉, 이는 우리가 원하는 요소가 몇 번 나타나야 하는지를 지정하는 방식이며, 정규 표현식에서 매우 중요한 개념입니다. 예를 들어 다음과 같은 형식의 문자열로 구성된 어떤 '양들의 언어'를 가정해 봅시다.
- study_note: 물음표를 수량자(quantifier) 관점에서 설명합니다. '0 또는 1'이라는 정의가 이후 등장할 별표(*)나 플러스(+) 기호와 대조되는 지점입니다.

## Block 5
- type: code
- source_text:
  baa!
  baaa!
  baaaa!
  baaaaa!
  ...
- korean_translation:
  baa!
  baaa!
  baaaa!
  baaaaa!
  ...
- study_note: 특정 문자가 반복되는 패턴을 시각적으로 보여 주는 예시 목록입니다.

## Block 6
- type: margin_note
- source_text: Kleene *
- korean_translation: 클레이니 별표(Kleene *)
- study_note: 미국의 수학자 스티븐 클레이니의 이름을 딴 반복 연산자 키워드입니다.

## Block 7
- type: paragraph
- source_text: This language consists of strings with a b, followed by at least two a’s, followed by an exclamation point. The set of operators that allows us to say things like “some number of as” are based on the asterisk or *, commonly called the Kleene * (generally pronounced “cleany star”). The Kleene star means “zero or more occurrences of the immediately previous character or regular expression”. So /a*/ means “any string of zero or more as”. This will match a or aaaaaa, but it will also match Off Minor since the string Off Minor has zero a’s. So the regular expression for matching one or more a is /aa*/, meaning one a followed by zero or more as. More complex patterns can also be repeated. So /[ab]*/ means “zero or more a’s or b’s” (not “zero or more right square braces”). This will match strings like aaaa or ababab or bbbb.
- korean_translation: 이 언어는 b 다음에 적어도 두 개의 a가 오고, 그 뒤에 느낌표가 오는 문자열들로 이루어져 있습니다. “어떤 수의 a들” 같은 표현을 가능하게 해 주는 연산자 집합은 별표, 즉 보통 클레이니 별표(Kleene *)라고 불리는 기호 *에 기반합니다. 클레이니 별표는 “바로 앞의 문자 또는 정규 표현식이 0번 이상 나타남”을 뜻합니다. 따라서 /a*/는 “a가 0번 이상 나타나는 임의의 문자열”을 의미합니다. 이것은 a나 aaaaaa와 일치할 뿐 아니라, Off Minor처럼 a가 0개인 문자열과도 일치합니다. 따라서 하나 이상의 a와 일치하는 정규 표현식은 /aa*/이며, 이는 a 하나 다음에 0개 이상의 a가 오는 형태를 뜻합니다. 더 복잡한 패턴도 반복될 수 있습니다. 따라서 /[ab]*/는 “a 또는 b가 0번 이상 나타남”을 의미합니다(“오른쪽 대괄호가 0번 이상 나타남”이라는 뜻이 아닙니다). 이 표현은 aaaa, ababab, bbbb 같은 문자열과 일치합니다.
- study_note: 클레이니 별표(*)는 반복을 표현하는 가장 핵심적인 수량자입니다. 특히 0번도 허용한다는 점 때문에, 해당 문자가 전혀 없는 문자열과도 일치할 수 있다는 점을 꼭 기억해야 합니다. 또한 `[ab]*`처럼 문자 집합과 결합하면 복합적인 반복 패턴을 간단하게 표현할 수 있습니다.
# Pages 5-6

Source: `2. Regular Expressions, Text Normalization, Edit Distance.pdf`
Workflow: `html-codex-flash`
Status: accepted

# Page 5

## Block 1
- type: other
- source_text: 2.1 • REGULAR EXPRESSIONS 5
- korean_translation: 2.1 • 정규 표현식 5
- study_note: 페이지 상단의 섹션 번호와 제목, 그리고 페이지 번호(5)를 나타내는 헤더입니다.

## Block 2
- type: paragraph
- source_text: start of a line. Thus, the caret ^ has three uses: to match the start of a line, to indicate a negation inside of square brackets, and just to mean a caret. (What are the contexts that allow grep or Python to know which function a given caret is supposed to have?) The dollar sign $ matches the end of a line. So the pattern ␣$ is a useful pattern for matching a space at the end of a line, and /^The dog\.$/ matches a line that contains only the phrase The dog. (We have to use the backslash here since we want the . to mean “period” and not the wildcard.)
- korean_translation: 줄의 시작입니다. 따라서 캐럿(^)은 세 가지 용도로 쓰입니다: 줄의 시작 부분과 일치시키기 위해, 대괄호 안에서 부정을 나타내기 위해, 그리고 단순히 캐럿 기호 자체를 의미하기 위해 사용됩니다. (grep이나 Python과 같은 도구들이 어떤 문맥에서 캐럿이 어떤 기능을 수행해야 하는지 어떻게 알 수 있을까요?) 달러 기호($)는 줄의 끝과 일치합니다. 따라서 ␣$ 패턴은 줄 끝의 공백을 찾는 데 유용하며, /^The dog\.$/는 오직 "The dog."이라는 구구절만 포함된 줄과 일치합니다. (여기서는 마침표(.)를 와일드카드가 아닌 실제 마침표 의미로 사용하기 위해 백슬래시를 사용해야 합니다.)
- study_note: 캐럿(^)의 세 가지 중의적 용도를 정리하고, 줄의 시작(^)과 끝($)을 나타내는 앵커(anchor)의 기초를 설명합니다. 특히 마침표(.)와 같은 특수 문자를 일반 문자로 취급하기 위한 이스케이프(\) 처리의 중요성을 언급합니다.

## Block 3
- type: table
- source_text:
  [table]
  row 1: RE | Match
  row 2: ^ | start of line
  row 3: $ | end of line
  row 4: \b | word boundary
  row 5: \B | non-word boundary
- korean_translation:
  [table]
  행 1: 정규 표현식(RE) | 일치 대상
  행 2: ^ | 줄의 시작
  행 3: $ | 줄의 끝
  행 4: \b | 단어 경계
  행 5: \B | 단어 경계가 아님
- study_note: 텍스트 내의 특정 위치를 지정하는 앵커 기호들을 표로 정리한 것입니다. 이들은 실제 문자와 매칭되는 것이 아니라 문자의 '위치' 조건과 매칭됩니다.

## Block 4
- type: figure_caption
- source_text: Figure 2.7 Anchors in regular expressions.
- korean_translation: 그림 2.7 정규 표현식에서의 앵커.
- study_note: 위 표의 내용을 설명하는 캡션으로, 앵커(anchors)라는 용어를 공식화합니다.

## Block 5
- type: paragraph
- source_text: There are also two other anchors: \b matches a word boundary, and \B matches a non-boundary. Thus, /\bthe\b/ matches the word the but not the word other. More technically, a “word” for the purposes of a regular expression is defined as any sequence of digits, underscores, or letters; this is based on the definition of “words” in programming languages. For example, /\b99\b/ will match the string 99 in There are 99 bottles of beer on the wall (because 99 follows a space) but not 99 in There are 299 bottles of beer on the wall (since 99 follows a number). But it will match 99 in $99 (since 99 follows a dollar sign ($), which is not a digit, underscore, or letter).
- korean_translation: 앵커에는 이 밖에도 두 가지가 더 있습니다. \b는 단어 경계(word boundary)와 일치하고, \B는 단어 경계가 아닌 위치와 일치합니다. 따라서 /\bthe\b/는 the라는 단어와는 일치하지만 other라는 단어와는 일치하지 않습니다. 좀 더 기술적으로 말하면, 정규 표현식에서의 “단어”는 숫자, 밑줄, 또는 문자로 이루어진 임의의 연속열로 정의되며, 이는 프로그래밍 언어에서의 “단어” 정의를 따른 것입니다. 예를 들어 /\b99\b/는 There are 99 bottles of beer on the wall에서의 99와는 일치합니다(99 앞에 공백이 있기 때문입니다). 하지만 There are 299 bottles of beer on the wall에서의 99와는 일치하지 않습니다(99 앞에 숫자가 오기 때문입니다). 반면 $99에서의 99와는 일치합니다(99 앞에 있는 달러 기호($)는 숫자, 밑줄, 또는 문자가 아니기 때문입니다).
- study_note: \b와 \B는 실제 문자와 매칭되는 것이 아니라 단어의 경계를 판별하는 위치 조건입니다. 여기서 “단어”의 정의가 일상적인 의미가 아니라 문자, 숫자, 밑줄 중심의 기술적 정의라는 점이 중요합니다.

# Page 6

## Block 1
- type: other
- source_text: 6 CHAPTER 2 • REGULAR EXPRESSIONS, TEXT NORMALIZATION, EDIT DISTANCE
- korean_translation: 6 제2장 • 정규 표현식, 텍스트 정규화, 편집 거리
- study_note: 페이지 상단의 장 제목과 페이지 번호(6) 정보입니다.

## Block 2
- type: paragraph
- source_text: /(Column␣[0-9]+␣*)*/ to match the word Column, followed by a number and optional spaces, the whole pattern repeated zero or more times.
- korean_translation: /(Column␣[0-9]+␣*)*/ 패턴은 단어 Column 뒤에 숫자와 선택적인 공백들이 뒤따르는 전체 패턴이 0번 이상 반복되는 경우와 일치합니다.
- study_note: 전 페이지에서 이어지는 내용으로, 소괄호를 사용하여 복합적인 패턴(Column + 숫자 + 공백)을 하나의 단위로 묶어 반복 연산(*)을 적용하는 방법을 보여 줍니다.

## Block 3
- type: paragraph
- source_text: This idea that one operator may take precedence over another, requiring us to sometimes use parentheses to specify what we mean, is formalized by the operator precedence hierarchy for regular expressions. The following table gives the order of RE operator precedence, from highest precedence to lowest precedence.
- korean_translation: 어떤 연산자가 다른 연산자보다 우선순위를 가질 수 있다는 개념, 그리고 때로는 의도를 명확히 하기 위해 괄호를 사용해야 한다는 점은 정규 표현식의 연산자 우선순위 계층 구조로 공식화되어 있습니다. 다음 표는 정규 표현식 연산자의 순위를 가장 높은 것부터 가장 낮은 것 순으로 보여 줍니다.
- study_note: 여러 연산자가 섞여 있을 때 어떤 것이 먼저 계산되는지 결정하는 '우선순위(precedence)' 개념을 도입합니다. 수학의 사칙연산 우선순위와 같은 원리입니다.

## Block 4
- type: margin_note
- source_text: operator precedence
- korean_translation: 연산자 우선순위
- study_note: 연산자 간의 처리 순서를 나타내는 핵심 용어입니다.

## Block 5
- type: table
- source_text:
  [table]
  row 1: Parenthesis | ()
  row 2: Counters | * + ? {}
  row 3: Sequences and anchors | the ^my end$
  row 4: Disjunction | |
- korean_translation:
  [table]
  행 1: 괄호 | ()
  행 2: 수량자(Counters) | * + ? {}
  행 3: 시퀀스 및 앵커 | the ^my end$
  행 4: 선택(Disjunction) | |
- study_note: 정규 표현식 연산자의 우선순위를 표로 정리한 것입니다. 맨 위의 괄호가 가장 우선권이 높고, 맨 아래의 선택(|) 연산자가 가장 낮습니다.

## Block 6
- type: paragraph
- source_text: Thus, because counters have a higher precedence than sequences, /the*/ matches theeeee but not thethe. Because sequences have a higher precedence than disjunction, /the|any/ matches the or any but not thany or theny.
- korean_translation: 따라서 수량자가 시퀀스보다 높은 우선순위를 갖기 때문에, /the*/는 'theeeee'와는 일치하지만 'thethe'와는 일치하지 않습니다. 또한 시퀀스가 선택 연산자보다 우선순위가 높기 때문에, /the|any/는 'the' 또는 'any'와는 일치하지만 'thany'나 'theny'와는 일치하지 않습니다.
- study_note: 우선순위가 실제 매칭 결과에 어떤 영향을 주는지 예시를 들어 설명합니다. /the*/에서 `*`가 `the` 전체가 아닌 마지막 `e`에만 적용되는 이유가 바로 수량자의 높은 우선순위 때문입니다.

## Block 7
- type: paragraph
- source_text: Patterns can be ambiguous in another way. Consider the expression /[a-z]*/ when matching against the text once upon a time. Since /[a-z]*/ matches zero or more letters, this expression could match nothing, or just the first letter o, on, onc, or once. In these cases regular expressions always match the largest string they can; we say that patterns are greedy, expanding to cover as much of a string as they can.
- korean_translation: 패턴은 다른 방식으로도 모호해질 수 있습니다. "once upon a time"이라는 텍스트에 대해 /[a-z]*/라는 표현식을 매칭하는 경우를 생각해 봅시다. /[a-z]*/는 0개 이상의 문자와 일치하므로, 이 표현식은 아무것도 선택하지 않거나, 첫 글자인 o, 혹은 on, onc, once 중 어느 것과도 일치할 수 있습니다. 이런 경우 정규 표현식은 항상 가능한 가장 긴 문자열과 일치합니다. 우리는 이를 패턴이 탐욕적(greedy)이라고 하며, 가능한 한 많은 문자열을 포함하도록 확장된다고 말합니다.
- study_note: 정규 표현식의 중요한 속성인 '탐욕적 매칭(greedy matching)'을 설명합니다. 여러 가능성이 있을 때 기본적으로 가장 긴 범위를 선택하려는 성향을 뜻합니다.

## Block 8
- type: margin_note
- source_text: greedy non-greedy *? +?
- korean_translation: 탐욕적/비탐욕적 *? +?
- study_note: 매칭 범위를 결정하는 방식과 이를 조절하는 기호를 나타냅니다.

## Block 9
- type: paragraph
- source_text: There are, however, ways to enforce non-greedy matching, using another meaning of the ? qualifier. The operator *? is a Kleene star that matches as little text as possible. The operator +? is a Kleene plus that matches as little text as possible.
- korean_translation: 하지만 물음표(?) 수량자의 다른 의미를 사용하여 비탐욕적(non-greedy) 매칭을 강제하는 방법도 있습니다. 연산자 *?는 가능한 한 적은 텍스트와 일치하는 클레이니 별표입니다. 연산자 +?는 가능한 한 적은 텍스트와 일치하는 클레이니 플러스입니다.
- study_note: 탐욕적 성향을 억제하고 최소한의 범위만 매칭하게 만드는 비탐욕적 연산자들을 소개합니다. 기존 수량자 뒤에 물음표를 붙여서 표현합니다.

## Block 10
- type: section_title
- source_text: 2.1.3 A Simple Example
- korean_translation: 2.1.3 간단한 예시
- study_note: 지금까지 배운 개념들을 종합하여 실제 문제를 해결해 보는 실습 섹션입니다.

## Block 11
- type: paragraph
- source_text: Suppose we wanted to write a RE to find cases of the English article the. A simple (but incorrect) pattern might be:
- korean_translation: 영어의 관사 'the'를 찾는 정규 표현식을 작성하고 싶다고 가정해 봅시다. 간단하지만 (잘못된) 패턴은 다음과 같을 수 있습니다.
- study_note: 단순한 매칭 시도가 가질 수 있는 문제점들을 하나씩 해결해 나가는 과정을 예고합니다.

## Block 12
- type: code
- source_text: /the/
- korean_translation: /the/
- study_note: 가장 직관적이지만 많은 예외를 남기는 기초적인 패턴입니다.

## Block 13
- type: paragraph
- source_text: One problem is that this pattern will miss the word when it begins a sentence and hence is capitalized (i.e., The). This might lead us to the following pattern:
- korean_translation: 한 가지 문제는 이 패턴이 문장 처음에 와서 대문자로 표기된 단어(즉, The)를 놓친다는 점입니다. 이는 우리를 다음과 같은 패턴으로 이끕니다.
- study_note: 대소문자 매칭 문제를 인지하는 단계입니다.

## Block 14
- type: code
- source_text: /[tT]he/
- korean_translation: /[tT]he/
- study_note: 대괄호를 사용하여 't'와 'T'를 모두 수용하도록 개선된 패턴입니다.

## Block 15
- type: paragraph
- source_text: But we will still incorrectly return texts with the embedded in other words (e.g., other or theology). So we need to specify that we want instances with a word boundary on both sides:
- korean_translation: 하지만 여전히 다른 단어 속에 포함된 'the'를 가진 텍스트(예: other 또는 theology)를 잘못 반환할 것입니다. 따라서 우리는 양쪽에 단어 경계가 있는 사례를 원한다고 지정해야 합니다.
- study_note: 단어의 일부로 포함된 문자열을 걸러내기 위해 단어 경계(\b)의 필요성을 설명합니다.

## Block 16
- type: code
- source_text: /\b[tT]he\b/
- korean_translation: /\b[tT]he\b/
- study_note: 단어 경계 앵커를 추가하여 독립된 단어로서의 'the'만 찾도록 정교화된 패턴입니다.

## Block 17
- type: paragraph
- source_text: Suppose we wanted to do this without the use of \b. We might want this since \b won’t treat underscores and numbers as word boundaries; but we might want to find the in some context where it might also have underlines or numbers nearby (the_ or the25). We need to specify that we want instances in which there are no alphabetic letters on either side of the the:
- korean_translation: 만약 \b를 사용하지 않고 이 작업을 수행하고 싶다고 가정해 봅시다. \b는 밑줄(_)이나 숫자를 단어 경계로 취급하지 않기 때문에, 근처에 밑줄이나 숫자가 있는 문맥(the_ 또는 the25)에서 the를 찾고 싶을 때는 이 방식이 필요할 수 있습니다. 우리는 the의 양옆에 알파벳 문자가 없는 사례를 지정해야 합니다.
- study_note: 특수한 환경(밑줄이나 숫자가 포함된 경우)을 고려하여 `\b` 대신 사용자 정의 경계 조건을 설정하는 이유를 설명합니다.

## Block 18
- type: code
- source_text: /[^a-zA-Z][tT]he[^a-zA-Z]/
- korean_translation: /[^a-zA-Z][tT]he[^a-zA-Z]/
- study_note: 부정을 나타내는 대괄호를 사용하여 양옆에 알파벳이 오지 않아야 함을 명시한 패턴입니다.

## Block 19
- type: paragraph
- source_text: But there is still one more problem with this pattern: it won’t find the word the when it begins a line. This is because the regular expression [^a-zA-Z], which we used to avoid embedded instances of the, implies that there must be some single (although non-alphabetic) character before the the. We can avoid this by specifying that before the the we require either the beginning-of-line or a non-alphabetic character, and the same at the end of the line:
- korean_translation: 하지만 이 패턴에도 아직 한 가지 문제가 더 있습니다. 바로 줄의 시작 부분에 오는 단어 the를 찾지 못한다는 점입니다. 이는 우리가 the가 다른 단어에 포함되는 것을 피하기 위해 사용한 정규 표현식 [^a-zA-Z]가, the 앞에 반드시 어떤 단일 문자(알파벳이 아닌 것이라도)가 '존재해야 함'을 전제하기 때문입니다. 우리는 the 앞에 '줄의 시작' 혹은 '알파벳이 아닌 문자'가 오도록 지정하고, 줄의 끝에서도 마찬가지로 처리함으로써 이 문제를 피할 수 있습니다.
- study_note: 줄의 시작 부분에는 앞에 문자가 존재하지 않기 때문에 발생하는 매칭 실패 문제를 분석합니다. 위치 정보(줄의 시작)와 문자 범위를 결합해야 함을 시사합니다.
# Pages 7-8

Source: `2. Regular Expressions, Text Normalization, Edit Distance.pdf`
Workflow: `html-codex-flash`
Status: accepted

# Page 7

## Block 1
- type: code
- source_text: /(^|[^a-zA-Z])[tT]he([^a-zA-Z]|$)/
- korean_translation: /(^|[^a-zA-Z])[tT]he([^a-zA-Z]|$)/
- study_note: 줄의 시작(^)이나 줄의 끝($)을 포함하여, 단어 'the' 전후에 알파벳이 아닌 문자가 오거나 아무것도 없는 위치를 정확히 지정한 최종 정규 표현식입니다.

## Block 2
- type: paragraph
- source_text:
  The process we just went through was based on fixing two kinds of errors: false positives, strings that we incorrectly matched like other or there, and false negatives, strings that we incorrectly missed, like The. Addressing these two kinds of errors comes up again and again in implementing speech and language processing systems. Reducing the overall error rate for an application thus involves two antagonistic efforts:
  • Increasing precision (minimizing false positives)
  • Increasing recall (minimizing false negatives)
  We’ll come back to precision and recall with more precise definitions in Chapter 4.
- korean_translation:
  방금 우리가 거친 과정은 두 가지 종류의 오류를 해결하는 데 기반을 두고 있습니다: 하나는 'other'나 'there'처럼 잘못 매칭된 문자열인 거짓 양성(false positives)이고, 다른 하나는 'The'처럼 일치해야 함에도 놓친 문자열인 거짓 음성(false negatives)입니다. 이러한 두 가지 종류의 오류를 다루는 일은 음성 및 언어 처리 시스템을 구현할 때 반복해서 등장합니다. 따라서 애플리케이션의 전체적인 오류율을 줄이는 데에는 다음과 같은 두 가지 상충되는 노력이 포함됩니다:
  • 정밀도(precision) 향상 (거짓 양성 최소화)
  • 재현율(recall) 향상 (거짓 음성 최소화)
  우리는 4장에서 더 정밀한 정의와 함께 정밀도와 재현율에 대해 다시 다룰 것입니다.
- study_note: 검색 및 분류 성능을 평가하는 핵심 지표인 정밀도와 재현율의 개념을 소개합니다. 시스템이 얼마나 정확하게(정밀도) 그리고 빠짐없이(재현율) 목표를 찾아내는지 이해하는 것이 중요합니다.

## Block 3
- type: margin_note
- source_text:
  false positives
  false negatives
- korean_translation:
  거짓 양성 (오탐)
  거짓 음성 (미탐)
- study_note: 정규 표현식 설계 과정에서 반드시 관리해야 할 두 가지 주요 오류 유형입니다.

## Block 4
- type: section_title
- source_text: 2.1.4 More Operators
- korean_translation: 2.1.4 추가 연산자들
- study_note: 정규 표현식을 더욱 간결하고 강력하게 만들어 주는 확장된 문법들을 배웁니다.

## Block 5
- type: paragraph
- source_text: Figure 2.8 shows some aliases for common ranges, which can be used mainly to save typing. Besides the Kleene * and Kleene + we can also use explicit numbers as counters, by enclosing them in curly brackets. The regular expression /{3}/ means “exactly 3 occurrences of the previous character or expression”. So /a.{24}z/ will match a followed by 24 dots followed by z (but not a followed by 23 or 25 dots followed by a z).
- korean_translation: 그림 2.8은 주로 타이핑 시간을 절약하기 위해 사용되는 일반적인 범위의 별칭(aliases)들을 보여 줍니다. 클레이니 별표(*)와 클레이니 플러스(+) 외에도, 중괄호 안에 명시적인 숫자를 넣어 수량자로 사용할 수 있습니다. 정규 표현식 /{3}/은 "앞선 문자나 표현식이 정확히 3번 나타남"을 의미합니다. 따라서 /a.{24}z/는 a 뒤에 24개의 점이 오고 그 뒤에 z가 오는 경우와 일치합니다 (점이 23개나 25개인 경우는 해당하지 않습니다).
- study_note: 반복 횟수를 숫자로 정확히 지정하는 `{n}` 문법과 자주 쓰이는 문자 집합의 단축 기호(별칭)를 소개합니다.

## Block 6
- type: table
- source_text:
  [table]
  row 1: RE | Expansion | Match | First Matches
  row 2: \d | [0-9] | any digit | Party␣of␣5
  row 3: \D | [^0-9] | any non-digit | Blue␣moon
  row 4: \w | [a-zA-Z0-9_] | any alphanumeric/underscore | Daiyu
  row 5: \W | [^\w] | a non-alphanumeric | !!!!
  row 6: \s | [␣\r\t\n\f] | whitespace (space, tab) | 
  row 7: \S | [^\s] | Non-whitespace | in␣Concord
- korean_translation:
  [table]
  행 1: RE | 확장 형태 | 일치 대상 | 첫 번째 일치 항목
  행 2: \d | [0-9] | 임의의 한 자리 숫자 | Party␣of␣5
  행 3: \D | [^0-9] | 숫자가 아닌 문자 | Blue␣moon
  행 4: \w | [a-zA-Z0-9_] | 임의의 영숫자 또는 밑줄 | Daiyu
  행 5: \W | [^\w] | 영숫자가 아닌 문자 | !!!!
  행 6: \s | [␣\r\t\n\f] | 공백 문자 (띄어쓰기, 탭 등) | 
  행 7: \S | [^\s] | 공백이 아닌 문자 | in␣Concord
- study_note: 실무에서 가장 많이 쓰이는 특수 시퀀스들입니다. 특히 `\w`는 프로그래밍 언어의 변수명 규칙(영문자, 숫자, 밑줄)을 따르는 "단어 문자"를 의미한다는 점을 기억하세요.

## Block 7
- type: figure_caption
- source_text: Figure 2.8 Aliases for common sets of characters.
- korean_translation: 그림 2.8 일반적인 문자 집합에 대한 별칭들.
- study_note: 자주 쓰이는 문자 클래스를 간략하게 표현하는 기호들을 정리한 표에 대한 설명입니다.

## Block 8
- type: paragraph
- source_text: A range of numbers can also be specified. So /{n,m}/ specifies from n to m occurrences of the previous char or expression, and /{n,}/ means at least n occurrences of the previous expression. REs for counting are summarized in Fig. 2.9.
- korean_translation: 숫자의 범위 또한 지정할 수 있습니다. 예를 들어 /{n,m}/은 앞선 문자나 표현식이 n번에서 m번 사이로 나타남을 의미하며, /{n,}/은 최소 n번 이상 나타남을 의미합니다. 수량을 세기 위한 정규 표현식 연산자들은 그림 2.9에 요약되어 있습니다.
- study_note: 반복 횟수의 최소값과 최대값을 지정하는 유연한 수량자 문법을 설명합니다.

## Block 9
- type: table
- source_text:
  [table]
  row 1: RE | Match
  row 2: * | zero or more occurrences of the previous char or expression
  row 3: + | one or more occurrences of the previous char or expression
  row 4: ? | exactly zero or one occurrence of the previous char or expression
  row 5: {n} | n occurrences of the previous char or expression
  row 6: {n,m} | from n to m occurrences of the previous char or expression
  row 7: {n,} | at least n occurrences of the previous char or expression
  row 8: {,m} | up to m occurrences of the previous char or expression
- korean_translation:
  [table]
  행 1: RE | 일치 대상
  행 2: * | 앞선 문자나 표현식이 0번 이상 나타남
  행 3: + | 앞선 문자나 표현식이 1번 이상 나타남
  행 4: ? | 앞선 문자나 표현식이 0번 또는 1번 나타남
  행 5: {n} | 앞선 문자나 표현식이 정확히 n번 나타남
  행 6: {n,m} | 앞선 문자나 표현식이 n번에서 m번 사이로 나타남
  행 7: {n,} | 앞선 문자나 표현식이 최소 n번 이상 나타남
  행 8: {,m} | 앞선 문자나 표현식이 최대 m번까지 나타남
- study_note: 정규 표현식의 모든 수량자 연산자를 한데 모은 참조 표입니다. 앞서 배운 `*`, `+`, `?` 기호들이 각각 대응하는 중괄호 문법의 특수한 형태임을 알 수 있습니다.

## Block 10
- type: figure_caption
- source_text: Figure 2.9 Regular expression operators for counting.
- korean_translation: 그림 2.9 수량을 세기 위한 정규 표현식 연산자들.
- study_note: 횟수와 관련된 모든 핵심 연산자들을 정리한 도표의 제목입니다.

## Block 11
- type: paragraph
- source_text: Finally, certain special characters are referred to by special notation based on the backslash (\) (see Fig. 2.10). The most common of these are the newline character \n and the tab character \t. To refer to characters that are special themselves (like ., *, [, and \), precede them with a backslash, (i.e., /\./, /\*/, /\[/, and /\\/).
- korean_translation: 마지막으로, 특정 특수 문자들은 백슬래시(\)를 기반으로 한 특별한 표기법으로 나타냅니다 (그림 2.10 참조). 가장 흔한 것은 개행 문자 \n과 탭 문자 \t입니다. 정규 표현식 자체에서 특별한 의미를 갖는 문자들(예: ., *, [, \)을 그대로 찾고 싶을 때는 그 앞에 백슬래시를 붙여야 합니다 (즉, /\./, /\*/, /\[/, /\\/).
- study_note: 눈에 보이지 않는 제어 문자(\n, \t)의 표기법과, 메타 문자의 기능을 무력화하고 문자 그대로 인식시키는 이스케이프(escape) 처리 방법을 설명합니다.

## Block 12
- type: margin_note
- source_text: newline
- korean_translation: 개행 문자
- study_note: 줄바꿈을 나타내는 특수한 표기 방식인 `\n`과 관련된 키워드입니다.

# Page 8

## Block 1
- type: other
- source_text: 8 CHAPTER 2 • REGULAR EXPRESSIONS, TEXT NORMALIZATION, EDIT DISTANCE
- korean_translation: 8 제2장 • 정규 표현식, 텍스트 정규화, 편집 거리
- study_note: 페이지 상단의 장 제목과 페이지 번호(8) 정보입니다.

## Block 2
- type: table
- source_text:
  [table]
  row 1: RE | Match | First Patterns Matched
  row 2: \* | an asterisk “*” | “K*A*P*L*A*N”
  row 3: \. | a period “.” | “Dr. Livingston, I presume”
  row 4: \? | a question mark | “Why don’t they come and lend a hand?”
  row 5: \n | a newline | 
  row 6: \t | a tab | 
- korean_translation:
  [table]
  행 1: RE | 일치 대상 | 첫 번째 매칭 패턴
  행 2: \* | 별표 “*” | “K*A*P*L*A*N”
  행 3: \. | 마침표 “.” | “Dr. Livingston, I presume”
  행 4: \? | 물음표 | “Why don’t they come and lend a hand?”
  행 5: \n | 개행 문자 | 
  행 6: \t | 탭 문자 | 
- study_note: 특수 기호를 문자 그대로 검색할 때 백슬래시를 사용하는 예시들입니다. 특히 `.`이나 `?` 같은 기호들은 정규 표현식에서 의미가 매우 강하므로 주의가 필요합니다.

## Block 3
- type: figure_caption
- source_text: Figure 2.10 Some characters that need to be backslashed.
- korean_translation: 그림 2.10 백슬래시가 필요한 일부 문자들.
- study_note: 텍스트 내의 특수 기호를 있는 그대로 찾기 위해 '이스케이프' 처리가 필요한 대상들을 정리한 표입니다.

## Block 4
- type: section_title
- source_text: 2.1.5 A More Complex Example
- korean_translation: 2.1.5 더 복잡한 예시
- study_note: 여러 제약 조건이 섞인 실제 상황에서 정규 표현식을 설계하는 과정을 살펴봅니다.

## Block 5
- type: paragraph
- source_text: Let’s try out a more significant example of the power of REs. Suppose we want to build an application to help a user buy a computer on the Web. The user might want “any machine with at least 6 GHz and 500 GB of disk space for less than $1000”. To do this kind of retrieval, we first need to be able to look for expressions like 6 GHz or 500 GB or Mac or $999.99. In the rest of this section we’ll work out some simple regular expressions for this task. First, let’s complete our regular expression for prices. Here’s a regular expression for a dollar sign followed by a string of digits:
- korean_translation: 정규 표현식의 위력을 보여주는 더 중요한 예시를 시도해 봅시다. 웹에서 사용자가 컴퓨터를 구매하는 것을 돕는 애플리케이션을 구축한다고 가정해 봅시다. 사용자는 "6 GHz 이상, 디스크 공간 500 GB 이상이며 가격은 $1000 미만인 모든 기기"를 원할 수 있습니다. 이런 종류의 검색을 수행하려면 먼저 6 GHz, 500 GB, Mac 또는 $999.99와 같은 표현을 찾을 수 있어야 합니다. 이 섹션의 남은 부분에서 우리는 이 작업을 위한 몇 가지 간단한 정규 표현식을 만들어 볼 것입니다. 먼저 가격을 위한 표현식을 완성해 봅시다. 다음은 달러 기호($) 뒤에 숫자 문자열이 뒤따르는 정규 표현식입니다.
- study_note: 사용자의 자연어 요구 사항에서 핵심 정보를 추출하기 위한 복합적인 정규 표현식 설계 과정을 시작합니다.

## Block 6
- type: code
- source_text: /$[0-9]+/
- korean_translation: /$[0-9]+/
- study_note: 달러 기호와 그 뒤에 오는 하나 이상의 숫자를 찾는 기초적인 가격 패턴입니다.

## Block 7
- type: paragraph
- source_text: Note that the $ character has a different function here than the end-of-line function we discussed earlier. Most regular expression parsers are smart enough to realize that $ here doesn’t mean end-of-line. (As a thought experiment, think about how regex parsers might figure out the function of $ from the context.)
- korean_translation: 여기서 $ 문자는 앞서 다루었던 줄의 끝(end-of-line)과는 다른 기능을 수행한다는 점에 유의하십시오. 대부분의 정규 표현식 파서(parser)는 여기서 $가 줄의 끝을 의미하지 않는다는 것을 충분히 인식할 만큼 똑똑합니다. (사고 실험으로서, 정규 표현식 파서가 문맥을 통해 $의 기능을 어떻게 파악하는지 생각해 보십시오.)
- study_note: `$` 기호가 위치에 따라 '줄의 끝'이라는 앵커 역할과 '달러 기호'라는 일반 문자 역할을 겸하는 중의성을 설명합니다.

## Block 8
- type: paragraph
- source_text: Now we just need to deal with fractions of dollars. We’ll add a decimal point and two digits afterwards:
- korean_translation: 이제 달러의 소수점 단위를 처리해야 합니다. 소수점과 그 뒤에 오는 두 자리 숫자를 추가해 보겠습니다.
- study_note: 정확한 가격 표현을 위해 소수점 이하 단위를 포함하도록 패턴을 확장합니다.

## Block 9
- type: code
- source_text: /$[0-9]+\.[0-9][0-9]/
- korean_translation: /$[0-9]+\.[0-9][0-9]/
- study_note: 소수점 이하까지 포함된 가격을 찾는 패턴입니다. 여기서 `\.`은 실제 마침표 문자를 의미하기 위해 백슬래시로 이스케이프 처리되었습니다.

## Block 10
- type: paragraph
- source_text: This pattern only allows $199.99 but not $199. We need to make the cents optional and to make sure we’re at a word boundary:
- korean_translation: 이 패턴은 $199.99는 찾지만 $199는 찾지 못합니다. 우리는 센트(cents) 단위를 선택사항으로 만들고, 단어 경계(\b)에 있는지 확인해야 합니다.
- study_note: 정수 가격과 소수점 가격을 모두 수용하고, 다른 문자열에 포함된 숫자가 오답으로 걸리지 않도록 `?`와 `\b`를 활용해 개선합니다.

## Block 11
- type: code
- source_text: /(^|\W)$[0-9]+(\.[0-9][0-9])?\b/
- korean_translation: /(^|\W)$[0-9]+(\.[0-9][0-9])?\b/
- study_note: 줄의 시작이나 영숫자가 아닌 문자 뒤에 달러가 오고, 센트 단위는 있을 수도 없을 수도 있는(`?`) 완성도 높은 가격 매칭 패턴입니다.

## Block 12
- type: paragraph
- source_text: One last catch! This pattern allows prices like $199999.99 which would be far too expensive! We need to limit the dollars:
- korean_translation: 마지막 함정입니다! 이 패턴은 $199999.99와 같이 너무 비싼 가격도 허용하고 맙니다! 우리는 달러 단위를 제한해야 합니다.
- study_note: 숫자의 반복 횟수를 지정하여 실제 컴퓨터 가격 범위를 벗어나는 거대 숫자를 제외하는 조건을 추가합니다.

## Block 13
- type: code
- source_text: /(^|\W)$[0-9]{0,3}(\.[0-9][0-9])?\b/
- korean_translation: /(^|\W)$[0-9]{0,3}(\.[0-9][0-9])?\b/
- study_note: `{0,3}`을 사용하여 소수점 앞 숫자가 최대 3자리(즉, $999.99 이하)까지만 오도록 제약한 버전입니다.

## Block 14
- type: paragraph
- source_text: How about disk space? We’ll need to allow for optional fractions again (5.5 GB); note the use of ? for making the final s optional, and the of /␣*/ to mean “zero or more spaces” since there might always be extra spaces lying around:
- korean_translation: 디스크 공간은 어떨까요? 여기에서도 선택적인 소수점 단위(5.5 GB)를 허용해야 합니다. 마지막 s를 선택사항으로 만들기 위한 ?의 사용과, 주변에 여분의 공백이 있을 때를 대비해 "0개 이상의 공백"을 의미하는 /␣*/를 사용한 점에 유의하십시오.
- study_note: 용량 단위인 GB와 기가바이트(Gigabytes)를 모두 처리하고, 숫자와 단위 사이의 공백 유무에 유연하게 대응하는 패턴을 설계합니다.

## Block 15
- type: code
- source_text: /\b[0-9]+(\.[0-9]+)?␣*(GB|[Gg]igabytes?)\b/
- korean_translation: /\b[0-9]+(\.[0-9]+)?␣*(GB|[Gg]igabytes?)\b/
- study_note: 소수점 용량, 공백 처리, 그리고 다양한 단위 표기(GB, gigabyte, gigabytes)를 모두 수용하는 복합적인 패턴입니다.

## Block 16
- type: paragraph
- source_text: Modifying this regular expression so that it only matches more than 500 GB is left as an exercise for the reader.
- korean_translation: 이 정규 표현식을 500 GB 이상인 경우만 일치하도록 수정하는 것은 독자를 위한 연습 문제로 남겨 두겠습니다.
- study_note: 숫자 범위를 논리적으로 제한하는 응용 과제를 제시합니다.

## Block 17
- type: section_title
- source_text: 2.1.6 Substitution, Capture Groups, and ELIZA
- korean_translation: 2.1.6 치환, 캡처 그룹, 그리고 ELIZA
- study_note: 정규 표현식을 단순히 찾는 것에서 나아가, 찾은 내용을 바꾸는(substitution) 강력한 기능을 배울 차례입니다.

## Block 18
- type: margin_note
- source_text: substitution
- korean_translation: 치환(substitution)
- study_note: 매칭된 문자열을 다른 문자열로 교체하는 작업을 뜻하는 키워드입니다.

## Block 19
- type: paragraph
- source_text: An important use of regular expressions is in substitutions. For example, the substitution operator s/regexp1/pattern/ used in Python and in Unix commands like vim or sed allows a string characterized by a regular expression to be replaced by another string:
- korean_translation: 정규 표현식의 중요한 용도 중 하나는 치환입니다. 예를 들어 Python이나 vim, sed와 같은 Unix 명령에서 사용되는 치환 연산자 s/regexp1/pattern/은 정규 표현식에 의해 식별된 문자열을 다른 문자열로 대체할 수 있게 해 줍니다. [다음 페이지에서 계속]
- study_note: 치환의 기본적인 문법 구조인 `s/검색패턴/바꿀패턴/` 기법을 소개하며, 이를 지원하는 다양한 도구들을 언급합니다.
# Pages 9-10

Source: `2. Regular Expressions, Text Normalization, Edit Distance.pdf`
Workflow: `html-codex-flash`
Status: accepted

# Page 9

## Block 1
- type: code
- source_text: s/colour/color/
- korean_translation: s/colour/color/
- study_note: 영국식 철자인 'colour'를 미국식 철자인 'color'로 바꾸는 가장 기본적인 치환 예시입니다.

## Block 2
- type: paragraph
- source_text: It is often useful to be able to refer to a particular subpart of the string matching the first pattern. For example, suppose we wanted to put angle brackets around all integers in a text, for example, changing the 35 boxes to the <35> boxes. We’d like a way to refer to the integer we’ve found so that we can easily add the brackets. To do this, we put parentheses ( and ) around the first pattern and use the number operator \1 in the second pattern to refer back. Here’s how it looks:
- korean_translation: 첫 번째 패턴과 일치하는 문자열의 특정 일부분을 참조할 수 있다면 매우 유용할 때가 많습니다. 예를 들어, 텍스트에 포함된 모든 정수에 꺾쇠괄호를 씌우고 싶다고 가정해 봅시다. 즉, '35 boxes'를 '<35> boxes'로 바꾸는 것입니다. 우리가 찾은 정수를 참조해서 괄호를 쉽게 씌울 방법이 필요합니다. 이를 위해 첫 번째 패턴 주위에 소괄호 ( 와 )를 두르고, 두 번째 패턴에서 숫자 연산자 \1을 사용하여 이를 다시 참조합니다. 다음과 같은 모습입니다.
- study_note: 매칭된 문자열의 일부를 기억해 두었다가 나중에 다시 사용하는 '역참조(backreference)'의 기본 개념을 설명합니다. 소괄호는 기억할 범위를 지정하고, `\1`은 그 기억된 내용을 불러오는 통로 역할을 합니다.

## Block 3
- type: code
- source_text: s/([0-9]+)/<\1>/
- korean_translation: s/([0-9]+)/<\1>/
- study_note: 숫자들을 찾아서(`([0-9]+)`) 그 찾은 내용물(`\1`)의 앞뒤에 `<`와 `>`를 붙여 치환하는 정규 표현식입니다.

## Block 4
- type: paragraph
- source_text: The parenthesis and number operators can also specify that a certain string or expression must occur twice in the text. For example, suppose we are looking for the pattern “the Xer they were, the Xer they will be”, where we want the two X’s to be the same string. We do this by surrounding the first X with the parenthesis operator, and replacing the second X with the number operator \1, as follows:
- korean_translation: 소괄호와 숫자 연산자는 특정 문자열이나 표현식이 텍스트 내에서 두 번 나타나야 함을 지정할 때도 쓰일 수 있습니다. 예를 들어, "the Xer they were, the Xer they will be"라는 패턴을 찾고 있는데, 두 개의 X가 반드시 동일한 문자열이어야 한다고 가정해 봅시다. 우리는 첫 번째 X를 소괄호 연산자로 감싸고, 두 번째 X를 숫자 연산자 \1로 교체함으로써 이를 구현할 수 있습니다.
- study_note: 역참조를 활용해 '반복되는 동일한 패턴'을 찾는 방법을 설명합니다. 단순히 형태가 같은 것이 아니라, 실제로 매칭된 '값' 자체가 동일해야 하는 제약 조건을 걸 때 사용합니다.

## Block 5
- type: code
- source_text: /the (.*)er they were, the \1er they will be/
- korean_translation: /the (.*)er they were, the \1er they will be/
- study_note: 첫 번째 괄호에서 매칭된 내용(`(.*)`)이 뒤의 `\1` 자리에서도 똑같이 나타나야 함을 의미합니다.

## Block 6
- type: paragraph
- source_text: Here the \1 will be replaced by whatever string matched the first item in parentheses. So this will match the bigger they were, the bigger they will be but not the bigger they were, the faster they will be.
- korean_translation: 여기서 \1은 소괄호 안의 첫 번째 항목과 일치했던 문자열로 대체됩니다. 따라서 이 패턴은 "the bigger they were, the bigger they will be"와는 일치하지만, "the bigger they were, the faster they will be"와는 일치하지 않습니다.
- study_note: 역참조가 어떻게 '동일성'을 보장하는지 구체적인 예시를 통해 보여줍니다.

## Block 7
- type: margin_note
- source_text:
  capture group
  register
- korean_translation:
  캡처 그룹
  레지스터
- study_note: 소괄호로 묶인 패턴과 그 패턴이 매칭된 결과를 저장하는 임시 저장 공간을 일컫는 용어들입니다.

## Block 8
- type: paragraph
- source_text: This use of parentheses to store a pattern in memory is called a capture group. Every time a capture group is used (i.e., parentheses surround a pattern), the resulting match is stored in a numbered register. If you match two different sets of parentheses, \2 means whatever matched the second capture group. Thus
- korean_translation: 패턴을 메모리에 저장하기 위해 소괄호를 사용하는 것을 캡처 그룹(capture group)이라고 부릅니다. 캡처 그룹이 사용될 때마다(즉, 패턴을 소괄호로 감쌀 때마다), 그 결과로 얻은 매칭 값은 번호가 매겨진 레지스터(register)에 저장됩니다. 만약 두 쌍의 소괄호를 사용해 매칭한다면, \2는 두 번째 캡처 그룹과 일치한 내용물을 의미하게 됩니다. 따라서
- study_note: 캡처 그룹과 번호가 매겨진 레지스터의 관계를 설명합니다. 괄호가 열리는 순서대로 `\1`, `\2`, `\3` 등의 번호가 부여됩니다.

## Block 9
- type: code
- source_text: /the (.*)er they (.*), the \1er we \2/
- korean_translation: /the (.*)er they (.*), the \1er we \2/
- study_note: 두 개의 서로 다른 캡처 그룹을 각각 `\1`과 `\2`로 역참조하는 복합 패턴의 예시입니다.

## Block 10
- type: paragraph
- source_text:
  will match the faster they ran, the faster we ran but not the faster they ran, the faster we ate. Similarly, the third capture group is stored in \3, the fourth is in \4, and so on.
  Parentheses thus have a double function in regular expressions; they are used to group terms for specifying the order in which operators should apply, and they are used to capture something in a register. Occasionally we might want to use parentheses for grouping, but don’t want to capture the resulting pattern in a register. In that case we use a non-capturing group, which is specified by putting the commands ?: after the open paren, in the form (?: pattern ).
- korean_translation:
  이 패턴은 "the faster they ran, the faster we ran"과는 일치하지만 "the faster they ran, the faster we ate"와는 일치하지 않을 것입니다. 마찬가지로 세 번째 캡처 그룹은 \3에, 네 번째는 \4에 저장되는 식입니다.
  이처럼 정규 표현식에서 소괄호는 이중적인 기능을 가집니다. 연산자가 적용되는 순서를 지정하기 위해 항들을 묶는(grouping) 용도로 쓰이기도 하고, 레지스터에 무언가를 캡처(capture)하는 용도로도 쓰입니다. 때때로 그룹화는 하고 싶지만 그 결과를 레지스터에 캡처하고 싶지는 않을 때가 있습니다. 그런 경우에는 여는 괄호 뒤에 ?: 명령어를 붙여 (?: pattern ) 형식으로 쓰는 비캡처 그룹(non-capturing group)을 사용합니다.
- study_note: 소괄호의 두 가지 역할(그룹화 및 캡처)을 구분하고, 메모리 낭비를 줄이거나 번호를 꼬이지 않게 하기 위한 '비캡처 그룹'(`(?:)`)의 사용법을 설명합니다.

## Block 11
- type: margin_note
- source_text:
  non-capturing group
- korean_translation:
  비캡처 그룹
- study_note: 매칭 결과 저장(캡처) 기능 없이 오직 그룹화 기능만 수행하는 소괄호 형태입니다.

## Block 12
- type: code
- source_text: /(?:some|a few) (people|cats) like some \1/
- korean_translation: /(?:some|a few) (people|cats) like some \1/
- study_note: 첫 번째 괄호는 비캡처 그룹이므로 `\1`은 두 번째 괄호인 `(people|cats)`를 참조하게 됩니다.

## Block 13
- type: paragraph
- source_text:
  will match some cats like some cats but not some cats like some a few.
  Substitutions and capture groups are very useful in implementing simple chatbots like ELIZA (Weizenbaum, 1966). Recall that ELIZA simulates a Rogerian psychologist by carrying on conversations like the following:
- korean_translation:
  이 패턴은 "some cats like some cats"와는 일치하지만 "some cats like some a few"와는 일치하지 않을 것입니다.
  치환과 캡처 그룹은 엘리자(ELIZA, Weizenbaum, 1966)와 같은 간단한 챗봇을 구현할 때 매우 유용합니다. 엘리자는 다음과 같은 대화를 이어감으로써 로저스(Rogerian) 심리 치료사를 흉내 낸다는 점을 기억해 보십시오.
- study_note: 캡처 그룹과 치환 기법이 실제 응용 사례인 초기 인공지능 챗봇 '엘리자'에서 어떻게 활용되는지 소개하며 흥미를 유발합니다.

## Block 14
- type: table
- source_text:
  [table]
  row 1: User1: | Men are all alike.
  row 2: ELIZA1: | IN WHAT WAY
  row 3: User2: | They’re always bugging us about something or other.
  row 4: ELIZA2: | CAN YOU THINK OF A SPECIFIC EXAMPLE
  row 5: User3: | Well, my boyfriend made me come here.
  row 6: ELIZA3: | YOUR BOYFRIEND MADE YOU COME HERE
  row 7: User4: | He says I’m depressed much of the time.
  row 8: ELIZA4: | I AM SORRY TO HEAR YOU ARE DEPRESSED
- korean_translation:
  [table]
  행 1: 사용자1: | 남자들은 다 똑같아요.
  행 2: 엘리자1: | 어떤 면에서요?
  행 3: 사용자2: | 그들은 항상 이런저런 일로 우리를 괴롭혀요.
  행 4: 엘리자2: | 구체적인 예를 하나 들어줄 수 있나요?
  행 5: 사용자3: | 음, 제 남자친구가 여기 오게 했어요.
  행 6: 엘리자3: | 당신의 남자친구가 당신을 여기 오게 했군요.
  행 7: 사용자4: | 그는 제가 거의 항상 우울해 보인대요.
  행 8: 엘리자4: | 당신이 우울하다니 안타까운 일이네요.
- study_note: 엘리자의 대화 예시입니다. 사용자의 입력을 적절히 변형하여(치환) 다시 질문하는 방식을 통해 대화를 이어가는 것을 볼 수 있습니다.

## Block 15
- type: paragraph
- source_text: ELIZA works by having a series or cascade of regular expression substitutions each of which matches and changes some part of the input lines. Input lines are
- korean_translation: 엘리자는 입력된 줄의 일부를 매칭하고 변경하는 일련의 정규 표현식 치환(substitutions) 과정을 거쳐 작동합니다. 입력된 줄들은 [다음 페이지에서 계속]
- study_note: 엘리자의 작동 원리가 정규 표현식 기반의 단계적인 치환 알고리즘임을 설명합니다.

# Page 10

## Block 1
- type: other
- source_text: 10 CHAPTER 2 • REGULAR EXPRESSIONS, TEXT NORMALIZATION, EDIT DISTANCE
- korean_translation: 10 제2장 • 정규 표현식, 텍스트 정규화, 편집 거리
- study_note: 페이지 상단의 장 제목과 페이지 번호(10) 정보입니다.

## Block 2
- type: paragraph
- source_text:
  first uppercased. The first substitutions then change all instances of MY to YOUR, and I’M to YOU ARE, and so on. The next set of substitutions matches and replaces other patterns in the input. Here are some examples:
- korean_translation:
  먼저 대문자로 변환됩니다. 그 후 첫 번째 치환 과정에서 모든 'MY'는 'YOUR'로, 'I'M'은 'YOU ARE' 등으로 바뀝니다. 그다음 치환 세트는 입력값의 다른 패턴들을 매칭하고 교체합니다. 몇 가지 예시는 다음과 같습니다.
- study_note: 엘리자가 대화를 생성하기 위해 거치는 전처리(대문자화)와 1인칭-2인칭 전환 과정을 설명합니다.

## Block 3
- type: code
- source_text:
  s/.* I’M (depressed|sad) .*/I AM SORRY TO HEAR YOU ARE \1/
  s/.* I AM (depressed|sad) .*/WHY DO YOU THINK YOU ARE \1/
  s/.* all .*/IN WHAT WAY/
  s/.* always .*/CAN YOU THINK OF A SPECIFIC EXAMPLE/
- korean_translation:
  s/.* I’M (depressed|sad) .*/당신이 \1하다니 안타까운 일이네요/
  s/.* I AM (depressed|sad) .*/왜 당신이 \1하다고 생각하시나요?/
  s/.* all .*/어떤 면에서요?/
  s/.* always .*/구체적인 예를 하나 들어줄 수 있나요?/
- study_note: 엘리자의 핵심 로직인 치환 규칙들입니다. `\1`을 사용해 사용자의 기분(depressed/sad)을 그대로 가져와 답변에 반영하는 것을 볼 수 있습니다.

## Block 4
- type: paragraph
- source_text:
  Since multiple substitutions can apply to a given input, substitutions are assigned a rank and applied in order. Creating patterns is the topic of Exercise 2.3, and we return to the details of the ELIZA architecture in Chapter 24.
- korean_translation:
  하나의 입력에 여러 치환 규칙이 적용될 수 있으므로, 각 치환에는 순위(rank)가 매겨지며 순서대로 적용됩니다. 패턴을 설계하는 것은 연습 문제 2.3의 주제이며, 엘리자 아키텍처에 대한 자세한 내용은 24장에서 다시 다룹니다.
- study_note: 챗봇 시스템에서 규칙 간의 충돌을 방지하고 우선순위를 부여하는 '순위(rank)' 개념을 언급합니다.

## Block 5
- type: section_title
- source_text: 2.1.7 Lookahead Assertions
- korean_translation: 2.1.7 룩어헤드 어설션 (Lookahead Assertions)
- study_note: 현재 위치 뒤에 특정 패턴이 오는지 여부를 확인하지만, 실제로 그 문자를 '소비'하지는 않는 특수한 조건 확인 기법인 룩어헤드(전방 탐색)를 배웁니다.

## Block 6
- type: paragraph
- source_text:
  Finally, there will be times when we need to predict the future: look ahead in the text to see if some pattern matches, but not advance the match cursor, so that we can then deal with the pattern if it occurs.
- korean_translation:
  마지막으로, 미래를 예측해야 할 때가 있을 것입니다. 즉, 텍스트의 앞부분을 미리 살펴서 특정 패턴이 일치하는지 확인하되, 매칭 커서(cursor)를 이동시키지는 않음으로써 패턴이 발생했을 때 이를 추가로 처리할 수 있게 하는 것입니다.
- study_note: 룩어헤드의 정의를 '미래 예측'에 비유하여 설명합니다. 가장 큰 특징은 확인만 할 뿐 커서가 이동하지 않는다는 점입니다.

## Block 7
- type: margin_note
- source_text:
  lookahead
  zero-width
- korean_translation:
  룩어헤드 (전방 탐색)
  제로 너비 (zero-width)
- study_note: 룩어헤드와 그 성질(문자를 차지하지 않음)을 나타내는 주요 키워드입니다.

## Block 8
- type: paragraph
- source_text: These lookahead assertions make use of the (? syntax that we saw in the previous section for non-capture groups. The operator (?= pattern) is true if pattern occurs, but is zero-width, i.e. the match pointer doesn’t advance. The operator (?! pattern) only returns true if a pattern does not match, but again is zero-width and doesn’t advance the cursor. Negative lookahead is commonly used when we are parsing some complex pattern but want to rule out a special case. For example suppose we want to match, at the beginning of a line, any single word that doesn’t start with “Volcano”. We can use negative lookahead to do this:
- korean_translation: 이러한 룩어헤드 어설션은 앞 절에서 비캡처 그룹을 설명할 때 보았던 `(?` 구문을 활용합니다. `(?= pattern)` 연산자는 pattern이 나타나면 참이 되지만 제로 너비이므로, 즉 매치 포인터가 앞으로 이동하지 않습니다. `(?! pattern)` 연산자는 pattern이 일치하지 않을 때만 참을 반환하며, 이 경우에도 제로 너비이므로 커서를 전진시키지 않습니다. 부정 룩어헤드는 복잡한 패턴을 해석하면서 특정한 예외 경우를 배제하고 싶을 때 흔히 사용됩니다. 예를 들어, 줄의 시작에서 “Volcano”로 시작하지 않는 임의의 한 단어와 일치시키고 싶다고 가정해 봅시다. 이를 위해 다음과 같이 할 수 있습니다:
- study_note: 룩어헤드는 조건을 검사하지만 문자열을 소비하지 않는다는 점이 핵심입니다. 특히 부정 룩어헤드는 “이 패턴만은 제외하고 싶다”는 조건을 걸 때 매우 유용합니다.
# Pages 11-12

Source: `2. Regular Expressions, Text Normalization, Edit Distance.pdf`
Workflow: `html-codex-flash`
Status: accepted

# Page 11

## Block 1
- type: paragraph
- source_text: duce other complications with regard to defining words. Let’s look at one utterance from Switchboard; an utterance is the spoken correlate of a sentence:
- korean_translation: 단어를 정의하는 데 있어 또 다른 복잡한 문제들이 발생합니다. 스위치보드(Switchboard) 코퍼스에서 추출한 하나의 발화(utterance)를 살펴봅시다. 발화란 문장에 대응되는 구어적 실체를 의미합니다.
- study_note: 구어(spoken language) 데이터에서 문장에 해당하는 단위를 '발화(utterance)'라고 부릅니다. 이는 텍스트 데이터의 문장과는 다른 특성을 가집니다.

## Block 2
- type: margin_note
- source_text: utterance
- korean_translation: 발화(utterance)
- study_note: 구어에서 한 번의 호흡이나 의미 단위로 내뱉는 말의 묶음을 뜻합니다.

## Block 3
- type: code
- source_text: I do uh main- mainly business data processing
- korean_translation: I do uh main- mainly business data processing (저는 어, 주- 주로 비즈니스 데이터 처리를 합니다)
- study_note: 실제 구어 데이터의 예시로, 중간에 말이 끊기거나 'uh'와 같은 추임새가 섞여 있는 것을 볼 수 있습니다.

## Block 4
- type: paragraph
- source_text: This utterance has two kinds of disfluencies. The broken-off word main- is called a fragment. Words like uh and um are called fillers or filled pauses. Should we consider these to be words? Again, it depends on the application. If we are building a speech transcription system, we might want to eventually strip out the disfluencies.
- korean_translation: 이 발화에는 두 가지 종류의 비유창성(disfluencies)이 나타납니다. 'main-'처럼 중간에 끊긴 단어는 파편(fragment)이라고 부릅니다. 'uh'나 'um' 같은 단어들은 충진어(fillers) 또는 채워진 일시 정지(filled pauses)라고 합니다. 이것들을 단어로 간주해야 할까요? 이 역시 애플리케이션에 따라 다릅니다. 만약 우리가 음성 전사(speech transcription) 시스템을 구축한다면, 결국 이러한 비유창성 요소들을 제거하고 싶을 것입니다.
- study_note: 구어 시스템 구축 시 마주하는 비유창성 요소들인 파편(fragment)과 충진어(fillers)를 정의합니다. 이를 단어로 처리할지 여부는 목적에 따라 결정됩니다.

## Block 5
- type: margin_note
- source_text:
  disfluency
  fragment
  filled pause
- korean_translation:
  비유창성(disfluency)
  파편(fragment)
  채워진 일시 정지(filled pause)
- study_note: 구어 분석에서 말이 매끄럽게 이어지지 않는 현상과 그 세부 유형들을 일컫는 용어들입니다.

## Block 6
- type: paragraph
- source_text: But we also sometimes keep disfluencies around. Disfluencies like uh or um are actually helpful in speech recognition in predicting the upcoming word, because they may signal that the speaker is restarting the clause or idea, and so for speech recognition they are treated as regular words. Because people use different disfluencies they can also be a cue to speaker identification. In fact Clark and Fox Tree (2002) showed that uh and um have different meanings. What do you think they are?
- korean_translation: 하지만 때로는 비유창성 요소들을 유지하기도 합니다. 'uh'나 'um' 같은 비유창성은 실제로 음성 인식에서 다음에 올 단어를 예측하는 데 도움이 될 수 있는데, 이는 화자가 절(clause)이나 아이디어를 다시 시작하려 한다는 신호가 될 수 있기 때문입니다. 따라서 음성 인식에서는 이를 일반 단어처럼 취급합니다. 또한 사람마다 사용하는 비유창성 요소가 다르기 때문에 화자 식별(speaker identification)의 단서가 되기도 합니다. 실제로 클라크와 폭스 트리(Clark and Fox Tree, 2002)는 'uh'와 'um'이 서로 다른 의미를 가지고 있음을 보여주었습니다. 그것들이 무엇이라고 생각하시나요?
- study_note: 비유창성 요소가 단순한 소음이 아니라 화자의 상태나 정체성을 파악하는 정보원으로서 가치를 가질 수 있음을 설명합니다.

## Block 7
- type: paragraph
- source_text: Are capitalized tokens like They and uncapitalized tokens like they the same word? These are lumped together in some tasks (speech recognition), while for part-of-speech or named-entity tagging, capitalization is a useful feature and is retained.
- korean_translation: 'They'와 같이 대문자로 시작하는 토큰과 'they'처럼 소문자로 된 토큰은 같은 단어일까요? 어떤 작업(음성 인식)에서는 이들을 하나로 묶어 처리하는 반면, 품사 부착(part-of-speech tagging)이나 개체명 인식(named-entity tagging)에서는 대문자 여부가 유용한 특징(feature)이 되므로 그대로 유지합니다.
- study_note: 대소문자 구분이 작업의 성격에 따라 중요한 정보가 될 수도, 무시해야 할 차이가 될 수도 있음을 보여줍니다.

## Block 8
- type: paragraph
- source_text: How about inflected forms like cats versus cat? These two words have the same lemma cat but are different wordforms. A lemma is a set of lexical forms having the same stem, the same major part-of-speech, and the same word sense. The wordform is the full inflected or derived form of the word. For morphologically complex languages like Arabic, we often need to deal with lemmatization. For many tasks in English, however, wordforms are sufficient.
- korean_translation: 'cats'와 'cat' 같은 굴절 형태들은 어떨까요? 이 두 단어는 동일한 표제어(lemma)인 'cat'을 공유하지만 서로 다른 어형(wordforms)입니다. 표제어는 동일한 어간, 동일한 주요 품사, 그리고 동일한 단어 의미를 가진 어휘 형태들의 집합입니다. 어형은 단어의 완전한 굴절 또는 파생 형태입니다. 아랍어와 같이 형태론적으로 복잡한 언어의 경우, 우리는 흔히 표제어 추출(lemmatization) 과정을 거쳐야 합니다. 하지만 영어의 많은 작업에서는 어형만으로도 충분한 경우가 많습니다.
- study_note: 표제어(lemma)와 어형(wordform)의 차이점을 정의합니다. 표제어 추출은 문법적 변형을 제거하고 기본형을 찾는 중요한 전처리 단계입니다.

## Block 9
- type: margin_note
- source_text:
  lemma
  wordform
- korean_translation:
  표제어(lemma)
  어형(wordform)
- study_note: 단어의 기본 사전형인 표제어와, 실제 텍스트에 나타나는 다양한 변형 형태인 어형을 구분하는 개념입니다.

## Block 10
- type: paragraph
- source_text: How many words are there in English? To answer this question we need to distinguish two ways of talking about words. Types are the number of distinct words in a corpus; if the set of words in the vocabulary is V, the number of types is the vocabulary size |V|. Tokens are the total number N of running words. If we ignore punctuation, the following Brown sentence has 16 tokens and 14 types:
- korean_translation: 영어에는 얼마나 많은 단어가 있을까요? 이 질문에 답하기 위해 우리는 단어를 이야기하는 두 가지 방식을 구분해야 합니다. 유형(Types)은 코퍼스에 나타나는 서로 다른 단어의 수입니다. 어휘 집합이 V라면, 유형의 수는 어휘 크기인 |V|가 됩니다. 토큰(Tokens)은 사용된 단어의 총 개수 N을 의미합니다. 문장 부호를 무시한다면, 다음의 브라운 코퍼스 문장에는 16개의 토큰과 14개의 유형이 있습니다.
- study_note: 코퍼스의 규모를 측정하는 두 가지 척도인 토큰(전체 사용 횟수)과 유형(유니크한 단어 수)을 정의합니다. 유형의 수는 곧 어휘 목록의 크기를 의미합니다.

## Block 11
- type: margin_note
- source_text:
  word type
  word token
- korean_translation:
  단어 유형(word type)
  단어 토큰(word token)
- study_note: 유니크한 단어의 개수(유형)와 전체 단어의 개수(토큰)를 뜻하는 기초적이며 중요한 통계 용어입니다.

## Block 12
- type: code
- source_text: They picnicked by the pool, then lay back on the grass and looked at the stars.
- korean_translation: They picnicked by the pool, then lay back on the grass and looked at the stars. (그들은 수영장가에서 소풍을 즐겼고, 풀밭에 누워 별들을 바라보았다.)
- study_note: 총 16개의 단어로 이루어져 있지만, 'the'와 같은 단어가 반복되므로 유니크한 단어(유형)는 14개가 되는 예시 문장입니다.

## Block 13
- type: paragraph
- source_text: When we speak about the number of words in the language, we are generally referring to word types.
- korean_translation: 우리가 한 언어의 단어 개수에 대해 말할 때는, 일반적으로 단어 유형(word types)을 의미합니다.
- study_note: 특정 언어나 분야의 어휘 규모를 논할 때는 중복을 제외한 단어 유형의 개수가 기준이 됩니다.

## Block 14
- type: table
- source_text:
  [table]
  row 1: Corpus | Tokens = N | Types = |V|
  row 2: Shakespeare | 884 thousand | 31 thousand
  row 3: Brown corpus | 1 million | 38 thousand
  row 4: Switchboard telephone conversations | 2.4 million | 20 thousand
  row 5: COCA | 440 million | 2 million
  row 6: Google n-grams | 1 trillion | 13 million
- korean_translation:
  [table]
  행 1: 코퍼스 | 토큰 수 = N | 유형 수 = |V|
  행 2: 셰익스피어 전집 | 88만 4천 | 3만 1천
  행 3: 브라운 코퍼스 | 100만 | 3만 8천
  행 4: 스위치보드 전화 대화 | 240만 | 2만
  행 5: COCA (미국 현대 영어 코퍼스) | 4억 4천만 | 200만
  행 6: 구글 N-gram | 1조 | 1,300만
- study_note: 다양한 코퍼스의 토큰 수와 유형 수의 관계를 보여줍니다. 데이터의 규모(토큰 수)가 커짐에 따라 어휘의 종류(유형 수)도 늘어나지만, 그 증가 속도는 점차 둔화되는 양상을 보입니다.

## Block 15
- type: figure_caption
- source_text: Figure 2.11 Rough numbers of types and tokens for some English language corpora. The largest, the Google n-grams corpus, contains 13 million types, but this count only includes types appearing 40 or more times, so the true number would be much larger.
- korean_translation: 그림 2.11 일부 영어 코퍼스에 대한 유형 수와 토큰 수의 대략적인 수치. 가장 큰 규모인 구글 N-gram 코퍼스는 1,300만 개의 유형을 포함하고 있지만, 이 수치는 40번 이상 나타난 유형들만 포함한 것이므로 실제 수치는 훨씬 더 클 것입니다.
- study_note: 코퍼스 통계 수치를 설명하는 캡션입니다. 구글 데이터의 경우 희귀 단어들을 제외했음에도 막대한 어휘 규모를 보여준다는 점이 특징입니다.

## Block 16
- type: paragraph
- source_text: Fig. 2.11 shows the rough numbers of types and tokens computed from some popular English corpora. The larger the corpora we look at, the more word types we find, and in fact this relationship between the number of types |V| and number of tokens N is called Herdan’s Law (Herdan, 1960) or Heaps’ Law (Heaps, 1978) after its discoverers (in linguistics and information retrieval respectively). It is shown in Eq. 2.1, where k and β are positive constants, and 0 < β < 1.
- korean_translation: 그림 2.11은 널리 사용되는 일부 영어 코퍼스에서 계산된 유형 수와 토큰 수의 대략적인 수치를 보여줍니다. 우리가 보는 코퍼스의 규모가 커질수록 더 많은 단어 유형을 발견하게 되는데, 실제로 유형의 수 |V|와 토큰의 수 N 사이의 이러한 관계는 발견자들의 이름을 따서 (각각 언어학과 정보 검색 분야에서) 허단 법칙(Herdan’s Law, 1960) 또는 힙스 법칙(Heaps’ Law, 1978)이라고 불립니다. 이는 식 2.1에 나타나 있으며, 여기서 k와 β는 양의 상수이고 0 < β < 1입니다.
- study_note: 코퍼스의 크기(N)와 어휘의 크기(|V|) 사이의 수학적 관계인 힙스 법칙을 소개합니다. 데이터가 늘어남에 따라 새로운 단어가 발견되는 속도가 어떻게 변하는지 수학적으로 모델링합니다.

## Block 17
- type: margin_note
- source_text:
  Herdan’s Law
  Heaps’ Law
- korean_translation:
  허단 법칙 (Herdan’s Law)
  힙스 법칙 (Heaps’ Law)
- study_note: 어휘 수의 증가 법칙을 일컫는 고유 명칭입니다.

## Block 18
- type: formula
- source_text: |V| = k N^β (2.1)
- korean_translation: |V| = k N^β (2.1)
- study_note: 힙스 법칙의 수식입니다. 어휘 크기가 전체 토큰 수의 거듭제곱(β < 1)에 비례한다는 것을 보여주며, 이는 어휘의 증가 속도가 점차 느려짐을 의미합니다.

# Page 12

## Block 1
- type: other
- source_text: 12 CHAPTER 2 • REGULAR EXPRESSIONS, TEXT NORMALIZATION, EDIT DISTANCE
- korean_translation: 12 제2장 • 정규 표현식, 텍스트 정규화, 편집 거리
- study_note: 페이지 상단의 장 제목과 페이지 번호(12) 정보입니다.

## Block 2
- type: paragraph
- source_text: The value of β depends on the corpus size and the genre, but at least for the large corpora in Fig. 2.11, β ranges from .67 to .75. Roughly then we can say that the vocabulary size for a text goes up significantly faster than the square root of its length in words.
- korean_translation: β 값은 코퍼스의 크기와 장르에 따라 달라지지만, 적어도 그림 2.11에 제시된 대규모 코퍼스들의 경우 β는 0.67에서 0.75 사이의 범위를 가집니다. 대략적으로 말하자면, 텍스트의 어휘 크기는 단어 길이의 제곱근보다 훨씬 더 빠르게 증가한다고 할 수 있습니다.
- study_note: 힙스 법칙에서 지수 β의 일반적인 범위를 설명합니다. 이는 데이터가 늘어날 때 새로운 단어가 추가되는 양상이 단순 제곱근(0.5)보다 더 가파르다는 점을 시사합니다.

## Block 3
- type: paragraph
- source_text: Another measure of the number of words in the language is the number of lemmas instead of wordform types. Dictionaries can help in giving lemma counts; dictionary entries or boldface forms are a very rough upper bound on the number of lemmas (since some lemmas have multiple boldface forms). The 1989 edition of the Oxford English Dictionary had 615,000 entries.
- korean_translation: 한 언어의 단어 수를 측정하는 또 다른 방법은 어형 유형 대신 표제어(lemmas)의 개수를 세는 것입니다. 사전은 표제어 개수를 파악하는 데 유용한 도구가 될 수 있습니다. 사전 항목이나 굵은 표제어 형태는 표제어 수의 아주 대략적인 상한선이 됩니다(일부 표제어는 여러 개의 굵은 표제어 형태를 가질 수 있기 때문입니다). 1989년판 옥스퍼드 영어 사전(OED)에는 615,000개의 항목이 수록되어 있었습니다.
- study_note: 단어 변형을 제외한 기본 사전형인 표제어 관점에서의 단어 규모를 설명합니다. 사전의 수록어 개수는 해당 언어의 표제어 규모를 가늠하는 지표가 됩니다.

## Block 4
- type: section_title
- source_text: 2.3 Corpora
- korean_translation: 2.3 코퍼스 (말뭉치)
- study_note: 자연어 처리의 핵심 원천인 코퍼스(말뭉치)의 개념과 특성을 깊이 있게 다루는 새로운 섹션입니다.

## Block 5
- type: paragraph
- source_text: Words don’t appear out of nowhere. Any particular piece of text that we study is produced by one or more specific speakers or writers, in a specific dialect of a specific language, at a specific time, in a specific place, for a specific function.
- korean_translation: 단어는 갑자기 나타나는 것이 아닙니다. 우리가 연구하는 모든 텍스트는 하나 이상의 구체적인 화자나 저자에 의해, 특정 언어의 특정 방언으로, 특정 시간에, 특정 장소에서, 특정한 목적을 위해 생산됩니다.
- study_note: 텍스트가 가진 맥락적(발화자, 방언, 시간, 장소 등) 특성을 강조합니다. 코퍼스는 이러한 맥락의 집합체입니다.

## Block 6
- type: paragraph
- source_text: Perhaps the most important dimension of variation is the language. NLP algorithms are most useful when they apply across many languages. The world has 7097 languages at the time of this writing, according to the online Ethnologue catalog (Simons and Fennig, 2018). It is important to test algorithms on more than one language, and particularly on languages with different properties; by contrast there is an unfortunate current tendency for NLP algorithms to be developed or tested just on English (Bender, 2019). Even when algorithms are developed beyond English, they tend to be developed for the official languages of large industrialized nations (Chinese, Spanish, Japanese, German etc.), but we don’t want to limit tools to just these few languages. Furthermore, most languages also have multiple varieties, often spoken in different regions or by different social groups. Thus, for example, if we’re processing text that uses features of African American English (AAE) or African American Vernacular English (AAVE) — the variations of English used by millions of people in African American communities (King 2020) — we must use NLP tools that function with features of those varieties. Twitter posts might use features often used by speakers of African American English, such as constructions like iont (I don’t in Mainstream American English (MAE)), or talmbout corresponding to MAE talking about, both examples that influence word segmentation (Blodgett et al. 2016, Jones 2015).
- korean_translation: 변이의 가장 중요한 차원은 아마도 언어일 것입니다. NLP 알고리즘은 많은 언어에 걸쳐 적용될 때 가장 유용합니다. 온라인 Ethnologue 목록(Simons and Fennig, 2018)에 따르면, 이 글을 쓰는 시점에 세계에는 7097개의 언어가 있습니다. 알고리즘은 둘 이상의 언어, 특히 서로 다른 성질을 가진 언어들에서 시험되어야 합니다. 그러나 불행하게도 현재 NLP 알고리즘은 영어만을 대상으로 개발되거나 시험되는 경향이 있습니다(Bender, 2019). 영어를 넘어 개발되는 경우에도 대개는 대규모 산업 국가들의 공식 언어(중국어, 스페인어, 일본어, 독일어 등)를 위해 개발되는 경향이 있지만, 우리는 분석 도구가 이러한 소수의 언어들에만 국한되는 것을 원치 않습니다. 더욱이 대부분의 언어에는 여러 변종이 존재하며, 이들은 대개 서로 다른 지역이나 사회 집단에 의해 사용됩니다. 따라서 예를 들어 아프리카계 미국인 영어(AAE) 또는 아프리카계 미국인 구어체 영어(AAVE) — 수백만 명의 아프리카계 미국인 공동체 사람들이 사용하는 영어의 변종(King 2020) — 의 특징이 담긴 텍스트를 처리할 때면, 해당 변종의 언어적 특성을 반영하여 작동하는 NLP 도구를 반드시 사용해야 합니다. 트위터 게시물에는 아프리카계 미국인 영어 화자들이 자주 사용하는 특징들이 나타날 수 있는데, 예를 들어 주류 미국 영어(MAE)의 "I don't"에 해당하는 "iont"나, MAE의 "talking about"에 해당하는 "talmbout"과 같은 구문들은 단어 분절(word segmentation)에 직접적인 영향을 미치는 사례들입니다(Blodgett et al. 2016, Jones 2015).
- study_note: 코퍼스와 NLP 도구가 특정 표준 언어에만 맞춰져서는 안 된다는 점을 강하게 강조하는 문단입니다. 방언과 사회언어학적 변이를 무시하면 실제 언어 데이터를 제대로 처리할 수 없습니다.
# Pages 13-14

Source: `2. Regular Expressions, Text Normalization, Edit Distance.pdf`
Workflow: `html-codex-flash`
Status: accepted

# Page 13

## Block 1
- type: paragraph
- source_text: or transcripts of television shows or movies. It might come from work situations like doctors’ notes, legal text, or parliamentary or congressional proceedings.
- korean_translation: 혹은 TV 쇼나 영화의 대본일 수도 있습니다. 의사의 소견서, 법률 문서, 혹은 의회나 국회의 의사록과 같은 업무 상황에서 발생한 텍스트일 수도 있습니다.
- study_note: 텍스트가 발생하는 다양한 실제 상황(장르)에 대한 예시들입니다. 각 장르마다 언어적 특성이 다름을 인지해야 합니다.

## Block 2
- type: paragraph
- source_text: Text also reflects the demographic characteristics of the writer (or speaker): their age, gender, race, socioeconomic class can all influence the linguistic properties of the text we are processing.
- korean_translation: 텍스트는 또한 저자(혹은 화자)의 인구통계학적 특성을 반영합니다. 연령, 성별, 인종, 사회경제적 계층 등은 우리가 처리하는 텍스트의 언어적 속성에 모두 영향을 미칠 수 있습니다.
- study_note: 발화자의 개인적 배경이 언어 사용 방식에 미치는 영향(인구통계학적 변이)을 설명합니다.

## Block 3
- type: paragraph
- source_text: And finally, time matters too. Language changes over time, and for some languages we have good corpora of texts from different historical periods.
- korean_translation: 마지막으로, 시간 또한 중요합니다. 언어는 시간이 지남에 따라 변하며, 일부 언어의 경우 다양한 역사적 시기에 걸친 훌륭한 텍스트 코퍼스를 보유하고 있기도 합니다.
- study_note: 언어의 역사적 변화(통시적 변이)와 이를 연구하기 위한 역사적 코퍼스의 중요성을 언급합니다.

## Block 4
- type: paragraph
- source_text: Because language is so situated, when developing computational models for language processing from a corpus, it’s important to consider who produced the language, in what context, for what purpose. How can a user of a dataset know all these details? The best way is for the corpus creator to build a datasheet (Gebru et al., 2020) or data statement (Bender and Friedman, 2018) for each corpus. A datasheet specifies properties of a dataset like:
- korean_translation: 언어는 이처럼 상황에 따라 크게 달라지기 때문에, 코퍼스로부터 언어 처리를 위한 계산 모델을 개발할 때는 누가, 어떤 맥락에서, 어떤 목적으로 그 언어를 생산했는지 고려하는 것이 중요합니다. 데이터셋 사용자가 이러한 모든 세부 사항을 어떻게 알 수 있을까요? 가장 좋은 방법은 코퍼스 제작자가 각 코퍼스에 대해 데이터시트(datasheet, Gebru et al., 2020)나 데이터 명세서(data statement, Bender and Friedman, 2018)를 작성하는 것입니다. 데이터시트는 다음과 같은 데이터셋의 속성들을 명시합니다.
- study_note: 데이터의 맥락을 투명하게 공개하기 위한 '데이터시트'의 필요성을 강조합니다. 이는 AI 윤리와 데이터 편향성 문제를 해결하는 핵심 도구입니다.

## Block 5
- type: margin_note
- source_text: datasheet
- korean_translation: 데이터시트(datasheet)
- study_note: 데이터셋의 기원, 구성, 의도된 용도 등을 기록한 표준화된 문서 양식입니다.

## Block 6
- type: paragraph
- source_text:
  Motivation: Why was the corpus collected, by whom, and who funded it?
  Situation: When and in what situation was the text written/spoken? For example, was there a task? Was the language originally spoken conversation, edited text, social media communication, monologue vs. dialogue?
  Language variety: What language (including dialect/region) was the corpus in?
  Speaker demographics: What was, e.g., age or gender of the authors of the text?
  Collection process: How big is the data? If it is a subsample how was it sampled? Was the data collected with consent? How was the data pre-processed, and what metadata is available?
  Annotation process: What are the annotations, what are the demographics of the annotators, how were they trained, how was the data annotated?
  Distribution: Are there copyright or other intellectual property restrictions?
- korean_translation:
  동기(Motivation): 코퍼스가 왜 수집되었는가, 누구에 의해 수집되었는가, 그리고 누가 자금을 지원했는가?
  상황(Situation): 텍스트가 언제, 어떤 상황에서 쓰여지거나 말해졌는가? 예를 들어, 특정 과업이 주어졌는가? 언어가 원래 구어체 대화였는가, 편집된 텍스트인가, 소셜 미디어 소통인가, 독백인가 대화인가?
  언어 변종(Language variety): 코퍼스는 어떤 언어(방언/지역 포함)로 되어 있는가?
  화자 인구통계(Speaker demographics): 텍스트 저자들의 연령이나 성별 등은 무엇인가?
  수집 과정(Collection process): 데이터의 규모는 어느 정도인가? 부분 표본이라면 어떻게 샘플링되었는가? 데이터 수집 시 동의를 얻었는가? 데이터는 어떻게 전처리되었으며, 어떤 메타데이터를 사용할 수 있는가?
  주석화 과정(Annotation process): 주석(annotation)은 무엇인가, 주석 작업자들의 인구통계학적 특성은 어떠하며 어떻게 교육받았는가, 데이터에 주석이 어떻게 달렸는가?
  배포(Distribution): 저작권이나 기타 지적 재산권 제한 사항이 있는가?
- study_note: 데이터시트에 포함되어야 할 7가지 필수 항목들을 설명합니다. 데이터의 신뢰성과 재현성을 보장하는 데 매우 중요한 체크리스트입니다.

## Block 7
- type: section_title
- source_text: 2.4 Text Normalization
- korean_translation: 2.4 텍스트 정규화 (Text Normalization)
- study_note: 가공되지 않은 텍스트를 분석 가능한 형태로 표준화하는 핵심 전처리 단계를 다룹니다.

## Block 8
- type: paragraph
- source_text:
  Before almost any natural language processing of a text, the text has to be normalized. At least three tasks are commonly applied as part of any normalization process:
  1. Tokenizing (segmenting) words
  2. Normalizing word formats
  3. Segmenting sentences
  In the next sections we walk through each of these tasks.
- korean_translation:
  텍스트에 대한 거의 모든 자연어 처리에 앞서, 텍스트는 정규화되어야 합니다. 정규화 과정의 일부로 대개 세 가지 작업이 공통적으로 적용됩니다.
  1. 단어 토큰화 (단어 분절)
  2. 단어 형식 정규화
  3. 문장 분절
  다음 섹션들에서 우리는 이러한 각 작업들을 살펴볼 것입니다.
- study_note: 텍스트 정규화의 3대 핵심 작업인 토큰화, 형식 표준화, 문장 분리를 정의합니다.

## Block 9
- type: section_title
- source_text: 2.4.1 Unix Tools for Crude Tokenization and Normalization
- korean_translation: 2.4.1 기본적인 토큰화와 정규화를 위한 Unix 도구들
- study_note: 프로그래밍 없이도 Unix 터미널 명령어를 통해 빠르게 텍스트 데이터를 처리하는 실무적인 방법을 배웁니다.

## Block 10
- type: paragraph
- source_text: Let’s begin with an easy, if somewhat naive version of word tokenization and normalization (and frequency computation) that can be accomplished for English solely in a single UNIX command-line, inspired by Church (1994). We’ll make use of some Unix commands: tr, used to systematically change particular characters in the input; sort, which sorts input lines in alphabetical order; and uniq, which collapses and counts adjacent identical lines.
- korean_translation: 처치(Church, 1994)로부터 영감을 받아, 오직 단일 UNIX 명령줄만으로 수행할 수 있는 쉽고도 약간은 단순한 버전의 단어 토큰화 및 정규화(그리고 빈도 계산)부터 시작해 봅시다. 우리는 몇 가지 Unix 명령어를 활용할 것입니다. 입력된 특정 문자들을 체계적으로 변경하는 데 사용하는 tr, 입력된 줄들을 알파벳 순서대로 정렬하는 sort, 그리고 인접한 동일한 줄들을 하나로 합치고 개수를 세는 uniq가 그것입니다.
- study_note: `tr`, `sort`, `uniq`라는 고전적이지만 아주 강력한 Unix 텍스트 처리 도구 트리오를 소개합니다.

## Block 11
- type: paragraph
- source_text: For example let’s begin with the ‘complete words’ of Shakespeare in one file, sh.txt. We can use tr to tokenize the words by changing every sequence of non-alphabetic characters to a newline (’A-Za-z’ means alphabetic, the -c option complements to non-alphabet, and the -s option squeezes all sequences into a single character):
- korean_translation: 예를 들어, 셰익스피어 전집(complete words)이 들어 있는 'sh.txt' 파일로 시작해 봅시다. 우리는 tr을 사용하여 모든 비알파벳 문자 시퀀스를 개행 문자(newline)로 바꿈으로써 단어들을 토큰화할 수 있습니다 ('A-Za-z'는 알파벳을 의미하며, -c 옵션은 알파벳이 아닌 것들로 보집합을 만들고, -s 옵션은 연속된 모든 시퀀스를 단일 문자로 압축합니다).
- study_note: `tr` 명령어의 옵션들을 조합해 텍스트에서 단어만 추출하여 한 줄에 하나씩 나열하는 토큰화 기법을 설명합니다.

# Page 14

## Block 1
- type: code
- source_text: tr -sc 'A-Za-z' '\n' < sh.txt
- korean_translation: tr -sc 'A-Za-z' '\n' < sh.txt
- study_note: 알파벳이 아닌 모든 문자(-c)를 줄바꿈(\n)으로 바꾸되, 연속된 것은 하나로 압축(-s)하여 단어만 추출하는 명령어입니다.

## Block 2
- type: paragraph
- source_text: The output of this command will be:
- korean_translation: 이 명령어의 출력 결과는 다음과 같습니다.
- study_note: 위 명령어를 실행했을 때 실제 터미널에 나타나는 형태를 예고합니다.

## Block 3
- type: code
- source_text:
  THE
  SONNETS
  by
  William
  Shakespeare
  From
  fairest
  creatures
  We
  ...
- korean_translation:
  THE
  SONNETS
  by
  William
  Shakespeare
  From
  fairest
  creatures
  We
  ...
- study_note: 공백 및 기호들이 제거되고 각 단어가 행 단위로 분리된 토큰화 결과입니다.

## Block 4
- type: paragraph
- source_text: Now that there is one word per line, we can sort the lines, and pass them to uniq -c which will collapse and count them:
- korean_translation: 이제 한 줄에 한 단어가 있게 되었으므로, 줄들을 정렬한 뒤 uniq -c에 전달하여 중복을 합치고 개수를 셀 수 있습니다.
- study_note: 단어별 빈도수 측정을 위해 정렬(`sort`)과 중복 제거 및 카운트(`uniq -c`) 과정을 연결합니다.

## Block 5
- type: code
- source_text: tr -sc 'A-Za-z' '\n' < sh.txt | sort | uniq -c
- korean_translation: tr -sc 'A-Za-z' '\n' < sh.txt | sort | uniq -c
- study_note: 파이프(`|`)를 사용하여 여러 명령어를 연결한 완성된 빈도수 계산 파이프라인입니다.

## Block 6
- type: paragraph
- source_text: with the following output:
- korean_translation: 출력 결과는 다음과 같습니다.
- study_note: 빈도수와 단어가 함께 출력되는 형식을 보여줍니다.

## Block 7
- type: code
- source_text:
  1945 A
  72 AARON
  19 ABBESS
  25 Aaron
  6 Abate
  1 Abates
  5 Abbess
  6 Abbey
  3 Abbot
  ...
- korean_translation:
  1945 A
  72 AARON
  19 ABBESS
  25 Aaron
  6 Abate
  1 Abates
  5 Abbess
  6 Abbey
  3 Abbot
  ...
- study_note: 알파벳 순서대로 정렬된 빈도 결과입니다. 'ABBESS'와 'Abbess'가 대소문자 차이로 인해 별도로 집계된 것을 확인할 수 있습니다.

## Block 8
- type: paragraph
- source_text: Alternatively, we can collapse all the upper case to lower case:
- korean_translation: 대신, 모든 대문자를 소문자로 통합할 수 있습니다.
- study_note: 대소문자 구분을 없애기 위해 소문자로 변환하는 정규화 과정을 추가합니다.

## Block 9
- type: code
- source_text: tr -sc 'A-Za-z' '\n' < sh.txt | tr A-Z a-z | sort | uniq -c
- korean_translation: tr -sc 'A-Za-z' '\n' < sh.txt | tr A-Z a-z | sort | uniq -c
- study_note: 중간에 `tr A-Z a-z`를 추가하여 모든 단어를 소문자 기준으로 집계합니다.

## Block 10
- type: paragraph
- source_text: whose output is
- korean_translation: 이 명령의 출력은 다음과 같습니다.
- study_note: 소문자화된 결과의 예시입니다.

## Block 11
- type: code
- source_text:
  14725 a
  97 aaron
  1 abaissiez
  10 abandon
  2 abandoned
  2 abase
  1 abash
  14 abate
  3 abated
  3 abatement
  ...
- korean_translation:
  14725 a
  97 aaron
  1 abaissiez
  10 abandon
  2 abandoned
  2 abase
  1 abash
  14 abate
  3 abated
  3 abatement
  ...
- study_note: 대소문자 통합으로 인해 'a'의 빈도가 훨씬 늘어났고, 모든 단어가 소문자로 정렬되었습니다.

## Block 12
- type: paragraph
- source_text: Now we can sort again to find the frequent words. The -n option to sort means to sort numerically rather than alphabetically, and the -r option means to sort in reverse order (highest-to-lowest):
- korean_translation: 이제 가장 빈번한 단어들을 찾기 위해 다시 정렬할 수 있습니다. sort의 -n 옵션은 알파벳순이 아닌 숫자순으로 정렬하라는 뜻이고, -r 옵션은 역순(가장 높은 것에서 낮은 것 순서)으로 정렬하라는 뜻입니다.
- study_note: 알파벳순 정렬된 결과를 빈도(숫자)순으로 다시 정렬하여 상위 키워드를 추출하는 옵션을 설명합니다.

## Block 13
- type: code
- source_text: tr -sc 'A-Za-z' '\n' < sh.txt | tr A-Z a-z | sort | uniq -c | sort -n -r
- korean_translation: tr -sc 'A-Za-z' '\n' < sh.txt | tr A-Z a-z | sort | uniq -c | sort -n -r
- study_note: 텍스트 파일을 읽어 토큰화하고, 정규화하며, 빈도를 계산하고, 최종적으로 가장 많이 사용된 단어 순으로 정렬하는 전 과정의 명령어입니다.

## Block 14
- type: paragraph
- source_text: The results show that the most frequent words in Shakespeare, as in any other corpus, are the short function words like articles, pronouns, prepositions:
- korean_translation: 결과는 셰익스피어 전집에서도 다른 코퍼스와 마찬가지로, 가장 많이 등장하는 단어들이 관사, 대명사, 전치사와 같은 짧은 기능어(function words)들이라는 것을 보여줍니다.
- study_note: 빈도 분석의 결과를 요약합니다. 가장 많이 쓰이는 말들은 문법적 역할을 하는 기능어들이라는 보편적인 현상을 확인합니다.
# Page 15

## Block 1
- type: code
- source_text:
  27378 the
  26084 and
  22538 i
  19771 to
  17481 of
  14725 a
  13826 you
  12489 my
  11318 that
  11112 in
  ...
- korean_translation:
  27378 the
  26084 and
  22538 i
  19771 to
  17481 of
  14725 a
  13826 you
  12489 my
  11318 that
  11112 in
  ...
- study_note: 셰익스피어 코퍼스 분석 결과, 빈도수 1위부터 10위까지의 단어 목록입니다. 전체 코퍼스의 매우 높은 비중을 이러한 기능어들이 차지하고 있음을 알 수 있습니다.

## Block 2
- type: paragraph
- source_text: Unix tools of this sort can be very handy in building quick word count statistics for any corpus.
- korean_translation: 이러한 종류의 Unix 도구들은 모든 코퍼스에 대해 빠른 단어 수 통계를 구축하는 데 매우 유용합니다.
- study_note: 전문적인 NLP 라이브러리를 쓰기 전, 데이터의 전반적인 특징을 파악하는 데 Unix 명령어 조합(tr, sort, uniq)이 효율적임을 강조합니다.

## Block 3
- type: section_title
- source_text: 2.4.2 Word Tokenization
- korean_translation: 2.4.2 단어 토큰화 (Word Tokenization)
- study_note: 텍스트 정규화의 첫 번째 단계인 토큰화의 상세한 규칙과 예외 상황들을 다룹니다.

## Block 4
- type: paragraph
- source_text: The simple UNIX tools above were fine for getting rough word statistics but more sophisticated algorithms are generally necessary for tokenization, the task of segmenting running text into words.
- korean_translation: 위의 간단한 UNIX 도구들은 대략적인 단어 통계를 얻는 데는 괜찮았지만, 연속된 텍스트를 단어로 분절하는 작업인 토큰화(tokenization)를 위해서는 일반적으로 더 정교한 알고리즘이 필요합니다.
- study_note: 단순한 공백/기호 제거를 넘어 문맥을 고려한 정교한 토큰화의 필요성을 제기합니다.

## Block 5
- type: margin_note
- source_text: tokenization
- korean_translation: 토큰화(tokenization)
- study_note: 문장 등의 텍스트를 토큰이라는 최소 단위로 나누는 과정입니다.

## Block 6
- type: paragraph
- source_text: While the Unix command sequence just removed all the numbers and punctuation, for most NLP applications we’ll need to keep these in our tokenization. We often want to break off punctuation as a separate token; commas are a useful piece of information for parsers, periods help indicate sentence boundaries. But we’ll often want to keep the punctuation that occurs word internally, in examples like m.p.h., Ph.D., AT&T, and cap’n. Special characters and numbers will need to be kept in prices ($45.55) and dates (01/02/06); we don’t want to segment that price into separate tokens of “45” and “55”. And there are URLs (http://www.stanford.edu), Twitter hashtags (#nlproc), or email addresses (someone@cs.colorado.edu).
- korean_translation: Unix 명령어 시퀀스는 단순히 모든 숫자와 문장 부호를 제거했지만, 대부분의 NLP 응용 프로그램에서는 토큰화 과정에서 이들을 유지해야 합니다. 우리는 종종 문장 부호를 별개의 토큰으로 분리하고 싶어 합니다. 쉼표는 구문 분석기(parser)에게 유용한 정보를 제공하고, 마침표는 문장 경계를 나타내는 데 도움이 되기 때문입니다. 하지만 단어 내부에 나타나는 문장 부호는 유지해야 할 때가 많습니다. m.p.h., Ph.D., AT&T, cap’n 같은 예시들이 그렇습니다. 가격($45.55)이나 날짜(01/02/06)에 포함된 특수 문자나 숫자도 유지되어야 합니다. 우리는 가격을 "45"와 "55"라는 별개의 토큰으로 분리하고 싶지 않기 때문입니다. 또한 URL(http://www.stanford.edu), 트위터 해시태그(#nlproc), 이메일 주소(someone@cs.colorado.edu) 등도 마찬가지입니다.
- study_note: 토큰화의 까다로운 지점들을 설명합니다. 문장 부호를 떼어내야 할 때(문장 끝 마침표)와 붙여두어야 할 때(줄임표, URL, 가격 등)를 구분하는 것이 중요합니다.

## Block 7
- type: paragraph
- source_text: Number expressions introduce other complications as well; while commas normally appear at word boundaries, commas are used inside numbers in English, every three digits: 555,500.50. Languages, and hence tokenization requirements, differ on this; many continental European languages like Spanish, French, and German, by contrast, use a comma to mark the decimal point, and spaces (or sometimes periods) where English puts commas, for example, 555 500,50.
- korean_translation: 숫자 표현 또한 다른 복잡한 문제들을 불러일으킵니다. 쉼표는 보통 단어 경계에 나타나지만, 영어에서 숫자를 표기할 때는 세 자리마다 쉼표를 사용합니다(예: 555,500.50). 언어에 따라, 따라서 토큰화 요구 사항에 따라 이 기준은 달라집니다. 스페인어, 프랑스어, 독일어와 같은 많은 대륙계 유럽 언어들은 반대로 쉼표를 소수점으로 사용하고, 영어에서 쉼표가 들어가는 자리에 공백(또는 때로는 마침표)을 사용합니다(예: 555 500,50).
- study_note: 언어권마다 다른 숫자 표기 규약(쉼표와 마침표의 역할)이 토큰화 알고리즘에 미치는 영향을 설명합니다.

## Block 8
- type: paragraph
- source_text: A tokenizer can also be used to expand clitic contractions that are marked by apostrophes, for example, converting what’re to the two tokens what are, and we’re to we are. A clitic is a part of a word that can’t stand on its own, and can only occur when it is attached to another word. Some such contractions occur in other alphabetic languages, including articles and pronouns in French (j’ai, l’homme).
- korean_translation: 토크나이저는 아포스트로피로 표시된 속사(clitic) 축약형을 확장하는 데에도 사용될 수 있습니다. 예를 들어 "what’re"를 "what"과 "are"라는 두 개의 토큰으로 변환하거나, "we’re"를 "we"와 "are"로 바꾸는 식입니다. 속사(clitic)란 독자적으로는 존재할 수 없고 다른 단어에 붙어 있을 때만 나타날 수 있는 단어의 일부분을 말합니다. 이러한 축약형은 프랑스어의 관사나 대명사(j’ai, l’homme)를 포함한 다른 알파벳 언어들에서도 나타납니다.
- study_note: '속사(clitic)'의 개념을 소개합니다. 형태적으로는 한 단어처럼 보이지만 의미적으로는 두 개 이상의 단어가 결합된 경우, 이를 적절히 분리하는 것이 토큰화의 역할 중 하나입니다.

## Block 9
- type: margin_note
- source_text: clitic
- korean_translation: 속사(clitic)
- study_note: 자립성은 없으나 문법적으로 단어에 준하는 기능을 하는 언어 요소입니다.

## Block 10
- type: paragraph
- source_text: Depending on the application, tokenization algorithms may also tokenize multiword expressions like New York or rock ’n’ roll as a single token, which requires a multiword expression dictionary of some sort. Tokenization is thus intimately tied up with named entity recognition, the task of detecting names, dates, and organizations (Chapter 8).
- korean_translation: 애플리케이션에 따라, 토큰화 알고리즘은 "New York"이나 "rock ’n’ roll" 같은 다어절 표현(multiword expressions)을 하나의 토큰으로 토큰화할 수도 있습니다. 이를 위해서는 일종의 다어절 표현 사전이 필요합니다. 따라서 토큰화는 이름, 날짜, 조직 등을 탐지하는 작업인 개체명 인식(named entity recognition, 8장)과 밀접하게 연관되어 있습니다.
- study_note: 토큰화가 단순히 '나누기'만 하는 것이 아니라, "New York"처럼 의미상 하나로 묶어야 하는 '공동 참조' 단어들을 처리하는 과정과도 연결됨을 설명합니다.

## Block 11
- type: paragraph
- source_text: One commonly used tokenization standard is known as the Penn Treebank tokenization standard, used for the parsed corpora (treebanks) released by the Linguistic Data Consortium (LDC), the source of many useful datasets. This standard separates out clitics (doesn’t becomes does plus n’t), keeps hyphenated words together, and separates out all punctuation (to save space we’re showing visible spaces ‘␣’ between tokens, although newlines is a more common output):
- korean_translation: 흔히 사용되는 토큰화 표준 중 하나는 펜 트리뱅크(Penn Treebank) 토큰화 표준으로 알려져 있습니다. 이는 많은 유용한 데이터셋의 원천인 LDC(Linguistic Data Consortium)에서 출시한 구문 분석 코퍼스(트리뱅크)에 사용됩니다. 이 표준은 속사를 분리하고("doesn’t"는 "does"와 "n’t"가 됨), 하이픈으로 연결된 단어들은 하나로 유지하며, 모든 문장 부호를 분리합니다 (공간 절약을 위해 토큰 사이에 가시적인 공백 '␣'을 표시하여 보여주겠지만, 실제 출력으로는 줄바꿈이 더 일반적입니다).
- study_note: NLP 연구에서 정석적으로 사용되는 펜 트리뱅크 토큰화 규칙을 소개합니다. "n't"를 별도 토큰으로 떼어내는 방식이 특징적입니다.

## Block 12
- type: margin_note
- source_text: Penn Treebank tokenization
- korean_translation: 펜 트리뱅크 토큰화
- study_note: 영어 NLP 데이터의 표준이 되는 토큰화 규약입니다.

---

# Page 16

## Block 1
- type: code
- source_text:
  Input: "The San Francisco-based restaurant," they said, "doesn't charge $10".
  Output: " ␣ The ␣ San ␣ Francisco-based ␣ restaurant ␣ , ␣ " ␣ they ␣ said ␣ , ␣ " ␣ does ␣ n't ␣ charge ␣ $ ␣ 10 ␣ " ␣ .
- korean_translation:
  입력: "The San Francisco-based restaurant," they said, "doesn't charge $10".
  출력: " ␣ The ␣ San ␣ Francisco-based ␣ restaurant ␣ , ␣ " ␣ they ␣ said ␣ , ␣ " ␣ does ␣ n't ␣ charge ␣ $ ␣ 10 ␣ " ␣ .
- study_note: 펜 트리뱅크 표준에 따른 실제 토큰화 예시입니다. 하이픈(-based)은 유지되고, 따옴표("), 쉼표(,), 소속어(n't), 달러 기호($)는 모두 독립된 토큰으로 분리된 것을 볼 수 있습니다.

## Block 2
- type: paragraph
- source_text: In practice, since tokenization needs to be run before any other language processing, it needs to be very fast. The standard method for tokenization is therefore to use deterministic algorithms based on regular expressions compiled into very efficient finite state automata. For example, Fig. 2.12 shows an example of a basic regular expression that can be used to tokenize with the nltk.regexp_tokenize function of the Python-based Natural Language Toolkit (NLTK) (Bird et al. 2009; http://www.nltk.org).
- korean_translation: 실제로 토큰화는 다른 모든 언어 처리보다 먼저 실행되어야 하므로 매우 빨라야 합니다. 따라서 토큰화의 표준적인 방법은 매우 효율적인 유한 상태 오토마타(finite state automata)로 컴파일된 정규 표현식 기반의 결정론적 알고리즘을 사용하는 것입니다. 예를 들어, 그림 2.12는 Python 기반의 자연어 도구 모음인 NLTK(Natural Language Toolkit, Bird et al. 2009; http://www.nltk.org)의 `nltk.regexp_tokenize` 함수를 사용하여 토큰화할 수 있는 기본적인 정규 표현식의 예시를 보여줍니다.
- study_note: 대용량 데이터를 처리하기 위해 토큰화는 속도가 중요하며, 이를 위해 정규 표현식을 효율적인 상태 기계로 변환하여 실행한다는 기술적 배경을 설명합니다.

## Block 3
- type: code
- source_text:
  >>> text = 'That U.S.A. poster-print costs $12.40...'
  >>> pattern = r'''(?x)    # set flag to allow verbose regexps
  ...     ([A-Z]\.)+        # abbreviations, e.g. U.S.A.
  ...   | \w+(- \w+)*       # words with optional internal hyphens
  ...   | \$?\d+(\.\d+)?%?  # currency and percentages, e.g. $12.40, 82%
  ...   | \.\.\.            # ellipsis
  ...   | [][.,;"'?():-_`]  # these are separate tokens; includes ], [
  ... '''
  >>> nltk.regexp_tokenize(text, pattern)
  ['That', 'U.S.A.', 'poster-print', 'costs', '$12.40', '...']
- korean_translation:
  >>> text = 'That U.S.A. poster-print costs $12.40...'
  >>> pattern = r'''(?x)    # 자세한 정규 표현식을 허용하기 위한 플래그 설정
  ...     ([A-Z]\.)+        # 약어(U.S.A. 등)
  ...   | \w+(- \w+)*       # 내부 하이픈이 포함될 수 있는 단어
  ...   | \$?\d+(\.\d+)?%?  # 통계 및 퍼센트($12.40, 82% 등)
  ...   | \.\.\.            # 줄임표
  ...   | [][.,;"'?():-_`]  # 이들은 개별 토큰임; ], [ 포함
  ... '''
  >>> nltk.regexp_tokenize(text, pattern)
  ['That', 'U.S.A.', 'poster-print', 'costs', '$12.40', '...']
- study_note: NLTK를 활용한 실제 정규 표현식 토큰화 코드입니다. 주석을 통해 각 정규 표현식 덩어리가 어떤 형태의 텍스트(약어, 하이픈 단어, 금액 등)를 잡아내는지 잘 보여줍니다.

## Block 4
- type: figure_caption
- source_text: Figure 2.12 A Python trace of regular expression tokenization in the NLTK Python-based natural language processing toolkit (Bird et al., 2009), commented for readability; the (?x) verbose flag tells Python to strip comments and whitespace. Figure from Chapter 3 of Bird et al. (2009).
- korean_translation: 그림 2.12 가독성을 위해 주석을 단 NLTK(Python 기반 자연어 처리 도구 모음)에서의 정규 표현식 토큰화 실행 과정(Bird et al., 2009). `(?x)` 플래그는 Python에게 주석과 공백을 무시하라고 지시합니다. Bird et al. (2009)의 3장에서 가져온 그림입니다.
- study_note: 위 코드 예시의 정체와 `(?x)` 플래그의 역할을 설명하는 캡션입니다.

## Block 5
- type: paragraph
- source_text: Carefully designed deterministic algorithms can deal with the ambiguities that arise, such as the fact that the apostrophe needs to be tokenized differently when used as a genitive marker (as in the book’s cover), a quotative as in ‘The other class’, she said, or in clitics like they’re.
- korean_translation: 정교하게 설계된 결정론적 알고리즘은 아포스트로피가 소유격 표시어("the book’s cover"), 인용 부호("‘The other class’, she said"), 혹은 속사("they’re")로 쓰일 때 각각 다르게 토큰화되어야 한다는 사실과 같이 발생하는 중의성들을 처리할 수 있습니다.
- study_note: 동일한 기호(아포스트로피)가 문맥에 따라 다른 용도로 쓰일 때의 처리 난이도를 언급합니다.

## Block 6
- type: paragraph
- source_text: Word tokenization is more complex in languages like written Chinese, Japanese, and Thai, which do not use spaces to mark potential word-boundaries. In Chinese, for example, words are composed of characters (called hanzi in Chinese). Each character generally represents a single unit of meaning (called a morpheme) and is pronounceable as a single syllable. Words are about 2.4 characters long on average. But deciding what counts as a word in Chinese is complex. For example, consider the following sentence:
- korean_translation: 단어 경계를 표시하기 위해 공백을 사용하지 않는 중국어, 일본어, 태국어와 같은 언어들에서는 단어 토큰화가 더욱 복잡해집니다. 예를 들어 중국어의 경우, 단어는 문자(중국어로 한자(hanzi)라고 부름)들로 구성됩니다. 각 문자는 일반적으로 하나의 의미 단위(형태소(morpheme))를 나타내며 하나의 음절로 발음됩니다. 단어는 평균적으로 약 2.4자 길이입니다. 하지만 중국어에서 무엇을 단어로 간주할지는 매우 복잡합니다. 예를 들어, 다음 문장을 봅시다.
- study_note: 공백이 없는 동양권 언어의 토큰화 문제를 소개합니다. 한자 단위가 아닌 형태소와 단어 단위의 경계를 찾는 것이 핵심 과제임을 알 수 있습니다.

## Block 7
- type: margin_note
- source_text: hanzi
- korean_translation: 한자(hanzi)
- study_note: 중국어의 기본 표기 단위인 한자를 뜻합니다.

## Block 8
- type: code
- source_text:
  (2.4) 姚明进入总决赛
  “Yao Ming reaches the finals”
  As Chen et al. (2017) point out, this could be treated as 3 words (‘Chinese Treebank’ segmentation):
  (2.5) 姚明 进入 总决赛
  YaoMing reaches finals
  or as 5 words (‘Peking University’ segmentation):
  (2.6) 姚 明 进入 总 决赛
  Yao Ming reaches overall finals
- korean_translation:
  (2.4) 姚明进入总决赛
  "야오밍이 결승에 진출하다"
  Chen et al. (2017)이 지적했듯이, 이것은 3개의 단어('중국어 트리뱅크' 분절)로 처리될 수도 있고:
  (2.5) 姚明 进入 总决赛
  야오밍 진출하다 결승전
  혹은 5개의 단어('북경 대학교' 분절)로 처리될 수도 있습니다:
  (2.6) 姚 명 进入 总 决赛
  야오 명 진출하다 총 결승전
- study_note: 중국어 분절의 모호함을 보여주는 유명한 예시입니다. 야오밍의 이름을 한 단어로 볼지(姚明), 아니면 성과 이름을 나눌지(姚 명)에 따라 단어 수가 달라집니다.

## Block 9
- type: paragraph
- source_text: Finally, it is possible in Chinese simply to ignore words altogether and use characters as the basic elements, treating the sentence as a series of 7 characters:
- korean_translation: 마지막으로, 중국어에서는 단어라는 단위를 아예 무시하고 문자를 기본 요소로 사용하여 문장을 다음처럼 7개의 문자 시퀀스로 취급하는 것도 가능합니다. [다음 페이지에서 계속]
- study_note: 단어 단위 분절의 어려움 때문에 아예 글자 하나하나를 최소 단위로 보기도 한다는 점을 설명합니다.
# Page 17

## Block 1
- type: code
- source_text:
  (2.7) 姚 明 进 入 总 决 赛
  Yao Ming enter enter overall decision game
- korean_translation:
  (2.7) 姚 명 进 入 总 决 赛
  야오 명 진 출 총 결 승
- study_note: 중국어 문장을 단어 단위가 아닌 개별 한자(글자) 단위로 나열한 예시입니다. 각 한자가 나름의 의미를 가짐을 알 수 있습니다.

## Block 2
- type: paragraph
- source_text: In fact, for most Chinese NLP tasks it turns out to work better to take characters rather than words as input, since characters are at a reasonable semantic level for most applications, and since most word standards, by contrast, result in a huge vocabulary with large numbers of very rare words (Li et al., 2019).
- korean_translation: 사실 대부분의 중국어 NLP 작업에서는 단어보다 문자를 입력으로 사용하는 것이 더 효과적이라는 사실이 밝혀졌습니다. 문자는 대부분의 응용 프로그램에 적합한 의미 수준(semantic level)에 있으며, 반대로 대부분의 단어 기준은 매우 희귀한 단어들이 대량으로 포함된 거대한 어휘 집합을 생성하기 때문입니다(Li et al., 2019).
- study_note: 중국어에서 '단어' 단위를 정의하기 어렵고 희귀 단어가 많아지는 문제를 해결하기 위해, 글자(character) 단위를 기본 입력으로 사용하는 것이 더 효율적일 수 있음을 설명합니다.

## Block 3
- type: paragraph
- source_text: However, for Japanese and Thai the character is too small a unit, and so algorithms for word segmentation are required. These can also be useful for Chinese in the rare situations where word rather than character boundaries are required. The standard segmentation algorithms for these languages use neural sequence models trained via supervised machine learning on hand-segmented training sets; we’ll introduce sequence models in Chapter 8 and Chapter 9.
- korean_translation: 하지만 일본어나 태국어의 경우 문자는 너무 작은 단위이므로 단어 분절(word segmentation) 알고리즘이 필요합니다. 이는 단어 경계가 문자 경계보다 더 중요하게 요구되는 드문 상황의 중국어에서도 유용할 수 있습니다. 이러한 언어들의 표준 분절 알고리즘은 수동으로 분절된 학습 세트에서 지도 학습(supervised machine learning)을 통해 훈련된 신경망 시퀀스 모델(neural sequence models)을 사용합니다. 시퀀스 모델에 대해서는 8장과 9장에서 소개할 예정입니다.
- study_note: 일본어와 태국어처럼 문자 단위가 너무 작은 경우에는 단어 분절이 필수적이며, 이를 위해 딥러닝 기반의 시퀀스 모델이 사용됨을 언급합니다.

## Block 4
- type: margin_note
- source_text: word segmentation
- korean_translation: 단어 분절(word segmentation)
- study_note: 공백 없는 텍스트에서 단어 사이의 경계를 찾아내는 인위적인 분리 과정입니다.

## Block 5
- type: section_title
- source_text: 2.4.3 Byte-Pair Encoding for Tokenization
- korean_translation: 2.4.3 토큰화를 위한 바이트 쌍 인코딩 (Byte-Pair Encoding, BPE)
- study_note: 현대 NLP(특히 LLM)에서 사실상 표준으로 쓰이는 하위 단어 토큰화 기법인 BPE를 다룹니다.

## Block 6
- type: paragraph
- source_text: There is a third option to tokenizing text. Instead of defining tokens as words (whether delimited by spaces or more complex algorithms), or as characters (as in Chinese), we can use our data to automatically tell us what the tokens should be. This is especially useful in dealing with unknown words, an important problem in language processing. As we will see in the next chapter, NLP algorithms often learn some facts about language from one corpus (a training corpus) and then use these facts to make decisions about a separate test corpus and its language. Thus if our training corpus contains, say the words low, new, newer, but not lower, then if the word lower appears in our test corpus, our system will not know what to do with it.
- korean_translation: 텍스트를 토큰화하는 세 번째 방법이 있습니다. 토큰을 단어로 정의하거나(공백이나 복잡한 알고리즘에 의해 구분되든) 혹은 문자로 정의하는(중국어의 경우처럼) 대신, 우리 데이터를 사용하여 토큰이 무엇이어야 할지 자동으로 결정하게 할 수 있습니다. 이는 언어 처리에서 중요한 문제인 미등록 단어(unknown words)를 다루는 데 특히 유용합니다. 다음 장에서 보겠지만, NLP 알고리즘은 종종 하나의 코퍼스(학습 코퍼스)에서 언어에 대한 사실들을 배우고, 이 지식을 바탕으로 별도의 테스트 코퍼스와 그 언어에 대한 결정을 내립니다. 만약 학습 코퍼스에 'low', 'new', 'newer'라는 단어는 있지만 'lower'가 없다면, 테스트 코퍼스에 'lower'가 나타났을 때 우리 시스템은 이를 어떻게 처리해야 할지 알 수 없게 됩니다.
- study_note: 단어 단위(너무 큼)와 문자 단위(너무 작음)의 절충안으로서, 데이터로부터 최적의 단위를 스스로 찾아내는 방식이 왜 필요한지 OOV(Out-of-Vocabulary) 문제를 통해 설명합니다.

## Block 7
- type: paragraph
- source_text: To deal with this unknown word problem, modern tokenizers automatically induce sets of tokens that include tokens smaller than words, called subwords. Subwords can be arbitrary substrings, or they can be meaning-bearing units like the morphemes -est or -er. (A morpheme is the smallest meaning-bearing unit of a language; for example the word unlikeliest has the morphemes un-, likely, and -est.) In modern tokenization schemes, most tokens are words, but some tokens are frequently occurring morphemes or other subwords like -er. Every unseen word like lower can thus be represented by some sequence of known subword units, such as low and er, or even as a sequence of individual letters if necessary.
- korean_translation: 이러한 미등록 단어 문제를 해결하기 위해, 현대의 토크나이저들은 단어보다 작은 단위인 하위 단어(subwords)를 포함하는 토큰 집합을 자동으로 유도해 냅니다. 하위 단어는 임의의 부분 문자열일 수도 있고, '-est'나 '-er'와 같은 의미를 담은 단위인 형태소(morphemes)일 수도 있습니다. (형태소는 언어에서 의미를 가진 가장 작은 단위입니다. 예를 들어 'unlikeliest'라는 단어는 'un-', 'likely', '-est'라는 형태소로 이루어져 있습니다.) 현대의 토큰화 체계에서 대부분의 토큰은 단어이지만, 일부 토큰은 빈번하게 나타나는 형태소나 '-er'와 같은 하위 단어들입니다. 따라서 'lower'와 같은 처음 보는 단어도 알고 있는 하위 단어 단위(예: 'low'와 'er')의 시퀀스로 표현할 수 있으며, 필요하다면 개별 글자의 시퀀스로도 표현할 수 있습니다.
- study_note: 하위 단어의 정의와 형태소와의 관계를 설명합니다. 처음 보는 단어를 이미 알고 있는 조각(subword)들로 조립하여 처리할 수 있다는 것이 핵심입니다.

## Block 8
- type: margin_note
- source_text: subwords
- korean_translation: 하위 단어(subwords)
- study_note: 단어를 더 쪼갠 단위로, 미등록 단어 문제 해결을 위한 현대 NLP의 핵심 요소입니다.

## Block 9
- type: paragraph
- source_text: Most tokenization schemes have two parts: a token learner, and a token segmenter. The token learner takes a raw training corpus (sometimes roughly preseparated into words, for example by whitespace) and induces a vocabulary, a set of tokens. The token segmenter takes a raw test sentence and segments it into the tokens in the vocabulary. Three algorithms are widely used: byte-pair encoding (Sennrich et al., 2016), unigram language modeling (Kudo, 2018), and WordPiece (Schuster and Nakajima, 2012); there is also a SentencePiece library that includes implementations of the first two of the three (Kudo and Richardson, 2018).
- korean_translation: 대부분의 토큰화 체계는 토큰 학습기(token learner)와 토큰 분절기(token segmenter)라는 두 부분으로 나뀝니다. 토큰 학습기는 가공되지 않은 학습 코퍼스를 가져와 어휘 집합(vocabulary)인 토큰들의 묶음을 유도해 냅니다. 토큰 분절기는 가공되지 않은 테스트 문장을 가져와 어휘 집합에 있는 토큰들로 분절합니다. 널리 쓰이는 세 가지 알고리즘은 바이트 쌍 인코딩(BPE, Sennrich et al., 2016), 유니그램 언어 모델링(unigram language modeling, Kudo, 2018), 그리고 워드피스(WordPiece, Schuster and Nakajima, 2012)입니다. 또한 이 중 처음 두 알고리즘의 구현체를 포함하는 SentencePiece 라이브러리(Kudo and Richardson, 2018)도 있습니다.
- study_note: 토큰화 방식의 구성 요소와 주요 알고리즘들(BPE, WordPiece 등)을 소개합니다.

## Block 10
- type: paragraph
- source_text: In this section we introduce the simplest of the three, the byte-pair encoding or BPE algorithm (Sennrich et al., 2016); see Fig. 2.13. The BPE token learner begins with a vocabulary that is just the set of all individual characters. It then examines the training corpus, chooses the two symbols that are most frequently adjacent (say ‘A’, ‘B’), adds a new merged symbol ‘AB’ to the vocabulary, and replaces every adjacent ‘A’ ‘B’ in the corpus with the new ‘AB’. It continues to count and merge, creating new longer and longer character strings, until k merges have been done creating k novel tokens; k is thus a parameter of the algorithm. The resulting vocabulary consists of the original set of characters plus k new symbols.
- korean_translation: 이 섹션에서는 세 가지 중 가장 간단한 바이트 쌍 인코딩(BPE) 알고리즘(Sennrich et al., 2016)을 소개합니다(그림 2.13 참조). BPE 토큰 학습기는 모든 개별 문자들의 집합으로 이루어진 어휘 집합에서 시작합니다. 그다음 학습 코퍼스를 조사하여 가장 빈번하게 인접한 두 기호(예: 'A', 'B')를 선택하고, 어휘 집합에 새로운 병합 기호 'AB'를 추가한 뒤, 코퍼스 내의 모든 인접한 'A' 'B'를 새로운 'AB'로 교체합니다. 이러한 계산과 병합 과정을 반복하여 점점 더 긴 문자열을 만들어 내며, k번의 병합이 완료되어 k개의 새로운 토큰이 만들어질 때까지 계속합니다. 따라서 k는 알고리즘의 파라미터가 됩니다. 최종적인 어휘 집합은 원래의 문자 집합에 k개의 새로운 기호가 추가된 형태가 됩니다.
- study_note: BPE 알고리즘의 작동 방식을 단계별로 설명합니다. 가장 많이 붙어 다니는 문자들을 합쳐서 하나의 토큰으로 만드는 상향식(bottom-up) 방식을 취합니다.

## Block 11
- type: margin_note
- source_text: BPE
- korean_translation: BPE (Byte-Pair Encoding)
- study_note: 바이트 쌍 인코딩의 약어입니다.

---

# Page 18

## Block 1
- type: other
- source_text: 18 CHAPTER 2 • REGULAR EXPRESSIONS, TEXT NORMALIZATION, EDIT DISTANCE
- korean_translation: 18 제2장 • 정규 표현식, 텍스트 정규화, 편집 거리
- study_note: 페이지 상단의 장 제목과 페이지 번호(18) 정보입니다.

## Block 2
- type: paragraph
- source_text:
  The algorithm is usually run inside words (not merging across word boundaries), so the input corpus is first white-space-separated to give a set of strings, each corresponding to the characters of a word, plus a special end-of-word symbol _, and its counts. Let’s see its operation on the following tiny input corpus of 18 word tokens with counts for each word (the word low appears 5 times, the word newer 6 times, and so on), which would have a starting vocabulary of 11 letters:
- korean_translation:
  알고리즘은 보통 단어 내부에서 실행되며(단어 경계를 넘어 병합하지 않음), 따라서 입력 코퍼스는 먼저 공백으로 구분되어 단어의 각 문자와 특수 단어 끝 기호 _, 그리고 그 빈도수가 포함된 문자열 집합을 생성합니다. 각 단어의 빈도수(단어 'low'는 5번, 단어 'newer'는 6번 나타나는 식)가 포함된 18개의 단어 토큰으로 이루어진 아주 작은 입력 코퍼스 예시를 통해 작동 방식을 살펴봅시다. 이 예시의 시작 어휘 집합은 11개의 글자로 구성됩니다.
- study_note: BPE의 구체적인 작동 예시를 시작합니다. 단어 끝을 알리는 기호(`_`)의 사용과 단어 단위 내에서만 병합이 이루어진다는 제약 조건을 설명합니다.

## Block 3
- type: table
- source_text:
  [table]
  행 1: corpus | vocabulary
  행 2: 5 l o w _ | _, d, e, i, l, n, o, r, s, t, w
  행 3: 2 l o w e s t _ | 
  행 4: 6 n e w e r _ | 
  행 5: 3 w i d e r _ | 
  행 6: 2 n e w _ | 
- korean_translation:
  [table]
  행 1: 코퍼스 | 어휘 집합
  행 2: 5 l o w _ | _, d, e, i, l, n, o, r, s, t, w
  행 3: 2 l o w e s t _ | 
  행 4: 6 n e w e r _ | 
  행 5: 3 w i d e r _ | 
  행 6: 2 n e w _ | 
- study_note: BPE 시작 단계의 데이터 상태입니다. 모든 단어가 글자 단위로 쪼개져 있습니다.

## Block 4
- type: paragraph
- source_text:
  The BPE algorithm first counts all pairs of adjacent symbols: the most frequent is the pair e r because it occurs in newer (frequency of 6) and wider (frequency of 3) for a total of 9 occurrences¹. We then merge these symbols, treating er as one symbol, and count again:
- korean_translation:
  BPE 알고리즘은 먼저 인접한 기호의 모든 쌍을 계산합니다. 가장 빈번한 쌍은 'e'와 'r'인데, 이는 'newer'(빈도 6)와 'wider'(빈도 3)에서 총 9번¹ 나타나기 때문입니다. 그런 다음 이 기호들을 병합하여 'er'을 하나의 기호로 취급하고 다시 빈도를 계산합니다.
- study_note: 첫 번째 병합 과정입니다. 가장 많이 나타나는 인접 쌍인 'e'와 'r'을 'er'로 합칩니다.

## Block 5
- type: table
- source_text:
  [table]
  행 1: corpus | vocabulary
  행 2: 5 l o w _ | _, d, e, i, l, n, o, r, s, t, w, er
  행 3: 2 l o w e s t _ | 
  행 4: 6 n e w er _ | 
  행 5: 3 w i d er _ | 
  행 6: 2 n e w _ | 
- korean_translation:
  [table]
  행 1: 코퍼스 | 어휘 집합
  행 2: 5 l o w _ | _, d, e, i, l, n, o, r, s, t, w, er
  행 3: 2 l o w e s t _ | 
  행 4: 6 n e w er _ | 
  행 5: 3 w i d er _ | 
  행 6: 2 n e w _ | 
- study_note: 첫 번째 병합 결과입니다. 'er'이 하나의 토큰으로 어휘 집합에 추가되었습니다.

## Block 6
- type: paragraph
- source_text:
  Now the most frequent pair is er _, which we merge; our system has learned that there should be a token for word-final er, represented as er_:
- korean_translation:
  이제 가장 빈번한 쌍은 'er'과 '_'이며, 이를 병합합니다. 우리 시스템은 단어 끝에 오는 'er'을 위한 토큰인 'er_'가 있어야 함을 학습하게 됩니다.
- study_note: 두 번째 병합입니다. 'er' 뒤에 단어 끝 기호가 오는 패턴(`er_`)을 하나의 토큰으로 만들었습니다.

## Block 7
- type: table
- source_text:
  [table]
  행 1: corpus | vocabulary
  행 2: 5 l o w _ | _, d, e, i, l, n, o, r, s, t, w, er, er_
  행 3: 2 l o w e s t _ | 
  행 4: 6 n e w er_ | 
  행 5: 3 w i d er_ | 
  행 6: 2 n e w _ | 
- korean_translation:
  [table]
  행 1: 코퍼스 | 어휘 집합
  행 1: 5 l o w _ | _, d, e, i, l, n, o, r, s, t, w, er, er_
  행 3: 2 l o w e s t _ | 
  행 4: 6 n e w er_ | 
  행 5: 3 w i d er_ | 
  행 6: 2 n e w _ | 
- study_note: 두 번째 병합 결과입니다. 어휘 집합이 점점 풍성해지고 있습니다.

## Block 8
- type: paragraph
- source_text: Next n e (total count of 8) get merged to ne:
- korean_translation: 다음으로 'n'과 'e'(총 8회)가 병합되어 'ne'가 됩니다.
- study_note: 세 번째 병합 과정입니다. 'newer'와 'new'에 공통적으로 들어가는 'ne'가 병합됩니다.

## Block 9
- type: table
- source_text:
  [table]
  행 1: corpus | vocabulary
  행 2: 5 l o w _ | _, d, e, i, l, n, o, r, s, t, w, er, er_, ne
  행 3: 2 l o w e s t _ | 
  행 4: 6 ne w er_ | 
  행 5: 3 w i d er_ | 
  행 6: 2 ne w _ | 
- korean_translation:
  [table]
  행 1: 코퍼스 | 어휘 집합
  행 2: 5 l o w _ | _, d, e, i, l, n, o, r, s, t, w, er, er_, ne
  행 3: 2 l o w e s t _ | 
  행 4: 6 ne w er_ | 
  행 5: 3 w i d er_ | 
  행 6: 2 ne w _ | 
- study_note: 세 번째 병합 결과입니다.

## Block 10
- type: paragraph
- source_text: If we continue, the next merges are:
- korean_translation: 계속 진행한다면, 다음 병합들은 다음과 같습니다.
- study_note: 이어지는 병합 단계들을 표로 제시하기 전의 안내 문구입니다.

## Block 11
- type: table
- source_text:
  [table]
  행 1: Merge | Current Vocabulary
  행 2: (ne, w) | _, d, e, i, l, n, o, r, s, t, w, er, er_, ne, new
  행 3: (l, o) | _, d, e, i, l, n, o, r, s, t, w, er, er_, ne, new, lo
  행 4: (lo, w) | _, d, e, i, l, n, o, r, s, t, w, er, er_, ne, new, lo, low
  행 5: (new, er_) | _, d, e, i, l, n, o, r, s, t, w, er, er_, ne, new, lo, low, newer_
  행 6: (low, _) | _, d, e, i, l, n, o, r, s, t, w, er, er_, ne, new, lo, low, newer_, low_
- korean_translation:
  [table]
  행 1: 병합 대상 | 현재 어휘 집합
  행 2: (ne, w) | _, d, e, i, l, n, o, r, s, t, w, er, er_, ne, new
  행 3: (l, o) | _, d, e, i, l, n, o, r, s, t, w, er, er_, ne, new, lo
  행 4: (lo, w) | _, d, e, i, l, n, o, r, s, t, w, er, er_, ne, new, lo, low
  행 5: (new, er_) | _, d, e, i, l, n, o, r, s, t, w, er, er_, ne, new, lo, low, newer_
  행 6: (low, _) | _, d, e, i, l, n, o, r, s, t, w, er, er_, ne, new, lo, low, newer_, low_
- study_note: 순차적인 병합을 통해 'new', 'low', 'newer_', 'low_'와 같은 단어 또는 단어에 근접한 토큰들이 생성되는 과정을 보여줍니다.

## Block 12
- type: paragraph
- source_text: Once we’ve learned our vocabulary, the token parser is used to tokenize a test sentence. The token parser just runs on the test data the merges we have learned
- korean_translation: 일단 어휘 집합을 학습하고 나면, 토큰 파서(token parser)를 사용하여 테스트 문장을 토큰화합니다. 토큰 파서는 우리가 학습한 병합 규칙들을 테스트 데이터에 그대로 적용합니다. [다음 페이지에서 계속]
- study_note: 학습된 규칙(병합 순서)을 새로운 데이터에 적용하여 토큰화하는 '분절(segmentation)' 단계에 대한 설명입니다.

## Block 13
- type: paragraph
- source_text: 1 Note that there can be ties; we could have instead chosen to merge r _ first, since that also has a frequency of 9.
- korean_translation: 1 빈도수가 동일한 경우가 있을 수 있음에 유의하십시오. 예를 들어 'r'과 '_'의 쌍도 빈도수가 9이므로 이를 먼저 병합하도록 선택할 수도 있었습니다.
- study_note: 빈도가 같은 인접 쌍들 사이에서 선택 우선순위가 발생할 수 있음을 지적하는 기술적인 주석입니다.
# Page 19

## Block 1
- type: other
- source_text: 2.4 • TEXT NORMALIZATION 19
- korean_translation: 2.4 • 텍스트 정규화 19
- study_note: 페이지 상단 헤더입니다.

## Block 2
- type: code
- source_text: |
    function BYTE-PAIR ENCODING(strings C, number of merges k) returns vocab V
      V ← all unique characters in C    # initial set of tokens is characters
      for i = 1 to k do                 # merge tokens til k times
        t_L, t_R ← Most frequent pair of adjacent tokens in C
        t_NEW ← t_L + t_R               # make new token by concatenating
        V ← V + t_NEW                   # update the vocabulary
        Replace each occurrence of t_L, t_R in C with t_NEW    # and update the corpus
      return V
- korean_translation: |
    함수 BYTE-PAIR ENCODING(문자열 C, 병합 횟수 k) 반환 어휘집 V
      V ← C에 있는 모든 고유한 문자들    # 초기 토큰 집합은 문자 단위
      i = 1부터 k까지 반복:             # k번 병합될 때까지 반복
        t_L, t_R ← C에서 가장 빈번하게 인접한 토큰 쌍
        t_NEW ← t_L + t_R               # 두 토큰을 이어 붙여 새 토큰 생성
        V ← V + t_NEW                   # 어휘집 업데이트
        C에 나타나는 모든 t_L, t_R 쌍을 t_NEW로 교체    # 코퍼스 업데이트
      반환 V
- study_note: BPE(Byte-Pair Encoding) 알고리즘의 의사코드(pseudocode)입니다. 가장 많이 붙어 나오는 두 조각을 합쳐서 새로운 토큰을 만들고 이를 반복하여 단어 조각들을 학습하는 과정을 보여줍니다.

## Block 3
- type: figure_caption
- source_text: Figure 2.13 The token learner part of the BPE algorithm for taking a corpus broken up into individual characters or bytes, and learning a vocabulary by iteratively merging tokens. Figure adapted from Bostrom and Durrett (2020).
- korean_translation: 그림 2.13 개별 문자나 바이트로 쪼개진 코퍼스에서 토큰을 반복적으로 병합하여 어휘집을 학습하는 BPE 알고리즘의 토큰 학습기 부분. Bostrom and Durrett (2020)에서 수정 인용.
- study_note: BPE 알고리즘의 핵심인 '학습' 단계를 설명하는 그림 캡션입니다.

## Block 4
- type: paragraph
- source_text: from the training data, greedily, in the order we learned them. (Thus the frequencies in the test data don’t play a role, just the frequencies in the training data). So first we segment each test sentence word into characters. Then we apply the first rule: replace every instance of e r in the test corpus with er, and then the second rule: replace every instance of er _ in the test corpus with er_, and so on. By the end, if the test corpus contained the word n e w e r _, it would be tokenized as a full word. But a new (unknown) word like l o w e r _ would be merged into the two tokens low er_.
- korean_translation: 학습 데이터로부터 우리가 배운 순서대로 탐욕적(greedily)으로 적용됩니다. (따라서 테스트 데이터의 빈도는 역할을 하지 않으며, 오직 학습 데이터의 빈도만이 고려됩니다). 따라서 먼저 테스트 문장의 각 단어를 문자 단위로 분절합니다. 그런 다음 첫 번째 규칙을 적용합니다: 테스트 코퍼스의 모든 'e' 'r' 인스턴스를 'er'로 교체합니다. 그다음 두 번째 규칙을 적용합니다: 테스트 코퍼스의 모든 'er' '_' 인스턴스를 'er_'로 교체하는 식입니다. 마지막에 테스트 코퍼스에 'n e w e r _'라는 단어가 포함되어 있다면 이는 하나의 전체 단어로 토큰화될 것입니다. 하지만 'l o w e r _'와 같은 새로운(미등록) 단어는 'low'와 'er_'라는 두 개의 토큰으로 병합될 것입니다.
- study_note: BPE가 학습된 병합 규칙을 새로운 데이터에 어떻게 적용하는지 설명합니다. 이미 학습된 조각들을 활용하여 처음 보는 단어도 의미 있는 단위로 쪼갤 수 있다는 점이 핵심입니다.

## Block 5
- type: paragraph
- source_text: Of course in real algorithms BPE is run with many thousands of merges on a very large input corpus. The result is that most words will be represented as full symbols, and only the very rare words (and unknown words) will have to be represented by their parts.
- korean_translation: 물론 실제 알고리즘에서 BPE는 매우 거대한 입력 코퍼스에 대해 수천 번의 병합을 수행하며 실행됩니다. 그 결과 대부분의 단어는 완전한 기호로 표현될 것이며, 아주 드문 단어(그리고 미등록 단어)만이 그 부분적인 조각들로 표현될 것입니다.
- study_note: 실제 BPE 적용 환경에서는 병합 횟수를 크게 설정하여 자주 쓰이는 단어는 단어 단위로, 드문 단어는 서브워드(subword) 단위로 처리하게 됨을 설명합니다.

## Block 6
- type: section_title
- source_text: 2.4.4 Word Normalization, Lemmatization and Stemming
- korean_translation: 2.4.4 단어 정규화, 표제어 추출 및 어간 추출
- study_note: 텍스트 데이터를 표준화하기 위한 다양한 기법들을 다루는 섹션입니다.

## Block 7
- type: margin_note
- source_text: normalization
- korean_translation: 정규화(normalization)
- study_note: 서로 다른 형태의 단어들을 하나의 표준 형태로 통일하는 과정입니다.

## Block 8
- type: paragraph
- source_text: Word normalization is the task of putting words/tokens in a standard format, choosing a single normal form for words with multiple forms like USA and US or uh-huh and uhhuh. This standardization may be valuable, despite the spelling information that is lost in the normalization process. For information retrieval or information extraction about the US, we might want to see information from documents whether they mention the US or the USA.
- korean_translation: 단어 정규화는 'USA'와 'US' 또는 'uh-huh'와 'uhhuh'처럼 여러 형태를 갖는 단어들에 대해 단일한 표준 형태를 선택하여 단어/토큰을 표준 형식으로 만드는 작업입니다. 이러한 표준화는 정규화 과정에서 철자 정보가 손실됨에도 불구하고 가치가 있을 수 있습니다. 미국(US)에 관한 정보 검색이나 정보 추출의 경우, 문서에 'US'로 되어 있든 'USA'로 되어 있든 상관없이 정보를 확인하고 싶을 것이기 때문입니다.
- study_note: 정규화의 정의와 필요성을 설명합니다. 검색 시스템 등에서 동일한 대상을 가리키는 다양한 표기법을 통합함으로써 성능을 높일 수 있습니다.

## Block 9
- type: margin_note
- source_text: case folding
- korean_translation: 대소문자 통합(case folding)
- study_note: 모든 텍스트를 소문자로 변환하여 대소문자 구분을 없애는 기법입니다.

## Block 10
- type: paragraph
- source_text: Case folding is another kind of normalization. Mapping everything to lower case means that Woodchuck and woodchuck are represented identically, which is very helpful for generalization in many tasks, such as information retrieval or speech recognition. For sentiment analysis and other text classification tasks, capitalization can be quite helpful and case folding is generally not done. This is because maintaining the difference between, for example, US the country and us the pronoun can outweigh the advantage in generalization that case folding would have provided for other words.
- korean_translation: 대소문자 통합은 정규화의 또 다른 종류입니다. 모든 것을 소문자로 매핑하는 것은 'Woodchuck'과 'woodchuck'이 동일하게 표현됨을 의미하며, 이는 정보 검색이나 음성 인식과 같은 많은 작업에서 일반화(generalization)에 큰 도움이 됩니다. 감성 분석이나 기타 텍스트 분류 작업의 경우 대소문자가 상당히 유용할 수 있으므로 일반적으로 대소문자 통합을 수행하지 않습니다. 이는 예를 들어 국가인 'US'와 대명사인 'us' 사이의 차이를 유지하는 것이, 대소문자 통합이 다른 단어들에게 제공했을 일반화의 이점보다 클 수 있기 때문입니다.
- study_note: 대소문자 통합의 장단점을 설명합니다. 작업의 목적에 따라(예: 정보 검색 vs 감성 분석) 정규화 적용 여부를 결정해야 합니다.

## Block 11
- type: paragraph
- source_text: For many natural language processing situations we also want two morphologically different forms of a word to behave similarly. For example in web search, someone may type the string woodchucks but a useful system might want to also return pages that mention woodchuck with no s. This is especially common in morphologically complex languages like Russian, where for example the word Moscow has different endings in the phrases Moscow, of Moscow, to Moscow, and so on.
- korean_translation: 많은 자연어 처리 상황에서 우리는 또한 형태론적으로 서로 다른 두 형태의 단어가 비슷하게 작동하기를 원합니다. 예를 들어 웹 검색에서 누군가 'woodchucks'라는 문자열을 입력했을 때, 유용한 시스템이라면 's'가 없는 'woodchuck'을 언급하는 페이지도 반환하고 싶을 것입니다. 이는 특히 러시아어와 같이 형태론적으로 복잡한 언어에서 흔히 나타나는데, 예를 들어 '모스크바(Moscow)'라는 단어는 '모스크바(Moscow)', '모스크바의(of Moscow)', '모스크바로(to Moscow)' 등의 문구에서 서로 다른 어미를 가집니다.
- study_note: 검색 효율성을 높이기 위해 단어의 형태적 변형(단수/복수, 격 변화 등)을 넘어서는 처리가 필요함을 역설합니다.

## Block 12
- type: paragraph
- source_text: Lemmatization is the task of determining that two words have the same root, despite their surface differences. The words am, are, and is have the shared lemma [다음 페이지에서 계속]
- korean_translation: 표제어 추출(Lemmatization)은 표면적인 차이에도 불구하고 두 단어가 동일한 뿌리를 가지고 있음을 판단하는 작업입니다. 'am', 'are', 'is'라는 단어들은 공유하는 표제어 [다음 페이지에서 계속]
- study_note: 표제어 추출의 정의를 내리고 예시를 시작합니다. 문장이 다음 페이지로 이어짐을 표시합니다.

---

# Page 20

## Block 1
- type: other
- source_text: 20 CHAPTER 2 • REGULAR EXPRESSIONS, TEXT NORMALIZATION, EDIT DISTANCE
- korean_translation: 20 제2장 • 정규 표현식, 텍스트 정규화, 편집 거리
- study_note: 페이지 상단 헤더입니다.

## Block 2
- type: paragraph
- source_text: be; the words dinner and dinners both have the lemma dinner. Lemmatizing each of these forms to the same lemma will let us find all mentions of words in Russian like Moscow. The lemmatized form of a sentence like He is reading detective stories would thus be He be read detective story.
- korean_translation: [이전 페이지에서 계속] 'be'를 가집니다. 'dinner'와 'dinners'라는 단어는 모두 'dinner'라는 표제어를 갖습니다. 이러한 각 형태를 동일한 표제어로 추출하면 러시아어의 '모스크바'와 같은 단어들의 모든 언급을 찾을 수 있게 됩니다. "He is reading detective stories"와 같은 문장의 표제어 추출 형태는 따라서 "He be read detective story"가 될 것입니다.
- study_note: 표제어 추출을 적용한 후의 결과를 예시 문장을 통해 보여줍니다. 모든 변화된 동사와 명사가 원천적인 사전형(lemma)으로 돌아간 것을 확인할 수 있습니다.

## Block 3
- type: paragraph
- source_text: How is lemmatization done? The most sophisticated methods for lemmatization involve complete morphological parsing of the word. Morphology is the study of the way words are built up from smaller meaning-bearing units called morphemes. Two broad classes of morphemes can be distinguished: stems—the central morpheme of the word, supplying the main meaning—and affixes—adding “additional” meanings of various kinds. So, for example, the word fox consists of one morpheme (the morpheme fox) and the word cats consists of two: the morpheme cat and the morpheme -s. A morphological parser takes a word like cats and parses it into the two morphemes cat and s, or parses a Spanish word like amaren (‘if in the future they would love’) into the morpheme amar ‘to love’, and the morphological features 3PL and future subjunctive.
- korean_translation: 표제어 추출은 어떻게 이루어질까요? 표제어 추출의 가장 정교한 방법은 단어에 대한 완전한 형태론적 분석(morphological parsing)을 포함합니다. 형태론(Morphology)은 단어가 '형태소(morphemes)'라고 불리는 더 작은 의미 단위들로부터 어떻게 구성되는지를 연구하는 학문입니다. 형태소는 크게 두 가지 클래스로 구분될 수 있습니다: 단어의 중심 형태소로서 주요 의미를 제공하는 어간(stems)과, 다양한 종류의 '부가적인' 의미를 더하는 접사(affixes)입니다. 예를 들어, 'fox'라는 단어는 하나의 형태소('fox' 형태소)로 구성되지만, 'cats'라는 단어는 'cat' 형태소와 '-s' 형태소 두 개로 구성됩니다. 형태론적 분석기는 'cats'와 같은 단어를 가져와 'cat'과 's'라는 두 형태소로 분석하거나, 'amaren'(만약 미래에 그들이 사랑한다면)과 같은 스페인어 단어를 'amar'(사랑하다)라는 형태소와 3인칭 복수(3PL) 및 미래 가상법(future subjunctive)이라는 형태론적 특징들로 분석합니다.
- study_note: 형태소 분석을 통한 정교한 표제어 추출 과정을 설명합니다. 어간(stem)과 접사(affix)의 개념을 사용하여 단어의 구조를 해체합니다.

## Block 4
- type: margin_note
- source_text: |
    morpheme
    stem
    affix
- korean_translation: |
    형태소(morpheme)
    어간(stem)
    접사(affix)
- study_note: 단어 구성의 핵심 단위들에 대한 용어 정리입니다.

## Block 5
- type: subsection_title
- source_text: The Porter Stemmer
- korean_translation: 포터 어간 추출기(The Porter Stemmer)
- study_note: 영어 어간 추출에서 가장 널리 쓰이는 알고리즘 중 하나인 포터 스테머를 다룹니다.

## Block 6
- type: paragraph
- source_text: Lemmatization algorithms can be complex. For this reason we sometimes make use of a simpler but cruder method, which mainly consists of chopping off word-final affixes. This naive version of morphological analysis is called stemming. One of the most widely used stemming algorithms is the Porter (1980). The Porter stemmer applied to the following paragraph:
- korean_translation: 표제어 추출 알고리즘은 복잡할 수 있습니다. 이런 이유로 우리는 때때로 더 단순하지만 대략적인 방법을 사용하기도 하는데, 이는 주로 단어 끝의 접사를 잘라내는 방식으로 이루어집니다. 이러한 단순한 버전의 형태론적 분석을 어간 추출(stemming)이라고 부릅니다. 가장 널리 사용되는 어간 추출 알고리즘 중 하나는 포터(Porter, 1980) 알고리즘입니다. 다음 단락에 포터 어간 추출기를 적용해 보겠습니다.
- study_note: 표제어 추출(복잡함)의 대안으로서의 어간 추출(단순함)의 정의와 특징을 설명합니다.

## Block 7
- type: margin_note
- source_text: |
    stemming
    Porter stemmer
- korean_translation: |
    어간 추출(stemming)
    포터 어간 추출기(Porter stemmer)
- study_note: 단어의 끝부분을 기계적으로 잘라내는 기법과 그 대표 알고리즘에 대한 용어입니다.

## Block 8
- type: paragraph
- source_text: This was not the map we found in Billy Bones’s chest, but an accurate copy, complete in all things-names and heights and soundings-with the single exception of the red crosses and the written notes.
- korean_translation: 이것은 빌리 본즈의 궤짝에서 우리가 발견한 그 지도는 아니었지만, 모든 것이 완벽하게 갖추어진 정밀한 사본이었다. 이름들, 고도들, 그리고 수심 측량 결과들이 있었으며, 단 하나의 예외라면 붉은 십자가 표시들과 적혀 있는 노트들뿐이었다.
- study_note: 어간 추출 알고리즘을 테스트하기 위한 샘플 텍스트입니다. (보물섬 서문 인용)

## Block 9
- type: code
- source_text: Thi wa not the map we found in Billi Bone s chest but an accur copi complet in all thing name and height and sound with the singl except of the red cross and the written note
- korean_translation: Thi wa not the map we found in Billi Bone s chest but an accur copi complet in all thing name and height and sound with the singl except of the red cross and the written note
- study_note: 포터 스테머를 적용한 결과입니다. 'This'가 'Thi', 'was'가 'wa', 'accurate'가 'accur'로 기계적으로 잘려 나간 것을 볼 수 있습니다. 이는 어간 추출의 '거친(crude)' 속성을 잘 보여줍니다.

## Block 10
- type: margin_note
- source_text: cascade
- korean_translation: 연쇄(cascade)
- study_note: 여러 규칙이 순차적으로 적용되는 방식을 의미합니다.

## Block 11
- type: paragraph
- source_text: The algorithm is based on series of rewrite rules run in series, as a cascade, in which the output of each pass is fed as input to the next pass; here is a sampling of the rules:
- korean_translation: 이 알고리즘은 연쇄적인 재작성 규칙(rewrite rules)들의 연속을 기반으로 하며, 각 단계의 출력이 다음 단계의 입력으로 전달되는 방식으로 작동합니다. 다음은 그 규칙들의 예시입니다.
- study_note: 포터 스테머가 규칙들을 단계별로 적용하는 방식(cascade)을 설명합니다.

## Block 12
- type: code
- source_text: |
    ATIONAL → ATE (e.g., relational → relate)
    ING → ε if stem contains vowel (e.g., motoring → motor)
    SSES → SS (e.g., grasses → grass)
- korean_translation: |
    ATIONAL → ATE (예: relational → relate)
    ING → ε 어간에 모음이 포함된 경우 (예: motoring → motor)
    SSES → SS (예: grasses → grass)
- study_note: 포터 스테머의 규칙 예시입니다. 특정 접미사를 찾아 다른 형태로 바꾸거나(ATIONAL → ATE) 제거하는(ING → ε) 규칙들을 보여줍니다. ε(입실론)은 빈 문자열을 의미합니다.

## Block 13
- type: paragraph
- source_text: Detailed rule lists for the Porter stemmer, as well as code (in Java, Python, etc.) can be found on Martin Porter’s homepage; see also the original paper (Porter, 1980).
- korean_translation: 포터 어간 추출기에 대한 상세한 규칙 리스트와 코드(Java, Python 등)는 마틴 포터의 홈페이지에서 확인할 수 있습니다. 원본 논문(Porter, 1980)도 참고하십시오.
- study_note: 알고리즘에 관한 추가 정보 출처를 안내합니다.

## Block 14
- type: paragraph
- source_text: Simple stemmers can be useful in cases where we need to collapse across different variants of the same lemma. Nonetheless, they do tend to commit errors of both over- and under-generalizing, as shown in the table below (Krovetz, 1993):
- korean_translation: 단순한 어간 추출기는 동일한 표제어의 다양한 변형들을 하나로 묶어야 하는 경우에 유용할 수 있습니다. 그럼에도 불구하고, 아래 표(Krovetz, 1993)에서 보듯이 이들은 과잉 일반화(over-generalizing)와 과소 일반화(under-generalizing)라는 두 종류의 오류를 범하는 경향이 있습니다.
- study_note: 어간 추출기의 한계점인 두 가지 유형의 오류를 소개합니다.

## Block 15
- type: table
- source_text: |
    Errors of Commission | Errors of Omission
    organization organ   | European Europe
    doing        doe     | analysis analyzes
    numerical    numerous| noise    noisy
    policy       police  | sparse   sparsity
- korean_translation: |
    과잉 일반화 오류 (Errors of Commission) | 과소 일반화 오류 (Errors of Omission)
    organization organ                     | European Europe
    doing        doe                       | analysis analyzes
    numerical    numerous                  | noise    noisy
    policy       police                    | sparse   sparsity
- study_note: 어간 추출의 오류 사례표입니다. 과잉 일반화(Commission)는 관련 없는 단어를 같은 어근으로 묶는 오류(예: policy-police), 과소 일반화(Omission)는 관련 있는 단어를 묶지 못하는 오류(예: Europe-European)를 의미합니다.
# Page 21

## Block 1
- type: other
- source_text: 2.5 • MINIMUM EDIT DISTANCE 21
- korean_translation: 2.5 • 최소 편집 거리 21
- study_note: 페이지 상단 헤더 정보입니다.

## Block 2
- type: section_title
- source_text: 2.4.5 Sentence Segmentation
- korean_translation: 2.4.5 문장 분절 (Sentence Segmentation)
- study_note: 텍스트를 개별 문장 단위로 나누는 단계를 다룹니다.

## Block 3
- type: margin_note
- source_text: sentence segmentation
- korean_translation: 문장 분절 (sentence segmentation)
- study_note: 문장 경계 식별을 의미하는 핵심 용어입니다.

## Block 4
- type: paragraph
- source_text: Sentence segmentation is another important step in text processing. The most useful cues for segmenting a text into sentences are punctuation, like periods, question marks, and exclamation points. Question marks and exclamation points are relatively unambiguous markers of sentence boundaries. Periods, on the other hand, are more ambiguous. The period character “.” is ambiguous between a sentence boundary marker and a marker of abbreviations like Mr. or Inc. The previous sentence that you just read showed an even more complex case of this ambiguity, in which the final period of Inc. marked both an abbreviation and the sentence boundary marker. For this reason, sentence tokenization and word tokenization may be addressed jointly.
- korean_translation: 문장 분절(Sentence segmentation)은 텍스트 처리의 또 다른 중요한 단계입니다. 텍스트를 문장으로 분절하는 데 가장 유용한 단서는 마침표, 물음표, 느낌표와 같은 문장 부호입니다. 물음표와 느낌표는 비교적 모호하지 않은 문장 경계 표지입니다. 반면에 마침표는 더 모호합니다. 마침표 문자 “.”는 문장 경계 표지와 Mr. 또는 Inc.와 같은 약어 표지 사이에서 중의적입니다. 방금 읽으신 이전 문장은 이러한 중의성의 훨씬 더 복잡한 사례를 보여주는데, 여기서 Inc.의 마지막 마침표는 약어 표지이자 문장 경계 표지의 역할을 동시에 수행했습니다. 이러한 이유로 문장 토크나이징과 단어 토크나이징은 함께 다루어질 수 있습니다.
- study_note: 마침표(.)가 문장의 마침과 약어를 나타내는 용도 두 가지로 쓰일 때 발생하는 중의성과 그 해결의 필요성을 설명합니다.

# Page 22

## Block 1
- type: other
- source_text: 22 CHAPTER 2 • REGULAR EXPRESSIONS, TEXT NORMALIZATION, EDIT DISTANCE
- korean_translation: 22 제2장 • 정규 표현식, 텍스트 정규화, 편집 거리
- study_note: 페이지 상단 헤더 정보입니다.

## Block 2
- type: code
- source_text: |
    I N T E * N T I O N
    | | | | | | | | | |
    * E X E C U T I O N
    d s s   i s
- korean_translation: |
    I N T E * N T I O N
    | | | | | | | | | |
    * E X E C U T I O N
    d s s   i s
- study_note: 'intention'을 'execution'으로 변환하는 과정을 정렬(alignment) 형태로 보여줍니다. '*'는 공백(gap)을 의미하며, 하단의 d(삭제), s(치환), i(삽입)는 각 단계의 편집 연산을 나타냅니다.

## Block 3
- type: figure_caption
- source_text: Figure 2.14 Representing the minimum edit distance between two strings as an alignment. The final row gives the operation list for converting the top string into the bottom string: d for deletion, s for substitution, i for insertion.
- korean_translation: 그림 2.14 두 문자열 사이의 최소 편집 거리를 정렬(alignment)로 표현한 것. 마지막 행은 상단 문자열을 하단 문자열로 변환하기 위한 연산 리스트를 제공함: d는 삭제(deletion), s는 치환(substitution), i는 삽입(insertion)을 의미함.
- study_note: 최소 편집 거리를 시각화하는 표준적인 방법인 정렬(alignment)과 각 편집 연산 기호의 의미를 설명하는 캡션입니다.

## Block 4
- type: paragraph
- source_text: We can also assign a particular cost or weight to each of these operations. The Levenshtein distance between two sequences is the simplest weighting factor in which each of the three operations has a cost of 1 (Levenshtein, 1966)—we assume that the substitution of a letter for itself, for example, t for t, has zero cost. The Levenshtein distance between intention and execution is 5. Levenshtein also proposed an alternative version of his metric in which each insertion or deletion has a cost of 1 and substitutions are not allowed. (This is equivalent to allowing substitution, but giving each substitution a cost of 2 since any substitution can be represented by one insertion and one deletion). Using this version, the Levenshtein distance between intention and execution is 8.
- korean_translation: 우리는 또한 이러한 각 연산에 특정한 비용이나 가중치를 할당할 수 있습니다. 두 시퀀스 사이의 레벤슈타인 거리(Levenshtein distance)는 가장 단순한 가중치 방식으로, 세 가지 연산 각각에 1의 비용을 부여합니다(Levenshtein, 1966). 예를 들어 t를 t로 바꾸는 것과 같이 문자 자신을 자신으로 치환하는 것은 비용이 0이라고 가정합니다. 이 경우 'intention'과 'execution' 사이의 레벤슈타인 거리는 5입니다. 레벤슈타인은 또한 각 삽입이나 삭제에 1의 비용을 부여하고 치환은 허용하지 않는 대체 버전을 제안했습니다. (이는 치환을 허용하되, 모든 치환은 하나의 삽입과 하나의 삭제로 표현될 수 있으므로 각 치환에 2의 비용을 부여하는 것과 동일합니다). 이 버전을 사용하면 'intention'과 'execution' 사이의 레벤슈타인 거리는 8이 됩니다.
- study_note: 연산별 비용 할당 방식에 따른 편집 거리 값의 변화를 설명합니다. 특히 치환 비용을 2로 책정하는 방식(Standard Levenshtein)과 1로 책정하는 방식의 차이를 이해하는 것이 중요합니다.

## Block 5
- type: section_title
- source_text: 2.5.1 The Minimum Edit Distance Algorithm
- korean_translation: 2.5.1 최소 편집 거리 알고리즘
- study_note: 효율적으로 최소 편집 거리를 계산하기 위한 알고리즘적 접근을 다루기 시작합니다.

## Block 6
- type: paragraph
- source_text: How do we find the minimum edit distance? We can think of this as a search task, in which we are searching for the shortest path—a sequence of edits—from one string to another.
- korean_translation: 최소 편집 거리를 어떻게 찾을 수 있을까요? 우리는 이것을 하나의 문자열에서 다른 문자열로 가는 최단 경로(일련의 편집 연산들)를 찾는 탐색 작업(search task)으로 생각할 수 있습니다.
- study_note: 편집 거리 계산 문제를 그래프에서의 최단 경로 탐색 문제로 추상화하여 접근합니다.

## Block 7
- type: code
- source_text: |
    intention
    / | \
    del ins subst
    / | \
    ntention intecntion inxention
- korean_translation: |
    intention
    / | \
    삭제 삽입 치환
    / | \
    ntention intecntion inxention
- study_note: 'intention'에서 파생될 수 있는 초기 편집 연산들을 트리 구조로 단순화하여 보여줍니다. 실제 탐색 공간이 어떻게 확장될 수 있는지를 시각화한 것입니다.

## Block 8
- type: figure_caption
- source_text: Figure 2.15 Finding the edit distance viewed as a search problem
- korean_translation: 그림 2.15 탐색 문제로 간주하여 편집 거리를 찾는 과정
- study_note: 텍스트로 표현된 트리에 대한 설명 캡션입니다.

## Block 9
- type: paragraph
- source_text: The space of all possible edits is enormous, so we can’t search naively. However, lots of distinct edit paths will end up in the same state (string), so rather than recomputing all those paths, we could just remember the shortest path to a state each time we saw it. We can do this by using dynamic programming. Dynamic programming is the name for a class of algorithms, first introduced by Bellman (1957), that apply a table-driven method to solve problems by combining solutions to sub-problems. Some of the most commonly used algorithms in natural language processing make use of dynamic programming, such as the Viterbi algorithm (Chapter 8) and the CKY algorithm for parsing (Chapter 13).
- korean_translation: 가능한 모든 편집의 공간은 거대하기 때문에 순진하게(naively) 탐색할 수는 없습니다. 하지만 많은 서로 다른 편집 경로들이 결국 동일한 상태(문자열)에 도달하게 되므로, 그 모든 경로들을 다시 계산하는 대신 각 상태에 도달하는 최단 경로를 볼 때마다 기억해 둘 수 있습니다. 우리는 동적 계획법(dynamic programming)을 사용하여 이를 수행할 수 있습니다. 동적 계획법은 Bellman(1957)이 처음 도입한 알고리즘 클래스의 명칭으로, 하위 문제(sub-problems)들에 대한 해답을 결합하여 문제를 해결하기 위해 테이블 기반(table-driven) 방식을 적용합니다. 자연어 처리에서 가장 흔히 사용되는 알고리즘 중 일부는 비터비 알고리즘(8장) 및 구문 분석을 위한 CKY 알고리즘(13장)과 같이 동적 계획법을 활용합니다.
- study_note: 단순 탐색의 비효율성을 극복하기 위한 수단으로 동적 계획법을 소개하며, 그 핵심인 '하위 문제 해답의 재사용(Memoization)'을 강조합니다.

## Block 10
- type: margin_note
- source_text: dynamic programming
- korean_translation: 동적 계획법(dynamic programming)
- study_note: 복잡한 문제를 작은 하위 문제로 나누어 푸는 알고리즘 설계 패러다임입니다.

## Block 11
- type: paragraph
- source_text: The intuition of a dynamic programming problem is that a large problem can be solved by properly combining the solutions to various sub-problems. Consider the shortest path of transformed words that represents the minimum edit distance between the strings intention and execution shown in Fig. 2.16.
- korean_translation: 동적 계획법 문제의 직관은 큰 문제를 다양한 하위 문제들에 대한 해답을 적절히 결합함으로써 해결할 수 있다는 것입니다. 그림 2.16에 표시된 'intention'과 'execution' 문자열 사이의 최소 편집 거리를 나타내는 변환된 단어들의 최단 경로를 생각해 봅시다.
- study_note: 동적 계획법의 기본 원리인 최적 부분 구조(optimal substructure)를 예시를 통해 설명하려는 도입부입니다.

## Block 12
- type: paragraph
- source_text: Imagine some string (perhaps it is exention) that is in this optimal path (whatever it is). The intuition of dynamic programming is that if exention is in the optimal operation list, then the optimal sequence must also include the optimal path from intention to exention. Why? If there were a shorter path from intention to exention, [다음 페이지에서 계속]
- korean_translation: (그것이 무엇이든) 이 최적 경로 상에 있는 어떤 문자열(예를 들어 'exention')을 상상해 봅시다. 동적 계획법의 직관은 만약 'exention'이 최적 연산 리스트에 포함되어 있다면, 그 최적 시퀀스는 'intention'에서 'exention'까지의 최적 경로 또한 반드시 포함해야 한다는 것입니다. 왜일까요? 만약 'intention'에서 'exention'으로 가는 더 짧은 경로가 있다면, [다음 페이지에서 계속]
- study_note: '최단 경로의 부분 경로는 역시 최단 경로여야 한다'는 동적 계획법의 핵심 귀납적 논리를 설명하고 있으며, 문장이 페이지를 넘어가므로 계속됨을 표시했습니다.
# Page 23

## Block 1
- type: code
- source_text: |
    intention
    ntention         <-- delete i
    etention         <-- substitute n by e
    exention         <-- substitute t by x
    exenution        <-- insert u
    execution        <-- substitute n by c
- korean_translation: |
    intention
    ntention         <-- i 삭제 (delete i)
    etention         <-- n을 e로 치환 (substitute n by e)
    exention         <-- t를 x로 치환 (substitute t by x)
    exenution        <-- u 삽입 (insert u)
    execution        <-- n을 c로 치환 (substitute n by c)
- study_note: 'intention'에서 'execution'으로 변하는 과정을 단계별 편집 연산(삭제, 치환, 삽입)으로 보여주는 예시입니다.

## Block 2
- type: figure_caption
- source_text: Figure 2.16 Path from intention to execution.
- korean_translation: 그림 2.16 intention에서 execution으로 가는 경로.
- study_note: 이전 페이지에서 논의된 최적 경로(optimal path)의 구체적인 예시입니다.

## Block 3
- type: paragraph
- source_text: then we could use it instead, resulting in a shorter overall path, and the optimal sequence wouldn’t be optimal, thus leading to a contradiction.
- korean_translation: 그렇다면 우리는 대신 그 경로를 사용할 수 있을 것이고, 결과적으로 전체 경로가 더 짧아지게 되어 원래의 최적 시퀀스가 최적이 아니라는 모순에 도달하게 됩니다.
- study_note: [이전 페이지에서 계속되는 문장] 동적 계획법의 핵심인 '최적 부분 구조(optimal substructure)'를 귀류법으로 증명하는 문장의 마무리 부분입니다.

## Block 4
- type: paragraph
- source_text: The minimum edit distance algorithm algorithm was named by Wagner and Fischer (1974) but independently discovered by many people (see the Historical Notes section of Chapter 8).
- korean_translation: 최소 편집 거리 알고리즘(minimum edit distance algorithm)은 Wagner와 Fischer (1974)에 의해 명명되었지만, 많은 사람들에 의해 독립적으로 발견되었습니다 (8장의 역사적 노트 섹션 참조).
- study_note: 알고리즘의 명칭 유래와 역사적 배경을 언급합니다. 흔히 Wagner-Fischer 알고리즘이라고도 불립니다.

## Block 5
- type: margin_note
- source_text: minimum edit distance algorithm
- korean_translation: 최소 편집 거리 알고리즘(minimum edit distance algorithm)
- study_note: 편집 거리를 계산하는 전형적인 동적 계획법 알고리즘입니다.

## Block 6
- type: paragraph
- source_text: Let’s first define the minimum edit distance between two strings. Given two strings, the source string X of length n, and target string Y of length m, we’ll define $D[i,j]$ as the edit distance between $X[1..i]$ and $Y[1..j]$, i.e., the first i characters of X and the first j characters of Y. The edit distance between X and Y is thus $D[n,m]$.
- korean_translation: 먼저 두 문자열 사이의 최소 편집 거리를 정의해 봅시다. 두 문자열, 즉 길이가 n인 원본 문자열 X와 길이가 m인 대상 문자열 Y가 주어졌을 때, $D[i,j]$를 $X[1..i]$와 $Y[1..j]$ 사이의 편집 거리, 즉 X의 처음 i개 문자와 Y의 처음 j개 문자 사이의 거리로 정의하겠습니다. 따라서 X와 Y 사이의 편집 거리는 $D[n,m]$이 됩니다.
- study_note: 동적 계획법을 위한 상태 공간 $D[i,j]$를 수학적으로 정의합니다. 행렬의 각 셀이 부분 문자열 간의 거리를 나타내게 됩니다.

## Block 7
- type: paragraph
- source_text: We’ll use dynamic programming to compute $D[n,m]$ bottom up, combining solutions to subproblems. In the base case, with a source substring of length i but an empty target string, going from i characters to 0 requires i deletes. With a target substring of length j but an empty source going from 0 characters to j characters requires j inserts. Having computed $D[i,j]$ for small i, j we then compute larger $D[i,j]$ based on previously computed smaller values. The value of $D[i,j]$ is computed by taking the minimum of the three possible paths through the matrix which arrive there:
- korean_translation: 우리는 동적 계획법을 사용하여 하위 문제들에 대한 해답을 결합하며 상향식(bottom up)으로 $D[n,m]$을 계산할 것입니다. 기저 사례(base case)의 경우, 길이가 i인 원본 부분 문자열에서 빈 대상 문자열로 가는 데는 i개의 삭제가 필요합니다. 길이가 j인 대상 부분 문자열에 대해 빈 원본 문자열에서 시작하여 j개 문자로 가는 데는 j개의 삽입이 필요합니다. 작은 i, j에 대해 $D[i,j]$를 계산한 후, 이전에 계산된 작은 값들을 바탕으로 더 큰 $D[i,j]$를 계산합니다. $D[i,j]$의 값은 행렬을 통해 해당 위치에 도달할 수 있는 세 가지 가능한 경로 중 최솟값을 취하여 계산됩니다.
- study_note: 알고리즘의 기저 사례(빈 문자열과의 거리)와 점화식의 논리적 근거를 설명합니다.

## Block 8
- type: formula
- source_text: |
    D[i, j] = min {
      D[i - 1, j] + del-cost(source[i])
      D[i, j - 1] + ins-cost(target[j])
      D[i - 1, j - 1] + sub-cost(source[i], target[j])
    }
- korean_translation: |
    D[i, j] = min {
      D[i - 1, j] + del-cost(source[i])
      D[i, j - 1] + ins-cost(target[j])
      D[i - 1, j - 1] + sub-cost(source[i], target[j])
    }
- study_note: 최소 편집 거리를 구하는 가장 일반적인 점화식입니다. 삭제, 삽입, 치환 비용을 각각 고려합니다.

## Block 9
- type: paragraph
- source_text: If we assume the version of Levenshtein distance in which the insertions and deletions each have a cost of 1 (ins-cost(·) = del-cost(·) = 1), and substitutions have a cost of 2 (except substitution of identical letters have zero cost), the computation for $D[i,j]$ becomes:
- korean_translation: 삽입과 삭제의 비용이 각각 1이고(ins-cost(·) = del-cost(·) = 1), 치환 비용이 2인(동일한 문자로의 치환은 비용이 0인 경우 제외) 레벤슈타인 거리 버전을 가정하면, $D[i,j]$에 대한 계산은 다음과 같이 됩니다.
- study_note: 표준 레벤슈타인 거리(Standard Levenshtein distance)의 가중치 설정을 설명합니다.

## Block 10
- type: formula
- source_text: |
    D[i, j] = min {
      D[i - 1, j] + 1
      D[i, j - 1] + 1
      D[i - 1, j - 1] + { 2; if source[i] != target[j] 
                          0; if source[i] == target[j]
    } (2.8)
- korean_translation: |
    D[i, j] = min {
      D[i - 1, j] + 1
      D[i, j - 1] + 1
      D[i - 1, j - 1] + { 2; if source[i] != target[j] 
                          0; if source[i] == target[j]
    } (2.8)
- study_note: 식 (2.8). 구체적인 비용이 대입된 레벤슈타인 거리 점화식입니다.

## Block 11
- type: paragraph
- source_text: The algorithm is summarized in Fig. 2.17; Fig. 2.18 shows the results of applying the algorithm to the distance between intention and execution with the version of Levenshtein in Eq. 2.8.
- korean_translation: 알고리즘은 그림 2.17에 요약되어 있으며, 그림 2.18은 식 2.8의 레벤슈타인 버전을 사용하여 'intention'과 'execution' 사이의 거리에 알고리즘을 적용한 결과를 보여줍니다.
- study_note: 다음 페이지에 보게 될 의사코드와 행렬 예시를 안내합니다.

## Block 12
- type: section_title
- source_text: Alignment
- korean_translation: 정렬 (Alignment)
- study_note: 편집 거리 알고리즘의 중요한 부산물인 '정렬' 개념을 소개합니다.

## Block 13
- type: paragraph
- source_text: Knowing the minimum edit distance is useful for algorithms like finding potential spelling error corrections. But the edit distance algorithm is important in another way; with a small change, it can also provide the minimum cost alignment between two strings. Aligning two strings is useful throughout speech and language processing. In speech recognition, minimum edit distance alignment is [다음 페이지에서 계속]
- korean_translation: 최소 편집 거리를 아는 것은 잠재적인 철자 오류 수정을 찾는 것과 같은 알고리즘에 유용합니다. 하지만 편집 거리 알고리즘은 또 다른 면에서 중요합니다. 약간의 변경을 통해 두 문자열 사이의 최소 비용 정렬(alignment)을 제공할 수도 있기 때문입니다. 두 문자열을 정렬하는 것은 음성 및 언어 처리 전반에 걸쳐 유용합니다. 음성 인식에서 최소 편집 거리 정렬은 [다음 페이지에서 계속]
- study_note: 편집 거리가 단순한 숫자 값을 넘어서, 두 문자열의 '대응 관계'를 찾아내는 정렬 업무에도 핵심적임을 설명합니다.

---

# Page 24

## Block 1
- type: other
- source_text: 24 CHAPTER 2 • REGULAR EXPRESSIONS, TEXT NORMALIZATION, EDIT DISTANCE
- korean_translation: 24 제2장 • 정규 표현식, 텍스트 정규화, 편집 거리
- study_note: 페이지 상단 정보입니다.

## Block 2
- type: code
- source_text: |
    function MIN-EDIT-DISTANCE(source, target) returns min-distance
        n ← LENGTH(source)
        m ← LENGTH(target)
        Create a distance matrix distance[n+1,m+1]

        # Initialization: the zeroth row and column is the distance from the empty string
        D[0,0] = 0
        for each row i from 1 to n do
            D[i,0] ← D[i-1,0] + del-cost(source[i])
        for each column j from 1 to m do
            D[0,j] ← D[0,j-1] + ins-cost(target[j])

        # Recurrence relation:
        for each row i from 1 to n do
            for each column j from 1 to m do
                D[i,j] ← MIN( D[i-1,j] + del-cost(source[i]),
                              D[i-1,j-1] + sub-cost(source[i], target[j]),
                              D[i,j-1] + ins-cost(target[j]) )

        # Termination
        return D[n,m]
- korean_translation: |
    함수 MIN-EDIT-DISTANCE(source, target) 반환 최소-거리
        n ← LENGTH(source)
        m ← LENGTH(target)
        거리 행렬 distance[n+1,m+1] 생성

        # 초기화: 0번째 행과 열은 빈 문자열로부터의 거리임
        D[0,0] = 0
        1부터 n까지 각 행 i에 대해:
            D[i,0] ← D[i-1,0] + del-cost(source[i])
        1부터 m까지 각 열 j에 대해:
            D[0,j] ← D[0,j-1] + ins-cost(target[j])

        # 점화식(Recurrence relation):
        1부터 n까지 각 행 i에 대해:
            1부터 m까지 각 열 j에 대해:
                D[i,j] ← MIN( D[i-1,j] + del-cost(source[i]),
                              D[i-1,j-1] + sub-cost(source[i], target[j]),
                              D[i,j-1] + ins-cost(target[j]) )

        # 종료
        return D[n,m]
- study_note: 최소 편집 거리를 구하는 알고리즘의 의사코드입니다. 초기화, 반복문을 통한 행렬 채우기(Tabulation), 최종 값 반환의 전형적인 동적 계획법 구조를 가집니다.

## Block 3
- type: figure_caption
- source_text: Figure 2.17 The minimum edit distance algorithm, an example of the class of dynamic programming algorithms. The various costs can either be fixed (e.g., ∀x, ins-cost(x) = 1) or can be specific to the letter (to model the fact that some letters are more likely to be inserted than others). We assume that there is no cost for substituting a letter for itself (i.e., sub-cost(x,x) = 0).
- korean_translation: 그림 2.17 동적 계획법 알고리즘 클래스의 예시인 최소 편집 거리 알고리즘. 다양한 비용들은 고정될 수도 있고(예: 모든 x에 대해 ins-cost(x) = 1), 특정 문자에 따라 다를 수도 있습니다 (일부 문자가 다른 문자보다 더 자주 삽입될 수 있다는 사실을 모델링하기 위함). 우리는 문자 자신을 자신으로 치환하는 데는 비용이 들지 않는다고 가정합니다(즉, sub-cost(x,x) = 0).
- study_note: 알고리즘의 비용 설정 유연성에 대한 추가 설명입니다. 문자에 따른 가중치 조절이 가능함을 시사합니다.

## Block 4
- type: table
- source_text: |
    Src\Tar | # | e | x | e | c | u | t | i | o | n
    ------- | - | - | - | - | - | - | - | - | - | -
    #       | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9
    i       | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 6 | 7 | 8
    n       | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 7 | 8 | 7
    t       | 3 | 4 | 5 | 6 | 7 | 8 | 7 | 8 | 9 | 8
    e       | 4 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10| 9
    n       | 5 | 4 | 5 | 6 | 7 | 8 | 9 | 10| 11| 10
    t       | 6 | 5 | 6 | 7 | 8 | 9 | 8 | 9 | 10| 11
    i       | 7 | 6 | 7 | 8 | 9 | 10| 9 | 8 | 9 | 10
    o       | 8 | 7 | 8 | 9 | 10| 11| 10| 9 | 8 | 9
    n       | 9 | 8 | 9 | 10| 11| 12| 11| 10| 9 | 8
- korean_translation: |
    원본\대상 | # | e | x | e | c | u | t | i | o | n
    ------- | - | - | - | - | - | - | - | - | - | -
    #       | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9
    i       | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 6 | 7 | 8
    n       | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 7 | 8 | 7
    t       | 3 | 4 | 5 | 6 | 7 | 8 | 7 | 8 | 9 | 8
    e       | 4 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10| 9
    n       | 5 | 4 | 5 | 6 | 7 | 8 | 9 | 10| 11| 10
    t       | 6 | 5 | 6 | 7 | 8 | 9 | 8 | 9 | 10| 11
    i       | 7 | 6 | 7 | 8 | 9 | 10| 9 | 8 | 9 | 10
    o       | 8 | 7 | 8 | 9 | 10| 11| 10| 9 | 8 | 9
    n       | 9 | 8 | 9 | 10| 11| 12| 11| 10| 9 | 8
- study_note: Wagner-Fischer 알고리즘의 실행 결과인 거리 행렬입니다. 오른쪽 하단 끝의 값 '8'이 최종적인 최소 편집 거리를 나타냅니다.

## Block 5
- type: figure_caption
- source_text: Figure 2.18 Computation of minimum edit distance between intention and execution with the algorithm of Fig. 2.17, using Levenshtein distance with cost of 1 for insertions or deletions, 2 for substitutions.
- korean_translation: 그림 2.18 삽입이나 삭제에 비용 1, 치환에 비용 2를 사용하는 레벤슈타인 거리를 적용하여 그림 2.17의 알고리즘으로 계산한 intention과 execution 사이의 최소 편집 거리.
- study_note: 행렬 데이터의 기반이 되는 비용 설정을 설명합니다.

## Block 6
- type: paragraph
- source_text: used to compute the word error rate (Chapter 26). Alignment plays a role in machine translation, in which sentences in a parallel corpus (a corpus with a text in two languages) need to be matched to each other.
- korean_translation: [이전 페이지에서 계속] 단어 오류율(Word Error Rate, 26장)을 계산하는 데 사용됩니다. 정렬은 기계 번역에서 중요한 역할을 하는데, 병렬 코퍼스(두 가지 언어의 텍스트가 있는 코퍼스) 내의 문장들이 서로 매칭되어야 하기 때문입니다.
- study_note: 음성 인식의 WER(단어 오류율) 계산이나 기계 번역의 문장 매칭 등 정렬의 실제 활용 사례를 설명합니다.

## Block 7
- type: paragraph
- source_text: To extend the edit distance algorithm to produce an alignment, we can start by visualizing an alignment as a path through the edit distance matrix. Figure 2.19 shows this path with the boldfaced cell. Each boldfaced cell represents an alignment of a pair of letters in the two strings. If two boldfaced cells occur in the same row, there will be an insertion in going from the source to the target; two boldfaced cells in the same column indicate a deletion.
- korean_translation: 편집 거리 알고리즘을 정렬을 생성할 수 있도록 확장하기 위해, 먼저 정렬을 편집 거리 행렬을 통과하는 경로로 시각화해 볼 수 있습니다. 그림 2.19는 굵게 표시된 셀을 통해 이 경로를 보여줍니다. 각 굵게 표시된 셀은 두 문자열의 문자 쌍 정렬을 나타냅니다. 만약 두 개의 굵게 표시된 셀이 같은 행에서 발생한다면, 원본에서 대상으로 가는 과정에 삽입이 있음을 의미합니다. 같은 열에 있는 두 개의 굵은 셀은 삭제를 나타냅니다.
- study_note: 거리 행렬의 경로를 통해 어떻게 정렬을 유도할 수 있는지 기하학적인 직관을 제공합니다. 다음 페이지의 그림 2.19에 대한 사전 설명입니다.
# Page 25

## Block 1
- type: other
- source_text: 2.6 • SUMMARY 25
- korean_translation: 2.6 • 요약 25
- study_note: 페이지 상단 헤더 정보입니다.

## Block 2
- type: paragraph
- source_text: Figure 2.19 also shows the intuition of how to compute this alignment path. The computation proceeds in two steps. In the first step, we augment the minimum edit distance algorithm to store backpointers in each cell. The backpointer from a cell points to the previous cell (or cells) that we came from in entering the current cell. We’ve shown a schematic of these backpointers in Fig. 2.19. Some cells have multiple backpointers because the minimum extension could have come from multiple previous cells. In the second step, we perform a backtrace. In a backtrace, we start from the last cell (at the final row and column), and follow the pointers back through the dynamic programming matrix. Each complete path between the final cell and the initial cell is a minimum distance alignment. Exercise 2.7 asks you to modify the minimum edit distance algorithm to store the pointers and compute the backtrace to output an alignment.
- korean_translation: 그림 2.19는 또한 이 정렬 경로(alignment path)를 계산하는 방법에 대한 직관을 보여줍니다. 계산은 두 단계로 진행됩니다. 첫 번째 단계에서는 각 셀에 역포인터(backpointer)를 저장하도록 최소 편집 거리 알고리즘을 확장합니다. 셀의 역포인터는 현재 셀로 들어올 때 거쳐 온 이전 셀(또는 셀들)을 가리킵니다. 그림 2.19에 이러한 역포인터들의 개략도를 나타냈습니다. 어떤 셀들은 여러 개의 역포인터를 가질 수 있는데, 이는 최소 거리를 만드는 확장이 여러 이전 셀로부터 올 수 있었기 때문입니다. 두 번째 단계에서는 역추적(backtrace)을 수행합니다. 역추적에서는 마지막 셀(최종 행과 열)에서 시작하여 동적 계획법 행렬을 통해 포인터들을 거꾸로 따라갑니다. 최종 셀과 시작 셀 사이의 각 완성된 경로는 최소 거리 정렬을 형성합니다. 연습 문제 2.7에서는 포인터를 저장하고 역추적을 계산하여 정렬을 출력하도록 최소 편집 거리 알고리즘을 수정해 볼 것을 요구합니다.
- study_note: 최소 편집 거리 계산 후에 실제 정렬(대응 관계)을 어떻게 찾아내는지 설명합니다. 역포인터를 저장하고(메모이제이션 확장), 뒤에서부터 거꾸로 따라가는(역추적) 과정이 핵심입니다.

## Block 3
- type: margin_note
- source_text: backtrace
- korean_translation: 역추적 (backtrace)
- study_note: 동적 계획법 행렬을 거꾸로 훑어 최적 경로를 찾아내는 기법을 의미하는 키워드입니다.

## Block 4
- type: table
- source_text: |
    # | # | e | x | e | c | u | t | i | o | n 
    --|---|---|---|---|---|---|---|---|---|---|
    # | 0 | ←1| ←2| ←3| ←4| ←5| ←6| ←7| ←8| ←9
    i | ↑1| ↖↑2| ↖↑3| ↖↑4| ↖↑5| ↖↑6| ↖↑7| ↖6 | ←7| ←8
    n | ↑2| ↖↑3| ↖↑4| ↖↑5| ↖↑6| ↖↑7| ↖↑8| ↑7 | ↖↑8| ↖7
    t | ↑3| ↖↑4| ↖↑5| ↖↑6| ↖↑7| ↖↑8| ↖7 | ←8 | ↖↑9| ↑8
    e | ↑4| ↖3 | ←4 | ↖5 | ↖↑6| ↖↑7| ↑8 | ↖↑9| ↖↑10| ↑9
    n | ↑5| ↑4 | ↖↑5| ↖↑6| ↖↑7| ↖↑8| ↖↑9| ↖↑10| ↖↑11| ↖10
    t | ↑6| ↑5 | ↖↑6| ↖↑7| ↖↑8| ↖↑9| ↖8 | ←9 | ↖↑10| ↖↑11
    i | ↑7| ↑6 | ↖↑7| ↖↑8| ↖↑9| ↖↑10| ↑9 | ↖8 | ←9 | ↖↑10
    o | ↑8| ↑7 | ↖↑8| ↖↑9| ↖↑10| ↖↑11| ↑10| ↑9 | ↖8 | ←9
    n | ↑9| ↑8 | ↖↑9| ↖↑10| ↖↑11| ↖↑12| ↑11| ↑10| ↑9 | ↖8
- korean_translation: |
    # | # | e | x | e | c | u | t | i | o | n 
    --|---|---|---|---|---|---|---|---|---|---|
    # | 0 | ←1| ←2| ←3| ←4| ←5| ←6| ←7| ←8| ←9
    i | ↑1| ↖↑2| ↖↑3| ↖↑4| ↖↑5| ↖↑6| ↖↑7| ↖6 | ←7| ←8
    n | ↑2| ↖↑3| ↖↑4| ↖↑5| ↖↑6| ↖↑7| ↖↑8| ↑7 | ↖↑8| ↖7
    t | ↑3| ↖↑4| ↖↑5| ↖↑6| ↖↑7| ↖↑8| ↖7 | ←8 | ↖↑9| ↑8
    e | ↑4| ↖3 | ←4 | ↖5 | ↖↑6| ↖↑7| ↑8 | ↖↑9| ↖↑10| ↑9
    n | ↑5| ↑4 | ↖↑5| ↖↑6| ↖↑7| ↖↑8| ↖↑9| ↖↑10| ↖↑11| ↖10
    t | ↑6| ↑5 | ↖↑6| ↖↑7| ↖↑8| ↖↑9| ↖8 | ←9 | ↖↑10| ↖↑11
    i | ↑7| ↑6 | ↖↑7| ↖↑8| ↖↑9| ↖↑10| ↑9 | ↖8 | ←9 | ↖↑10
    o | ↑8| ↑7 | ↖↑8| ↖↑9| ↖↑10| ↖↑11| ↑10| ↑9 | ↖8 | ←9
    n | ↑9| ↑8 | ↖↑9| ↖↑10| ↖↑11| ↖↑12| ↑11| ↑10| ↑9 | ↖8
- study_note: 화살표는 각 셀에 저장된 역포인터(backpointers)를 나타냅니다. ↖(대각선)은 교체나 일치, ←(왼쪽)은 삽입, ↑(위쪽)은 삭제를 통해 도달했음을 의미합니다.

## Block 5
- type: figure_caption
- source_text: Figure 2.19 When entering a value in each cell, we mark which of the three neighboring cells we came from with up to three arrows. After the table is full we compute an alignment (minimum edit path) by using a backtrace, starting at the 8 in the lower-right corner and following the arrows back. The sequence of bold cells represents one possible minimum cost alignment between the two strings. Diagram design after Gusfield (1997).
- korean_translation: 그림 2.19 각 셀에 값을 입력할 때, 최대 3개의 화살표를 사용하여 우리가 거쳐 온 인접한 세 셀 중 어느 것인지를 표시합니다. 표가 채워지면 오른쪽 하단 모서리의 8에서 시작하여 화살표를 뒤로 따라가는 역추적(backtrace)을 사용하여 정렬(최소 편집 경로)을 계산합니다. 굵게 표시된 셀의 시퀀스는 두 문자열 사이의 가능한 최소 비용 정렬 중 하나를 나타냅니다. 다이어그램 디자인은 Gusfield (1997)를 따름.
- study_note: 역추적 알고리즘의 구체적인 작동 방식과 그림 2.19 행렬의 시각적 요소를 설명하는 캡션입니다.

## Block 6
- type: paragraph
- source_text: While we worked our example with simple Levenshtein distance, the algorithm in Fig. 2.17 allows arbitrary weights on the operations. For spelling correction, for example, substitutions are more likely to happen between letters that are next to each other on the keyboard. The Viterbi algorithm is a probabilistic extension of minimum edit distance. Instead of computing the “minimum edit distance” between two strings, Viterbi computes the “maximum probability alignment” of one string with another. We’ll discuss this more in Chapter 8.
- korean_translation: 우리가 단순한 레벤슈타인 거리로 예제를 다루었지만, 그림 2.17의 알고리즘은 연산에 임의의 가중치를 부여하는 것을 허용합니다. 예를 들어 철자 교정의 경우, 키보드에서 서로 인접한 글자들 사이에서 치환이 일어날 가능성이 더 높습니다. 비터비(Viterbi) 알고리즘은 최소 편집 거리의 확률적 확장판입니다. 비터비는 두 문자열 사이의 "최소 편집 거리"를 계산하는 대신, 한 문자열과 다른 문자열의 "최대 확률 정렬"을 계산합니다. 이에 대해서는 8장에서 더 자세히 논의하겠습니다.
- study_note: 편집 거리의 확장 개념인 가중치 적용과 확률적 모델(비터비 알고리즘)로의 발전을 소개합니다.

## Block 7
- type: section_title
- source_text: 2.6 Summary
- korean_translation: 2.6 요약
- study_note: 2장에서 다룬 주요 개념들을 정리하는 섹션입니다.

## Block 8
- type: paragraph
- source_text: |
    This chapter introduced a fundamental tool in language processing, the regular expression, and showed how to perform basic text normalization tasks including word segmentation and normalization, sentence segmentation, and stemming. We also introduced the important minimum edit distance algorithm for comparing strings. Here’s a summary of the main points we covered about these ideas:
    • The regular expression language is a powerful tool for pattern-matching.
    • Basic operations in regular expressions include concatenation of symbols, disjunction of symbols ([], |, and .), counters (*, +, and {n,m}), anchors (^, $) and precedence operators ( (,) ).
- korean_translation: |
    이 장에서는 언어 처리의 핵심 도구인 정규 표현식을 소개하고, 단어 분절 및 정규화, 문장 분절, 어간 추출을 포함한 기본적인 텍스트 정규화 작업을 수행하는 방법을 살펴보았습니다. 또한 문자열을 비교하기 위한 중요한 최소 편집 거리 알고리즘을 도입했습니다. 여기 이 주제들에 대해 우리가 다룬 주요 내용들을 요약합니다.
    • 정규 표현식 언어는 패턴 매칭을 위한 강력한 도구입니다.
    • 정규 표현식의 기본 연산에는 기호의 연결(concatenation), 기호의 선택([], |, .), 카운터(*, +, {n,m}), 앵커(^, $), 그리고 우선순위 연산자((, )) 등이 포함됩니다.
- study_note: 2장 전체에서 배운 핵심 전처리 기술들과 정규 표현식의 기본 요소를 정리합니다.

# Page 26

## Block 1
- type: paragraph
- source_text: |
    • Word tokenization and normalization are generally done by cascades of simple regular expression substitutions or finite automata.
    • The Porter algorithm is a simple and efficient way to do stemming, stripping off affixes. It does not have high accuracy but may be useful for some tasks.
    • The minimum edit distance between two strings is the minimum number of operations it takes to edit one into the other. Minimum edit distance can be computed by dynamic programming, which also results in an alignment of the two strings.
- korean_translation: |
    • 단어 토큰화와 정규화는 일반적으로 단순한 정규 표현식 치환이나 유한 오토마타의 연쇄(cascades)를 통해 수행됩니다.
    • 포터(Porter) 알고리즘은 접사를 제거하여 어간 추출(stemming)을 수행하는 단순하고 효율적인 방법입니다. 정확도가 높지는 않지만 일부 작업에는 유용할 수 있습니다.
    • 두 문자열 사이의 최소 편집 거리는 하나의 문자열을 다른 문자열로 편집하는 데 필요한 최소 연산 횟수입니다. 최소 편집 거리는 동적 계획법으로 계산할 수 있으며, 이는 두 문자열의 정렬(alignment) 결과로도 이어집니다.
- study_note: 2장에서 다룬 핵심 개념들(토큰화, 어간 추출, 편집 거리)의 요약을 마무리합니다.

## Block 2
- type: section_title
- source_text: Bibliographical and Historical Notes
- korean_translation: 참고 문헌 및 역사적 노트
- study_note: 2장에서 다룬 기술들의 역사적 배경과 주요 문헌을 소개하는 섹션입니다.

## Block 3
- type: paragraph
- source_text: Kleene (1951, 1956) first defined regular expressions and the finite automaton, based on the McCulloch-Pitts neuron. Ken Thompson was one of the first to build regular expressions compilers into editors for text searching (Thompson, 1968). His editor ed included a command “g/regular expression/p”, or Global Regular Expression Print, which later became the Unix grep utility.
- korean_translation: Kleene (1951, 1956)는 McCulloch-Pitts 뉴런을 기반으로 정규 표현식과 유한 오토마타를 처음으로 정의했습니다. Ken Thompson은 텍스트 검색을 위한 에디터에 정규 표현식 컴파일러를 내장시킨 최초의 인물 중 하나였습니다(Thompson, 1968). 그의 에디터 ed에는 “g/정규표현식/p”, 즉 Global Regular Expression Print라는 명령어가 포함되어 있었으며, 이는 나중에 유닉스의 grep 유틸리티가 되었습니다.
- study_note: 정규 표현식의 수학적 기원(Kleene)과 실용적 도구로서의 발전(Thompson, grep의 유래)을 설명합니다.

## Block 4
- type: paragraph
- source_text: Text normalization algorithms have been applied since the beginning of the field. One of the earliest widely used stemmers was Lovins (1968). Stemming was also applied early to the digital humanities, by Packard (1973), who built an affix-stripping morphological parser for Ancient Greek. Currently a wide variety of code for tokenization and normalization is available, such as the Stanford Tokenizer (http://nlp.stanford.edu/software/tokenizer.shtml) or specialized tokenizers for Twitter (O’Connor et al., 2010), or for sentiment (http://sentiment.christopherpotts.net/tokenizing.html). See Palmer (2012) for a survey of text preprocessing. NLTK is an essential tool that offers both useful Python libraries (http://www.nltk.org) and textbook descriptions (Bird et al., 2009) of many algorithms including text normalization and corpus interfaces.
- korean_translation: 텍스트 정규화 알고리즘은 이 분야의 시작부터 적용되어 왔습니다. 초기 가장 널리 사용된 어간 추출기 중 하나는 Lovins (1968)였습니다. 어간 추출은 Packard (1973)에 의해 디지털 인문학 분야에도 일찍 적용되었는데, 그는 고대 그리스어를 위한 접사 제거 기반의 형태소 분석기를 만들었습니다. 현재는 Stanford Tokenizer (http://nlp.stanford.edu/software/tokenizer.shtml)나 트위터를 위한 특화된 토크나이저 (O’Connor et al., 2010), 또는 감성 분석용 (http://sentiment.christopherpotts.net/tokenizing.html) 등 다양한 토큰화 및 정규화 코드를 사용할 수 있습니다. 텍스트 전처리에 대한 조사는 Palmer (2012)를 참고하십시오. NLTK는 유용한 파이썬 라이브러리 (http://www.nltk.org)와 텍스트 정규화 및 코퍼스 인터페이스를 포함한 많은 알고리즘의 교재 설명 (Bird et al., 2009)을 모두 제공하는 필수적인 도구입니다.
- study_note: 텍스트 정규화 기술의 역사와 현대에 사용되는 주요 도구(NLTK, Stanford Tokenizer 등) 및 라이브러리를 안내합니다.

## Block 5
- type: paragraph
- source_text: For more on Herdan’s law and Heaps’ Law, see Herdan (1960, p. 28), Heaps (1978), Egghe (2007) and Baayen (2001); Yasseri et al. (2012) discuss the relationship with other measures of linguistic complexity. For more on edit distance, see the excellent Gusfield (1997). Our example measuring the edit distance from ‘intention’ to ‘execution’ was adapted from Kruskal (1983). There are various publicly available packages to compute edit distance, including Unix diff and the NIST sclite program (NIST, 2005).
- korean_translation: Herdan의 법칙과 Heaps의 법칙에 대한 자세한 내용은 Herdan (1960, p. 28), Heaps (1978), Egghe (2007) 및 Baayen (2001)을 참고하십시오. Yasseri 등 (2012)은 언어적 복잡성의 다른 측정치들과의 관계를 논의합니다. 편집 거리에 대한 더 자세한 내용은 Gusfield (1997)의 훌륭한 저서를 참고하십시오. 'intention'에서 'execution'까지의 편집 거리를 측정하는 우리의 예제는 Kruskal (1983)에서 가져온 것입니다. 유닉스의 diff와 NIST의 sclite 프로그램 (NIST, 2005)을 포함하여 편집 거리를 계산하기 위한 다양한 공개 패키지들이 존재합니다.
- study_note: 어휘 통계 법칙(Herdan, Heaps)과 편집 거리에 관한 심화 문헌 및 도구를 소개합니다.

## Block 6
- type: paragraph
- source_text: In his autobiography Bellman (1984) explains how he originally came up with the term dynamic programming:
- korean_translation: Bellman (1984)은 그의 자서전에서 '동적 계획법(dynamic programming)'이라는 용어를 원래 어떻게 생각해냈는지 설명합니다.
- study_note: 동적 계획법이라는 명칭의 유래에 대한 도입부입니다.

## Block 7
- type: paragraph
- source_text: |
    “...The 1950s were not good years for mathematical research. [the] Secretary of Defense ...had a pathological fear and hatred of the word, research... I decided therefore to use the word, “programming”. I wanted to get across the idea that this was dynamic, this was multistage... I thought, let’s ... take a word that has an absolutely precise meaning, namely dynamic... it’s impossible to use the word, dynamic, in a pejorative sense. Try thinking of some combination that will possibly give it a pejorative meaning. It’s impossible. Thus, I thought dynamic programming was a good name. It was something not even a Congressman could object to.”
- korean_translation: |
    “...1950년대는 수학적 연구에 좋은 시절이 아니었습니다. 국방장관은 '연구(research)'라는 단어에 대해 병적인 공포와 증오를 가지고 있었습니다... 그래서 나는 '계획법(programming)'이라는 단어를 사용하기로 결정했습니다. 나는 이것이 동적(dynamic)이고 다단계(multistage)라는 아이디어를 전달하고 싶었습니다... 나는 절대적으로 정밀한 의미를 가진 단어, 즉 '동적(dynamic)'이라는 단어를 가져오자고 생각했습니다... 동적이라는 단어를 경멸적인 의미로 사용하는 것은 불가능합니다. 그것에 경멸적인 의미를 부여할 수 있는 조합을 생각해보려 노력해보십시오. 불가능합니다. 그래서 나는 동적 계획법이 좋은 이름이라고 생각했습니다. 그것은 국회의원조차 반대할 수 없는 것이었습니다.”
- study_note: 리처드 벨먼이 정치적인 이유(국방부의 '연구' 예산 삭감 기조)를 피해 '동적 계획법'이라는 세련되고 반대하기 어려운 용어를 선택하게 된 흥미로운 실화를 담고 있습니다.
