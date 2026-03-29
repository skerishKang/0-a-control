# Playwright-CLI Skill 확장 프롬프트

작성일: 2026-03-27  
목적: 위의 공통 스킬 초안을 각 에이전트 환경(Codex / Claude Code / Kilo Code / 기타 Anthropic 계열)에 맞게 변환하도록 지시하는 프롬프트 모음

기준 문서:
- `docs/skills/playwright-cli-web-automation-skill.md`

## 1. Codex용 프롬프트

```text
아래 기준 문서를 바탕으로 Codex 환경에서 쓸 수 있는 Playwright-CLI 반복 웹업무 스킬 초안을 만들어라.

기준 문서:
G:\Ddrive\BatangD\task\workdiary\0-a-control\docs\skills\playwright-cli-web-automation-skill.md

목표:
- Codex가 반복 웹업무를 Playwright-CLI 방식으로 수행할 수 있게 한다.
- 처음 보는 사이트 탐색은 제외하고, 반복 루틴 자동화에 초점을 맞춘다.

반드시 포함할 것:
1. 언제 이 스킬을 써야 하는지
2. 입력 계약
3. 실행 순서
4. 실패 시 보고 방식
5. 예시 3개
6. 민감 작업 제한 규칙

출력 형식:
- Codex용 skill 초안
- 사용 예시
- 확장 포인트
```

## 2. Claude Code / Anthropic 계열용 프롬프트

```text
아래 기준 문서를 바탕으로 Claude Code 또는 Anthropic 계열 에이전트에서 쓸 수 있는 Playwright-CLI 웹업무 자동화 스킬 초안을 만들어라.

기준 문서:
G:\Ddrive\BatangD\task\workdiary\0-a-control\docs\skills\playwright-cli-web-automation-skill.md

목표:
- 자연어 지시를 반복 웹업무 자동화 루틴으로 안정적으로 변환하는 스킬을 만든다.
- MCP를 대체하려는 것이 아니라, 반복 운영용 보조 채널로 설계한다.

반드시 포함할 것:
1. 스킬 목적
2. 반복 루틴에 맞는 사용 조건
3. URL 접속 -> 상태 확인 -> 입력 -> 실행 -> 결과 요약 순서
4. screenshot / video 옵션
5. 실패 시 fallback 규칙
6. 예시 3개

출력 형식:
- Claude/Anthropic 계열용 skill 초안
- 예시 명령
- 운영 규칙
```

## 3. Kilo Code용 프롬프트

```text
아래 기준 문서를 바탕으로 Kilo Code 환경에서 쓸 수 있는 Playwright-CLI 반복 웹업무 스킬 초안을 만들어라.

기준 문서:
G:\Ddrive\BatangD\task\workdiary\0-a-control\docs\skills\playwright-cli-web-automation-skill.md

목표:
- Kilo Code에서 MCP 없이도 반복 웹업무를 자연어 -> CLI 루틴으로 실행할 수 있게 만든다.
- 고정된 사이트/고정된 폼/고정된 조회 루틴에 맞춰 설계한다.

반드시 포함할 것:
1. 이 스킬이 맞는 경우 / 안 맞는 경우
2. 입력값 구조
3. 단계별 명령 흐름
4. 결과 요약 형식
5. screenshot/video 남기는 방식
6. 테스트용 예시

출력 형식:
- Kilo Code용 skill 초안
- 테스트 예시
- 주의사항
```

## 4. 공통 변환 지침

어느 플랫폼이든 아래 원칙은 유지하는 것이 좋다.

1. 처음 탐색은 MCP가 더 낫다.
2. 반복 루틴만 스킬화한다.
3. 결과는 항상 텍스트로 요약한다.
4. 중요한 작업은 캡처를 남긴다.
5. 민감 작업은 자동 실행하지 않는다.

## 5. 추천 운영 방식

1. 먼저 하나의 실제 대상 사이트를 정한다.
2. 공통 스킬 초안으로 1차 버전을 만든다.
3. 그 플랫폼에 맞게 프롬프트로 변환한다.
4. 테스트한다.
5. 통과하면 사이트별 세부 스킬로 쪼갠다.

한 줄 결론:
- 먼저 공통 스킬을 만든 뒤,
- 플랫폼별 프롬프트로 얇게 변환하는 방식이 가장 안정적이다.
