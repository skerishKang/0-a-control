from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ExecutionContext(str, Enum):
    REMOTE_DOABLE = "remote_doable"
    GITHUB_WEB_MODEL_NEEDED = "github_web_model_needed"
    LOCAL_NEEDED = "local_needed"
    MIXED_REMOTE_CODE_LOCAL_VALIDATION = "mixed_remote_code_local_validation"


class PromptType(str, Enum):
    IMPLEMENTATION = "implementation"
    LOCAL_VALIDATION = "local_validation"
    GITHUB_WEB = "github_web"
    DOCUMENT_REVIEW = "document_review"
    PR_REVIEW = "pr_review"
    STATUS_CHECK = "status_check"


@dataclass(frozen=True)
class ExecutorPromptTemplate:
    prompt_type: str
    title: str
    sections: tuple[str, ...]
    description: str


PROMPT_TEMPLATES: dict[str, ExecutorPromptTemplate] = {
    PromptType.IMPLEMENTATION: ExecutorPromptTemplate(
        prompt_type=PromptType.IMPLEMENTATION,
        title="구현 프롬프트",
        sections=(
            "목표",
            "대상 저장소",
            "브랜치",
            "작업 범위",
            "제외 범위",
            "구현 기준",
            "검증 명령",
            "보고 형식",
            "완료 기준",
        ),
        description="코드 또는 문서 변경을 수행하는 프롬프트",
    ),
    PromptType.LOCAL_VALIDATION: ExecutorPromptTemplate(
        prompt_type=PromptType.LOCAL_VALIDATION,
        title="로컬 검증 프롬프트",
        sections=(
            "환경 확인 명령",
            "실행 명령",
            "기대 결과",
            "PASS/FAIL 기준",
            "실패 요약 방식",
        ),
        description="서버 실행, 테스트, 브라우저 확인 등 로컬 검증을 수행하는 프롬프트",
    ),
    PromptType.GITHUB_WEB: ExecutorPromptTemplate(
        prompt_type=PromptType.GITHUB_WEB,
        title="GitHub 웹모델 프롬프트",
        sections=(
            "실행 대상 작업",
            "GitHub UI 조작 절차",
            "승인 기준",
        ),
        description="GitHub API 실패 시 GitHub UI 기반 작업을 수행하는 프롬프트",
    ),
    PromptType.DOCUMENT_REVIEW: ExecutorPromptTemplate(
        prompt_type=PromptType.DOCUMENT_REVIEW,
        title="문서 리뷰 프롬프트",
        sections=(
            "리뷰 기준",
            "링크 검토 항목",
            "외부 프로젝트 혼입 여부",
            "중복/충돌 확인",
        ),
        description="문서 변경의 범위, 정확성, 충돌 가능성을 리뷰하는 프롬프트",
    ),
    PromptType.PR_REVIEW: ExecutorPromptTemplate(
        prompt_type=PromptType.PR_REVIEW,
        title="PR 리뷰 프롬프트",
        sections=(
            "변경 범위",
            "merge readiness 판단",
            "관련 이슈",
            "검증 결과",
            "blocking condition",
        ),
        description="PR 변경 범위와 merge readiness를 판단하는 프롬프트",
    ),
    PromptType.STATUS_CHECK: ExecutorPromptTemplate(
        prompt_type=PromptType.STATUS_CHECK,
        title="상태 점검 프롬프트",
        sections=(
            "현재 상태",
            "자동 분류",
            "수동 override",
            "검증 상태",
            "다음 액션",
            "stale 여부",
        ),
        description="이슈/PR/작업 큐 상태를 갱신하는 프롬프트",
    ),
}


@dataclass
class PromptInput:
    work_item: dict[str, Any] | None = None
    classification: dict[str, Any] | None = None
    manual_override: dict[str, Any] | None = None
    validation_checklist: dict[str, Any] | None = None
    repository: dict[str, Any] | None = None
    changed_files: list[str] | None = None
    execution_context: str = ExecutionContext.REMOTE_DOABLE
    guards: tuple[str, ...] = ()
    links: dict[str, str] | None = None


