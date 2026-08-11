(() => {
  "use strict";

  const membersList = document.getElementById("members-list");
  const candidatesList = document.getElementById("candidates-list");
  const placesList = document.getElementById("places-list");
  const setupStatus = document.getElementById("setup-status");
  const setupOverlay = document.getElementById("setup-overlay");
  const setupDrawer = document.getElementById("setup-drawer");
  const emptyState = document.getElementById("empty-state");
  const workspace = document.getElementById("workspace");
  const headerActions = document.getElementById("header-actions");
  const workspaceContext = document.getElementById("workspace-context");
  const impactSection = document.getElementById("impact-section");
  const applyAnalyzeBtn = document.getElementById("apply-analyze");
  const saveWorkspaceBtn = document.getElementById("save-workspace");
  const workspacesOverlay = document.getElementById("workspaces-overlay");
  const workspacesDrawer = document.getElementById("workspaces-drawer");
  const workspacesList = document.getElementById("workspaces-list");
  const workspacesStatus = document.getElementById("workspaces-status");
  const workspaceSaveStatus = document.getElementById("workspace-save-status");

  let memberSeq = 1;
  let candidateSeq = 1;
  let lastMembersPayload = [];
  let lastCandidatesPayload = [];
  let impactByCandidateId = {};
  let analyzed = false;
  let activeWorkspaceId = null;

  const DEMO = {
    teamName: "AI Platform Team",
    coverageProfile: "ai_ml_product_delivery",
    targetRole: "ML Engineer",
    members: [
      {
        member_id: "A",
        display_name: "Alex",
        current_role: "ML Engineer",
        birth_date: "1986-02-08",
        birth_time: "20:20",
        birth_place: "Kingisepp, Russia",
      },
      {
        member_id: "B",
        display_name: "Bella",
        current_role: "ML Engineer",
        birth_date: "1985-09-11",
        birth_time: "00:21",
        birth_place: "Kazan, Russia",
      },
      {
        member_id: "D",
        display_name: "Daniel",
        current_role: "Solutions Engineer",
        birth_date: "1990-06-15",
        birth_time: "14:30",
        birth_place: "Miami, USA",
      },
    ],
    candidates: [
      {
        candidate_id: "C",
        display_name: "Chris",
        birth_date: "1997-01-28",
        birth_time: "10:00",
        birth_place: "Miami, USA",
      },
      {
        candidate_id: "E1",
        display_name: "Ava",
        birth_date: "1986-02-08",
        birth_time: "20:20",
        birth_place: "Kingisepp, Russia",
      },
      {
        candidate_id: "E2",
        display_name: "Elena",
        birth_date: "1983-10-29",
        birth_time: "14:30",
        birth_place: "Miami, USA",
      },
    ],
  };

  function escapeHtml(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function setStatus(el, message, kind) {
    if (!el) return;
    el.textContent = message || "";
    el.classList.remove("error", "loading");
    if (kind) el.classList.add(kind);
  }

  function statusChip(status) {
    const map = {
      missing: ["chip-missing", "Missing"],
      single_coverage: ["chip-single", "Single Coverage"],
      represented: ["chip-represented", "Represented"],
    };
    const [cls, label] = map[status] || ["chip-single", status || "Unknown"];
    return `<span class="chip ${cls}">${escapeHtml(label)}</span>`;
  }

  function listBlock(title, items) {
    if (!items || !items.length) return "";
    return `<div class="field-block"><h4>${escapeHtml(title)}</h4><ul>${
      items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")
    }</ul></div>`;
  }

  function textBlock(title, text) {
    if (!text) return "";
    return `<div class="field-block"><h4>${escapeHtml(title)}</h4><p>${escapeHtml(text)}</p></div>`;
  }

  function openSetup() {
    setupOverlay.hidden = false;
    setupDrawer.hidden = false;
    document.body.style.overflow = "hidden";
    const first = setupDrawer.querySelector("input, select, button");
    if (first) first.focus();
  }

  function closeSetup() {
    setupOverlay.hidden = true;
    setupDrawer.hidden = true;
    document.body.style.overflow = "";
  }

  function showWorkspaceShell() {
    emptyState.hidden = true;
    workspace.hidden = false;
    headerActions.hidden = false;
    workspaceContext.hidden = false;
  }

  function createMemberCard(data = {}) {
    const card = document.createElement("article");
    card.className = "person-card";
    card.innerHTML = `
      <div class="person-card-head">
        <strong>Team Member</strong>
        <button type="button" class="btn btn-danger remove-item">Remove</button>
      </div>
      <div class="person-fields">
        <label class="field"><span>Member ID</span><input name="member_id" required value="${escapeHtml(data.member_id || "")}" /></label>
        <label class="field"><span>Display Name</span><input name="display_name" required value="${escapeHtml(data.display_name || "")}" /></label>
        <label class="field"><span>Current Role</span><input name="current_role" value="${escapeHtml(data.current_role || "")}" /></label>
        <label class="field"><span>Birth Date</span><input name="birth_date" type="date" required value="${escapeHtml(data.birth_date || "")}" /></label>
        <label class="field"><span>Birth Time (optional)</span><input name="birth_time" type="time" value="${escapeHtml(data.birth_time || "")}" /></label>
        <label class="field"><span>Birth Place</span><input name="birth_place" list="places-list" required value="${escapeHtml(data.birth_place || "")}" /></label>
      </div>
    `;
    card.querySelector(".remove-item").addEventListener("click", () => {
      if (membersList.children.length <= 1) {
        setStatus(setupStatus, "Keep at least one team member.", "error");
        return;
      }
      card.remove();
    });
    memberSeq += 1;
    return card;
  }

  function createCandidateCard(data = {}) {
    const card = document.createElement("article");
    card.className = "person-card";
    card.innerHTML = `
      <div class="person-card-head">
        <strong>Candidate</strong>
        <button type="button" class="btn btn-danger remove-item">Remove</button>
      </div>
      <div class="person-fields">
        <label class="field"><span>Candidate ID</span><input name="candidate_id" required value="${escapeHtml(data.candidate_id || "")}" /></label>
        <label class="field"><span>Display Name</span><input name="display_name" required value="${escapeHtml(data.display_name || "")}" /></label>
        <label class="field"><span>Birth Date</span><input name="birth_date" type="date" required value="${escapeHtml(data.birth_date || "")}" /></label>
        <label class="field"><span>Birth Time (optional)</span><input name="birth_time" type="time" value="${escapeHtml(data.birth_time || "")}" /></label>
        <label class="field"><span>Birth Place</span><input name="birth_place" list="places-list" required value="${escapeHtml(data.birth_place || "")}" /></label>
      </div>
    `;
    card.querySelector(".remove-item").addEventListener("click", () => card.remove());
    candidateSeq += 1;
    return card;
  }

  function readFields(card) {
    const get = (name) => {
      const el = card.querySelector(`[name="${name}"]`);
      return el ? el.value.trim() : "";
    };
    return {
      member_id: get("member_id"),
      candidate_id: get("candidate_id"),
      display_name: get("display_name"),
      current_role: get("current_role") || null,
      birth_date: get("birth_date"),
      birth_time: get("birth_time") || null,
      birth_place: get("birth_place"),
    };
  }

  function collectMembers() {
    const members = [];
    for (const card of membersList.querySelectorAll(".person-card")) {
      const raw = readFields(card);
      if (!raw.member_id || !raw.display_name || !raw.birth_date || !raw.birth_place) {
        throw new Error("Each team member needs ID, name, birth date, and birth place.");
      }
      members.push({
        member_id: raw.member_id,
        display_name: raw.display_name,
        current_role: raw.current_role,
        birth_date: raw.birth_date,
        birth_time: raw.birth_time,
        birth_place: raw.birth_place,
      });
    }
    if (!members.length) throw new Error("Add at least one team member.");
    return members;
  }

  function collectCandidates() {
    const candidates = [];
    for (const card of candidatesList.querySelectorAll(".person-card")) {
      const raw = readFields(card);
      if (!raw.candidate_id || !raw.display_name || !raw.birth_date || !raw.birth_place) {
        throw new Error("Each candidate needs ID, name, birth date, and birth place.");
      }
      candidates.push({
        candidate_id: raw.candidate_id,
        display_name: raw.display_name,
        birth_date: raw.birth_date,
        birth_time: raw.birth_time,
        birth_place: raw.birth_place,
      });
    }
    return candidates;
  }

  async function apiRequest(path, options = {}) {
    const response = await fetch(path, {
      headers: { Accept: "application/json", ...(options.body ? { "Content-Type": "application/json" } : {}) },
      ...options,
    });
    if (response.status === 204) return null;
    let data = null;
    try {
      data = await response.json();
    } catch (_err) {
      data = null;
    }
    if (!response.ok) {
      const detail = data && (data.detail || data.message);
      const message = typeof detail === "string"
        ? detail
        : Array.isArray(detail)
          ? detail.map((item) => item.msg || JSON.stringify(item)).join("; ")
          : `Request failed (${response.status})`;
      throw new Error(message);
    }
    return data;
  }

  async function apiPost(path, body) {
    return apiRequest(path, { method: "POST", body: JSON.stringify(body) });
  }

  async function apiPut(path, body) {
    return apiRequest(path, { method: "PUT", body: JSON.stringify(body) });
  }

  async function apiGet(path) {
    return apiRequest(path, { method: "GET" });
  }

  async function apiDelete(path) {
    return apiRequest(path, { method: "DELETE" });
  }

  function normalizeTimeValue(value) {
    if (!value) return "";
    return String(value).slice(0, 5);
  }

  function updateSaveButtonLabel() {
    if (!saveWorkspaceBtn) return;
    saveWorkspaceBtn.textContent = activeWorkspaceId ? "Save Changes" : "Save Workspace";
  }

  function collectWorkspacePayload() {
    const members = collectMembers();
    const candidates = collectCandidates();
    return {
      team_name: document.getElementById("team-name").value.trim() || "Team",
      coverage_profile: document.getElementById("coverage-profile").value,
      target_role: document.getElementById("target-role").value.trim() || null,
      members,
      candidates,
    };
  }

  function fillWorkspaceForms(record) {
    document.getElementById("team-name").value = record.team_name || "";
    document.getElementById("coverage-profile").value = record.coverage_profile || "ai_ml_product_delivery";
    document.getElementById("target-role").value = record.target_role || "";
    membersList.innerHTML = "";
    candidatesList.innerHTML = "";
    (record.members || []).forEach((member) => {
      membersList.appendChild(createMemberCard({
        ...member,
        birth_time: normalizeTimeValue(member.birth_time),
      }));
    });
    (record.candidates || []).forEach((candidate) => {
      candidatesList.appendChild(createCandidateCard({
        ...candidate,
        birth_time: normalizeTimeValue(candidate.birth_time),
      }));
    });
    if (!membersList.children.length) {
      membersList.appendChild(createMemberCard({
        member_id: "A",
        display_name: "",
        current_role: "Engineer",
      }));
    }
  }

  function formatUpdatedAt(value) {
    try {
      return new Date(value).toLocaleDateString(undefined, {
        month: "short",
        day: "numeric",
        year: "numeric",
      });
    } catch (_err) {
      return value || "";
    }
  }

  function openWorkspacesPanel() {
    workspacesOverlay.hidden = false;
    workspacesDrawer.hidden = false;
    document.body.style.overflow = "hidden";
    refreshWorkspacesList();
  }

  function closeWorkspacesPanel() {
    workspacesOverlay.hidden = true;
    workspacesDrawer.hidden = true;
    document.body.style.overflow = "";
  }

  async function refreshWorkspacesList() {
    setStatus(workspacesStatus, "Loading saved workspaces…", "loading");
    workspacesList.innerHTML = "";
    try {
      const data = await apiGet("/api/v1/workspaces");
      const items = (data && data.workspaces) || [];
      if (!items.length) {
        setStatus(workspacesStatus, "No saved workspaces yet.");
        workspacesList.innerHTML = `<p class="meta">Save the current workspace to see it here.</p>`;
        return;
      }
      setStatus(workspacesStatus, "");
      workspacesList.innerHTML = items.map((item) => `
        <article class="workspace-card" data-workspace-id="${escapeHtml(item.workspace_id)}">
          <h3>${escapeHtml(item.team_name)}</h3>
          <p class="meta">${escapeHtml(item.target_role || "—")}</p>
          <p class="meta">${item.member_count} team member${item.member_count === 1 ? "" : "s"} · ${item.candidate_count} candidate${item.candidate_count === 1 ? "" : "s"}</p>
          <p class="meta">Updated ${escapeHtml(formatUpdatedAt(item.updated_at))}</p>
          <div class="compare-actions">
            <button type="button" class="btn btn-primary open-workspace" data-workspace-id="${escapeHtml(item.workspace_id)}">Open</button>
            <button type="button" class="btn btn-danger delete-workspace" data-workspace-id="${escapeHtml(item.workspace_id)}">Delete</button>
          </div>
        </article>
      `).join("");
      workspacesList.querySelectorAll(".open-workspace").forEach((btn) => {
        btn.addEventListener("click", () => openWorkspace(btn.getAttribute("data-workspace-id")));
      });
      workspacesList.querySelectorAll(".delete-workspace").forEach((btn) => {
        btn.addEventListener("click", () => deleteWorkspace(btn.getAttribute("data-workspace-id")));
      });
    } catch (err) {
      setStatus(workspacesStatus, err.message, "error");
    }
  }

  async function saveCurrentWorkspace() {
    setStatus(workspaceSaveStatus, activeWorkspaceId ? "Saving changes…" : "Saving workspace…", "loading");
    try {
      const payload = collectWorkspacePayload();
      // Persist INPUT STATE only — never Team Map / Gap / Impact responses.
      let record;
      if (activeWorkspaceId) {
        record = await apiPut(`/api/v1/workspaces/${activeWorkspaceId}`, payload);
      } else {
        record = await apiPost("/api/v1/workspaces", payload);
      }
      activeWorkspaceId = record.workspace_id;
      updateSaveButtonLabel();
      setStatus(workspaceSaveStatus, "Workspace saved");
      renderWorkspaceHeader(
        { member_count: payload.members.length },
        payload.candidates.length,
      );
    } catch (err) {
      setStatus(workspaceSaveStatus, err.message, "error");
    }
  }

  async function openWorkspace(workspaceId) {
    setStatus(workspacesStatus, "Opening workspace…", "loading");
    try {
      const record = await apiGet(`/api/v1/workspaces/${workspaceId}`);
      fillWorkspaceForms(record);
      activeWorkspaceId = record.workspace_id;
      updateSaveButtonLabel();
      closeWorkspacesPanel();
      setStatus(workspaceSaveStatus, "");
      await analyzeTeam({ fromDemo: false });
    } catch (err) {
      setStatus(workspacesStatus, err.message, "error");
    }
  }

  async function deleteWorkspace(workspaceId) {
    if (!window.confirm("Delete this saved workspace?")) return;
    setStatus(workspacesStatus, "Deleting…", "loading");
    try {
      await apiDelete(`/api/v1/workspaces/${workspaceId}`);
      if (activeWorkspaceId === workspaceId) {
        activeWorkspaceId = null;
        updateSaveButtonLabel();
        setStatus(workspaceSaveStatus, "Workspace deleted. Current view is unsaved.");
      }
      await refreshWorkspacesList();
    } catch (err) {
      setStatus(workspacesStatus, err.message, "error");
    }
  }

  function fillDemoForms() {
    document.getElementById("team-name").value = DEMO.teamName;
    document.getElementById("coverage-profile").value = DEMO.coverageProfile;
    document.getElementById("target-role").value = DEMO.targetRole;
    membersList.innerHTML = "";
    candidatesList.innerHTML = "";
    DEMO.members.forEach((member) => membersList.appendChild(createMemberCard(member)));
    DEMO.candidates.forEach((candidate) => candidatesList.appendChild(createCandidateCard(candidate)));
  }

  function renderWorkspaceHeader(teamMap, candidateCount) {
    const teamName = document.getElementById("team-name").value.trim() || "Team";
    const targetRole = document.getElementById("target-role").value.trim() || "—";
    const teamCount = teamMap ? teamMap.member_count : lastMembersPayload.length;
    const shortlistCount = typeof candidateCount === "number"
      ? candidateCount
      : lastCandidatesPayload.length;
    document.getElementById("context-team-name").textContent = teamName;
    document.getElementById("context-target-role").textContent =
      `${targetRole} · ${teamCount} team member${teamCount === 1 ? "" : "s"} · ${shortlistCount} shortlisted candidate${shortlistCount === 1 ? "" : "s"}`;
  }

  function statusTransitionHtml(beforeStatus, afterStatus, afterExtra) {
    return `
      <div class="delta-flow" role="group" aria-label="Before and after coverage status">
        <div class="delta-side">
          <span class="delta-label">Before</span>
          ${statusChip(beforeStatus)}
        </div>
        <div class="delta-arrow" aria-hidden="true">→</div>
        <div class="delta-side">
          <span class="delta-label">After</span>
          ${statusChip(afterStatus)}
          ${afterExtra ? `<span class="delta-extra">${escapeHtml(afterExtra)}</span>` : ""}
        </div>
      </div>
    `;
  }

  function renderWorkflowStrip(gap) {
    const root = document.getElementById("workflow-strip");
    const priority = document.getElementById("gap-priority");
    if (!gap || !gap.required_functions) {
      root.innerHTML = `<p class="meta">Coverage data unavailable.</p>`;
      priority.innerHTML = "";
      return;
    }

    const stages = gap.required_functions;
    const parts = [];
    stages.forEach((item, index) => {
      const statusClass = item.status === "missing"
        ? "is-missing"
        : item.status === "single_coverage"
          ? "is-single"
          : "";
      const memberNames = (item.member_ids || [])
        .map((id) => {
          const member = (lastMembersPayload || []).find((m) => m.member_id === id);
          return member ? member.display_name : id;
        })
        .join(", ");
      parts.push(`
        <article class="workflow-stage ${statusClass}">
          <h3>${escapeHtml(item.workflow_stage)}</h3>
          <p class="fn">${escapeHtml(item.team_function)}</p>
          ${statusChip(item.status)}
          <p class="members">${memberNames ? escapeHtml(memberNames) : "—"}</p>
        </article>
      `);
      if (index < stages.length - 1) {
        parts.push(`<div class="workflow-arrow" aria-hidden="true">→</div>`);
      }
    });
    root.innerHTML = parts.join("");

    const missing = stages.filter((item) => item.status === "missing");
    if (!missing.length) {
      priority.className = "gap-priority is-clear";
      priority.innerHTML = `
        <h3>Current Workflow Gap</h3>
        <p class="fn">No required workflow function is currently missing for this coverage profile.</p>
      `;
      return;
    }

    const first = missing[0];
    priority.className = "gap-priority";
    priority.innerHTML = `
      <h3>Current Workflow Gap</h3>
      <p class="stage">${escapeHtml(first.workflow_stage)}</p>
      <p class="fn">${escapeHtml(first.team_function)}</p>
      ${statusChip("missing")}
      <p class="why">${escapeHtml(first.why_it_matters)}</p>
    `;
  }

  function renderTeamMap(data) {
    const root = document.getElementById("team-map-cards");
    if (!data || !data.members || !data.members.length) {
      root.innerHTML = `<p class="meta">No team members returned.</p>`;
      return;
    }
    root.innerHTML = data.members.map((member) => {
      if (!member.profile_available) {
        return `
          <article class="profile-card unavailable">
            <h3>${escapeHtml(member.display_name)}</h3>
            <p class="meta">${escapeHtml(member.current_role || "—")}</p>
            <div class="function-tag">Profile unavailable</div>
            <p class="meta">${escapeHtml(member.error || "No profile could be produced for this member.")}</p>
          </article>
        `;
      }
      const topSkills = (member.top_skills || []).slice(0, 3);
      const keyRisks = (member.key_risks || []).slice(0, 2);
      const restSkills = (member.top_skills || []).slice(3);
      const restRisks = (member.key_risks || []).slice(2);
      return `
        <article class="profile-card">
          <h3>${escapeHtml(member.display_name)}</h3>
          <p class="meta">${escapeHtml(member.current_role || "—")}</p>
          <div class="function-tag">${escapeHtml(member.team_function || "—")}</div>
          ${listBlock("Top strengths", topSkills)}
          ${listBlock("Key risks", keyRisks)}
          <details class="more-details">
            <summary>View details</summary>
            ${textBlock("Thinking Style", member.thinking_style)}
            ${textBlock("Team Contribution", member.team_contribution)}
            ${listBlock("More strengths", restSkills)}
            ${listBlock("More risks", restRisks)}
            ${textBlock("Communication Style", member.communication_style)}
            ${listBlock("Onboarding Guidance", member.onboarding_guidance)}
            ${listBlock("Role Directions", member.role_directions)}
          </details>
        </article>
      `;
    }).join("");
  }

  function classifyImpactPreview(impactResult) {
    if (!impactResult || !impactResult.impact || !impactResult.impact.impact_available) {
      return {
        kind: "unavailable",
        label: "TEAM IMPACT UNAVAILABLE",
        detail: "",
        sub: (impactResult && impactResult.candidate && impactResult.candidate.error) || "",
        className: "unavailable",
      };
    }
    const impact = impactResult.impact;
    const beforeByFn = {};
    (impactResult.before.required_functions || []).forEach((item) => {
      beforeByFn[item.team_function] = item;
    });

    if (impact.closed_missing_functions && impact.closed_missing_functions.length) {
      const fn = impact.closed_missing_functions[0];
      const stage = impact.closed_workflow_stages && impact.closed_workflow_stages[0]
        ? impact.closed_workflow_stages[0]
        : (beforeByFn[fn] && beforeByFn[fn].workflow_stage) || "";
      return {
        kind: "closes",
        label: "CLOSES CURRENT GAP",
        detail: stage,
        sub: fn,
        className: "closes",
      };
    }
    if (impact.strengthened_single_coverage_functions && impact.strengthened_single_coverage_functions.length) {
      const fn = impact.strengthened_single_coverage_functions[0];
      const stage = (beforeByFn[fn] && beforeByFn[fn].workflow_stage) || "";
      return {
        kind: "strengthens",
        label: "STRENGTHENS SINGLE COVERAGE",
        detail: stage,
        sub: fn,
        className: "strengthens",
      };
    }
    if (impact.reinforced_represented_functions && impact.reinforced_represented_functions.length) {
      const fn = impact.reinforced_represented_functions[0];
      return {
        kind: "reinforces",
        label: "REINFORCES EXISTING FUNCTION",
        detail: fn,
        sub: "",
        className: "adds",
      };
    }
    if (impact.added_additional_functions && impact.added_additional_functions.length) {
      const fn = impact.added_additional_functions[0];
      return {
        kind: "adds",
        label: "ADDS ADDITIONAL FUNCTION",
        detail: fn,
        sub: "",
        className: "adds",
      };
    }
    if (impact.reinforced_additional_functions && impact.reinforced_additional_functions.length) {
      const fn = impact.reinforced_additional_functions[0];
      return {
        kind: "reinforces-additional",
        label: "REINFORCES ADDITIONAL FUNCTION",
        detail: fn,
        sub: "",
        className: "adds",
      };
    }
    return {
      kind: "none",
      label: "NO REQUIRED COVERAGE CHANGE",
      detail: "",
      sub: "",
      className: "unavailable",
    };
  }

  function previewHtml(preview) {
    return `
      <div class="impact-preview ${escapeHtml(preview.className)}">
        <p class="label">${escapeHtml(preview.label)}</p>
        ${preview.detail ? `<p class="detail">${escapeHtml(preview.detail)}</p>` : ""}
        ${preview.sub ? `<p class="sub">${escapeHtml(preview.sub)}</p>` : ""}
      </div>
    `;
  }

  function renderCompare(data) {
    const root = document.getElementById("compare-cards");
    if (!data || !data.candidates || !data.candidates.length) {
      if (lastCandidatesPayload.length === 1) {
        const only = lastCandidatesPayload[0];
        const impact = impactByCandidateId[only.candidate_id];
        const preview = classifyImpactPreview(impact);
        root.innerHTML = `
          <article class="compare-card">
            <h3>${escapeHtml(only.display_name)}</h3>
            <p class="meta">Single shortlist candidate</p>
            ${previewHtml(preview)}
            <div class="compare-actions">
              <button type="button" class="btn btn-primary view-impact" data-candidate-id="${escapeHtml(only.candidate_id)}">View Team Impact</button>
            </div>
          </article>
        `;
        bindImpactButtons(root);
        return;
      }
      root.innerHTML = `<p class="meta">Add candidates to compare structural impact.</p>`;
      return;
    }

    root.innerHTML = data.candidates.map((candidate) => {
      if (!candidate.profile_available) {
        return `
          <article class="compare-card unavailable">
            <h3>${escapeHtml(candidate.display_name)}</h3>
            <div class="function-tag">Profile unavailable</div>
            <p class="meta">${escapeHtml(candidate.error || "Profile could not be produced.")}</p>
          </article>
        `;
      }
      const impact = impactByCandidateId[candidate.candidate_id];
      const preview = classifyImpactPreview(impact);
      const topSkills = (candidate.top_skills || []).slice(0, 3);
      const keyRisks = (candidate.key_risks || []).slice(0, 2);
      return `
        <article class="compare-card">
          <h3>${escapeHtml(candidate.display_name)}</h3>
          <div class="function-tag">${escapeHtml(candidate.team_function || "—")}</div>
          ${previewHtml(preview)}
          ${listBlock("Top Skills", topSkills)}
          ${listBlock("Key Risks", keyRisks)}
          <details class="more-details">
            <summary>View profile details</summary>
            ${textBlock("Thinking Style", candidate.thinking_style)}
            ${textBlock("Team Contribution", candidate.team_contribution)}
            ${listBlock("Role Directions", candidate.role_directions)}
            ${listBlock("More skills", (candidate.top_skills || []).slice(3))}
            ${listBlock("More risks", (candidate.key_risks || []).slice(2))}
          </details>
          <div class="compare-actions">
            <button
              type="button"
              class="btn btn-primary view-impact"
              data-candidate-id="${escapeHtml(candidate.candidate_id)}"
            >View Team Impact</button>
          </div>
        </article>
      `;
    }).join("");
    bindImpactButtons(root);
  }

  function bindImpactButtons(root) {
    root.querySelectorAll(".view-impact").forEach((btn) => {
      btn.addEventListener("click", () => {
        const candidateId = btn.getAttribute("data-candidate-id");
        const candidate = lastCandidatesPayload.find((item) => item.candidate_id === candidateId);
        if (candidate) viewImpact(candidate);
      });
    });
  }

  function findStatus(snapshot, teamFunction) {
    return (snapshot.required_functions || []).find((item) => item.team_function === teamFunction);
  }

  function renderImpactDetail(data) {
    const root = document.getElementById("impact-content");
    const name = data.candidate && data.candidate.display_name
      ? data.candidate.display_name
      : "this candidate";

    if (!data.impact || !data.impact.impact_available) {
      root.innerHTML = `
        <h3 class="impact-title">What changes if we add ${escapeHtml(name)}?</h3>
        <div class="impact-unavailable">
          <strong>Candidate impact unavailable</strong>
          <p class="meta">${escapeHtml(
            (data.candidate && data.candidate.error) ||
            "Candidate impact could not be determined because the candidate profile is unavailable."
          )}</p>
        </div>
      `;
      return;
    }

    const impact = data.impact;
    const preview = classifyImpactPreview(data);
    let deltaBody = "";

    if (impact.closed_missing_functions.length) {
      const fn = impact.closed_missing_functions[0];
      const stage = impact.closed_workflow_stages[0] || "";
      const after = findStatus(data.after, fn);
      const memberLabel = after && after.member_ids && after.member_ids.length
        ? after.member_ids.map((id) => {
          if (id === data.candidate.candidate_id) return data.candidate.display_name;
          const member = lastMembersPayload.find((m) => m.member_id === id);
          return member ? member.display_name : id;
        }).join(", ")
        : data.candidate.display_name;
      deltaBody = `
        <div class="delta-card">
          <h3>Closes a current workflow gap</h3>
          <p class="stage"><strong>${escapeHtml(stage)}</strong></p>
          <p class="fn">${escapeHtml(fn)}</p>
          ${statusTransitionHtml("missing", "single_coverage", memberLabel)}
        </div>
      `;
    } else if (impact.strengthened_single_coverage_functions.length) {
      const fn = impact.strengthened_single_coverage_functions[0];
      const before = findStatus(data.before, fn);
      const stage = before ? before.workflow_stage : "";
      deltaBody = `
        <div class="delta-card">
          <h3>Strengthens a single-covered function</h3>
          <p class="stage"><strong>${escapeHtml(stage)}</strong></p>
          <p class="fn">${escapeHtml(fn)}</p>
          ${statusTransitionHtml("single_coverage", "represented")}
        </div>
      `;
    } else if (impact.added_additional_functions.length) {
      deltaBody = `
        <div class="delta-card">
          <h3>Adds an additional team function</h3>
          <p class="fn"><strong>${escapeHtml(impact.added_additional_functions[0])}</strong></p>
          <p class="meta">Required workflow coverage unchanged.</p>
        </div>
      `;
    } else if (impact.reinforced_represented_functions.length) {
      deltaBody = `
        <div class="delta-card">
          <h3>Reinforces an already represented function</h3>
          <p class="fn"><strong>${escapeHtml(impact.reinforced_represented_functions[0])}</strong></p>
        </div>
      `;
    } else if (impact.reinforced_additional_functions.length) {
      deltaBody = `
        <div class="delta-card">
          <h3>Reinforces an additional function</h3>
          <p class="fn"><strong>${escapeHtml(impact.reinforced_additional_functions[0])}</strong></p>
        </div>
      `;
    } else {
      deltaBody = `
        <div class="delta-card">
          <h3>${escapeHtml(preview.label)}</h3>
          <p class="meta">No required coverage state transition for this candidate.</p>
        </div>
      `;
    }

    const remaining = impact.remaining_missing_functions || [];
    const remainingHtml = remaining.length
      ? `<div class="remain-block"><strong>Workflow gaps that remain</strong><ul>${
        remaining.map((fn) => {
          const item = findStatus(data.after, fn);
          const stage = item ? item.workflow_stage : "";
          return `<li>${escapeHtml(stage)} · ${escapeHtml(fn)} · Missing</li>`;
        }).join("")
      }</ul></div>`
      : `<div class="remain-block"><strong>Remaining workflow gaps:</strong> None</div>`;

    const rows = (data.before.required_functions || []).map((beforeItem) => {
      const afterItem = findStatus(data.after, beforeItem.team_function);
      const changed = beforeItem.status !== (afterItem && afterItem.status);
      const afterMembers = afterItem && afterItem.member_ids
        ? afterItem.member_ids.map((id) => {
          if (data.candidate && id === data.candidate.candidate_id) return data.candidate.display_name;
          const member = lastMembersPayload.find((m) => m.member_id === id);
          return member ? member.display_name : id;
        }).join(", ")
        : "";
      const label = (status) => ({
        missing: "Missing",
        single_coverage: "Single",
        represented: "Represented",
      }[status] || status);
      return `
        <tr class="${changed ? "changed" : ""}">
          <td>${escapeHtml(beforeItem.workflow_stage)}</td>
          <td>${escapeHtml(label(beforeItem.status))}</td>
          <td>${escapeHtml(label(afterItem && afterItem.status))}${
            changed && afterMembers ? ` · ${escapeHtml(afterMembers)}` : ""
          }</td>
        </tr>
      `;
    }).join("");

    root.innerHTML = `
      <h3 class="impact-title">What changes if we add ${escapeHtml(name)}?</h3>
      ${deltaBody}
      ${remainingHtml}
      <details class="more-details">
        <summary>View Full Before / After</summary>
        <div class="ba-table-wrap">
          <table class="ba-table">
            <thead>
              <tr><th>Stage</th><th>Before</th><th>After</th></tr>
            </thead>
            <tbody>${rows}</tbody>
          </table>
        </div>
      </details>
    `;
  }

  async function loadImpactPreviews(candidates) {
    impactByCandidateId = {};
    const teamName = document.getElementById("team-name").value.trim() || "Team";
    const coverageProfile = document.getElementById("coverage-profile").value;
    const targetRole = document.getElementById("target-role").value.trim() || null;

    await Promise.all(candidates.map(async (candidate) => {
      try {
        const result = await apiPost("/api/v1/candidate-team-impact", {
          team_name: teamName,
          coverage_profile: coverageProfile,
          target_role: targetRole,
          members: lastMembersPayload,
          candidate,
        });
        impactByCandidateId[candidate.candidate_id] = result;
      } catch (_err) {
        impactByCandidateId[candidate.candidate_id] = {
          candidate: {
            candidate_id: candidate.candidate_id,
            display_name: candidate.display_name,
            profile_available: false,
            error: "Team impact unavailable",
          },
          impact: { impact_available: false },
          before: { required_functions: [] },
          after: { required_functions: [] },
        };
      }
    }));
  }

  async function analyzeTeam({ fromDemo = false } = {}) {
    setStatus(setupStatus, "");
    let members;
    let candidates;
    try {
      members = collectMembers();
      candidates = collectCandidates();
    } catch (err) {
      setStatus(setupStatus, err.message, "error");
      if (!fromDemo) openSetup();
      return;
    }

    lastMembersPayload = members;
    lastCandidatesPayload = candidates;
    impactByCandidateId = {};

    const teamName = document.getElementById("team-name").value.trim() || "Team";
    const coverageProfile = document.getElementById("coverage-profile").value;
    const targetRole = document.getElementById("target-role").value.trim() || null;

    applyAnalyzeBtn.disabled = true;
    document.getElementById("load-demo").disabled = true;
    document.getElementById("load-demo-empty").disabled = true;
    setStatus(setupStatus, "Analyzing team…", "loading");

    showWorkspaceShell();
    renderWorkspaceHeader(null, candidates.length);
    impactSection.hidden = true;
    document.getElementById("impact-content").innerHTML = "";
    setStatus(document.getElementById("team-map-status"), "Loading team map…", "loading");
    setStatus(document.getElementById("team-gap-status"), "Loading workflow coverage…", "loading");
    setStatus(document.getElementById("compare-status"), "", null);

    try {
      const [mapResult, gapResult] = await Promise.allSettled([
        apiPost("/api/v1/team-map", { team_name: teamName, members }),
        apiPost("/api/v1/team-gap", {
          team_name: teamName,
          coverage_profile: coverageProfile,
          members,
        }),
      ]);

      const teamMap = mapResult.status === "fulfilled" ? mapResult.value : null;
      const gap = gapResult.status === "fulfilled" ? gapResult.value : null;

      if (teamMap) {
        setStatus(document.getElementById("team-map-status"), "");
        renderTeamMap(teamMap);
      } else {
        setStatus(document.getElementById("team-map-status"), mapResult.reason.message, "error");
        document.getElementById("team-map-cards").innerHTML = `<p class="meta">Team map unavailable.</p>`;
      }

      if (gap) {
        setStatus(document.getElementById("team-gap-status"), "");
        renderWorkflowStrip(gap);
      } else {
        setStatus(document.getElementById("team-gap-status"), gapResult.reason.message, "error");
        document.getElementById("workflow-strip").innerHTML = `<p class="meta">Coverage unavailable.</p>`;
        document.getElementById("gap-priority").innerHTML = "";
      }

      renderWorkspaceHeader(teamMap, candidates.length);

      let compareData = null;
      if (candidates.length >= 2 && candidates.length <= 8) {
        setStatus(document.getElementById("compare-status"), "Comparing shortlist…", "loading");
        try {
          compareData = await apiPost("/api/v1/candidate-compare", {
            target_role: targetRole || "Role",
            candidates,
          });
          setStatus(document.getElementById("compare-status"), "Loading candidate impact previews…", "loading");
          await loadImpactPreviews(candidates);
          setStatus(document.getElementById("compare-status"), "");
          renderCompare(compareData);
        } catch (err) {
          setStatus(document.getElementById("compare-status"), err.message, "error");
          document.getElementById("compare-cards").innerHTML = `<p class="meta">Candidate compare unavailable.</p>`;
        }
      } else if (candidates.length === 1) {
        setStatus(document.getElementById("compare-status"), "Loading candidate impact preview…", "loading");
        await loadImpactPreviews(candidates);
        setStatus(
          document.getElementById("compare-status"),
          "Add a second shortlisted candidate for side-by-side compare. Impact preview is still available.",
        );
        renderCompare(null);
      } else {
        setStatus(document.getElementById("compare-status"), "No shortlisted candidates yet.");
        document.getElementById("compare-cards").innerHTML = `<p class="meta">Add candidates in Edit Team Data.</p>`;
      }

      analyzed = true;
      setStatus(setupStatus, "Team analysis complete.");
      closeSetup();
      document.getElementById("coverage-heading").scrollIntoView({ behavior: "smooth", block: "start" });
    } finally {
      applyAnalyzeBtn.disabled = false;
      document.getElementById("load-demo").disabled = false;
      document.getElementById("load-demo-empty").disabled = false;
    }
  }

  async function viewImpact(candidate) {
    impactSection.hidden = false;
    const status = document.getElementById("impact-status");
    const content = document.getElementById("impact-content");
    content.innerHTML = "";
    setStatus(status, `Loading impact for ${candidate.display_name}…`, "loading");

    let result = impactByCandidateId[candidate.candidate_id];
    if (!result || !result.impact) {
      const teamName = document.getElementById("team-name").value.trim() || "Team";
      const coverageProfile = document.getElementById("coverage-profile").value;
      const targetRole = document.getElementById("target-role").value.trim() || null;
      try {
        result = await apiPost("/api/v1/candidate-team-impact", {
          team_name: teamName,
          coverage_profile: coverageProfile,
          target_role: targetRole,
          members: lastMembersPayload,
          candidate,
        });
        impactByCandidateId[candidate.candidate_id] = result;
      } catch (err) {
        setStatus(status, err.message, "error");
        content.innerHTML = `<p class="meta">Impact request failed.</p>`;
        return;
      }
    }

    setStatus(status, "");
    renderImpactDetail(result);
    impactSection.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  async function loadDemoAndAnalyze() {
    activeWorkspaceId = null;
    updateSaveButtonLabel();
    setStatus(workspaceSaveStatus, "");
    fillDemoForms();
    setStatus(setupStatus, "Loading demo scenario…", "loading");
    await analyzeTeam({ fromDemo: true });
  }

  async function loadPlaces() {
    try {
      const response = await fetch("/api/v1/profile/places");
      if (!response.ok) return;
      const data = await response.json();
      if (!data || !Array.isArray(data.places)) return;
      placesList.innerHTML = data.places
        .map((place) => `<option value="${escapeHtml(place)}"></option>`)
        .join("");
    } catch (_err) {
      // Text input remains usable.
    }
  }

  document.getElementById("add-member").addEventListener("click", () => {
    membersList.appendChild(createMemberCard({
      member_id: `M${membersList.children.length + 1}`,
      current_role: "Engineer",
    }));
  });

  document.getElementById("add-candidate").addEventListener("click", () => {
    candidatesList.appendChild(createCandidateCard({
      candidate_id: `C${candidatesList.children.length + 1}`,
    }));
  });

  document.getElementById("setup-team").addEventListener("click", openSetup);
  document.getElementById("edit-team-data").addEventListener("click", openSetup);
  document.getElementById("load-demo-empty").addEventListener("click", loadDemoAndAnalyze);
  document.getElementById("load-demo").addEventListener("click", loadDemoAndAnalyze);
  document.getElementById("saved-workspaces").addEventListener("click", openWorkspacesPanel);
  document.getElementById("saved-workspaces-empty").addEventListener("click", openWorkspacesPanel);
  saveWorkspaceBtn.addEventListener("click", saveCurrentWorkspace);
  applyAnalyzeBtn.addEventListener("click", () => analyzeTeam());

  setupOverlay.querySelectorAll("[data-close-setup]").forEach((el) => {
    el.addEventListener("click", closeSetup);
  });
  workspacesOverlay.querySelectorAll("[data-close-workspaces]").forEach((el) => {
    el.addEventListener("click", closeWorkspacesPanel);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    if (!setupOverlay.hidden) closeSetup();
    if (!workspacesOverlay.hidden) closeWorkspacesPanel();
  });

  // Keep one blank member ready inside the secondary intake layer.
  membersList.appendChild(createMemberCard({
    member_id: "A",
    display_name: "",
    current_role: "Engineer",
  }));
  updateSaveButtonLabel();
  loadPlaces();
})();
