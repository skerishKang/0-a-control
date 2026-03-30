# Architecture Strategy: Control Tower vs. Working Files

## 1. Role Separation

| Component | Role | Data Store | Key Interaction |
| :--- | :--- | :--- | :--- |
| **Control Tower (지휘소)** | **Strategic Direction & Scheduling** | `control_tower.db` | "What do I do now?" / "What is the priority?" |
| **Working Files (작업철)** | **Deep Execution & Reasoning** | `docs/dossiers/*.md` | "Why are we doing this?" / "How do we solve this detail?" |

### Control Tower Responsibilities
- Mission/Quest assignment and lifecycle.
- Status management (`todo`, `doing`, `done`, `hold`).
- Due date tracking and urgency alerts.
- High-level "Operational Loop" (Morning/EOD).
- Entry point for all sessions.

### Working Files (Dossiers) Responsibilities
- **Context Preservation**: Strategic background that doesn't fit in a database cell.
- **AI Collaboration**: Summaries of debates between different models/agents (e.g., Red Team context).
- **Evidence Repository**: Links to source files, emails, or logs.
- **Deep Planning**: Breaking down complex missions into detailed logic before they become quests.

---

## 2. Working File Template (작업철 양식)
Every dossier must follow the standard structure located in `templates/dossier_template.md`.

### Core Sections
1. **목표 (Goal)**: Why this project exists.
2. **현재 상태 (Current State)**: What has been done vs. what's blocked.
3. **핵심 쟁점 (Core Issues)**: The hardest problems to solve right now.
4. **근거 자료 (Evidence)**: Links to relevant docs/logs.
5. **AI 토론 요약 (AI Discussion Summary)**: Insights from different agent sessions.
6. **결정 (Decisions)**: Critical choices made and their rationale.
7. **다음 질문 (Next Questions)**: What we need to clarify next.
8. **다음 액션 (Next Actions)**: Immediate next steps to take.

---

## 3. UX Connection: Board to Dossier

### ID-based Mapping
- Every `plan_item` will map to a dossier file: `docs/dossiers/[plan_item_id]-[slug].md`.
- **board-v2 UI Update**: A direct link or button ("Dossier View") will be added to the mission/quest cards.

### Command Line
- `scripts/workon.sh` should automatically suggest opening the corresponding dossier.