def _build_implementation_prompt(inp: PromptInput) -> str:
    parts: list[str] = []
    wi = inp.work_item or {}
    repo = inp.repository or {}

    parts.append("## 목표")
    parts.append(f"{wi.get('title', '작업 없음')} — {wi.get('description', '')}")
    parts.append("")
    parts.append("## 대상 저장소")
    parts.append(f"- 저장소: {repo.get('full_name', 'N/A')}")
    parts.append(f"- 브랜치: {wi.get('branch', 'main')}")
    parts.append(f"- 이슈: {wi.get('issue_url', 'N/A')}")
    parts.append("")
    parts.append("## 작업 범위")
    if inp.changed_files:
        parts.append("아래 파일만 수정합니다:")
        for f in inp.changed_files:
            parts.append(f"- {f}")
    else:
        parts.append("변경 파일 미지정")
    parts.append("")
    parts.append("## 제외 범위")
    parts.append("작업 범위에 포함되지 않은 파일/영역은 수정하지 않습니다.")
    if wi.get('exclusion'):
        parts.append(f"{wi['exclusion']}")
    parts.append("")
    parts.append("## 구현 기준")
    parts.append(f"- 목표: {wi.get('goal', 'N/A')}")
    parts.append(f"- acceptance: {wi.get('acceptance', 'N/A')}")
    parts.append("")
    parts.append("## 검증 명령")
    parts.append("```bash")
    parts.append("# 검증 명령을 여기에 작성")
    parts.append("```")
    parts.append("")
    parts.append("## 보고 형식")
    parts.append("- [ ] 작업 완료 여부")
    parts.append("- [ ] 검증 결과")
    parts.append("- [ ] 발생한 이슈")
    parts.append("")
    parts.append("## 완료 기준")
    parts.append("1. 모든 검증 명령 PASS")
    parts.append("2. 코드 컴파일/문법 체크 통과")
    parts.append("3. 테스트 통과")
    parts.append("")

    return "\n".join(parts)


def _build_local_validation_prompt(inp: PromptInput) -> str:
    parts: list[str] = []
    parts.append("## 환경 확인 명령")
    parts.append("```bash")
    parts.append("# 필요 도구/환경 확인")
    parts.append("```")
    parts.append("")
    parts.append("## 실행 명령")
    parts.append("```bash")
    parts.append("# 검증 실행")
    parts.append("```")
    parts.append("")
    parts.append("## 기대 결과")
    parts.append("- [정상 결과 설명]")
    parts.append("")
    parts.append("## PASS/FAIL 기준")
    parts.append("- PASS: 모든 검증 항목 정상")
    parts.append("- FAIL: 검증 항목 중 하나라도 비정상")
    parts.append("")
    parts.append("## 실패 요약 방식")
    parts.append("실패 시: 어떤 항목이, 왜 실패했는지 요약")
    parts.append("")

    return "\n".join(parts)


def _build_github_web_prompt(inp: PromptInput) -> str:
    parts: list[str] = []
    parts.append("## 실행 대상 작업")
    parts.append(f"{inp.work_item.get('title', 'N/A') if inp.work_item else 'N/A'}")
    parts.append("")
    parts.append("## GitHub UI 조작 절차")
    parts.append("1. 해당 이슈/PR 페이지로 이동")
    parts.append("2. 필요한 UI 작업 수행")
    parts.append("")
    parts.append("## 승인 기준")
    parts.append("- 고위험 작업(merge, close 등)은 별도 승인 필요")
    parts.append("")

    return "\n".join(parts)


def _build_document_review_prompt(inp: PromptInput) -> str:
    parts: list[str] = []
    parts.append("## 리뷰 기준")
    parts.append("- 범위 정확성")
    parts.append("- 링크 정확성")
    parts.append("- 외부 프로젝트 혼입 여부")
    parts.append("- 기존 문서와 중복/충돌 여부")
    parts.append("")
    parts.append("## 읽을 문서")
    if inp.changed_files:
        for f in inp.changed_files:
            parts.append(f"- {f}")
    else:
        parts.append("문서 파일 미지정")
    parts.append("")

    return "\n".join(parts)


def _build_pr_review_prompt(inp: PromptInput) -> str:
    parts: list[str] = []
    parts.append("## 변경 범위")
    if inp.changed_files:
        for f in inp.changed_files:
            parts.append(f"- {f}")
    parts.append("")
    parts.append("## merge readiness 판단")
    parts.append("- [ ] 범위 확인 완료")
    parts.append("- [ ] 검증 통과")
    parts.append("- [ ] blocking condition 없음")
    parts.append("")
    parts.append("## 관련 이슈")
    if inp.links and "issue" in inp.links:
        parts.append(f"{inp.links['issue']}")
    parts.append("")
    parts.append("## 검증 결과")
    if inp.validation_checklist:
        for item in inp.validation_checklist.get("items", []):
            parts.append(f"- [{item.get('status', ' ')}] {item.get('name', 'N/A')}")
    parts.append("")

    return "\n".join(parts)


