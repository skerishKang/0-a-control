// Correct copy for starting today's main mission as the current quest.
// Loaded after board-v2.js so this intentionally replaces only the affected action.
window.boardV2StartQuestFromMission = async function boardV2StartQuestFromMission() {
  if (!window.confirm("오늘의 주 임무로 작업을 시작할까요?")) return;

  try {
    const response = await fetch("/api/current-quest/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.error || "퀘스트 시작에 실패했습니다.");
    }
    await loadBoardV2();
    window.alert("오늘의 주 임무를 현재 퀘스트로 시작했습니다.");
    _reportDraft.summary = "";
    _reportDraft.assessment = "partial";
  } catch (error) {
    console.error("Failed to start quest from mission:", error);
    window.alert(`퀘스트 시작 실패: ${error.message}`);
  }
};
