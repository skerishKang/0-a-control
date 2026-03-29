# Platform Adoption Prompts

이 문서는 위 starter skill을 각 에이전트 환경으로 옮길 때 쓰는 프롬프트 모음이다.

## 1. Codex용

```text
아래 스킬 초안을 바탕으로 Codex 환경에서 사용할 수 있는 Playwright-CLI 반복 웹업무 스킬로 변환해라.

기준 문서:
G:\Ddrive\BatangD\task\workdiary\0-a-control\docs\skills\playwright-cli-starter-skill\SKILL.md

목표:
- 반복 웹업무를 자연어 -> CLI 루틴으로 수행할 수 있게 한다.
- 탐색형 작업이 아니라 반복 운영용으로 설계한다.

반드시 포함할 것:
1. 사용 조건
2. 입력 형식
3. 실행 순서
4. 실패 시 fallback
5. 예시 3개
6. 민감 작업 제한

출력:
- Codex용 skill 초안
```

## 2. Claude / Anthropic 계열용

```text
아래 스킬 초안을 바탕으로 Claude / Anthropic 계열에서 사용할 수 있는 Playwright-CLI 반복 웹업무 스킬로 변환해라.

기준 문서:
G:\Ddrive\BatangD\task\workdiary\0-a-control\docs\skills\playwright-cli-starter-skill\SKILL.md

목표:
- 자연어 명령을 반복 웹업무 실행 루틴으로 안정적으로 바꾸게 한다.
- MCP를 대체하는 만능 도구가 아니라, 반복 운영용 보조 채널로 설계한다.

반드시 포함할 것:
1. 맞는 경우 / 안 맞는 경우
2. 입력 계약
3. 실행 순서
4. screenshot / video 옵션
5. 실패 시 fallback
6. 예시 3개

출력:
- Claude/Anthropic용 skill 초안
```

## 3. Kilo Code용

```text
아래 스킬 초안을 바탕으로 Kilo Code 환경에서 사용할 수 있는 Playwright-CLI 반복 웹업무 스킬로 변환해라.

기준 문서:
G:\Ddrive\BatangD\task\workdiary\0-a-control\docs\skills\playwright-cli-starter-skill\SKILL.md

목표:
- Kilo Code에서 MCP 없이도 반복 웹업무를 자연어 -> CLI 실행 루틴으로 돌릴 수 있게 한다.

반드시 포함할 것:
1. 적합한 작업 유형
2. 입력값 구조
3. 단계별 실행 흐름
4. 결과 요약 형식
5. 실패 시 중단/보고 규칙
6. 테스트 예시

출력:
- Kilo Code용 skill 초안
```

## 4. 사용 순서

1. 먼저 `SKILL.md` 내용을 검토한다.
2. 실제 사이트 하나를 `site-template.md`로 정리한다.
3. 그다음 이 프롬프트 중 하나로 플랫폼별 스킬 초안을 만든다.
4. 작은 루틴 하나로 테스트한다.
