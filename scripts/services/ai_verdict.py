from __future__ import annotations

import json
import os
import shlex
import subprocess
from typing import Any


SYSTEM_INSTRUCTION = """You are the quest judge for a personal control tower.
Return JSON only with keys:
- verdict: one of done, partial, hold
- reason: short Korean explanation
- restart_point: where to resume from next time
- next_hint: next smallest action
- plan_impact: impact on today's/short-term/long-term plan

Judge based on:
- completion criteria
- actual work done
- remaining work
- blocker
- self assessment

Rules:
- done only if completion criteria is substantially met
- partial if there is meaningful progress but criteria is not fully met
- hold if it should pause for now
- keep outputs concise and practical
"""


def build_ai_prompt(
    quest_title: str,
    completion_criteria: str,
    work_summary: str,
    remaining_work: str,
    blocker: str,
    self_assessment: str,
) -> str:
    payload = {
        "quest_title": quest_title,
        "completion_criteria": completion_criteria,
        "work_summary": work_summary,
        "remaining_work": remaining_work,
        "blocker": blocker,
        "self_assessment": self_assessment,
    }
    return f"{SYSTEM_INSTRUCTION}\n\nINPUT_JSON:\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n"


def heuristic_verdict(
    quest_title: str,
    completion_criteria: str,
    work_summary: str,
    remaining_work: str,
    blocker: str,
    self_assessment: str,
) -> dict[str, str]:
    assessment = (self_assessment or "").strip().lower()
    has_remaining = bool((remaining_work or "").strip())
    has_blocker = bool((blocker or "").strip())
    has_progress = bool((work_summary or "").strip())

    if assessment in {"완료", "done"} and not has_remaining:
        verdict = "done"
    elif assessment in {"보류", "hold"} or (has_blocker and not has_progress):
        verdict = "hold"
    elif has_progress:
        verdict = "partial" if has_remaining or has_blocker or assessment in {"부분완료", "partial"} else "done"
    else:
        verdict = "hold"

    if verdict == "done":
        return {
            "verdict": "done",
            "reason": f"`{quest_title}`는 완료 기준에 실질적으로 도달한 것으로 판단했습니다. 기준: {completion_criteria}",
            "restart_point": "완료 처리됨. 필요 시 후속 퀘스트로 이동",
            "next_hint": "다음 우선 항목 또는 기한 임박 항목을 검토",
            "plan_impact": "현재 퀘스트 완료로 보고, 다음 퀘스트 또는 후속 계획으로 전환",
        }
    if verdict == "partial":
        return {
            "verdict": "partial",
            "reason": f"`{quest_title}`는 의미 있는 진전이 있었지만 완료 기준을 아직 모두 충족하지 못했습니다.",
            "restart_point": remaining_work.strip() or blocker.strip() or "마지막 작업 지점에서 다시 이어가기",
            "next_hint": remaining_work.strip() or "남은 완료 기준을 가장 작은 행동으로 쪼개기",
            "plan_impact": "현재 주 임무는 유지하되 퀘스트는 부분완료로 기록하고 다음 작은 행동으로 연결",
        }
    return {
        "verdict": "hold",
        "reason": f"`{quest_title}`는 지금 시점에서는 멈추는 편이 맞다고 판단했습니다.",
        "restart_point": blocker.strip() or remaining_work.strip() or "보류 사유를 먼저 해결",
        "next_hint": "보류 사유 해소 후 다시 시작",
        "plan_impact": "현재 퀘스트는 보류로 기록하고 우선순위 재검토 필요",
    }


def parse_model_output(raw: str) -> dict[str, str]:
    data = json.loads(raw)
    verdict = data.get("verdict", "").strip().lower()
    if verdict not in {"done", "partial", "hold"}:
        raise ValueError("invalid verdict from model")
    return {
        "verdict": verdict,
        "reason": str(data.get("reason", "")).strip(),
        "restart_point": str(data.get("restart_point", "")).strip(),
        "next_hint": str(data.get("next_hint", "")).strip(),
        "plan_impact": str(data.get("plan_impact", "")).strip(),
    }


def run_cli_verdict(prompt: str) -> dict[str, str]:
    command = os.environ.get("CONTROL_TOWER_VERDICT_COMMAND", "").strip()
    if not command:
        raise RuntimeError("CONTROL_TOWER_VERDICT_COMMAND is not configured")

    completed = subprocess.run(
        shlex.split(command),
        input=prompt,
        capture_output=True,
        text=True,
        check=True,
        timeout=int(os.environ.get("CONTROL_TOWER_VERDICT_TIMEOUT_SEC", "90")),
    )
    stdout = completed.stdout.strip()
    if not stdout:
        raise RuntimeError("empty model output")
    return parse_model_output(stdout)


def generate_verdict(
    quest_title: str,
    completion_criteria: str,
    work_summary: str,
    remaining_work: str,
    blocker: str,
    self_assessment: str,
) -> dict[str, Any]:
    prompt = build_ai_prompt(
        quest_title=quest_title,
        completion_criteria=completion_criteria,
        work_summary=work_summary,
        remaining_work=remaining_work,
        blocker=blocker,
        self_assessment=self_assessment,
    )
    provider = "heuristic"
    try:
        verdict = run_cli_verdict(prompt)
        provider = "cli"
    except Exception as exc:
        verdict = heuristic_verdict(
            quest_title=quest_title,
            completion_criteria=completion_criteria,
            work_summary=work_summary,
            remaining_work=remaining_work,
            blocker=blocker,
            self_assessment=self_assessment,
        )
        verdict["fallback_reason"] = str(exc)

    return {
        **verdict,
        "provider": provider,
        "prompt": prompt,
    }
