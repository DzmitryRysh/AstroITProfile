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
  const selfProfile = document.getElementById("self-profile");
  const selfProfileContent = document.getElementById("self-profile-content");
  const selfProfileStatus = document.getElementById("self-profile-status");
  const selfOverlay = document.getElementById("self-overlay");
  const selfDrawer = document.getElementById("self-drawer");
  const selfSetupStatus = document.getElementById("self-setup-status");
  const brandTitle = document.querySelector(".brand-title");
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
  const DEFAULT_BRAND_TITLE = "Team Intelligence";
  const SELF_BRAND_TITLE = "Your Mercury Profile";

  /** Presentation-only: named entry → person profile; empty name → self. */
  const PERSON_SECTION_TITLES = {
    thinking: "Thinking style",
    communication: "Communication style",
    learning: "Learning style",
    memory_focus: "Memory & focus",
    work_application: "Work-related patterns",
    context_risks: "Context & watch-outs",
  };

  const SELF_SECTION_TITLES = {
    thinking: "How you think",
    communication: "How you communicate",
    learning: "How you learn",
    memory_focus: "Memory & focus",
    work_application: "How it can show up in work",
    context_risks: "Context & watch-outs",
  };

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

  function setBrandTitleMode(mode) {
    if (!brandTitle) return;
    brandTitle.textContent = mode === "self" ? SELF_BRAND_TITLE : DEFAULT_BRAND_TITLE;
  }

  function resolveProfileAudience(displayName) {
    return String(displayName || "").trim() ? "person" : "self";
  }

  function possessiveLabel(name) {
    const trimmed = String(name || "").trim();
    if (!trimmed) return "";
    return /s$/i.test(trimmed) ? `${trimmed}'` : `${trimmed}'s`;
  }

  function profileHeaderTitle(audience, displayName) {
    if (audience === "person") {
      const name = String(displayName || "").trim();
      return name ? `${possessiveLabel(name)} Mercury Profile` : "Mercury Profile";
    }
    return SELF_BRAND_TITLE;
  }

  function setBrandTitleForProfile(audience, displayName) {
    if (!brandTitle) return;
    brandTitle.textContent = profileHeaderTitle(audience, displayName);
  }

  function sectionDisplayTitle(section, audience) {
    const map = audience === "person" ? PERSON_SECTION_TITLES : SELF_SECTION_TITLES;
    if (section && section.key && map[section.key]) return map[section.key];
    return (section && section.title) || "";
  }

  function humanFactorLabelFromSource(sourceKey) {
    const [type, ...rest] = String(sourceKey || "").split(":");
    const key = rest.join(":");
    if (type && key) return factorCardTitle(type, key);
    return provenanceLabel(sourceKey);
  }

  function recurringPatternsExplanation(audience, displayName, count) {
    const n = Number(count) || 0;
    const themeWord = n === 1 ? "recurring theme" : "recurring themes";
    let subjectTail;
    if (audience === "person") {
      const name = String(displayName || "").trim();
      if (name) {
        subjectTail = `${possessiveLabel(name)} profile`;
      } else {
        subjectTail = "this profile";
      }
    } else {
      subjectTail = "your profile";
    }
    return `We found ${n} ${themeWord} supported independently by at least two parts of ${subjectTail}:`;
  }

  function recurringPatternsEmptyCopy(audience) {
    const subject = audience === "person"
      ? "This profile is more distributed across individual themes."
      : "Your profile is more distributed across individual themes.";
    return `No repeated pattern stands out across multiple Mercury factors. ${subject}`;
  }

  function tensionsHeading(audience) {
    return audience === "person" ? "Tensions in this profile" : "Tensions in your profile";
  }

  function tensionsExplanation(count) {
    const n = Number(count) || 0;
    const tensionWord = n === 1 ? "tension" : "tensions";
    return `Different parts of this profile can pull in different directions. AstroIT keeps both signals instead of choosing a winner. We found ${n} ${tensionWord}:`;
  }

  function showWorkspaceShell() {
    emptyState.hidden = true;
    if (selfProfile) selfProfile.hidden = true;
    workspace.hidden = false;
    headerActions.hidden = false;
    workspaceContext.hidden = false;
    setBrandTitleMode("team");
  }

  function showEmptyShell() {
    if (selfProfile) selfProfile.hidden = true;
    workspace.hidden = true;
    headerActions.hidden = true;
    workspaceContext.hidden = true;
    emptyState.hidden = false;
    setBrandTitleMode("team");
  }

  function showSelfProfileShell() {
    emptyState.hidden = true;
    workspace.hidden = true;
    headerActions.hidden = true;
    workspaceContext.hidden = true;
    selfProfile.hidden = false;
    setBrandTitleMode("self");
  }

  const SELF_DEMOS = {
    avdey: {
      display_name: "Avdey",
      birth_date: "1986-07-14",
      birth_time: "07:10",
      birth_place: "Simferopol, Ukraine",
    },
    vlad: {
      display_name: "Vlad",
      birth_date: "1986-05-16",
      birth_time: "15:00",
      birth_place: "Dnipro, Ukraine",
    },
    dzmitry: {
      display_name: "Dzmitry",
      birth_date: "1985-11-12",
      birth_time: "14:15",
      birth_place: "Zhodino, Belarus",
    },
  };

  const CATEGORY_LABELS = {
    thinking: "Thinking",
    communication: "Communication",
    learning: "Learning",
    strength: "Strengths / Potential",
    risk: "Risks / Possible Difficulties",
    work_application: "Work / Application",
    environment: "Environment / Mobility",
    mobility: "Environment / Mobility",
    compensation: "Compensation (source material / detail)",
    secondary_gain: "Secondary Gain (source material / detail)",
    source_specific: "Source-Specific Claims",
    focus: "Focus",
    memory: "Memory",
  };

  const CATEGORY_ORDER = [
    "thinking",
    "communication",
    "learning",
    "strength",
    "risk",
    "work_application",
    "environment",
    "mobility",
    "compensation",
    "secondary_gain",
    "focus",
    "memory",
  ];

  function openSelfDrawer() {
    selfOverlay.hidden = false;
    selfDrawer.hidden = false;
    document.body.style.overflow = "hidden";
    const first = selfDrawer.querySelector("input, button");
    if (first) first.focus();
  }

  function closeSelfDrawer() {
    selfOverlay.hidden = true;
    selfDrawer.hidden = true;
    document.body.style.overflow = "";
  }

  function fillSelfDemo(key) {
    const demo = SELF_DEMOS[key];
    if (!demo) return;
    document.getElementById("self-name").value = demo.display_name;
    document.getElementById("self-birth-date").value = demo.birth_date;
    document.getElementById("self-birth-time").value = demo.birth_time;
    document.getElementById("self-birth-place").value = demo.birth_place;
    setStatus(selfSetupStatus, `Filled ${demo.display_name}. Click Build My Profile to call the API.`);
  }

  function titleCaseSignal(value) {
    return String(value || "")
      .split("_")
      .filter(Boolean)
      .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
      .join(" ");
  }

  function categoryLabel(category) {
    if (CATEGORY_LABELS[category]) return CATEGORY_LABELS[category];
    return titleCaseSignal(category);
  }

  function aspectPhrase(type, planet) {
    const map = {
      conjunction: "conjunct",
      opposition: "opposite",
      square: "square",
      trine: "trine",
      sextile: "sextile",
    };
    return map[String(type || "").toLowerCase()] || String(type || "");
  }

  function factorCardTitle(factorType, factorKey) {
    if (factorType === "sign") return `Mercury in ${factorKey}`;
    if (factorType === "house") return `Mercury in House ${factorKey}`;
    if (factorType === "motion") {
      if (String(factorKey).toLowerCase() === "retrograde") return "Retrograde Mercury";
      if (String(factorKey).toLowerCase() === "direct") return "Direct Mercury";
      return `Mercury ${titleCaseSignal(factorKey)}`;
    }
    if (factorType === "aspect") {
      const [type, ...rest] = String(factorKey).split("_");
      const planet = rest.join("_");
      return `Mercury ${aspectPhrase(type, planet)} ${planet}`;
    }
    return `${factorType}:${factorKey}`;
  }

  function formatOrb(orb) {
    if (orb == null || Number.isNaN(Number(orb))) return "";
    return `${Number(orb).toFixed(2)}°`;
  }

  function formatAspectChip(aspect) {
    const type = titleCaseSignal(aspect.type);
    const orb = formatOrb(aspect.orb_deg);
    return orb ? `${type} ${aspect.planet} · ${orb}` : `${type} ${aspect.planet}`;
  }

  function provenanceLabel(sourceKey) {
    const [type, ...rest] = String(sourceKey).split(":");
    const key = rest.join(":");
    if (type === "sign") return key;
    if (type === "house") return `House ${key}`;
    if (type === "motion") return titleCaseSignal(key);
    if (type === "aspect") {
      const [aspectType, ...planetParts] = key.split("_");
      return `${titleCaseSignal(aspectType)} ${planetParts.join("_")}`;
    }
    return sourceKey;
  }

  function compactProvenanceLabel(sourceKey) {
    const [type, ...rest] = String(sourceKey).split(":");
    const key = rest.join(":");
    if (type === "sign") return key;
    if (type === "house") return `House ${key}`;
    if (type === "motion") return titleCaseSignal(key);
    if (type === "aspect") {
      const parts = key.split("_");
      return parts.slice(1).join("_") || key;
    }
    return provenanceLabel(sourceKey);
  }

  function collectFactsByFactor(profile) {
    const calc = profile.calculated || {};
    const layers = [];

    if (calc.mercury_sign) {
      const signFacts = profile.sign_facts || [];
      layers.push({
        factor_type: "sign",
        factor_key: calc.mercury_sign,
        facts: signFacts,
        supported: signFacts.length > 0,
      });
    }

    if (calc.birth_time_known && calc.mercury_house != null && calc.mercury_house !== "") {
      const houseFacts = profile.house_facts || [];
      layers.push({
        factor_type: "house",
        factor_key: String(calc.mercury_house),
        facts: houseFacts,
        supported: houseFacts.length > 0,
      });
    }

    const motion = calc.mercury_motion ? String(calc.mercury_motion) : "";
    // Direct is the neutral calculated default — not an unsupported source pack.
    if (motion && motion.toLowerCase() !== "direct") {
      const motionFacts = profile.motion_facts || [];
      layers.push({
        factor_type: "motion",
        factor_key: motion,
        facts: motionFacts,
        supported: motionFacts.length > 0,
      });
    }

    const aspectFacts = profile.aspect_facts || [];
    const byKey = new Map();
    aspectFacts.forEach((fact) => {
      if (!byKey.has(fact.factor_key)) byKey.set(fact.factor_key, []);
      byKey.get(fact.factor_key).push(fact);
    });

    (calc.aspects || []).forEach((aspect) => {
      const key = `${aspect.type}_${aspect.planet}`;
      const facts = byKey.get(key) || [];
      layers.push({
        factor_type: "aspect",
        factor_key: key,
        facts,
        supported: facts.length > 0,
      });
    });

    return layers;
  }

  function countActiveSourceFacts(profile) {
    return [
      ...(profile.sign_facts || []),
      ...(profile.house_facts || []),
      ...(profile.motion_facts || []),
      ...(profile.aspect_facts || []),
    ].length;
  }

  function renderFactItem(fact) {
    const isRisk = fact.polarity === "risk" || fact.category === "risk";
    const nonDiagnostic = /non-diagnostic|not a medical conclusion/i.test(fact.text || "");
    const marker = isRisk
      ? `<span class="risk-mark" title="Possible difficulty">Risk</span>`
      : `<span class="fact-bullet" aria-hidden="true">•</span>`;
    const badge = nonDiagnostic
      ? `<span class="fact-note">Source wording — non-diagnostic</span>`
      : "";
    return `<li class="fact-item${isRisk ? " fact-risk" : ""}">${marker}<span class="fact-text">${escapeHtml(fact.text)}</span>${badge}</li>`;
  }

  function renderFactGroups(facts) {
    const sourceSpecific = facts.filter((f) => f.category === "source_specific");
    const compensation = facts.filter((f) => f.category === "compensation");
    const regular = facts.filter(
      (f) => f.category !== "source_specific" && f.category !== "compensation"
    );
    const byCategory = new Map();
    regular.forEach((fact) => {
      const key = fact.category || "other";
      if (!byCategory.has(key)) byCategory.set(key, []);
      byCategory.get(key).push(fact);
    });

    const ordered = [
      ...CATEGORY_ORDER.filter((key) => byCategory.has(key)),
      ...[...byCategory.keys()].filter((key) => !CATEGORY_ORDER.includes(key)),
    ];

    const groups = ordered.map((key) => {
      const items = byCategory.get(key) || [];
      const heading = key === "risk" ? "Risks / Possible Difficulties" : categoryLabel(key);
      return `<div class="fact-group">
        <h4>${escapeHtml(heading)}</h4>
        <ul class="fact-list">${items.map(renderFactItem).join("")}</ul>
      </div>`;
    }).join("");

    let compensationBlock = "";
    if (compensation.length) {
      compensationBlock = `<details class="source-specific-block compensation-detail-block">
        <summary>Compensation (source material / detail) <span class="factor-summary-meta">${compensation.length}</span></summary>
        <div class="source-specific-body">
          <p class="source-specific-note">Source material from the framework — not treated as an automatically active personality trait.</p>
          <ul class="fact-list">${compensation.map(renderFactItem).join("")}</ul>
        </div>
      </details>`;
    }

    let sourceBlock = "";
    if (sourceSpecific.length) {
      sourceBlock = `<details class="source-specific-block">
        <summary>Source-Specific Claims <span class="factor-summary-meta">${sourceSpecific.length}</span></summary>
        <div class="source-specific-body">
          <p class="source-specific-note">Shown because this wording exists in the source framework; it is not treated as a scientifically validated professional ability.</p>
          <ul class="fact-list">${sourceSpecific.map(renderFactItem).join("")}</ul>
        </div>
      </details>`;
    }

    return `${groups}${compensationBlock}${sourceBlock}`;
  }

  function synthesisFactMap(synthesis) {
    const map = new Map();
    const byId = (synthesis && synthesis.facts_by_id) || {};
    Object.keys(byId).forEach((id) => map.set(id, byId[id]));
    return map;
  }

  function renderPreviewFactItem(fact) {
    if (!fact) return "";
    const isRisk = fact.polarity === "risk";
    const marker = isRisk
      ? `<span class="risk-mark" title="Possible difficulty">Risk</span>`
      : `<span class="fact-bullet" aria-hidden="true">•</span>`;
    const provenance = compactProvenanceLabel(`${fact.factor_type}:${fact.factor_key}`);
    return `<li class="fact-item${isRisk ? " fact-risk" : ""}">${marker}<span class="fact-text">${escapeHtml(fact.text)}<span class="fact-provenance">${escapeHtml(provenance)}</span></span></li>`;
  }

  function renderStrongestPatterns(synthesis, audience, displayName) {
    const patterns = (synthesis && synthesis.strongest_patterns) || [];
    if (!patterns.length) {
      return `<section class="panel synthesis-patterns level-1">
        <div class="panel-head"><h2>Key recurring patterns</h2></div>
        <p class="section-helper patterns-empty">${escapeHtml(recurringPatternsEmptyCopy(audience))}</p>
      </section>`;
    }
    const intro = `<p class="section-helper">${escapeHtml(recurringPatternsExplanation(audience, displayName, patterns.length))}</p>`;
    const rows = patterns.map((signal) => {
      const count = Number(signal.source_count) || (signal.sources || []).length || 0;
      const supportLabel = count === 1
        ? "Supported by 1 profile factor"
        : `Supported by ${count} profile factors`;
      const whyItems = (signal.sources || [])
        .map((src) => `<li>${escapeHtml(humanFactorLabelFromSource(src))}</li>`)
        .join("");
      return `<article class="signal-row">
        <div class="signal-row-main">
          <strong class="signal-label">${escapeHtml(titleCaseSignal(signal.signal))}</strong>
          <span class="signal-meta">${escapeHtml(supportLabel)}</span>
        </div>
        <details class="signal-why">
          <summary>Why this appears</summary>
          <div class="signal-why-body">
            <p class="signal-why-label">Supported by:</p>
            <ul class="signal-why-list">${whyItems}</ul>
          </div>
        </details>
      </article>`;
    }).join("");
    return `<section class="panel synthesis-patterns level-1">
      <div class="panel-head"><h2>Key recurring patterns</h2></div>
      ${intro}
      <div class="result-list-group">${rows}</div>
    </section>`;
  }

  function renderGroupedFactItem(fact) {
    if (!fact) return "";
    const isRisk = fact.polarity === "risk";
    const marker = isRisk
      ? `<span class="risk-mark" title="Possible difficulty">Risk</span>`
      : `<span class="fact-bullet" aria-hidden="true">•</span>`;
    // Factor heading already establishes provenance — do not repeat it on every row.
    return `<li class="fact-item${isRisk ? " fact-risk" : ""}">${marker}<span class="fact-text">${escapeHtml(fact.text)}</span></li>`;
  }

  function factorTypeRank(factorType) {
    const order = { sign: 0, house: 1, motion: 2, aspect: 3 };
    return Object.prototype.hasOwnProperty.call(order, factorType) ? order[factorType] : 99;
  }

  function groupSectionFactsByFactor(section, facts) {
    const groups = new Map();
    const firstIndex = new Map();
    (section.resolved_fact_ids || []).forEach((id, index) => {
      const fact = facts.get(id);
      if (!fact) return;
      const key = `${fact.factor_type}:${fact.factor_key}`;
      if (!groups.has(key)) {
        groups.set(key, {
          factor_type: fact.factor_type,
          factor_key: fact.factor_key,
          facts: [],
        });
        firstIndex.set(key, index);
      }
      groups.get(key).facts.push(fact);
    });
    return [...groups.keys()]
      .sort((a, b) => {
        const groupA = groups.get(a);
        const groupB = groups.get(b);
        const rankDiff = factorTypeRank(groupA.factor_type) - factorTypeRank(groupB.factor_type);
        if (rankDiff !== 0) return rankDiff;
        return firstIndex.get(a) - firstIndex.get(b);
      })
      .map((key) => groups.get(key));
  }

  function renderSectionFactorExplore(section, facts) {
    const groups = groupSectionFactsByFactor(section, facts);
    if (!groups.length) return "";
    const rows = groups.map((group) => {
      const label = factorCardTitle(group.factor_type, group.factor_key);
      const n = group.facts.length;
      const countLabel = n === 1 ? "1 observation" : `${n} observations`;
      const items = group.facts.map(renderGroupedFactItem).filter(Boolean).join("");
      return `<details class="section-factor-group">
        <summary>
          <span class="section-factor-label">${escapeHtml(label)}</span>
          <span class="section-factor-meta">
            <span class="factor-summary-meta">${escapeHtml(countLabel)}</span>
            <span class="section-factor-chevron" aria-hidden="true"></span>
          </span>
        </summary>
        <ul class="fact-list section-factor-facts">${items}</ul>
      </details>`;
    }).join("");
    return `<div class="section-factor-explore">
      <p class="section-factor-explore-label">Profile factors behind this section</p>
      ${rows}
    </div>`;
  }

  function renderSectionBody(section, facts) {
    const previewIds = section.preview_fact_ids || [];
    const previewItems = previewIds
      .map((id) => renderPreviewFactItem(facts.get(id)))
      .filter(Boolean)
      .join("");
    const total = Number(section.resolved_fact_count) || (section.resolved_fact_ids || []).length;
    const evidence = `${total} source-backed observations across ${section.factor_count} factor${section.factor_count === 1 ? "" : "s"}`;
    const hasMore = total > previewIds.length;
    const exploreLabel = total === 1
      ? "Explore all 1 observation"
      : `Explore all ${total} observations`;
    // Preferred model: when open, CSS hides preview so factor groups can list ALL
    // section facts without duplicate visible IDs. Collapse control sits after the groups.
    const explore = hasMore
      ? `<details class="section-explore">
          <summary class="section-explore-summary">
            <span class="explore-all-label">${escapeHtml(exploreLabel)}</span>
          </summary>
          ${renderSectionFactorExplore(section, facts)}
          <button type="button" class="section-show-less" onclick="this.closest('details.section-explore').open=false">Show less</button>
        </details>`
      : "";
    return `<div class="section-body">
      <p class="section-evidence-meta">${escapeHtml(evidence)}</p>
      <ul class="fact-list section-preview">${previewItems}</ul>
      ${explore}
    </div>`;
  }

  function renderSynthesisSections(synthesis, audience) {
    if (!synthesis || !synthesis.sections) return "";
    const facts = synthesisFactMap(synthesis);
    return (synthesis.sections || []).map((section) => {
      if (!section.resolved_fact_count) return "";
      // Watch-outs render separately as a secondary collapsed block.
      if (section.key === "context_risks") return "";
      const title = sectionDisplayTitle(section, audience);
      return `<section class="panel synthesis-section level-1" data-section-key="${escapeHtml(section.key)}">
        <div class="panel-head"><h2>${escapeHtml(title)}</h2></div>
        ${renderSectionBody(section, facts)}
      </section>`;
    }).join("");
  }

  function renderContextWatchOuts(synthesis, audience) {
    if (!synthesis || !synthesis.sections) return "";
    const section = (synthesis.sections || []).find((item) => item.key === "context_risks");
    if (!section || !section.resolved_fact_count) return "";
    const facts = synthesisFactMap(synthesis);
    const title = sectionDisplayTitle(section, audience);
    const countLabel = section.resolved_fact_count === 1
      ? "1 source-backed observation"
      : `${section.resolved_fact_count} source-backed observations`;
    return `<section class="panel synthesis-watchouts level-2" data-section-key="context_risks">
      <details class="watchouts-block">
        <summary>
          <span class="watchouts-summary-main">${escapeHtml(title)}</span>
          <span class="factor-summary-meta">${escapeHtml(countLabel)}</span>
        </summary>
        <div class="watchouts-body">
          ${renderSectionBody(section, facts)}
        </div>
      </details>
    </section>`;
  }

  function renderTensionRows(tensions, factsLookup) {
    return (tensions || []).map((pair) => {
      const keysA = [...new Set((pair.facts_a || []).map((id) => {
        const fact = factsLookup.get(id);
        return fact ? `${fact.factor_type}:${fact.factor_key}` : id;
      }))];
      const keysB = [...new Set((pair.facts_b || []).map((id) => {
        const fact = factsLookup.get(id);
        return fact ? `${fact.factor_type}:${fact.factor_key}` : id;
      }))];
      const provA = keysA.map(provenanceLabel).join(" · ");
      const provB = keysB.map(provenanceLabel).join(" · ");
      return `<div class="contrast-row">
        <div class="contrast-pair">
          <div class="contrast-side">
            <h4>${escapeHtml(titleCaseSignal(pair.tag_a))}</h4>
          </div>
          <div class="contrast-arrow" aria-hidden="true">↕</div>
          <div class="contrast-side">
            <h4>${escapeHtml(titleCaseSignal(pair.tag_b))}</h4>
          </div>
        </div>
        <details class="contrast-sources">
          <summary>Sources</summary>
          <p class="meta">${escapeHtml(provA)} · ${escapeHtml(provB)}</p>
        </details>
      </div>`;
    }).join("");
  }

  function renderResolvedTensions(synthesis, audience) {
    const tensions = (synthesis && synthesis.resolved_tensions) || [];
    if (!tensions.length) return "";
    const facts = synthesisFactMap(synthesis);
    return `<section class="panel synthesis-tensions level-2">
      <div class="panel-head"><h2>${escapeHtml(tensionsHeading(audience))}</h2></div>
      <p class="section-helper">${escapeHtml(tensionsExplanation(tensions.length))}</p>
      <div class="result-list-group result-list-group-tensions">${renderTensionRows(tensions, facts)}</div>
    </section>`;
  }

  function renderConditionalTensions(synthesis) {
    const tensions = (synthesis && synthesis.conditional_tensions) || [];
    if (!tensions.length) return "";
    const facts = synthesisFactMap(synthesis);
    return `<section class="panel synthesis-conditional-tensions level-2">
      <div class="panel-head"><h2>Conditional tensions</h2></div>
      <p class="section-helper">These possibilities depend on source conditions that cannot currently be resolved from the available chart data.</p>
      ${renderTensionRows(tensions, facts)}
    </section>`;
  }

  function renderConditionalSourceNotesRow(synthesis) {
    const groups = (synthesis && synthesis.conditional_details) || [];
    if (!groups.length) return "";
    const facts = synthesisFactMap(synthesis);
    const body = groups.map((group) => {
      const label = factorCardTitle(group.factor_type, group.factor_key);
      const condition = (group.activation_conditions || []).join(" · ") || "Unresolved condition";
      const items = (group.fact_ids || [])
        .map((id) => {
          const fact = facts.get(id);
          if (!fact) return "";
          return `<li class="fact-item"><span class="fact-bullet" aria-hidden="true">•</span><span class="fact-text">${escapeHtml(fact.text)}</span></li>`;
        })
        .filter(Boolean)
        .join("");
      return `<div class="conditional-group">
        <h4>${escapeHtml(label)}</h4>
        <p class="condition-unresolved">Condition not resolved · ${escapeHtml(condition)}</p>
        <ul class="fact-list">${items}</ul>
      </div>`;
    }).join("");
    return `<details class="methodology-row conditional-notes-block">
      <summary>Conditional source notes <span class="factor-summary-meta">${groups.length}</span></summary>
      <div class="conditional-notes-body">
        <p class="section-helper">These source notes depend on conditions that are not resolved from the available chart data. They are not treated as active.</p>
        ${body}
      </div>
    </details>`;
  }

  function renderProfileNotesRow(profile) {
    const notes = (profile.limitations || []).filter(Boolean);
    if (!notes.length) return "";
    const items = notes.map((note) => `<li>${escapeHtml(note)}</li>`).join("");
    return `<details class="methodology-row profile-notes-block">
      <summary>Profile notes <span class="factor-summary-meta">${notes.length}</span></summary>
      <ul class="profile-notes-list">${items}</ul>
    </details>`;
  }

  function renderSourceLayers(profile) {
    const calc = profile.calculated || {};
    const layers = collectFactsByFactor(profile);
    const coverageStatus = profile.coverage && profile.coverage.status;
    const coverageHtml = coverageStatus === "partial"
      ? `<p class="self-coverage-meta">Source coverage: partial</p>`
      : "";
    const houseNote = calc.birth_time_known
      ? ""
      : `<p class="self-house-note">House not calculated — birth time required.</p>`;

    if (!layers.length) {
      return `${coverageHtml}${houseNote}<p class="meta">No calculated Mercury factors to display.</p>`;
    }

    const cards = layers.map((layer) => {
      const openAttr = "";
      const title = factorCardTitle(layer.factor_type, layer.factor_key);
      if (!layer.supported) {
        return `<details class="factor-card factor-unsupported"${openAttr}>
          <summary>
            <span class="factor-summary-main">${escapeHtml(title)}</span>
            <span class="factor-summary-meta">Not yet available</span>
          </summary>
          <div class="factor-body">
            <p class="factor-unavailable">Source interpretation not yet available in this prototype.</p>
          </div>
        </details>`;
      }
      const count = layer.facts.length;
      const countLabel = count === 1 ? "1 source statement" : `${count} source statements`;
      return `<details class="factor-card"${openAttr}>
        <summary>
          <span class="factor-summary-main">${escapeHtml(title)}</span>
          <span class="factor-summary-meta">${escapeHtml(countLabel)}</span>
        </summary>
        <div class="factor-body">${renderFactGroups(layer.facts)}</div>
      </details>`;
    }).join("");

    return `${coverageHtml}${houseNote}${cards}`;
  }

  function renderSourceEvidenceRow(profile) {
    return `<details class="methodology-row source-evidence-block">
      <summary>Explore full source evidence</summary>
      <div class="source-evidence-body">
        <p class="section-helper">Full factor-by-factor source evidence and references.</p>
        ${renderSourceLayers(profile)}
      </div>
    </details>`;
  }

  function factLookup(profile) {
    const map = new Map();
    [
      ...(profile.sign_facts || []),
      ...(profile.house_facts || []),
      ...(profile.motion_facts || []),
      ...(profile.aspect_facts || []),
      ...(profile.conditional_unresolved || []),
    ].forEach((fact) => map.set(fact.id, fact));
    return map;
  }

  function renderTraceabilityRow(profile, displayName, factCount) {
    const calc = profile.calculated || {};
    const layers = collectFactsByFactor(profile);
    const lines = [];
    lines.push(`Display name: ${displayName || "(not supplied)"}`);
    lines.push(`Active source facts: ${factCount}`);
    lines.push(`Mercury sign: ${calc.mercury_sign || "—"}`);
    lines.push(`Mercury house: ${calc.mercury_house ?? "—"}`);
    lines.push(`Mercury motion: ${calc.mercury_motion || "—"}`);
    lines.push(`Birth time known: ${calc.birth_time_known ? "yes" : "no"}`);
    lines.push(`Hard aspected: ${calc.hard_aspected ? "yes" : "no"}`);
    lines.push("");
    lines.push("Aspects:");
    (calc.aspects || []).forEach((aspect) => {
      lines.push(`  - ${aspect.type} ${aspect.planet} · orb ${formatOrb(aspect.orb_deg)}`);
    });
    lines.push("");
    lines.push("Factor provenance + source references + fact IDs:");
    layers.forEach((layer) => {
      lines.push(`  ${layer.factor_type}:${layer.factor_key}`);
      layer.facts.forEach((fact) => {
        lines.push(`    ${fact.id} | ${fact.source_reference} | ${fact.category}/${fact.polarity}`);
      });
    });
    if ((profile.repeated_signals || []).length) {
      lines.push("");
      lines.push("Repeated signals:");
      profile.repeated_signals.forEach((signal) => {
        lines.push(`  ${signal.signal} (${signal.source_count}) ← ${(signal.sources || []).join(", ")}`);
        lines.push(`    facts: ${(signal.fact_ids || []).join(", ")}`);
      });
    }
    const countPhrase = factCount === 1
      ? "1 active source fact was used in this profile."
      : `${factCount} active source facts were used in this profile.`;
    return `<details class="methodology-row trace-details">
      <summary>Why AstroIT shows this</summary>
      <div class="trace-body">
        <p class="section-helper self-tech-meta">${escapeHtml(countPhrase)}</p>
        <pre class="trace-pre">${escapeHtml(lines.join("\n"))}</pre>
      </div>
    </details>`;
  }

  function renderDetailsMethodology(profile, synthesis, displayName, factCount) {
    const conditional = renderConditionalSourceNotesRow(synthesis);
    const notes = renderProfileNotesRow(profile);
    const evidence = renderSourceEvidenceRow(profile);
    const why = renderTraceabilityRow(profile, displayName, factCount);
    if (!conditional && !notes && !evidence && !why) return "";
    return `<section class="panel details-methodology level-3">
      <div class="panel-head"><h2>Details &amp; methodology</h2></div>
      <div class="details-methodology-rows">
        ${conditional}
        ${notes}
        ${evidence}
        ${why}
      </div>
    </section>`;
  }

  function renderSelfProfile(profile, displayName) {
    const calc = profile.calculated || {};
    const synthesis = profile.synthesis || null;
    const audience = resolveProfileAudience(displayName);
    const motion = String(calc.mercury_motion || "");
    const motionHtml = motion.toLowerCase() === "retrograde"
      ? `<span class="motion-rx">Retrograde</span>`
      : escapeHtml(titleCaseSignal(motion) || "—");
    const aspectList = (calc.aspects || [])
      .map((aspect) => `<li>${escapeHtml(formatAspectChip(aspect))}</li>`)
      .join("");
    const factCount = countActiveSourceFacts(profile);
    setBrandTitleForProfile(audience, displayName);

    selfProfileContent.innerHTML = `
      <section class="panel self-header">
        <p class="self-calc-line">Mercury in ${escapeHtml(calc.mercury_sign || "—")} · House ${escapeHtml(String(calc.mercury_house ?? "—"))} · ${motionHtml}</p>
        ${aspectList ? `<ul class="self-aspect-list">${aspectList}</ul>` : `<p class="meta">No calculated aspects in orb.</p>`}
      </section>
      ${renderStrongestPatterns(synthesis, audience, displayName)}
      ${renderSynthesisSections(synthesis, audience)}
      ${renderResolvedTensions(synthesis, audience)}
      ${renderConditionalTensions(synthesis)}
      ${renderContextWatchOuts(synthesis, audience)}
      ${renderDetailsMethodology(profile, synthesis, displayName, factCount)}
    `;
  }

  async function buildMyProfile() {
    const displayName = document.getElementById("self-name").value.trim();
    const birthDate = document.getElementById("self-birth-date").value.trim();
    const birthTime = document.getElementById("self-birth-time").value.trim();
    const birthPlace = document.getElementById("self-birth-place").value.trim();

    if (!birthDate || !birthPlace) {
      setStatus(selfSetupStatus, "Birth date and birth place are required.", "error");
      return;
    }

    const payload = {
      birth_date: birthDate,
      birth_place: birthPlace,
    };
    if (birthTime) payload.birth_time = birthTime;

    setStatus(selfSetupStatus, "Building source-backed profile…", "loading");
    setStatus(selfProfileStatus, "Building source-backed profile…", "loading");
    showSelfProfileShell();
    selfProfileContent.innerHTML = "";

    try {
      const profile = await apiPost("/api/v1/mercury-source-profile", payload);
      closeSelfDrawer();
      renderSelfProfile(profile, displayName);
      setStatus(selfProfileStatus, "");
      setStatus(selfSetupStatus, "");
    } catch (err) {
      setStatus(selfSetupStatus, err.message, "error");
      setStatus(selfProfileStatus, err.message, "error");
    }
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
  document.getElementById("explore-yourself").addEventListener("click", openSelfDrawer);
  document.getElementById("build-my-profile").addEventListener("click", buildMyProfile);
  document.getElementById("self-back-start").addEventListener("click", showEmptyShell);
  document.getElementById("self-build-team").addEventListener("click", () => {
    closeSelfDrawer();
    openSetup();
  });
  document.querySelectorAll("[data-self-demo]").forEach((btn) => {
    btn.addEventListener("click", () => fillSelfDemo(btn.getAttribute("data-self-demo")));
  });
  document.getElementById("load-demo-empty").addEventListener("click", loadDemoAndAnalyze);
  document.getElementById("load-demo").addEventListener("click", loadDemoAndAnalyze);
  document.getElementById("saved-workspaces").addEventListener("click", openWorkspacesPanel);
  document.getElementById("saved-workspaces-empty").addEventListener("click", openWorkspacesPanel);
  saveWorkspaceBtn.addEventListener("click", saveCurrentWorkspace);
  applyAnalyzeBtn.addEventListener("click", () => analyzeTeam());

  setupOverlay.querySelectorAll("[data-close-setup]").forEach((el) => {
    el.addEventListener("click", closeSetup);
  });
  selfOverlay.querySelectorAll("[data-close-self]").forEach((el) => {
    el.addEventListener("click", closeSelfDrawer);
  });
  workspacesOverlay.querySelectorAll("[data-close-workspaces]").forEach((el) => {
    el.addEventListener("click", closeWorkspacesPanel);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    if (!setupOverlay.hidden) closeSetup();
    if (!selfOverlay.hidden) closeSelfDrawer();
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
