(() => {
  "use strict";

  const membersList = document.getElementById("members-list");
  const candidatesList = document.getElementById("candidates-list");
  const placesList = document.getElementById("places-list");
  const setupStatus = document.getElementById("setup-status");
  const analyzeBtn = document.getElementById("analyze-team");
  const loadDemoBtn = document.getElementById("load-demo");

  const teamMapSection = document.getElementById("team-map-section");
  const compareSection = document.getElementById("compare-section");
  const impactSection = document.getElementById("impact-section");

  let memberSeq = 1;
  let candidateSeq = 1;
  let lastMembersPayload = [];
  let lastCandidatesPayload = [];

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
    el.textContent = message || "";
    el.classList.remove("error", "loading");
    if (kind) el.classList.add(kind);
  }

  function emptyState(message) {
    return `<p class="gap-empty">${escapeHtml(message)}</p>`;
  }

  function listBlock(title, items) {
    if (!items || !items.length) return "";
    const lis = items.map((item) => `<li>${escapeHtml(item)}</li>`).join("");
    return `<div class="field-block"><h5>${escapeHtml(title)}</h5><ul>${lis}</ul></div>`;
  }

  function textBlock(title, text) {
    if (!text) return "";
    return `<div class="field-block"><h5>${escapeHtml(title)}</h5><p>${escapeHtml(text)}</p></div>`;
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

  function createMemberCard(data = {}) {
    const id = `member-${memberSeq++}`;
    const card = document.createElement("article");
    card.className = "person-card";
    card.dataset.kind = "member";
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
    card.dataset.uid = id;
    return card;
  }

  function createCandidateCard(data = {}) {
    const id = `candidate-${candidateSeq++}`;
    const card = document.createElement("article");
    card.className = "person-card";
    card.dataset.kind = "candidate";
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
    card.dataset.uid = id;
    return card;
  }

  function readPersonFields(card) {
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
      const raw = readPersonFields(card);
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
      const raw = readPersonFields(card);
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

  async function apiPost(path, body) {
    const response = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(body),
    });
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

  function renderTeamMap(data) {
    const root = document.getElementById("team-map-cards");
    if (!data || !data.members || !data.members.length) {
      root.innerHTML = emptyState("No team members returned.");
      return;
    }
    root.innerHTML = data.members.map((member) => {
      if (!member.profile_available) {
        return `
          <article class="profile-card unavailable">
            <h4>${escapeHtml(member.display_name)}</h4>
            <p class="meta">${escapeHtml(member.current_role || "—")}</p>
            <p class="function-tag">Profile unavailable</p>
            <p class="why">${escapeHtml(member.error || "No profile could be produced for this member.")}</p>
          </article>
        `;
      }
      return `
        <article class="profile-card">
          <h4>${escapeHtml(member.display_name)}</h4>
          <p class="meta">${escapeHtml(member.current_role || "—")}</p>
          <div class="function-tag">${escapeHtml(member.team_function || "—")}</div>
          ${textBlock("Thinking Style", member.thinking_style)}
          ${listBlock("Top Skills", member.top_skills)}
          ${listBlock("Key Risks", member.key_risks)}
          ${textBlock("Team Contribution", member.team_contribution)}
        </article>
      `;
    }).join("");
  }

  function renderCoverage(gap) {
    const root = document.getElementById("workflow-coverage");
    const summary = document.getElementById("gap-summary");
    if (!gap || !gap.required_functions) {
      root.innerHTML = emptyState("Coverage data unavailable.");
      summary.innerHTML = "";
      return;
    }

    root.innerHTML = gap.required_functions.map((item) => `
      <article class="coverage-card">
        <h4>${escapeHtml(item.workflow_stage)}</h4>
        <p class="fn">${escapeHtml(item.team_function)}</p>
        ${statusChip(item.status)}
        <p class="count-line">${item.count} profiled member${item.count === 1 ? "" : "s"}${
          item.member_ids && item.member_ids.length
            ? ` · ${escapeHtml(item.member_ids.join(", "))}`
            : ""
        }</p>
        <p class="why">${escapeHtml(item.why_it_matters)}</p>
      </article>
    `).join("");

    const missing = gap.required_functions.filter((item) => item.status === "missing");
    if (!missing.length) {
      summary.innerHTML = `<p class="gap-empty">No required workflow functions are currently missing for this coverage profile.</p>`;
      return;
    }

    summary.innerHTML = `
      <div class="gap-summary">
        <p class="meta">Current Workflow Gaps</p>
        ${missing.map((item) => `
          <article class="gap-card">
            <h4>${escapeHtml(item.workflow_stage)}</h4>
            <p class="fn">${escapeHtml(item.team_function)}</p>
            ${statusChip("missing")}
            <p class="why">${escapeHtml(item.why_it_matters)}</p>
          </article>
        `).join("")}
      </div>
    `;
  }

  function renderCompare(data) {
    const root = document.getElementById("compare-cards");
    if (!data || !data.candidates || !data.candidates.length) {
      root.innerHTML = emptyState("No candidates to compare.");
      return;
    }
    root.innerHTML = data.candidates.map((candidate) => {
      if (!candidate.profile_available) {
        return `
          <article class="compare-card unavailable">
            <h4>${escapeHtml(candidate.display_name)}</h4>
            <p class="function-tag">Profile unavailable</p>
            <p class="why">${escapeHtml(candidate.error || "Profile could not be produced.")}</p>
          </article>
        `;
      }
      return `
        <article class="compare-card">
          <h4>${escapeHtml(candidate.display_name)}</h4>
          <div class="function-tag">${escapeHtml(candidate.team_function || "—")}</div>
          ${textBlock("Thinking Style", candidate.thinking_style)}
          ${listBlock("Top Skills", candidate.top_skills)}
          ${listBlock("Key Risks", candidate.key_risks)}
          ${textBlock("Team Contribution", candidate.team_contribution)}
          ${listBlock("Role Directions", candidate.role_directions)}
          <div class="actions">
            <button
              type="button"
              class="btn btn-primary view-impact"
              data-candidate-id="${escapeHtml(candidate.candidate_id)}"
            >View Team Impact</button>
          </div>
        </article>
      `;
    }).join("");

    root.querySelectorAll(".view-impact").forEach((btn) => {
      btn.addEventListener("click", () => {
        const candidateId = btn.getAttribute("data-candidate-id");
        const candidate = lastCandidatesPayload.find((item) => item.candidate_id === candidateId);
        if (candidate) viewImpact(candidate);
      });
    });
  }

  function renderSnapshotColumn(title, snapshot) {
    const rows = (snapshot.required_functions || []).map((item) => {
      const members = item.member_ids && item.member_ids.length
        ? `<span class="meta"> · ${escapeHtml(item.member_ids.join(", "))}</span>`
        : "";
      return `
        <div class="stage-row">
          <div class="stage-name">${escapeHtml(item.workflow_stage)}</div>
          <div class="meta">${escapeHtml(item.team_function)}</div>
          <div>${statusChip(item.status)}${members}</div>
        </div>
      `;
    }).join("");
    return `
      <div class="ba-column">
        <h3>${escapeHtml(title)}</h3>
        ${rows || emptyState("No coverage data.")}
      </div>
    `;
  }

  function impactBlock(title, items) {
    if (!items || !items.length) return "";
    return `
      <article class="impact-summary-card">
        <h4>${escapeHtml(title)}</h4>
        <ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
      </article>
    `;
  }

  function renderImpact(data) {
    const root = document.getElementById("impact-content");
    const name = data.candidate && data.candidate.display_name
      ? data.candidate.display_name
      : "this candidate";

    if (!data.impact || !data.impact.impact_available) {
      root.innerHTML = `
        <h3 class="impact-title">What changes if we add ${escapeHtml(name)}?</h3>
        <div class="impact-unavailable">
          <strong>Candidate impact unavailable</strong>
          <p class="why">${escapeHtml(
            (data.candidate && data.candidate.error) ||
            "Candidate impact could not be determined because the candidate profile is unavailable."
          )}</p>
        </div>
      `;
      return;
    }

    const impact = data.impact;
    root.innerHTML = `
      <h3 class="impact-title">What changes if we add ${escapeHtml(name)}?</h3>
      <div class="before-after">
        ${renderSnapshotColumn("Before", data.before)}
        <div class="ba-arrow" aria-hidden="true">→</div>
        ${renderSnapshotColumn("After", data.after)}
      </div>
      <h3 class="section-label">Impact Summary</h3>
      <div class="impact-blocks">
        ${impactBlock("Closes a current workflow gap", impact.closed_missing_functions)}
        ${impactBlock("Closed workflow stages", impact.closed_workflow_stages)}
        ${impactBlock("Strengthens a single-covered function", impact.strengthened_single_coverage_functions)}
        ${impactBlock("Reinforces an already represented function", impact.reinforced_represented_functions)}
        ${impactBlock("Adds an additional team function", impact.added_additional_functions)}
        ${impactBlock("Reinforces an additional function", impact.reinforced_additional_functions)}
        ${impactBlock("Workflow gaps that remain", impact.remaining_missing_functions)}
        ${impactBlock("Workflow stages that remain uncovered", impact.remaining_uncovered_workflow_stages)}
      </div>
    `;
  }

  function loadDemo() {
    document.getElementById("team-name").value = DEMO.teamName;
    document.getElementById("coverage-profile").value = DEMO.coverageProfile;
    document.getElementById("target-role").value = DEMO.targetRole;
    membersList.innerHTML = "";
    candidatesList.innerHTML = "";
    DEMO.members.forEach((member) => membersList.appendChild(createMemberCard(member)));
    DEMO.candidates.forEach((candidate) => candidatesList.appendChild(createCandidateCard(candidate)));
    setStatus(setupStatus, "Demo scenario loaded. Click Analyze Team to continue.");
    teamMapSection.hidden = true;
    compareSection.hidden = true;
    impactSection.hidden = true;
  }

  async function analyzeTeam() {
    setStatus(setupStatus, "");
    let members;
    let candidates;
    try {
      members = collectMembers();
      candidates = collectCandidates();
    } catch (err) {
      setStatus(setupStatus, err.message, "error");
      return;
    }

    lastMembersPayload = members;
    lastCandidatesPayload = candidates;

    const teamName = document.getElementById("team-name").value.trim() || "Team";
    const coverageProfile = document.getElementById("coverage-profile").value;
    const targetRole = document.getElementById("target-role").value.trim() || null;

    analyzeBtn.disabled = true;
    loadDemoBtn.disabled = true;
    setStatus(setupStatus, "Analyzing team…", "loading");

    teamMapSection.hidden = false;
    compareSection.hidden = false;
    impactSection.hidden = true;
    document.getElementById("team-map-cards").innerHTML = "";
    document.getElementById("workflow-coverage").innerHTML = "";
    document.getElementById("gap-summary").innerHTML = "";
    document.getElementById("compare-cards").innerHTML = "";
    setStatus(document.getElementById("team-map-status"), "Loading team map…", "loading");
    setStatus(document.getElementById("team-gap-status"), "Loading workflow coverage…", "loading");
    setStatus(document.getElementById("compare-status"), "", null);

    const teamBody = {
      team_name: teamName,
      members,
    };
    const gapBody = {
      team_name: teamName,
      coverage_profile: coverageProfile,
      members,
    };

    try {
      const [mapResult, gapResult] = await Promise.allSettled([
        apiPost("/api/v1/team-map", teamBody),
        apiPost("/api/v1/team-gap", gapBody),
      ]);

      if (mapResult.status === "fulfilled") {
        setStatus(document.getElementById("team-map-status"), "");
        renderTeamMap(mapResult.value);
      } else {
        setStatus(document.getElementById("team-map-status"), mapResult.reason.message, "error");
        document.getElementById("team-map-cards").innerHTML = emptyState("Team map unavailable.");
      }

      if (gapResult.status === "fulfilled") {
        setStatus(document.getElementById("team-gap-status"), "");
        renderCoverage(gapResult.value);
      } else {
        setStatus(document.getElementById("team-gap-status"), gapResult.reason.message, "error");
        document.getElementById("workflow-coverage").innerHTML = emptyState("Coverage unavailable.");
        document.getElementById("gap-summary").innerHTML = "";
      }

      if (candidates.length >= 2 && candidates.length <= 8) {
        setStatus(document.getElementById("compare-status"), "Comparing shortlist…", "loading");
        try {
          const compare = await apiPost("/api/v1/candidate-compare", {
            target_role: targetRole || "Role",
            candidates,
          });
          setStatus(document.getElementById("compare-status"), "");
          renderCompare(compare);
        } catch (err) {
          setStatus(document.getElementById("compare-status"), err.message, "error");
          document.getElementById("compare-cards").innerHTML = emptyState("Candidate compare unavailable.");
        }
      } else if (candidates.length === 1) {
        setStatus(
          document.getElementById("compare-status"),
          "Add at least two shortlisted candidates to run Candidate Compare. You can still view team impact for a single candidate after analysis.",
        );
        const only = candidates[0];
        document.getElementById("compare-cards").innerHTML = `
          <article class="compare-card">
            <h4>${escapeHtml(only.display_name)}</h4>
            <p class="meta">Single shortlist candidate</p>
            <div class="actions">
              <button type="button" class="btn btn-primary" id="single-impact">View Team Impact</button>
            </div>
          </article>
        `;
        document.getElementById("single-impact").addEventListener("click", () => viewImpact(only));
      } else {
        setStatus(document.getElementById("compare-status"), "No shortlisted candidates yet.");
        document.getElementById("compare-cards").innerHTML = emptyState("Add candidates to compare.");
      }

      setStatus(setupStatus, "Team analysis complete.");
      teamMapSection.scrollIntoView({ behavior: "smooth", block: "start" });
    } finally {
      analyzeBtn.disabled = false;
      loadDemoBtn.disabled = false;
    }
  }

  async function viewImpact(candidate) {
    impactSection.hidden = false;
    const status = document.getElementById("impact-status");
    const content = document.getElementById("impact-content");
    content.innerHTML = "";
    setStatus(status, `Loading impact for ${candidate.display_name}…`, "loading");

    const teamName = document.getElementById("team-name").value.trim() || "Team";
    const coverageProfile = document.getElementById("coverage-profile").value;
    const targetRole = document.getElementById("target-role").value.trim() || null;

    analyzeBtn.disabled = true;
    try {
      const result = await apiPost("/api/v1/candidate-team-impact", {
        team_name: teamName,
        coverage_profile: coverageProfile,
        target_role: targetRole,
        members: lastMembersPayload,
        candidate,
      });
      setStatus(status, "");
      renderImpact(result);
      impactSection.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (err) {
      setStatus(status, err.message, "error");
      content.innerHTML = emptyState("Impact request failed.");
    } finally {
      analyzeBtn.disabled = false;
    }
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
      // Text input remains usable without suggestions.
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

  loadDemoBtn.addEventListener("click", loadDemo);
  analyzeBtn.addEventListener("click", analyzeTeam);

  membersList.appendChild(createMemberCard({
    member_id: "A",
    display_name: "",
    current_role: "Engineer",
  }));
  loadPlaces();
})();