def _build_status_check_prompt(inp: PromptInput) -> str:
    parts: list[str] = []
    parts.append("## 현재 상태")
    classification = inp.classification or {}
    parts.append(f"- 상태: {classification.get('status', 'N/A')}")
    parts.append(f"- 이유: {classification.get('reason', 'N/A')}")
    parts.append(f"- 다음 액션: {classification.get('next_action', 'N/A')}")
    parts.append("")
    parts.append("## 자동 분류")
    if inp.classification:
        for k, v in inp.classification.items():
            parts.append(f"- {k}: {v}")
    parts.append("")
    parts.append("## 수동 override")
    if inp.manual_override:
        parts.append(f"- 상태: {inp.manual_override.get('manual_status', 'N/A')}")
        parts.append(f"- 이유: {inp.manual_override.get('reason', 'N/A')}")
    else:
        parts.append("- 수동 override 없음")
    parts.append("")
    parts.append("## stale 여부")
    if inp.guards:
        parts.append(f"경고: {', '.join(inp.guards)}")
    else:
        parts.append("stale 아님")
    parts.append("")

    return "\n".join(parts)


SECTION_BUILDERS = {
    PromptType.IMPLEMENTATION: _build_implementation_prompt,
    PromptType.LOCAL_VALIDATION: _build_local_validation_prompt,
    PromptType.GITHUB_WEB: _build_github_web_prompt,
    PromptType.DOCUMENT_REVIEW: _build_document_review_prompt,
    PromptType.PR_REVIEW: _build_pr_review_prompt,
    PromptType.STATUS_CHECK: _build_status_check_prompt,
}

# legacy aliases
PROMPT_BUILDERS = SECTION_BUILDERS


def build_prompt(prompt_type: str, input_data: PromptInput | None = None) -> dict[str, Any]:
    if input_data is None:
        input_data = PromptInput()

    try:
        pt = prompt_type if isinstance(prompt_type, PromptType) else PromptType(prompt_type)
    except ValueError:
        return {
            "error": f"Unknown prompt type: {prompt_type}",
            "valid_types": [t.value for t in PromptType],
        }
    builder = SECTION_BUILDERS.get(pt)
    if builder is None:
        return {
            "error": f"Unknown prompt type: {prompt_type}",
            "valid_types": [t.value for t in PromptType],
        }

    body = builder(input_data)
    template = PROMPT_TEMPLATES.get(pt)

    warnings: list[str] = []
    if input_data.guards:
        warnings.append(f"경고 플래그: {', '.join(input_data.guards)}")
    if input_data.execution_context == ExecutionContext.GITHUB_WEB_MODEL_NEEDED:
        warnings.append("GitHub API 실패 시 GitHub 웹 UI 필요")
    if input_data.execution_context == ExecutionContext.LOCAL_NEEDED:
        warnings.append("로컬 실행 환경 필요 — 원격 실행 불가")

    source_data: dict[str, Any] = {
        "prompt_type": pt.value,
        "execution_context": input_data.execution_context,
        "work_item_number": input_data.work_item.get("number") if input_data.work_item else None,
        "repository": input_data.repository.get("full_name") if input_data.repository else None,
    }

    return {
        "prompt_title": template.title if template else prompt_type,
        "prompt_body": body,
        "warnings": warnings,
        "source_data": source_data,
    }


def generate_executor_prompt(
    prompt_type: str,
    work_item: dict[str, Any] | None = None,
    classification: dict[str, Any] | None = None,
    manual_override: dict[str, Any] | None = None,
    validation_checklist: dict[str, Any] | None = None,
    repository: dict[str, Any] | None = None,
    changed_files: list[str] | None = None,
    execution_context: str = ExecutionContext.REMOTE_DOABLE,
    guards: tuple[str, ...] = (),
    links: dict[str, str] | None = None,
    include_validation: bool = False,
    include_override: bool = False,
    include_links: bool = False,
) -> dict[str, Any]:
    inp = PromptInput(
        work_item=work_item,
        classification=classification,
        manual_override=manual_override if include_override else None,
        validation_checklist=validation_checklist if include_validation else None,
        repository=repository,
        changed_files=changed_files,
        execution_context=execution_context,
        guards=guards,
        links=links if include_links else None,
    )
    return build_prompt(prompt_type, inp)


def get_executor_prompt_templates() -> dict[str, Any]:
    templates = []
    for pt in PromptType:
        t = PROMPT_TEMPLATES[pt]
        templates.append({
            "prompt_type": t.prompt_type,
            "title": t.title,
            "sections": t.sections,
            "description": t.description,
        })

    return {
        "templates": templates,
        "execution_contexts": [e.value for e in ExecutionContext],
    }
