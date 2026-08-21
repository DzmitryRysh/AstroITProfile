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
  const SELF_BRAND_TITLE = "Your Work Profile";

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
  let activeProfileTab = "overview";

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

  const PERSON_PRONOUN_FORMS = {
    male: { subject: "he", object: "him", possessive: "his", independent: "his", reflexive: "himself", pluralVerb: false },
    female: { subject: "she", object: "her", possessive: "her", independent: "hers", reflexive: "herself", pluralVerb: false },
    they: { subject: "they", object: "them", possessive: "their", independent: "theirs", reflexive: "themselves", pluralVerb: true },
    you: { subject: "you", object: "you", possessive: "your", independent: "yours", reflexive: "yourself", pluralVerb: true },
  };

  function normalizePersonSex(value) {
    const token = String(value || "").trim().toLowerCase();
    if (["male", "m", "he", "him", "he/him"].includes(token)) return "male";
    if (["female", "f", "she", "her", "she/her"].includes(token)) return "female";
    if (["neutral", "they", "them", "they/them", "nonbinary", "non-binary"].includes(token)) return "neutral";
    return "unknown";
  }

  function buildPersonPerspective({ name, sex, perspective } = {}) {
    const trimmed = String(name || "").trim();
    const resolvedPerspective = perspective || (trimmed ? "third_person" : "self");
    const resolvedSex = normalizePersonSex(sex);
    let forms = PERSON_PRONOUN_FORMS.they;
    if (resolvedPerspective === "self") forms = PERSON_PRONOUN_FORMS.you;
    else if (resolvedSex === "male") forms = PERSON_PRONOUN_FORMS.male;
    else if (resolvedSex === "female") forms = PERSON_PRONOUN_FORMS.female;
    const subjectCap = forms.subject.charAt(0).toUpperCase() + forms.subject.slice(1);
    const possessiveCap = forms.possessive.charAt(0).toUpperCase() + forms.possessive.slice(1);
    return {
      name: trimmed,
      perspective: resolvedPerspective,
      sex: resolvedSex,
      subject: forms.subject,
      object: forms.object,
      possessive: forms.possessive,
      independent: forms.independent,
      reflexive: forms.reflexive,
      subjectCap,
      possessiveCap,
      pluralVerb: forms.pluralVerb,
    };
  }

  function fillPersonTemplate(template, person) {
    if (!template || !person) return template || "";
    const name = person.name || person.subjectCap;
    return String(template)
      .replaceAll("{name}", name)
      .replaceAll("{They}", person.subjectCap)
      .replaceAll("{they}", person.subject)
      .replaceAll("{them}", person.object)
      .replaceAll("{their}", person.possessive)
      .replaceAll("{theirs}", person.independent)
      .replaceAll("{themself}", person.reflexive);
  }

  function contextualizeNeutralSentence(text, person) {
    const stripped = String(text || "").trim();
    if (!person) return stripped;
    if (stripped.toLowerCase().startsWith("may ")) {
      let rest = stripped.slice(4);
      if (rest) rest = rest.charAt(0).toLowerCase() + rest.slice(1);
      return `${person.subjectCap} may ${rest}`;
    }
    return stripped;
  }

  function presentVerb(person, base, singular) {
    return person && person.pluralVerb ? base : singular;
  }

  function howThinksHeading(person) {
    if (!person || person.perspective === "self" || !person.name) return "How you think";
    return `How ${person.name} thinks`;
  }

  function howWorksHeading(person) {
    if (!person || person.perspective === "self" || !person.name) return "How you work";
    return `How ${person.name} works`;
  }

  function currentPersonPerspective() {
    const nameEl = document.getElementById("self-name");
    const sexEl = document.getElementById("self-sex");
    const name = nameEl ? String(nameEl.value || "").trim() : "";
    const sex = sexEl ? sexEl.value : "";
    return buildPersonPerspective({
      name,
      sex,
      perspective: name ? "third_person" : "self",
    });
  }

  function possessiveLabel(name) {
    const trimmed = String(name || "").trim();
    if (!trimmed) return "";
    return /s$/i.test(trimmed) ? `${trimmed}'` : `${trimmed}'s`;
  }

  function profileHeaderTitle(audience, displayName) {
    if (audience === "person") {
      const name = String(displayName || "").trim();
      return name ? `${possessiveLabel(name)} Work Profile` : "Work Profile";
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
      sex: "male",
    },
    vlad: {
      display_name: "Vlad",
      birth_date: "1986-05-16",
      birth_time: "15:00",
      birth_place: "Dnipro, Ukraine",
      sex: "male",
    },
    dzmitry: {
      display_name: "Dzmitry",
      birth_date: "1985-11-12",
      birth_time: "14:15",
      birth_place: "Zhodino, Belarus",
      sex: "male",
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

  // Recruiter-facing tension labels. Tags stay unchanged; labels only.
  // Bounded by approved human-copy meaning (e.g. Leo risk of intellectual
  // superficiality), not accusatory trait naming.
  const TENSION_TAG_LABELS = {
    superficiality: "Surface-level thinking risk",
    analytical_thinking: "Analytical thinking",
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
    const sexEl = document.getElementById("self-sex");
    if (sexEl) sexEl.value = demo.sex || "";
    setStatus(selfSetupStatus, `Filled ${demo.display_name}. Click Build My Profile to call the API.`);
  }

  function titleCaseSignal(value) {
    return String(value || "")
      .split("_")
      .filter(Boolean)
      .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
      .join(" ");
  }

  function tensionTagLabel(tag) {
    if (TENSION_TAG_LABELS[tag]) return TENSION_TAG_LABELS[tag];
    return titleCaseSignal(tag);
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

  function presentationTextMap(synthesis) {
    return (synthesis && synthesis.presentation_text_by_fact_id) || {};
  }

  function humanFactText(fact, presentationMap) {
    if (!fact) return "";
    const map = presentationMap || {};
    if (fact.id && map[fact.id]) return map[fact.id];
    return fact.text;
  }

  function renderPreviewFactItem(fact, presentationMap) {
    if (!fact) return "";
    const isRisk = fact.polarity === "risk";
    const marker = isRisk
      ? `<span class="risk-mark" title="Possible difficulty">Risk</span>`
      : `<span class="fact-bullet" aria-hidden="true">•</span>`;
    const provenance = compactProvenanceLabel(`${fact.factor_type}:${fact.factor_key}`);
    const text = humanFactText(fact, presentationMap);
    return `<li class="fact-item${isRisk ? " fact-risk" : ""}">${marker}<span class="fact-text">${escapeHtml(text)}<span class="fact-provenance">${escapeHtml(provenance)}</span></span></li>`;
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

  function renderGroupedFactItem(fact, presentationMap) {
    if (!fact) return "";
    const isRisk = fact.polarity === "risk";
    const marker = isRisk
      ? `<span class="risk-mark" title="Possible difficulty">Risk</span>`
      : `<span class="fact-bullet" aria-hidden="true">•</span>`;
    // Factor heading already establishes provenance — do not repeat it on every row.
    const text = humanFactText(fact, presentationMap);
    return `<li class="fact-item${isRisk ? " fact-risk" : ""}">${marker}<span class="fact-text">${escapeHtml(text)}</span></li>`;
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

  function renderSectionFactorExplore(section, facts, presentationMap) {
    const groups = groupSectionFactsByFactor(section, facts);
    if (!groups.length) return "";
    const rows = groups.map((group) => {
      const label = factorCardTitle(group.factor_type, group.factor_key);
      const n = group.facts.length;
      const countLabel = n === 1 ? "1 observation" : `${n} observations`;
      const items = group.facts
        .map((fact) => renderGroupedFactItem(fact, presentationMap))
        .filter(Boolean)
        .join("");
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

  function renderSectionBody(section, facts, presentationMap, options) {
    const hideMeta = options && options.hideMeta;
    const previewIds = section.preview_fact_ids || [];
    const previewItems = previewIds
      .map((id) => renderPreviewFactItem(facts.get(id), presentationMap))
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
          ${hideMeta ? "" : `<p class="section-evidence-meta">${escapeHtml(evidence)}</p>`}
          ${renderSectionFactorExplore(section, facts, presentationMap)}
          <button type="button" class="section-show-less" onclick="this.closest('details.section-explore').open=false">Show less</button>
        </details>`
      : "";
    return `<div class="section-body">
      ${hideMeta ? "" : `<p class="section-evidence-meta">${escapeHtml(evidence)}</p>`}
      <ul class="fact-list section-preview">${previewItems}</ul>
      ${explore}
    </div>`;
  }

  function renderSynthesisSections(synthesis, audience) {
    if (!synthesis || !synthesis.sections) return "";
    const facts = synthesisFactMap(synthesis);
    const presentation = presentationTextMap(synthesis);
    return (synthesis.sections || []).map((section) => {
      if (!section.resolved_fact_count) return "";
      // Watch-outs render separately as a secondary collapsed block.
      if (section.key === "context_risks") return "";
      const title = sectionDisplayTitle(section, audience);
      return `<section class="panel synthesis-section level-1" data-section-key="${escapeHtml(section.key)}">
        <div class="panel-head"><h2>${escapeHtml(title)}</h2></div>
        ${renderSectionBody(section, facts, presentation)}
      </section>`;
    }).join("");
  }

  function renderContextWatchOuts(synthesis, audience) {
    if (!synthesis || !synthesis.sections) return "";
    const section = (synthesis.sections || []).find((item) => item.key === "context_risks");
    if (!section || !section.resolved_fact_count) return "";
    const facts = synthesisFactMap(synthesis);
    const presentation = presentationTextMap(synthesis);
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
          ${renderSectionBody(section, facts, presentation)}
        </div>
      </details>
    </section>`;
  }

  function renderTensionRows(tensions, factsLookup, options) {
    const compact = options && options.compact;
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
      const sources = compact
        ? ""
        : `<details class="contrast-sources">
          <summary>Sources</summary>
          <p class="meta">${escapeHtml(provA)} · ${escapeHtml(provB)}</p>
        </details>`;
      return `<div class="contrast-row">
        <div class="contrast-pair">
          <div class="contrast-side">
            <h4>${escapeHtml(tensionTagLabel(pair.tag_a))}</h4>
          </div>
          <div class="contrast-arrow" aria-hidden="true">↕</div>
          <div class="contrast-side">
            <h4>${escapeHtml(tensionTagLabel(pair.tag_b))}</h4>
          </div>
        </div>
        ${sources}
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

  const MARS_PRIMARY_SECTION_KEYS = [
    "how_you_start",
    "how_you_execute",
    "work_rhythm",
    "when_you_get_stuck",
    "under_pressure",
    "how_you_handle_obstacles",
    "conflict_style",
    "best_work_conditions",
    "watchouts",
  ];
  const MARS_SECONDARY_SECTION_KEYS = [
    "compensations",
    "professional_associations",
  ];
  const MARS_PRESSURE_TAGS = [
    "effort_overload",
    "crisis_execution",
    "crisis_activation",
  ];

  function marsSectionTitle(section, person) {
    const key = section && section.key;
    if (person) {
      if (key === "how_you_start") return `How ${person.subject} ${presentVerb(person, "start", "starts")}`;
      if (key === "how_you_execute") return `How ${person.subject} ${presentVerb(person, "execute", "executes")}`;
      if (key === "work_rhythm") return `${person.possessiveCap} work rhythm`;
      if (key === "when_you_get_stuck") return `When ${person.subject} ${presentVerb(person, "get", "gets")} stuck`;
      if (key === "how_you_handle_obstacles") return `How ${person.subject} ${presentVerb(person, "handle", "handles")} obstacles`;
      if (key === "compensations") return `What helps ${person.object} work better`;
    }
    if (key === "compensations") return "What helps you work better";
    return (section && section.title) || "";
  }

  function marsGlanceTitle(card, person) {
    if (card && card.key === "execution_style") return "Execution style";
    if (card && card.key === "what_may_slow_you_down") {
      return person ? `What may slow ${person.object} down` : "What may slow them down";
    }
    if (card && card.key === "under_pressure") return "Under pressure";
    return (card && card.title) || "";
  }

  function marsGlanceText(card, person) {
    if (!card) return "";
    if (card.display_template) return fillPersonTemplate(card.display_template, person);
    return contextualizeNeutralSentence(card.text, person);
  }

  function marsShowsWatch(fact) {
    if (!fact) return false;
    if (fact.category === "watchout" || fact.category === "stuck_blocker") return true;
    if (fact.polarity !== "risk") return false;
    if (fact.category === "conflict" || fact.category === "action_start") return true;
    const tags = fact.tags || [];
    return MARS_PRESSURE_TAGS.some((tag) => tags.includes(tag));
  }

  function renderMarsPreviewFactItem(fact, presentationMap) {
    if (!fact) return "";
    const watch = marsShowsWatch(fact);
    const marker = watch
      ? `<span class="watch-mark" title="Friction to be aware of">Watch</span>`
      : `<span class="fact-bullet" aria-hidden="true">•</span>`;
    const text = humanFactText(fact, presentationMap);
    return `<li class="fact-item${watch ? " fact-watch" : ""}">${marker}<span class="fact-text">${escapeHtml(text)}</span></li>`;
  }

  function renderMarsGroupedFactItem(fact, presentationMap) {
    if (!fact) return "";
    const watch = marsShowsWatch(fact);
    const marker = watch
      ? `<span class="watch-mark" title="Friction to be aware of">Watch</span>`
      : `<span class="fact-bullet" aria-hidden="true">•</span>`;
    const text = humanFactText(fact, presentationMap);
    return `<li class="fact-item${watch ? " fact-watch" : ""}">${marker}<span class="fact-text">${escapeHtml(text)}</span></li>`;
  }

  function marsFactorCardTitle(factorType, factorKey) {
    if (factorType === "sign") return `Mars in ${factorKey}`;
    if (factorType === "house") return `House ${factorKey}`;
    if (factorType === "motion") {
      if (String(factorKey).toLowerCase() === "retrograde") return "Retrograde Mars";
      if (String(factorKey).toLowerCase() === "direct") return "Direct Mars";
      return `Mars ${titleCaseSignal(factorKey)}`;
    }
    if (factorType === "aspect") {
      const [type, ...rest] = String(factorKey).split("_");
      const planet = rest.join("_");
      return `Mars ${aspectPhrase(type, planet)} ${planet}`;
    }
    return `${factorType}:${factorKey}`;
  }

  function marsFactorLabelFromSource(sourceKey) {
    const [type, ...rest] = String(sourceKey || "").split(":");
    const key = rest.join(":");
    if (type && key) return marsFactorCardTitle(type, key);
    return provenanceLabel(sourceKey);
  }

  function marsGroupSectionFactsByFactor(section, facts) {
    const groups = new Map();
    const firstIndex = new Map();
    (section.fact_ids || []).forEach((id, index) => {
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

  function renderMarsSectionFactorExplore(section, facts, presentationMap) {
    const groups = marsGroupSectionFactsByFactor(section, facts);
    if (!groups.length) return "";
    const rows = groups.map((group) => {
      const label = marsFactorCardTitle(group.factor_type, group.factor_key);
      const n = group.facts.length;
      const countLabel = n === 1 ? "1 observation" : `${n} observations`;
      const items = group.facts
        .map((fact) => renderMarsGroupedFactItem(fact, presentationMap))
        .filter(Boolean)
        .join("");
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

  function renderMarsSectionBody(section, facts, presentationMap) {
    const previewIds = section.preview_fact_ids || [];
    const previewItems = previewIds
      .map((id) => renderMarsPreviewFactItem(facts.get(id), presentationMap))
      .filter(Boolean)
      .join("");
    const total = Number(section.fact_count) || (section.fact_ids || []).length;
    const evidence = `${total} source-backed observations across ${section.factor_count} factor${section.factor_count === 1 ? "" : "s"}`;
    const hasMore = total > previewIds.length;
    const exploreLabel = `Explore all ${total} observations`;
    const explore = hasMore
      ? `<details class="section-explore">
          <summary class="section-explore-summary">
            <span class="explore-all-label">${escapeHtml(exploreLabel)}</span>
          </summary>
          <p class="section-evidence-meta">${escapeHtml(evidence)}</p>
          ${renderMarsSectionFactorExplore(section, facts, presentationMap)}
          <button type="button" class="section-show-less" onclick="this.closest('details.section-explore').open=false">Show less</button>
        </details>`
      : "";
    return `<div class="section-body">
      <ul class="fact-list section-preview">${previewItems}</ul>
      ${explore}
    </div>`;
  }

  function renderMarsWorkGlance(synthesis, person, options) {
    const cards = (synthesis && synthesis.work_style_at_a_glance) || [];
    if (!cards.length) return "";
    const items = cards.map((card) => `<article class="work-glance-card" data-glance-key="${escapeHtml(card.key)}">
      <h3>${escapeHtml(marsGlanceTitle(card, person))}</h3>
      <p>${escapeHtml(marsGlanceText(card, person))}</p>
    </article>`).join("");
    if (options && options.cardsOnly) {
      return `<div class="work-glance">${items}</div>`;
    }
    return `<section class="panel work-style-glance level-1">
      <div class="panel-head"><h2>Work style at a glance</h2></div>
      <div class="work-glance">${items}</div>
    </section>`;
  }

  function renderMarsRecurringPatterns(synthesis) {
    const patterns = (synthesis && synthesis.repeated_signals) || [];
    if (!patterns.length) return "";
    const facts = synthesisFactMap(synthesis);
    const presentation = presentationTextMap(synthesis);
    const rows = patterns.map((signal) => {
      const count = Number(signal.source_count) || (signal.sources || []).length || 0;
      const supportLabel = count === 1
        ? "Supported by 1 profile factor"
        : `Supported by ${count} profile factors`;
      const firstId = (signal.fact_ids || [])[0];
      const takeawayFact = firstId ? facts.get(firstId) : null;
      const takeaway = takeawayFact ? humanFactText(takeawayFact, presentation) : "";
      const whyItems = (signal.sources || [])
        .map((src) => `<li>${escapeHtml(marsFactorLabelFromSource(src))}</li>`)
        .join("");
      return `<article class="signal-row">
        <div class="signal-row-main">
          <strong class="signal-label">${escapeHtml(titleCaseSignal(signal.signal))}</strong>
          ${takeaway ? `<p class="signal-takeaway">${escapeHtml(takeaway)}</p>` : ""}
        </div>
        <details class="signal-why">
          <summary>Why this appears</summary>
          <div class="signal-why-body">
            <p class="signal-why-label">Recurring patterns appear when more than one calculated factor supports the same work signal.</p>
            <p class="signal-why-label">${escapeHtml(supportLabel)}</p>
            <ul class="signal-why-list">${whyItems}</ul>
          </div>
        </details>
      </article>`;
    }).join("");
    return `<section class="panel synthesis-patterns level-1">
      <div class="panel-head"><h2>Recurring patterns</h2></div>
      <div class="result-list-group">${rows}</div>
    </section>`;
  }

  function renderMarsPrimarySections(synthesis, person) {
    if (!synthesis || !synthesis.sections) return "";
    const facts = synthesisFactMap(synthesis);
    const presentation = presentationTextMap(synthesis);
    return MARS_PRIMARY_SECTION_KEYS.map((key) => {
      const section = (synthesis.sections || []).find((item) => item.key === key);
      if (!section || !section.fact_count) return "";
      return `<section class="panel synthesis-section level-1" data-section-key="${escapeHtml(section.key)}">
        <div class="panel-head"><h2>${escapeHtml(marsSectionTitle(section, person))}</h2></div>
        ${renderMarsSectionBody(section, facts, presentation)}
      </section>`;
    }).join("");
  }

  function renderMarsSecondarySections(synthesis, person) {
    if (!synthesis || !synthesis.sections) return "";
    const facts = synthesisFactMap(synthesis);
    const presentation = presentationTextMap(synthesis);
    return MARS_SECONDARY_SECTION_KEYS.map((key) => {
      const section = (synthesis.sections || []).find((item) => item.key === key);
      if (!section || !section.fact_count) return "";
      return `<section class="panel synthesis-watchouts level-2" data-section-key="${escapeHtml(section.key)}">
        <details class="watchouts-block">
          <summary>
            <span class="watchouts-summary-main">${escapeHtml(marsSectionTitle(section, person))}</span>
          </summary>
          <div class="watchouts-body">
            ${renderMarsSectionBody(section, facts, presentation)}
          </div>
        </details>
      </section>`;
    }).join("");
  }

  function renderMarsDetailsMethodology(profile, synthesis, person) {
    const calc = (profile && profile.calculated) || {};
    const notes = (profile && profile.limitations) || [];
    const unresolved = (profile && profile.conditional_unresolved) || [];
    const sections = (synthesis && synthesis.sections) || [];
    const repeats = (synthesis && synthesis.repeated_signals) || [];
    const motion = String(calc.mars_motion || "");
    const motionLabel = motion.toLowerCase() === "retrograde" ? "Retrograde" : titleCaseSignal(motion);
    const aspectList = (calc.aspects || [])
      .map((aspect) => `${titleCaseSignal(aspect.type)} ${aspect.planet}`)
      .join(" · ");
    const calcLine = `Mars in ${calc.mars_sign || "—"} · House ${calc.mars_house ?? "—"} · ${motionLabel || "—"}`;
    const populated = sections.filter((section) => section.fact_count);
    const countItems = populated.map((section) => {
      const title = marsSectionTitle(section, person);
      const facts = section.fact_count === 1 ? "1 observation" : `${section.fact_count} observations`;
      const factors = section.factor_count === 1 ? "1 factor" : `${section.factor_count} factors`;
      return `<li>${escapeHtml(title)}: ${facts} across ${factors}</li>`;
    }).join("");
    const notesHtml = notes.length
      ? `<details class="methodology-row profile-notes-block">
          <summary>Profile notes <span class="factor-summary-meta">${notes.length}</span></summary>
          <ul class="profile-notes-list">${notes.map((note) => `<li>${escapeHtml(note)}</li>`).join("")}</ul>
        </details>`
      : "";
    const unresolvedHtml = unresolved.length
      ? `<details class="methodology-row conditional-notes-block">
          <summary>Conditional source notes <span class="factor-summary-meta">${unresolved.length}</span></summary>
          <p class="section-helper">These source notes depend on conditions that are not resolved from the available chart data. They are not treated as active.</p>
        </details>`
      : "";
    const countsHtml = countItems
      ? `<details class="methodology-row">
          <summary>Source-backed observation counts</summary>
          <ul class="profile-notes-list">${countItems}</ul>
        </details>`
      : "";
    const repeatsHtml = repeats.length
      ? `<details class="methodology-row">
          <summary>Recurring patterns</summary>
          <p class="section-helper">Recurring patterns appear when more than one calculated factor supports the same work signal.</p>
        </details>`
      : "";
    const professional = populated.find((section) => section.key === "professional_associations");
    const professionalHtml = professional
      ? `<details class="methodology-row">
          <summary>Professional associations</summary>
          <p class="section-helper">These are source-described associations and aptitudes, not recommended jobs, verified competencies, or hiring recommendations.</p>
        </details>`
      : "";
    const compensation = populated.find((section) => section.key === "compensations");
    const compensationHtml = compensation
      ? `<details class="methodology-row">
          <summary>${escapeHtml(marsSectionTitle(compensation, person))}</summary>
          <p class="section-helper">Source material from the framework — not treated as an automatically active work trait.</p>
        </details>`
      : "";
    const evidenceHtml = `<details class="methodology-row">
      <summary>Calculated work factors</summary>
      <p class="self-calc-line">${escapeHtml(calcLine)}</p>
      ${aspectList ? `<p class="meta">${escapeHtml(aspectList)}</p>` : ""}
    </details>`;
    return `<section class="panel details-methodology level-3">
      <div class="panel-head"><h2>Details &amp; methodology</h2></div>
      <div class="details-methodology-rows">
        ${unresolvedHtml}
        ${notesHtml}
        ${repeatsHtml}
        ${countsHtml}
        ${compensationHtml}
        ${professionalHtml}
        ${evidenceHtml}
      </div>
    </section>`;
  }

  const PROFILE_TABS = ["overview", "thinking", "working", "evidence"];
  const OVERVIEW_MERCURY_TAKEAWAY_LIMIT = 4;
  const OVERVIEW_MERCURY_RECURRING_LIMIT = 3;
  const OVERVIEW_MARS_RECURRING_LIMIT = 3;
  const GROUP_PREVIEW_LIMIT = 3;
  // Overview-only recruiter labels. Canonical signal ids / tags are unchanged.
  const OVERVIEW_MERCURY_SIGNAL_PRESENTATION = {
    technical_ability: {
      label: "Technical aptitude signal",
      takeaway: "The profile contains repeated source-described technical aptitude signals.",
    },
    debate: {
      label: "Debate tendency",
    },
    argumentation: {
      label: "Argumentation pattern",
    },
    sales: {
      label: "Sales-related aptitude signal",
    },
  };
  // Overview-only glance wording. Canonical card text remains in Thinking/Evidence.
  const OVERVIEW_MERCURY_GLANCE_PRESENTATION = {
    watchout: {
      appearance_of_competence:
        "There may be a risk that prepared phrasing creates an appearance of competence.",
    },
  };
  const MERCURY_THINKING_GROUPS = [
    {
      key: "thinking_problem_solving",
      title: "Thinking & problem solving",
      blurb: "Thinking style, memory, and focus.",
      sections: ["thinking", "memory_focus"],
      includeThinkingPatterns: true,
    },
    {
      key: "communication_influence",
      title: "Communication & influence",
      blurb: "How ideas are expressed and applied with others.",
      sections: ["communication", "work_application"],
    },
    {
      key: "learning_adaptation",
      title: "Learning & adaptation",
      blurb: "How new material is taken in.",
      sections: ["learning"],
    },
    {
      key: "tensions_context",
      title: "Tensions & context",
      blurb: "Contrasts and situational watch-outs.",
      sections: ["context_risks"],
      includeTensions: true,
    },
  ];
  const MARS_WORKING_GROUPS = [
    {
      key: "execution",
      title: "Execution",
      blurb: "Starting, carrying through, rhythm, and conditions.",
      sections: ["how_you_start", "how_you_execute", "work_rhythm", "best_work_conditions"],
    },
    {
      key: "friction_pressure",
      title: "Friction & pressure",
      blurb: "Where action slows, overloads, or needs caution.",
      sections: ["when_you_get_stuck", "under_pressure", "how_you_handle_obstacles", "watchouts"],
    },
    {
      key: "collaboration_conflict",
      title: "Collaboration & conflict",
      blurb: "How disagreement shows up at work.",
      sections: ["conflict_style"],
    },
    {
      key: "growth_support",
      title: "Growth & support",
      blurb: "What helps, plus source associations.",
      sections: ["compensations"],
      includeMarsPatterns: true,
      includeProfessional: true,
    },
  ];

  function mercurySectionByKey(synthesis, key) {
    return ((synthesis && synthesis.sections) || []).find((item) => item.key === key) || null;
  }

  function marsSectionByKey(synthesis, key) {
    return ((synthesis && synthesis.sections) || []).find((item) => item.key === key) || null;
  }

  function populatedMercurySection(synthesis, key) {
    const section = mercurySectionByKey(synthesis, key);
    return section && section.resolved_fact_count ? section : null;
  }

  function populatedMarsSection(synthesis, key) {
    const section = marsSectionByKey(synthesis, key);
    return section && section.fact_count ? section : null;
  }

  function signalTakeaway(signal, facts, presentation) {
    const firstId = (signal && signal.fact_ids || [])[0];
    const fact = firstId ? facts.get(firstId) : null;
    return fact ? humanFactText(fact, presentation) : "";
  }

  function renderCompactSignalRow(signal, facts, presentation) {
    if (!signal) return "";
    const takeaway = signalTakeaway(signal, facts, presentation);
    return `<article class="signal-row signal-row-compact">
      <div class="signal-row-main">
        <strong class="signal-label">${escapeHtml(titleCaseSignal(signal.signal))}</strong>
        ${takeaway ? `<p class="signal-takeaway">${escapeHtml(takeaway)}</p>` : ""}
      </div>
    </article>`;
  }

  function overviewMercurySignalLabel(signal) {
    const key = signal && signal.signal;
    const bounded = key ? OVERVIEW_MERCURY_SIGNAL_PRESENTATION[key] : null;
    if (bounded && bounded.label) return bounded.label;
    return titleCaseSignal(key);
  }

  function overviewMercurySignalTakeaway(signal, facts, presentation) {
    const key = signal && signal.signal;
    const bounded = key ? OVERVIEW_MERCURY_SIGNAL_PRESENTATION[key] : null;
    if (bounded && bounded.takeaway) return bounded.takeaway;
    return signalTakeaway(signal, facts, presentation);
  }

  function renderOverviewMercuryTakeawayRow(signal, facts, presentation) {
    if (!signal) return "";
    const takeaway = overviewMercurySignalTakeaway(signal, facts, presentation);
    return `<article class="signal-row signal-row-compact" data-signal="${escapeHtml(signal.signal)}">
      <div class="signal-row-main">
        <strong class="signal-label">${escapeHtml(overviewMercurySignalLabel(signal))}</strong>
        ${takeaway ? `<p class="signal-takeaway">${escapeHtml(takeaway)}</p>` : ""}
      </div>
    </article>`;
  }

  function renderQuietMercuryFact(fact, presentationMap) {
    if (!fact) return "";
    const text = humanFactText(fact, presentationMap);
    return `<li class="fact-item"><span class="fact-bullet" aria-hidden="true">•</span><span class="fact-text">${escapeHtml(text)}</span></li>`;
  }

  function collectPreviewFacts(sections, facts, presentation, limit, renderer) {
    const items = [];
    (sections || []).forEach((section) => {
      (section.preview_fact_ids || []).forEach((id) => {
        if (items.length >= limit) return;
        const fact = facts.get(id);
        const html = renderer(fact, presentation);
        if (html) items.push(html);
      });
    });
    return items.slice(0, limit);
  }

  function joinPreviewPieces(pieces, limit) {
    const chosen = (pieces || []).filter((item) => item && item.html).slice(0, limit);
    const parts = [];
    const facts = [];
    const flushFacts = () => {
      if (!facts.length) return;
      parts.push(`<ul class="fact-list">${facts.join("")}</ul>`);
      facts.length = 0;
    };
    chosen.forEach((item) => {
      if (item.type === "fact") {
        facts.push(item.html);
        return;
      }
      flushFacts();
      parts.push(item.html);
    });
    flushFacts();
    return parts.join("");
  }

  function renderProfileGroup(spec) {
    const preview = (spec.previewHtml || "").trim();
    const details = (spec.detailsHtml || "").trim();
    if (!preview && !details) return "";
    const explore = details
      ? `<details class="profile-group-explore">
          <summary class="section-explore-summary"><span class="explore-all-label">Explore details</span></summary>
          <div class="profile-group-details">${details}</div>
        </details>`
      : "";
    return `<section class="panel profile-group" data-group-key="${escapeHtml(spec.key)}">
      <div class="panel-head"><h2>${escapeHtml(spec.title)}</h2></div>
      ${spec.blurb ? `<p class="section-helper">${escapeHtml(spec.blurb)}</p>` : ""}
      ${preview}
      ${explore}
    </section>`;
  }

  function mercuryGlanceTitle(card) {
    if (!card) return "";
    if (card.key === "thinking_style") return "Thinking style";
    if (card.key === "communication_style") return "Communication style";
    if (card.key === "learning_style") return "Learning style";
    if (card.key === "watchout") return "Watchout";
    return card.title || "";
  }

  function mercuryGlanceText(card, person, options) {
    if (!card) return "";
    const overviewOnly = options && options.overviewOnly;
    if (overviewOnly && card.key === "watchout") {
      const tags = card.tags || [];
      for (const tag of tags) {
        const bounded = OVERVIEW_MERCURY_GLANCE_PRESENTATION.watchout[tag];
        if (bounded) return contextualizeNeutralSentence(bounded, person);
      }
    }
    if (card.display_template) return fillPersonTemplate(card.display_template, person);
    return contextualizeNeutralSentence(card.text, person);
  }

  function renderMercuryThinkGlance(synthesis, person, options) {
    const cards = (synthesis && synthesis.thinking_at_a_glance) || [];
    if (!cards.length) return "";
    const overviewOnly = options && options.cardsOnly;
    const items = cards.map((card) => `<article class="think-glance-card" data-glance-key="${escapeHtml(card.key)}">
      <h3>${escapeHtml(mercuryGlanceTitle(card))}</h3>
      <p>${escapeHtml(mercuryGlanceText(card, person, { overviewOnly }))}</p>
    </article>`).join("");
    if (options && options.cardsOnly) {
      return `<div class="think-glance">${items}</div>`;
    }
    return `<section class="panel think-style-glance level-1">
      <div class="panel-head"><h2>Thinking at a glance</h2></div>
      <div class="think-glance">${items}</div>
    </section>`;
  }

  function renderOverviewMercuryRecurringChip(signal) {
    if (!signal) return "";
    return `<span class="overview-recurring-chip" data-signal="${escapeHtml(signal.signal)}">${escapeHtml(overviewMercurySignalLabel(signal))}</span>`;
  }

  function renderMercuryOverviewRecurringPatterns(synthesis, audience) {
    const patterns = (synthesis && synthesis.strongest_patterns) || [];
    if (!patterns.length) return "";
    const chips = patterns.slice(0, OVERVIEW_MERCURY_RECURRING_LIMIT)
      .map((signal) => renderOverviewMercuryRecurringChip(signal))
      .filter(Boolean)
      .join("");
    if (!chips) return "";
    return `<div class="overview-mercury-recurring">
      <p class="overview-recurring-label">Recurring patterns</p>
      <div class="overview-recurring-chips">${chips}</div>
    </div>`;
  }

  function renderMercuryOverviewTakeaways(synthesis, audience, person) {
    const glance = renderMercuryThinkGlance(synthesis, person, { cardsOnly: true });
    const recurring = renderMercuryOverviewRecurringPatterns(synthesis, audience);
    if (!glance && !recurring) {
      const thinking = populatedMercurySection(synthesis, "thinking");
      if (!thinking) return `<p class="section-helper">${escapeHtml(recurringPatternsEmptyCopy(audience))}</p>`;
      const facts = synthesisFactMap(synthesis);
      const presentation = presentationTextMap(synthesis);
      const fallback = collectPreviewFacts(
        [thinking],
        facts,
        presentation,
        OVERVIEW_MERCURY_TAKEAWAY_LIMIT,
        renderQuietMercuryFact,
      );
      if (!fallback.length) return "";
      return `<ul class="fact-list">${fallback.join("")}</ul>`;
    }
    return `${glance}${recurring}`;
  }

  function renderOverviewTensions(synthesis) {
    const tensions = (synthesis && synthesis.resolved_tensions) || [];
    if (!tensions.length) return "";
    const facts = synthesisFactMap(synthesis);
    const first = tensions.slice(0, 1);
    return `<section class="panel overview-tensions">
      <div class="panel-head"><h2>Tensions to be aware of</h2></div>
      <div class="result-list-group result-list-group-tensions">${renderTensionRows(first, facts, { compact: true })}</div>
    </section>`;
  }

  function bridgeKindLabel(kind) {
    if (kind === "reinforcement") return "Reinforcement";
    if (kind === "friction") return "Friction";
    if (kind === "contrast") return "Contrast";
    return "";
  }

  function overviewBridgePatterns(bridge) {
    const all = (bridge && bridge.patterns) || [];
    const ids = (bridge && bridge.overview_pattern_ids) || [];
    if (ids.length) {
      const byId = new Map(all.map((pattern) => [pattern.id, pattern]));
      return ids.map((id) => byId.get(id)).filter(Boolean).slice(0, 2);
    }
    return all.slice(0, 2);
  }

  function renderThinkingToExecutionOverview(bridge) {
    const patterns = overviewBridgePatterns(bridge);
    if (!patterns.length) return "";
    const rows = patterns.map((pattern) => {
      const kind = bridgeKindLabel(pattern.kind);
      return `<article class="bridge-row" data-bridge-id="${escapeHtml(pattern.id)}">
        ${kind ? `<span class="bridge-kind">${escapeHtml(kind)}</span>` : ""}
        <strong class="bridge-title">${escapeHtml(pattern.title || "")}</strong>
        <p class="bridge-takeaway">${escapeHtml(pattern.presentation_text || "")}</p>
      </article>`;
    }).join("");
    return `<section class="panel thinking-to-execution">
      <div class="panel-head"><h2>From thinking to execution</h2></div>
      <div class="bridge-list">${rows}</div>
    </section>`;
  }

  function renderThinkingToExecutionEvidence(bridge) {
    const patterns = (bridge && bridge.patterns) || [];
    if (!patterns.length) return "";
    const rows = patterns.map((pattern) => {
      const mercuryProv = (pattern.mercury_provenance || []).map((item) => escapeHtml(item)).join(" · ");
      const marsProv = (pattern.mars_provenance || []).map((item) => escapeHtml(item)).join(" · ");
      return `<article class="bridge-evidence-row" data-bridge-id="${escapeHtml(pattern.id)}">
        <h3>${escapeHtml(pattern.title || "")}</h3>
        <details class="methodology-row">
          <summary>Mercury support</summary>
          <p class="meta">${escapeHtml(pattern.mercury_semantic || "")}</p>
          ${mercuryProv ? `<p class="meta">${mercuryProv}</p>` : ""}
        </details>
        <details class="methodology-row">
          <summary>Mars support</summary>
          <p class="meta">${escapeHtml(pattern.mars_semantic || "")}</p>
          ${marsProv ? `<p class="meta">${marsProv}</p>` : ""}
        </details>
        <details class="signal-why">
          <summary>Why this connection appears</summary>
          <p class="signal-why-label">${escapeHtml(pattern.why_this_appears || "")}</p>
        </details>
      </article>`;
    }).join("");
    return `<section class="panel thinking-to-execution-evidence">
      <div class="panel-head"><h2>Thinking → Execution evidence</h2></div>
      <div class="bridge-evidence-list">${rows}</div>
    </section>`;
  }

  function renderOverviewMarsRecurringChip(signal) {
    if (!signal) return "";
    return `<span class="overview-recurring-chip" data-signal="${escapeHtml(signal.signal)}">${escapeHtml(titleCaseSignal(signal.signal))}</span>`;
  }

  function renderMarsOverviewRecurringPatterns(synthesis) {
    const patterns = (synthesis && synthesis.repeated_signals) || [];
    if (!patterns.length) return "";
    const shown = patterns.slice(0, OVERVIEW_MARS_RECURRING_LIMIT);
    const chips = shown
      .map((signal) => renderOverviewMarsRecurringChip(signal))
      .filter(Boolean)
      .join("");
    if (!chips) return "";
    const label = shown.length === 1 ? "Recurring work pattern" : "Recurring work patterns";
    return `<div class="overview-mars-repeat">
      <p class="overview-recurring-label">${escapeHtml(label)}</p>
      <div class="overview-recurring-chips">${chips}</div>
    </div>`;
  }

  function renderProfileOverview(profile, marsProfile, person, audience, bridge) {
    const mercurySynthesis = (profile && profile.synthesis) || null;
    const marsSynthesis = (marsProfile && marsProfile.synthesis) || null;
    const thinks = renderMercuryOverviewTakeaways(mercurySynthesis, audience, person);
    const worksGlance = renderMarsWorkGlance(marsSynthesis, person, { cardsOnly: true });
    const marsRepeatHtml = renderMarsOverviewRecurringPatterns(marsSynthesis);
    const worksBody = `${worksGlance}${marsRepeatHtml}`;
    return `<div class="overview-grid">
      <section class="panel overview-dimension" data-overview-dimension="think">
        <div class="panel-head"><h2>${escapeHtml(howThinksHeading(person))}</h2></div>
        ${thinks}
        <button type="button" class="btn btn-ghost overview-cta" data-profile-tab="thinking">Explore Mercury</button>
      </section>
      <section class="panel overview-dimension" data-overview-dimension="work">
        <div class="panel-head"><h2>${escapeHtml(howWorksHeading(person))}</h2></div>
        ${worksBody}
        <button type="button" class="btn btn-ghost overview-cta" data-profile-tab="working">Explore work style</button>
      </section>
    </div>
    ${renderThinkingToExecutionOverview(bridge)}
    ${renderOverviewTensions(mercurySynthesis)}`;
  }

  function aspectGlyph(type) {
    const map = {
      conjunction: "☌",
      opposition: "☍",
      square: "□",
      trine: "△",
      sextile: "⚹",
    };
    return map[String(type || "").toLowerCase()] || "•";
  }

  function formatMajorAspectLine(aspect) {
    if (!aspect) return "";
    const glyph = aspectGlyph(aspect.aspect_type || aspect.type);
    const planet = aspect.planet || "";
    return `${glyph} ${planet}`.trim();
  }

  function deepFactText(factId, facts, presentation) {
    const fact = facts.get(factId);
    if (!fact) return "";
    return humanFactText(fact, presentation);
  }

  function renderDeepFactList(factIds, facts, presentation) {
    const items = (factIds || [])
      .map((id) => {
        const text = deepFactText(id, facts, presentation);
        if (!text) return "";
        const fact = facts.get(id);
        const risk = fact && fact.polarity === "risk";
        const marker = risk
          ? `<span class="risk-mark" title="Possible difficulty">Risk</span>`
          : `<span class="fact-bullet" aria-hidden="true">•</span>`;
        return `<li class="fact-item${risk ? " fact-risk" : ""}" data-fact-id="${escapeHtml(id)}">${marker}<span class="fact-text">${escapeHtml(text)}</span></li>`;
      })
      .filter(Boolean)
      .join("");
    return items ? `<ul class="fact-list deep-fact-list">${items}</ul>` : "";
  }

  function renderDeepSourceExplore(block, facts, presentation) {
    const allIds = block.fact_ids || [];
    if (!allIds.length) return "";
    // Full source lists every canonical fact id so the complete pack remains
    // inspectable. Highlights above use the same ids; they are not new evidence.
    const count = allIds.length;
    const label = count === 1
      ? "Explore all 1 source observation"
      : `Explore all ${count} source observations`;
    return `<details class="deep-source-explore">
      <summary class="section-explore-summary"><span class="explore-all-label">${escapeHtml(label)}</span></summary>
      <div class="deep-source-body">
        ${renderDeepFactList(allIds, facts, presentation)}
      </div>
    </details>`;
  }

  function renderDeepMercuryConfiguration(config) {
    if (!config) return "";
    const sign = config.mercury_sign
      ? `<p class="deep-config-line">Mercury in ${escapeHtml(config.mercury_sign)}</p>`
      : "";
    const house = config.house_available
      ? `<p class="deep-config-line">House ${escapeHtml(String(config.mercury_house))}</p>`
      : `<div class="deep-config-unavailable">
          <p class="deep-config-line">House unavailable</p>
          <p class="deep-config-note">${escapeHtml(config.house_unavailable_reason || "Birth time is required for house placement.")}</p>
        </div>`;
    const motion = config.mercury_motion
      ? `<p class="deep-config-line">${escapeHtml(titleCaseSignal(config.mercury_motion))}</p>`
      : "";
    const aspectLines = (config.aspects || [])
      .map((aspect) => `<li>${escapeHtml(formatMajorAspectLine(aspect))}</li>`)
      .join("");
    const aspects = aspectLines
      ? `<div class="deep-config-aspects">
          <h3>Major aspects</h3>
          <ul class="deep-aspect-list">${aspectLines}</ul>
        </div>`
      : `<p class="meta">No calculated major aspects in orb.</p>`;
    return `<section class="panel deep-mercury-config" data-deep-section="configuration">
      <div class="panel-head"><h2>Your Mercury</h2></div>
      <div class="deep-config-body">
        ${sign}
        ${house}
        ${motion}
        ${aspects}
      </div>
    </section>`;
  }

  function renderDeepFactorNarrative(narrative) {
    if (!narrative) return "";
    const subs = (narrative.subsections || []).map((item) => `<div class="deep-narrative-sub" data-narrative-sub="${escapeHtml(item.key)}">
      <h4>${escapeHtml(item.title)}</h4>
      <p>${escapeHtml(item.text)}</p>
    </div>`).join("");
    const deeper = subs
      ? `<details class="deep-deeper-themes">
          <summary class="section-explore-summary"><span class="explore-all-label">Explore deeper themes</span></summary>
          <div class="deep-narrative-subs">${subs}</div>
        </details>`
      : "";
    return `<div class="deep-factor-narrative">
      <p class="deep-core-theme">${escapeHtml(narrative.core_theme || "")}</p>
      <p class="deep-narrative-summary">${escapeHtml(narrative.summary || "")}</p>
      ${deeper}
    </div>`;
  }

  function renderDeepKeyObservations(block, facts, presentation) {
    const highlights = renderDeepFactList(block.highlight_fact_ids || [], facts, presentation);
    if (!highlights) return "";
    const count = (block.highlight_fact_ids || []).length;
    const label = count === 1
      ? "Key observations (1)"
      : `Key observations (${count})`;
    return `<details class="deep-key-observations">
      <summary class="section-explore-summary"><span class="explore-all-label">${escapeHtml(label)}</span></summary>
      <div class="deep-highlights">${highlights}</div>
    </details>`;
  }

  function renderDeepFactorBlock(block, facts, presentation, eyebrow, purposeFallback) {
    if (!block) return "";
    if (block.availability === "unavailable") {
      return `<section class="panel deep-factor-block deep-factor-unavailable" data-deep-factor="${escapeHtml(block.factor_type)}">
        <p class="deep-eyebrow">${escapeHtml(eyebrow)}</p>
        <div class="panel-head"><h2>${escapeHtml(block.title || eyebrow)}</h2></div>
        <p class="deep-unavailable-copy">${escapeHtml(block.unavailable_reason || "This layer is unavailable.")}</p>
      </section>`;
    }
    if (block.availability === "neutral_default") {
      return `<section class="panel deep-factor-block deep-factor-neutral" data-deep-factor="${escapeHtml(block.factor_type)}">
        <p class="deep-eyebrow">${escapeHtml(eyebrow)}</p>
        <div class="panel-head"><h2>${escapeHtml(block.title)}</h2></div>
        <p class="section-helper">No additional motion-specific source interpretation is active.</p>
      </section>`;
    }
    return `<section class="panel deep-factor-block" data-deep-factor="${escapeHtml(block.factor_type)}" data-factor-key="${escapeHtml(block.factor_key || "")}">
      <p class="deep-eyebrow">${escapeHtml(eyebrow)}</p>
      <div class="panel-head"><h2>${escapeHtml(block.title)}</h2></div>
      ${renderDeepFactorNarrative(block.narrative)}
      ${renderDeepKeyObservations(block, facts, presentation)}
      ${renderDeepSourceExplore(block, facts, presentation)}
    </section>`;
  }

  function renderDeepThemeList(items, labelKey) {
    const rows = (items || [])
      .map((item) => {
        const label = item.label
          || titleCaseSignal(item[labelKey] || item.tag || item.signal || "");
        return label ? `<li>${escapeHtml(label)}</li>` : "";
      })
      .filter(Boolean)
      .join("");
    return rows ? `<ul class="deep-theme-list">${rows}</ul>` : "";
  }

  function renderDeepAspectInteraction(interaction) {
    if (!interaction || !interaction.available) return "";
    const parts = [];
    if ((interaction.adds || []).length) {
      parts.push(`<div class="deep-modifier-group" data-modifier="adds">
        <h4>Adds</h4>
        ${renderDeepThemeList(interaction.adds, "tag")}
      </div>`);
    }
    if ((interaction.reinforcing || []).length) {
      parts.push(`<div class="deep-modifier-group" data-modifier="reinforces">
        <h4>Reinforces</h4>
        ${renderDeepThemeList(interaction.reinforcing, "signal")}
      </div>`);
    }
    if ((interaction.contrasting || []).length) {
      parts.push(`<div class="deep-modifier-group" data-modifier="contrasts">
        <h4>Complicates</h4>
        ${renderDeepThemeList(interaction.contrasting, "label")}
      </div>`);
    }
    const synthesis = interaction.statement
      ? `<p class="deep-interaction-statement">${escapeHtml(interaction.statement)}</p>`
      : "";
    if (!parts.length && !synthesis) return "";
    return `<div class="deep-aspect-synthesis">
      <h3>What this aspect changes</h3>
      ${synthesis}
      ${parts.length ? `<div class="deep-modifier-details">${parts.join("")}</div>` : ""}
    </div>`;
  }

  function renderDeepAspectSource(block, facts, presentation) {
    const allIds = block.fact_ids || [];
    const highlights = renderDeepFactList(block.highlight_fact_ids || [], facts, presentation);
    const fullList = allIds.length
      ? renderDeepFactList(allIds, facts, presentation)
      : "";
    if (!highlights && !fullList) {
      return `<p class="section-helper">No source observations for this aspect.</p>`;
    }
    const count = allIds.length;
    const label = count
      ? (count === 1 ? "Source observations (1)" : `Source observations (${count})`)
      : "Source observations";
    return `<details class="deep-aspect-source-explore">
      <summary class="section-explore-summary"><span class="explore-all-label">${escapeHtml(label)}</span></summary>
      <div class="deep-aspect-source-body">
        ${highlights ? `<div class="deep-aspect-highlights"><h4>Highlights</h4>${highlights}</div>` : ""}
        ${fullList ? `<div class="deep-aspect-full-source"><h4>All source observations</h4>${fullList}</div>` : ""}
      </div>
    </details>`;
  }

  function renderDeepAspectBlock(block, facts, presentation) {
    if (!block || !block.identity) return "";
    const title = block.identity.title
      || `Mercury ${aspectPhrase(block.identity.aspect_type, block.identity.planet)} ${block.identity.planet}`;
    return `<article class="panel deep-aspect-block" data-deep-aspect="${escapeHtml(block.identity.factor_key)}">
      <p class="deep-eyebrow">Aspect modifier</p>
      <div class="panel-head"><h2>${escapeHtml(title)}</h2></div>
      ${renderDeepAspectInteraction(block.interaction)}
      <div class="deep-aspect-source">
        ${renderDeepAspectSource(block, facts, presentation)}
      </div>
    </article>`;
  }

  function renderDeepIntegrated(integrated) {
    const items = integrated || [];
    if (!items.length) return "";
    const rows = items.map((item) => {
      const evidence = (item.provenance_keys || [])
        .map((key) => `<li>${escapeHtml(provenanceLabel(key))}</li>`)
        .join("");
      return `<li class="deep-integrated-item" data-integrated-key="${escapeHtml(item.key || "")}">
        <p class="deep-integrated-text">${escapeHtml(item.text || "")}</p>
        ${evidence ? `<details class="deep-integrated-evidence">
          <summary>Evidence</summary>
          <ul class="deep-provenance-list">${evidence}</ul>
        </details>` : ""}
      </li>`;
    }).join("");
    return `<section class="panel deep-integrated" data-deep-section="integrated">
      <p class="deep-eyebrow">How it works together</p>
      <div class="panel-head"><h2>Integrated Mercury</h2></div>
      <p class="section-helper">What kind of Mercury this chart produces. Supporting relationships stay under Evidence.</p>
      <ol class="deep-integrated-list">${rows}</ol>
    </section>`;
  }

  function renderDeepMercury(synthesis) {
    const deep = synthesis && synthesis.deep_profile;
    if (!deep) {
      return `<p class="section-helper">Deep Mercury presentation is not available for this profile.</p>`;
    }
    const facts = synthesisFactMap(synthesis);
    const presentation = presentationTextMap(synthesis);
    const aspects = (deep.aspects || [])
      .map((block) => renderDeepAspectBlock(block, facts, presentation))
      .join("");
    return `<div class="deep-mercury" data-deep-mercury="true">
      ${renderDeepMercuryConfiguration(deep.configuration)}
      ${renderDeepFactorBlock(deep.sign, facts, presentation, "Base Mercury", "The sign is the base Mercury mechanism.")}
      ${renderDeepFactorBlock(deep.house, facts, presentation, "Expression", "Where / through what domain this Mercury is expressed.")}
      ${renderDeepFactorBlock(deep.motion, facts, presentation, "Processing modifier", "What processing modifier is present.")}
      ${aspects ? `<div class="deep-aspects-wrap" data-deep-section="aspects">
        <p class="deep-section-label">Aspect modifiers</p>
        <div class="deep-aspects">${aspects}</div>
      </div>` : ""}
      ${renderDeepIntegrated(deep.integrated)}
    </div>`;
  }

  function renderWorkLensSectionDetails(section, facts, presentation, excludeFactIds) {
    const excluded = excludeFactIds || new Set();
    const remainingIds = (section.resolved_fact_ids || []).filter((id) => !excluded.has(id));
    const exploreSection = {
      key: section.key,
      title: section.title,
      categories: section.categories,
      resolved_fact_ids: remainingIds,
      resolved_fact_count: remainingIds.length,
      factor_keys: section.factor_keys,
      factor_count: section.factor_count,
      preview_fact_ids: [],
    };
    if (!remainingIds.length) {
      return `<section class="profile-subsection" data-section-key="${escapeHtml(section.key)}">
        <h3>${escapeHtml(section.title)}</h3>
        <p class="section-helper">Key observations for this group are already shown in the preview above.</p>
      </section>`;
    }
    return `<section class="profile-subsection" data-section-key="${escapeHtml(section.key)}">
      <h3>${escapeHtml(section.title)}</h3>
      ${renderSectionFactorExplore(exploreSection, facts, presentation)}
    </section>`;
  }

  function renderThinkingGroup(spec, synthesis, audience) {
    const facts = synthesisFactMap(synthesis);
    const presentation = presentationTextMap(synthesis);
    const sections = spec.sections
      .map((key) => populatedMercurySection(synthesis, key))
      .filter(Boolean);
    const patterns = spec.includeThinkingPatterns
      ? ((synthesis && synthesis.strongest_patterns) || []).filter((signal) => {
        const keys = signal.section_keys || [];
        return keys.some((key) => spec.sections.includes(key));
      })
      : [];
    const tensions = spec.includeTensions
      ? ((synthesis && synthesis.resolved_tensions) || [])
      : [];
    if (!sections.length && !patterns.length && !tensions.length) return "";
    const pieces = [];
    patterns.forEach((signal) => {
      const html = renderCompactSignalRow(signal, facts, presentation);
      if (html) pieces.push({ type: "pattern", html });
    });
    sections.forEach((section) => {
      (section.preview_fact_ids || []).forEach((id) => {
        const html = renderQuietMercuryFact(facts.get(id), presentation);
        if (html) pieces.push({ type: "fact", html, factId: id });
      });
    });
    if (tensions.length) {
      pieces.push({
        type: "tension",
        html: renderTensionRows(tensions.slice(0, 1), facts, { compact: true }),
      });
    }
    const chosen = pieces.filter((item) => item && item.html).slice(0, GROUP_PREVIEW_LIMIT);
    const previewFactIds = new Set(
      chosen.filter((item) => item.type === "fact" && item.factId).map((item) => item.factId)
    );
    const previewHtml = joinPreviewPieces(chosen, GROUP_PREVIEW_LIMIT);
    const detailsHtml = [
      sections.map((section) => renderWorkLensSectionDetails(
        {
          ...section,
          title: sectionDisplayTitle(section, audience),
        },
        facts,
        presentation,
        previewFactIds
      )).join(""),
      spec.includeTensions && tensions.length
        ? `<div class="profile-subsections-tensions">${renderTensionRows(tensions, facts, { compact: true })}</div>`
        : "",
    ].join("");
    return renderProfileGroup({
      key: spec.key,
      title: spec.title,
      blurb: spec.blurb,
      previewHtml,
      detailsHtml,
    });
  }

  function renderMercuryWorkLens(synthesis, audience) {
    const groups = MERCURY_THINKING_GROUPS
      .map((spec) => renderThinkingGroup(spec, synthesis, audience))
      .join("");
    if (!groups) return "";
    return `<section class="deep-work-lens" data-deep-section="work-lens">
      <p class="deep-eyebrow">Work lens</p>
      <h2 class="dimension-heading deep-work-lens-heading">How this Mercury can show up at work</h2>
      <p class="section-helper">Work translation of the Mercury configuration above. Reused observations are not new evidence.</p>
      ${groups}
    </section>`;
  }

  function renderProfileThinking(synthesis, audience) {
    const deepHtml = renderDeepMercury(synthesis);
    const workHtml = renderMercuryWorkLens(synthesis, audience);
    const html = `${deepHtml}${workHtml}`.trim();
    return html || `<p class="section-helper">No Mercury evidence is available for this profile.</p>`;
  }

  function renderWorkingGroup(spec, synthesis, person) {
    const facts = synthesisFactMap(synthesis);
    const presentation = presentationTextMap(synthesis);
    const sections = spec.sections
      .map((key) => populatedMarsSection(synthesis, key))
      .filter(Boolean);
    const patterns = spec.includeMarsPatterns
      ? ((synthesis && synthesis.repeated_signals) || [])
      : [];
    const professional = spec.includeProfessional
      ? populatedMarsSection(synthesis, "professional_associations")
      : null;
    if (!sections.length && !patterns.length && !professional) return "";
    const pieces = [];
    sections.forEach((section) => {
      (section.preview_fact_ids || []).forEach((id) => {
        const html = renderMarsPreviewFactItem(facts.get(id), presentation);
        if (html) pieces.push({ type: "fact", html });
      });
    });
    patterns.forEach((signal) => {
      const html = renderCompactSignalRow(signal, facts, presentation);
      if (html) pieces.push({ type: "pattern", html });
    });
    const previewHtml = joinPreviewPieces(pieces, GROUP_PREVIEW_LIMIT);
    const detailsHtml = [
      sections.map((section) => `<section class="profile-subsection" data-section-key="${escapeHtml(section.key)}">
        <h3>${escapeHtml(marsSectionTitle(section, person))}</h3>
        ${renderMarsSectionBody(section, facts, presentation)}
      </section>`).join(""),
      professional
        ? `<details class="watchouts-block profile-professional">
            <summary><span class="watchouts-summary-main">${escapeHtml(marsSectionTitle(professional, person))}</span></summary>
            <p class="section-helper">These are source-described associations and aptitudes, not recommended jobs, verified competencies, or hiring recommendations.</p>
            <div class="watchouts-body">${renderMarsSectionBody(professional, facts, presentation)}</div>
          </details>`
        : "",
    ].join("");
    return renderProfileGroup({
      key: spec.key,
      title: spec.title,
      blurb: spec.blurb,
      previewHtml,
      detailsHtml,
    });
  }

  function renderProfileWorking(marsProfile, error, person) {
    if (error) {
      return `<p class="status-line error how-you-work-error" role="status">${escapeHtml(error)}</p>`;
    }
    const synthesis = (marsProfile && marsProfile.synthesis) || null;
    const groups = MARS_WORKING_GROUPS
      .map((spec) => renderWorkingGroup(spec, synthesis, person))
      .join("");
    return groups || `<p class="section-helper">No work-style evidence is available for this profile.</p>`;
  }

  function renderMercuryCalculatedFactors(profile) {
    const calc = (profile && profile.calculated) || {};
    if (!calc.mercury_sign && calc.mercury_house == null && !calc.mercury_motion) return "";
    const motion = String(calc.mercury_motion || "");
    const motionHtml = motion.toLowerCase() === "retrograde"
      ? `<span class="motion-rx">Retrograde</span>`
      : escapeHtml(titleCaseSignal(motion) || "—");
    const aspectList = (calc.aspects || [])
      .map((aspect) => `<li>${escapeHtml(formatAspectChip(aspect))}</li>`)
      .join("");
    return `<details class="methodology-row">
      <summary>Calculated thinking factors</summary>
      <p class="self-calc-line">Mercury in ${escapeHtml(calc.mercury_sign || "—")} · House ${escapeHtml(String(calc.mercury_house ?? "—"))} · ${motionHtml}</p>
      ${aspectList ? `<ul class="self-aspect-list">${aspectList}</ul>` : `<p class="meta">No calculated aspects in orb.</p>`}
    </details>`;
  }

  function renderEvidencePatterns(mercurySynthesis, marsSynthesis) {
    const mercuryHtml = renderStrongestPatterns(mercurySynthesis, "person", "");
    const marsHtml = renderMarsRecurringPatterns(marsSynthesis);
    if (!mercuryHtml && !marsHtml) return "";
    return `${mercuryHtml}${marsHtml}`;
  }

  function renderProfileEvidence(profile, marsProfile, displayName, person, bridge) {
    const mercurySynthesis = (profile && profile.synthesis) || null;
    const factCount = profile ? countActiveSourceFacts(profile) : 0;
    const mercuryCalc = renderMercuryCalculatedFactors(profile);
    const patterns = renderEvidencePatterns(mercurySynthesis, marsProfile && marsProfile.synthesis);
    const tensions = renderResolvedTensions(mercurySynthesis, resolveProfileAudience(displayName));
    const conditional = renderConditionalTensions(mercurySynthesis);
    const mercuryMethod = profile
      ? renderDetailsMethodology(profile, mercurySynthesis, displayName, factCount)
      : "";
    const marsMethod = marsProfile
      ? renderMarsDetailsMethodology(marsProfile, marsProfile.synthesis, person)
      : "";
    return `<div class="evidence-stack">
      ${mercuryCalc}
      ${patterns}
      ${renderThinkingToExecutionEvidence(bridge)}
      ${tensions}
      ${conditional}
      ${mercuryMethod}
      ${marsMethod}
    </div>`;
  }

  function profileTabFromHash() {
    const raw = String(location.hash || "").replace("#", "");
    return PROFILE_TABS.includes(raw) ? raw : "overview";
  }

  function applyProfileTab(tab) {
    const next = PROFILE_TABS.includes(tab) ? tab : "overview";
    activeProfileTab = next;
    PROFILE_TABS.forEach((key) => {
      const panel = selfProfileContent.querySelector(`[data-profile-panel="${key}"]`);
      const nav = selfProfileContent.querySelector(`.profile-tab-nav [data-profile-tab="${key}"]`);
      if (panel) panel.hidden = key !== next;
      if (nav) {
        nav.classList.toggle("is-active", key === next);
        nav.setAttribute("aria-selected", key === next ? "true" : "false");
      }
    });
    const hash = `#${next}`;
    if (location.hash !== hash) history.replaceState(null, "", hash);
  }

  function bindProfileTabClicks() {
    selfProfileContent.querySelectorAll("[data-profile-tab]").forEach((btn) => {
      btn.addEventListener("click", () => applyProfileTab(btn.getAttribute("data-profile-tab")));
    });
  }

  function renderProfileTabNav() {
    const items = [
      ["overview", "Overview"],
      ["thinking", "Mercury"],
      ["working", "Working"],
      ["evidence", "Evidence"],
    ].map(([key, label]) => `<button type="button" class="profile-tab${key === "overview" ? " is-active" : ""}" data-profile-tab="${key}" role="tab" aria-selected="${key === "overview" ? "true" : "false"}">${escapeHtml(label)}</button>`).join("");
    return `<nav class="profile-tab-nav" role="tablist" aria-label="Profile sections">${items}</nav>`;
  }

  function renderHowYouWorkDimension(profile, error, person) {
    return renderProfileWorking(profile, error, person);
  }

  function renderSelfProfile(profile, displayName, marsProfile, marsError, bridge) {
    const synthesis = (profile && profile.synthesis) || null;
    const audience = resolveProfileAudience(displayName);
    const person = currentPersonPerspective();
    setBrandTitleForProfile(audience, displayName);
    activeProfileTab = profileTabFromHash();

    selfProfileContent.innerHTML = `
      ${renderProfileTabNav()}
      <div class="profile-tab-panels">
        <div class="profile-tab-panel" data-profile-panel="overview" role="tabpanel">${renderProfileOverview(profile, marsProfile, person, audience, bridge)}</div>
        <div class="profile-tab-panel how-you-think" data-profile-panel="thinking" data-dimension="think" role="tabpanel" hidden>
          ${renderProfileThinking(synthesis, audience)}
        </div>
        <div class="profile-tab-panel how-you-work" data-profile-panel="working" data-dimension="work" role="tabpanel" hidden>
          <h2 class="dimension-heading">${escapeHtml(howWorksHeading(person))}</h2>
          ${renderProfileWorking(marsProfile, marsError, person)}
        </div>
        <div class="profile-tab-panel" data-profile-panel="evidence" role="tabpanel" hidden>
          <h2 class="dimension-heading">Evidence</h2>
          ${renderProfileEvidence(profile, marsProfile, displayName, person, bridge)}
        </div>
      </div>
    `;
    bindProfileTabClicks();
    applyProfileTab(activeProfileTab);
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
    const sexEl = document.getElementById("self-sex");
    const bridgePayload = { ...payload };
    if (displayName) bridgePayload.display_name = displayName;
    if (sexEl && sexEl.value) bridgePayload.sex = sexEl.value;

    setStatus(selfSetupStatus, "Building source-backed profile…", "loading");
    setStatus(selfProfileStatus, "Building source-backed profile…", "loading");
    showSelfProfileShell();
    selfProfileContent.innerHTML = "";

    const mercuryPromise = apiPost("/api/v1/mercury-source-profile", payload);
    const marsPromise = apiPost("/api/v1/mars-source-profile", payload);
    const bridgePromise = apiPost("/api/v1/thinking-to-execution", bridgePayload);

    async function loadBridge() {
      try {
        return await bridgePromise;
      } catch (_err) {
        return null;
      }
    }

    let mercury = null;
    try {
      mercury = await mercuryPromise;
    } catch (err) {
      setStatus(selfSetupStatus, err.message, "error");
      setStatus(selfProfileStatus, err.message, "error");
      try {
        const marsOnly = await marsPromise;
        selfProfileContent.innerHTML = renderHowYouWorkDimension(marsOnly, null, currentPersonPerspective());
      } catch (marsErr) {
        selfProfileContent.innerHTML = renderHowYouWorkDimension(null, marsErr.message, currentPersonPerspective());
      }
      return;
    }

    closeSelfDrawer();
    renderSelfProfile(mercury, displayName, null, null, null);
    setStatus(selfProfileStatus, "");
    setStatus(selfSetupStatus, "");

    try {
      const mars = await marsPromise;
      renderSelfProfile(mercury, displayName, mars, null, await loadBridge());
    } catch (err) {
      renderSelfProfile(mercury, displayName, null, err.message, await loadBridge());
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
