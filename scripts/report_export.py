from __future__ import annotations

from pathlib import Path

from scripts.queue_runtime import report_export as _impl

REPORTS_DIR = _impl.REPORTS_DIR
generate_report_id = _impl.generate_report_id
generate_filename = _impl.generate_filename
save_json = _impl.save_json
connect = _impl.connect


def export_quest_report(
    quest_id: str,
    quest_title: str,
    completion_criteria: str,
    work_summary: str,
    remaining_work: str,
    blocker: str,
    self_assessment: str,
    session_id: str = "",
) -> Path:
    _impl.REPORTS_DIR = REPORTS_DIR
    return _impl.export_quest_report(
        quest_id=quest_id,
        quest_title=quest_title,
        completion_criteria=completion_criteria,
        work_summary=work_summary,
        remaining_work=remaining_work,
        blocker=blocker,
        self_assessment=self_assessment,
        session_id=session_id,
    )
