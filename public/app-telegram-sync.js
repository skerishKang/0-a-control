/**
 * Telegram Sync rendering module for Classic UI
 */

function getTelegramConnectionState() {
  const telegramStatus = state.telegramStatus || {};
  const missingConfig = Array.isArray(telegramStatus.missing_config) ? telegramStatus.missing_config : [];
  const hasUsableSession = Boolean(
    telegramStatus.configured &&
    telegramStatus.session_exists &&
    !telegramStatus.auth_required &&
    (telegramStatus.user || telegramStatus.last_seen || telegramStatus.session_path)
  );
  if (!telegramStatus.configured) {
    return {
      code: "unconfigured",
      label: "미설정",
      summary: "Telegram 내부 서비스 설정이 아직 없습니다.",
      detail: missingConfig.length
        ? `${missingConfig.join(", ")} 값을 먼저 설정해야 합니다.`
        : "TELEGRAM_API_ID / TELEGRAM_API_HASH와 핵심 소스 설정이 필요합니다.",
      tone: "warning",
    };
  }
  if (!hasUsableSession) {
    return {
      code: "auth",
      label: "인증 필요",
      summary: "Telegram 로그인 세션 확인이 필요합니다.",
      detail: telegramStatus.session_exists
        ? `세션이 끊겼거나 인증이 만료되었습니다. 세션 파일: ${telegramStatus.session_path || "-"}`
        : `세션 파일이 아직 없습니다. 첫 연결이 성공하면 ${telegramStatus.session_path || "-"} 에 생성됩니다.`,
      tone: "warning",
    };
  }
  const userLabel = telegramStatus.user?.username || telegramStatus.user?.first_name || "사용자";
  return {
    code: "connected",
    label: "연결됨",
    summary: `Telegram 내부 서비스가 ${userLabel} 계정으로 연결되어 있습니다.`,
    detail: telegramStatus.last_seen
      ? `마지막 확인 ${formatRecentLabel(telegramStatus.last_seen)}`
      : "인증 세션과 핵심 소스가 준비되어 있습니다.",
    tone: "success",
  };
}

function deriveTelegramFailureMessage(lastRun, sources) {
  const telegramStatus = state.telegramStatus || {};
  const missingConfig = Array.isArray(telegramStatus.missing_config) ? telegramStatus.missing_config : [];
  const hasUsableSession = Boolean(
    telegramStatus.configured &&
    telegramStatus.session_exists &&
    !telegramStatus.auth_required &&
    (telegramStatus.user || telegramStatus.last_seen || telegramStatus.session_path)
  );
  if (!telegramStatus.configured) {
    return {
      title: "동기화에 실패했습니다. Telegram 설정이 아직 없습니다.",
      detail: missingConfig.length
        ? `${missingConfig.join(", ")} 를 설정하고 서버를 다시 확인하세요.`
        : "TELEGRAM_API_ID / TELEGRAM_API_HASH를 설정하고 서버를 다시 확인하세요.",
    };
  }
  if (!sources.length) {
    return {
      title: "동기화할 핵심 소스가 없습니다.",
      detail: "telegram_sources에서 core 소스를 지정해야 sync-core가 동작합니다.",
    };
  }
  if (!hasUsableSession) {
    return {
      title: "동기화에 실패했습니다. Telegram 인증 세션이 필요합니다.",
      detail: "로그인 세션을 다시 연결한 뒤 sync-core를 다시 실행하세요.",
    };
  }
  return {
    title: "동기화에 실패했습니다. Telegram 응답을 확인해야 합니다.",
    detail: lastRun?.error ? `상세: ${lastRun.error}` : "일시적 오류일 수 있으니 잠시 후 다시 시도하세요.",
  };
}

function renderTelegramSetupHint(connectionState, sources) {
  const target = document.getElementById("telegramSetupHint");
  if (!target) return;
  const telegramStatus = state.telegramStatus || {};

  let hint = "동기화 전 준비: Telegram API ID/API HASH 설정, 로그인 세션 생성, 핵심 소스 지정이 필요합니다.";
  if (connectionState.code === "auth") {
    hint = `동기화 전 준비: ${connectionState.detail}`;
  } else if (connectionState.code === "connected") {
    hint = sources.length
      ? "동기화 전 준비 완료: 연결된 세션으로 핵심 소스만 가져옵니다."
      : "연결은 되어 있지만 sync-core용 핵심 소스 지정이 아직 없습니다.";
  } else if (telegramStatus.setup_message) {
    hint = `동기화 전 준비: ${telegramStatus.setup_message}`;
  }

  target.textContent = hint;
  target.className = `telegram-setup-hint ${connectionState.tone}`;
}

function renderTelegramSyncStatus() {
  const banner = document.getElementById("syncStatusBanner");
  const sourceStatus = document.getElementById("telegramSourceStatus");
  if (!banner) return;

  const sources = state.telegramSyncStatus?.sources || [];
  const telegramStatus = state.telegramStatus || {};
  const lastRun = state.lastTelegramSyncRun || null;
  const connectionState = getTelegramConnectionState();
  renderTelegramSetupHint(connectionState, sources);

  const lastRunDetails = Array.isArray(lastRun?.details) ? lastRun.details : [];
  const sourceDetailMap = new Map(lastRunDetails.map((detail) => [String(detail.source_id), detail]));
  if (sourceStatus) {
    sourceStatus.innerHTML = sources.map((source) => {
      const detail = sourceDetailMap.get(String(source.source_id));
      const hasError = Boolean(detail?.error) || /No module named 'telethon'/.test(String(telegramStatus.error || ""));
      const hasHistory = Boolean(source.last_synced_at) && !hasError;
      const label = hasError ? "실패" : hasHistory ? "연결됨" : "미수집";
      const klass = hasError ? "warning" : hasHistory ? "success" : "muted";
      const countLabel = Number(source.new_count || 0) > 0 ? ` · 새 ${Number(source.new_count || 0)}건` : "";
      const title = hasError
        ? detail.error
        : hasHistory
          ? `${source.source_name} · 마지막 ${formatRecentLabel(source.last_synced_at)}`
          : `${source.source_name} · 아직 동기화 이력 없음`;
      return `
        <div class="telegram-source-pill ${klass}" title="${escapeHtml(title)}">
          <strong>${escapeHtml(source.source_name || source.source_id)}</strong>
          <span>${escapeHtml(label)}${escapeHtml(countLabel)}</span>
        </div>
      `;
    }).join("");
  }

  if (state.telegramSyncRunning) {
    banner.innerHTML = `
      <span class="sync-status-text"><span class="telegram-status-chip ${connectionState.tone}">${escapeHtml(connectionState.label)}</span>핵심 소스를 확인하며 동기화를 실행하고 있습니다.</span>
      <span class="sync-status-time">Telegram 메시지를 직접 불러오는 중</span>
    `;
    banner.className = "sync-status-banner info";
    return;
  }

  if (!sources.length) {
    const setupHint = lastRun?.error
      ? deriveTelegramFailureMessage(lastRun, sources).detail
      : (telegramStatus.setup_message || connectionState.detail);
    banner.innerHTML = `
      <span class="sync-status-text"><span class="telegram-status-chip ${connectionState.tone}">${escapeHtml(connectionState.label)}</span>${escapeHtml(connectionState.summary)}</span>
      <span class="sync-status-time">${escapeHtml(setupHint)}</span>
    `;
    banner.className = "sync-status-banner warning";
    return;
  }

  const coreCount = sources.length;
  const syncedCount = sources.filter((s) => s.last_synced_at).length;
  const queuedNewCount = sources.reduce((sum, source) => sum + Number(source.new_count || 0), 0);
  const reviewingCount = sources.reduce((sum, source) => sum + Number(source.reviewing_count || 0), 0);
  let latestSync = null;
  sources.forEach((s) => {
    if (s.last_synced_at) {
      const d = new Date(s.last_synced_at);
      if (!latestSync || d > latestSync) latestSync = d;
    }
  });

  const timeLabel = latestSync ? formatRecentLabel(latestSync.toISOString()) : "이력 없음";
  const statusClass = lastRun && !lastRun.ok ? "warning" : "info";

  if (lastRun) {
    if (lastRun.ok) {
      const details = Array.isArray(lastRun.details) ? lastRun.details : [];
      const successCount = details.filter((detail) => !detail.error).length || syncedCount;
      const failedCount = details.filter((detail) => detail.error).length;
      const importedCount = Number(lastRun.synced_count || 0);

      banner.innerHTML = `
        <span class="sync-status-text"><span class="telegram-status-chip ${connectionState.tone}">${escapeHtml(connectionState.label)}</span>마지막 동기화 ${formatRecentLabel(lastRun.executed_at || latestSync?.toISOString() || "")} · 새 메시지 ${importedCount}건 반영</span>
        <span class="sync-status-time">핵심 ${coreCount}개 중 ${successCount}개 성공${failedCount ? ` / ${failedCount}개 실패` : ""} · 검토중 ${reviewingCount}건 보관</span>
      `;
      banner.className = "sync-status-banner success";
      return;
    }

    const failure = deriveTelegramFailureMessage(lastRun, sources);
    banner.innerHTML = `
      <span class="sync-status-text"><span class="telegram-status-chip ${connectionState.tone}">${escapeHtml(connectionState.label)}</span>${escapeHtml(failure.title)}</span>
      <span class="sync-status-time">마지막 시도 ${formatRecentLabel(lastRun.failed_at || "")} · ${escapeHtml(failure.detail)}</span>
    `;
    banner.className = "sync-status-banner warning";
    return;
  }

  banner.innerHTML = `
    <span class="sync-status-text"><span class="telegram-status-chip ${connectionState.tone}">${escapeHtml(connectionState.label)}</span>마지막 동기화 ${timeLabel} · 새 항목 ${queuedNewCount}건 대기</span>
    <span class="sync-status-time">핵심 ${coreCount}개 중 ${syncedCount}개 이력 있음 · 검토중 ${reviewingCount}건 보관</span>
  `;
  banner.className = `sync-status-banner ${statusClass}`;
}
