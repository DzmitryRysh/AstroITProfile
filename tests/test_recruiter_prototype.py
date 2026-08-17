import unittest
from pathlib import Path

from fastapi.responses import FileResponse
from starlette.routing import Mount, Route

from app.core.app import RECRUITER_UI_DIR, create_app

RECRUITER_INDEX = RECRUITER_UI_DIR / "index.html"
RECRUITER_CSS = RECRUITER_UI_DIR / "styles.css"
RECRUITER_JS = RECRUITER_UI_DIR / "app.js"


class RecruiterPrototypeAssetTests(unittest.TestCase):
    def test_recruiter_html_exists(self):
        self.assertTrue(RECRUITER_INDEX.is_file())

    def test_recruiter_css_exists(self):
        self.assertTrue(RECRUITER_CSS.is_file())

    def test_recruiter_js_exists(self):
        self.assertTrue(RECRUITER_JS.is_file())

    def test_recruiter_dir_is_pathlib_based(self):
        self.assertIsInstance(RECRUITER_UI_DIR, Path)
        self.assertTrue(RECRUITER_UI_DIR.is_dir())
        self.assertEqual(RECRUITER_UI_DIR.name, "recruiter")


class RecruiterPrototypeRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()

    def test_recruiter_route_is_registered(self):
        paths = {getattr(route, "path", None) for route in self.app.routes}
        self.assertIn("/recruiter", paths)

    def test_recruiter_serves_intended_index_file(self):
        route = next(
            item
            for item in self.app.routes
            if isinstance(item, Route) and item.path == "/recruiter"
        )
        response = route.endpoint()
        self.assertIsInstance(response, FileResponse)
        self.assertEqual(Path(response.path).resolve(), RECRUITER_INDEX.resolve())
        body = RECRUITER_INDEX.read_text(encoding="utf-8")
        self.assertIn("AstroIT", body)
        self.assertIn("Team Intelligence", body)
        self.assertIn("/recruiter/assets/styles.css", body)
        self.assertIn("/recruiter/assets/app.js", body)

    def test_recruiter_assets_mount_uses_ui_directory(self):
        mount = next(
            item
            for item in self.app.routes
            if isinstance(item, Mount) and item.path == "/recruiter/assets"
        )
        self.assertEqual(Path(mount.app.directory).resolve(), RECRUITER_UI_DIR.resolve())
        self.assertTrue((RECRUITER_UI_DIR / "styles.css").is_file())
        self.assertTrue((RECRUITER_UI_DIR / "app.js").is_file())

    def test_existing_api_routes_remain_registered(self):
        paths = {getattr(route, "path", None) for route in self.app.routes}
        self.assertIn("/api/v1/profile", paths)
        self.assertIn("/api/v1/mercury-work-profile", paths)
        self.assertIn("/api/v1/mercury-source-profile", paths)
        self.assertIn("/api/v1/candidate-compare", paths)
        self.assertIn("/api/v1/team-map", paths)
        self.assertIn("/api/v1/team-gap", paths)
        self.assertIn("/api/v1/candidate-team-impact", paths)
        self.assertIn("/api/v1/workspaces", paths)
        self.assertIn("/", paths)
        self.assertIn("/health", paths)


class RecruiterUxPolishTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = RECRUITER_INDEX.read_text(encoding="utf-8")
        cls.css = RECRUITER_CSS.read_text(encoding="utf-8")
        cls.js = RECRUITER_JS.read_text(encoding="utf-8")
        cls.blob = f"{cls.html}\n{cls.css}\n{cls.js}"

    def test_setup_forms_are_not_primary_visible_content(self):
        self.assertIn('id="empty-state"', self.html)
        self.assertIn('id="setup-overlay"', self.html)
        self.assertIn("hidden", self.html.split('id="setup-overlay"', 1)[1].split(">", 1)[0])
        empty_pos = self.html.find('id="empty-state"')
        members_pos = self.html.find('id="members-list"')
        self.assertLess(empty_pos, members_pos)
        self.assertIn("setup-drawer", self.html)

    def test_workspace_empty_state_exists(self):
        self.assertIn("Explore Yourself", self.html)
        self.assertIn("Understand how you think, communicate and learn", self.html)
        self.assertIn("Load Demo Scenario", self.html)
        self.assertIn("Set Up Team", self.html)

    def test_explore_yourself_entry_and_self_profile_input(self):
        self.assertIn('id="explore-yourself"', self.html)
        self.assertIn('id="self-overlay"', self.html)
        self.assertIn('id="self-drawer"', self.html)
        self.assertIn('id="build-my-profile"', self.html)
        self.assertIn("Build My Profile", self.html)
        self.assertIn('id="self-birth-date"', self.html)
        self.assertIn('id="self-birth-place"', self.html)
        self.assertIn('list="places-list"', self.html.split('id="self-birth-place"', 1)[1].split(">", 1)[0])
        self.assertIn('data-self-demo="avdey"', self.html)
        self.assertIn('data-self-demo="vlad"', self.html)
        self.assertIn('data-self-demo="dzmitry"', self.html)
        self.assertIn("Back to Start", self.html)
        self.assertIn("Build a Team", self.html)

    def test_self_profile_calls_mercury_source_profile_endpoint(self):
        self.assertIn('/api/v1/mercury-source-profile', self.js)
        self.assertIn("buildMyProfile", self.js)
        self.assertIn("renderSelfProfile", self.js)
        self.assertIn("Key recurring patterns", self.js)
        self.assertIn("renderStrongestPatterns", self.js)
        self.assertIn("renderSynthesisSections", self.js)
        self.assertIn("Explore full source evidence", self.js)
        self.assertIn("Details &amp; methodology", self.js)
        self.assertIn("Tensions in your profile", self.js)
        self.assertIn("Tensions in this profile", self.js)
        self.assertIn("Conditional tensions", self.js)
        self.assertIn("Conditional source notes", self.js)
        self.assertIn("Profile notes", self.js)
        self.assertIn("Why AstroIT shows this", self.js)
        self.assertIn("Source-Specific Claims", self.js)
        self.assertIn("Risks / Possible Difficulties", self.js)
        self.assertIn("fact-risk", self.js)
        self.assertIn("motion-rx", self.js)
        self.assertIn("Retrograde", self.js)
        # Presentation only — preserve source wording in evidence; human copy is additive.
        self.assertIn("escapeHtml(fact.text)", self.js)
        self.assertIn("humanFactText", self.js)
        self.assertIn("presentation_text_by_fact_id", self.js)
        self.assertNotIn("communication challenge", self.js.lower())
        self.assertNotIn("confidence risk", self.js.lower())
        self.assertNotIn("red flags", self.js.lower())
        self.assertNotIn("inferTeamFunction", self.js)
        self.assertNotIn("hardcodedProfile", self.js)

    def test_self_mode_title_and_presentation_hierarchy(self):
        self.assertIn('SELF_BRAND_TITLE = "Your Mercury Profile"', self.js)
        self.assertIn('DEFAULT_BRAND_TITLE = "Team Intelligence"', self.js)
        self.assertIn("setBrandTitleMode", self.js)
        self.assertIn("setBrandTitleForProfile", self.js)
        self.assertIn("resolveProfileAudience", self.js)
        self.assertIn('setBrandTitleMode("self")', self.js)
        self.assertIn("Team Intelligence", self.html)
        # Fact-count status is not the primary hierarchy; technical meta holds the count.
        self.assertNotIn("Source profile ready ·", self.js)
        self.assertIn("self-tech-meta", self.js)
        self.assertIn("active source facts were used in this profile", self.js)
        # Recurring Why disclosure collapsed by default.
        self.assertIn('class="signal-why"', self.js)
        self.assertIn("Why this appears", self.js)
        self.assertNotIn('class="signal-why" open', self.js)
        self.assertNotIn("<details class=\"signal-why\" open", self.js)
        # Factor cards live under collapsed source evidence; start closed.
        self.assertIn('class="factor-card"', self.js)
        self.assertIn("source-evidence-block", self.js)
        self.assertNotIn('class="source-evidence-block" open', self.js)
        self.assertNotIn('source-evidence-block" open', self.js)
        self.assertIn("source statements", self.js)
        self.assertIn("Supported by", self.js)
        self.assertIn("profile factors", self.js)
        self.assertNotIn("independent signals", self.js)
        self.assertIn("compactProvenanceLabel", self.js)
        self.assertIn("factor-summary-meta", self.js)
        # Compact fact rows, quieter risks, collapsed source-specific + traceability.
        self.assertIn("fact-bullet", self.js)
        self.assertIn("risk-mark", self.js)
        self.assertIn('class="source-specific-block"', self.js)
        self.assertNotIn('class="source-specific-block" open', self.js)
        self.assertIn("trace-details", self.js)
        self.assertNotIn('trace-details" open', self.js)
        self.assertNotIn('class="trace-details" open', self.js)
        self.assertIn("contrast-sources", self.js)
        # Synthesis is primary; legacy top-level repeats/tensions are not a second path.
        self.assertIn("synthesis.strongest_patterns", self.js)
        self.assertIn("synthesis.resolved_tensions", self.js)
        self.assertIn("preview_fact_ids", self.js)
        self.assertNotIn("renderRepeatedSignals(profile.repeated_signals)", self.js)
        self.assertNotIn("profile.contrasting_signals", self.js)
        self.assertNotIn("What repeats in your profile", self.js)
        self.assertNotIn("Patterns that repeat", self.js)
        # Team Intelligence product title remains the default HTML heading.
        self.assertIn('<h1 class="brand-title">Team Intelligence</h1>', self.html)

    def test_visual_hierarchy_and_secondary_details(self):
        # Helper text uses dedicated class (not trait styling).
        self.assertIn('class="section-helper"', self.js)
        self.assertIn(".section-helper", self.css)
        patterns_fn = self.js.split("function renderStrongestPatterns", 1)[1].split(
            "function renderSectionBody", 1
        )[0]
        tensions_fn = self.js.split("function renderResolvedTensions", 1)[1].split(
            "function renderConditionalTensions", 1
        )[0]
        self.assertIn("section-helper", patterns_fn)
        self.assertIn("section-helper", tensions_fn)
        self.assertNotIn("patterns-intro", self.js)
        self.assertNotIn("tension-intro", self.js)

        # Tensions before watch-outs; details zone last.
        self_profile_fn = self.js.split("function renderSelfProfile", 1)[1].split(
            "async function buildMyProfile", 1
        )[0]
        tensions_pos = self_profile_fn.find("renderResolvedTensions")
        watchouts_pos = self_profile_fn.find("renderContextWatchOuts")
        details_pos = self_profile_fn.find("renderDetailsMethodology")
        self.assertGreater(watchouts_pos, tensions_pos)
        self.assertGreater(details_pos, watchouts_pos)

        # Watch-outs collapsed by default; preview only inside expanded body.
        self.assertIn("function renderContextWatchOuts", self.js)
        self.assertIn('class="watchouts-block"', self.js)
        self.assertNotIn('class="watchouts-block" open', self.js)
        self.assertIn('data-section-key="context_risks"', self.js)
        self.assertIn('if (section.key === "context_risks") return ""', self.js)
        watchouts_fn = self.js.split("function renderContextWatchOuts", 1)[1].split(
            "function renderTensionRows", 1
        )[0]
        self.assertIn("renderSectionBody(section, facts, presentation)", watchouts_fn)
        self.assertIn("watchouts-body", watchouts_fn)

        # Secondary details zone groups conditional / evidence / why.
        self.assertIn("Details &amp; methodology", self.js)
        self.assertIn("details-methodology", self.js)
        self.assertIn("renderConditionalSourceNotesRow", self.js)
        self.assertIn("renderSourceEvidenceRow", self.js)
        self.assertIn("renderTraceabilityRow", self.js)
        details_fn = self.js.split("function renderDetailsMethodology", 1)[1].split(
            "function renderSelfProfile", 1
        )[0]
        self.assertIn("renderConditionalSourceNotesRow", details_fn)
        self.assertIn("renderSourceEvidenceRow", details_fn)
        self.assertIn("renderTraceabilityRow", details_fn)
        self.assertNotIn('class="trace-block"', self.js)
        self.assertNotIn("source-evidence-panel", self.js)
        # Fact count is contextual metadata inside Why, not a peer card headline.
        self.assertIn("active source facts were used in this profile", self.js)
        self.assertNotIn("<p class=\"self-tech-meta\">${escapeHtml(String(factCount))} active source facts</p>", self.js)
        # Conditional omitted when empty.
        self.assertIn("if (!groups.length) return \"\"", self.js)
        # No hiring/risk framing for watch-outs.
        lowered = self.js.lower()
        self.assertNotIn("red flags", lowered)
        self.assertNotIn("hiring risk", lowered)
        self.assertNotIn("candidate risk", lowered)

    def test_result_list_groups(self):
        patterns_fn = self.js.split("function renderStrongestPatterns", 1)[1].split(
            "function renderSectionBody", 1
        )[0]
        tensions_fn = self.js.split("function renderResolvedTensions", 1)[1].split(
            "function renderConditionalTensions", 1
        )[0]
        helpers = self.js.split("function recurringPatternsExplanation", 1)[1].split(
            "function showWorkspaceShell", 1
        )[0]
        # Text labels removed.
        self.assertNotIn("Recurring themes", self.js)
        self.assertNotIn("Tensions found", self.js)
        self.assertNotIn("result-list-label", self.js)
        self.assertNotIn(".result-list-label", self.css)
        # Dynamic count helper copy.
        self.assertIn("We found ${n} ${themeWord} supported independently by at least two parts of", helpers)
        self.assertIn('themeWord = n === 1 ? "recurring theme"', helpers)
        self.assertIn('subjectTail = "your profile"', helpers)
        self.assertIn('subjectTail = "this profile"', helpers)
        self.assertIn("${possessiveLabel(name)} profile", helpers)
        self.assertIn("parts of ${subjectTail}:", helpers)
        self.assertIn("We found ${n} ${tensionWord}:", helpers)
        self.assertIn('tensionWord = n === 1 ? "tension"', helpers)
        # Structural groups wrap actual results only on result paths.
        self.assertIn('class="result-list-group"', patterns_fn)
        self.assertIn('class="result-list-group result-list-group-tensions"', tensions_fn)
        self.assertIn(".result-list-group", self.css)
        helper_pos = patterns_fn.find("section-helper")
        group_pos = patterns_fn.find("result-list-group")
        self.assertGreater(group_pos, helper_pos)
        t_helper = tensions_fn.find("section-helper")
        t_group = tensions_fn.find("result-list-group")
        self.assertGreater(t_group, t_helper)
        # Empty recurring: no result group, no "We found 0".
        empty_branch = patterns_fn.split("if (!patterns.length)", 1)[1].split(
            "const intro =", 1
        )[0]
        self.assertNotIn("result-list-group", empty_branch)
        self.assertNotIn("We found 0", empty_branch)
        self.assertIn("patterns-empty", empty_branch)
        self.assertIn('if (!tensions.length) return ""', tensions_fn)
        # Primary observation sections do not use result groups.
        section_body = self.js.split("function renderSectionBody", 1)[1].split(
            "function renderSynthesisSections", 1
        )[0]
        synthesis_sections = self.js.split("function renderSynthesisSections", 1)[1].split(
            "function renderContextWatchOuts", 1
        )[0]
        self.assertNotIn("result-list-group", section_body)
        self.assertNotIn("result-list-group", synthesis_sections)
        self.assertNotIn("Strongest traits", self.js)
        self.assertNotIn("Top traits", self.js)
        self.assertNotIn("Main skills", self.js)

    def test_profile_audience_mode_copy(self):
        # Person mode: named subject, neutral section titles, no second-person framing.
        self.assertIn('audience === "person"', self.js)
        self.assertIn("PERSON_SECTION_TITLES", self.js)
        self.assertIn("SELF_SECTION_TITLES", self.js)
        self.assertIn("Thinking style", self.js)
        self.assertIn("Communication style", self.js)
        self.assertIn("Learning style", self.js)
        self.assertIn("Work-related patterns", self.js)
        self.assertIn("How you think", self.js)
        self.assertIn("How you communicate", self.js)
        self.assertIn("How you learn", self.js)
        self.assertIn("How it can show up in work", self.js)
        self.assertIn("possessiveLabel", self.js)
        self.assertIn("profileHeaderTitle", self.js)
        self.assertIn("Mercury Profile", self.js)
        self.assertIn("${possessiveLabel(name)} Mercury Profile", self.js)
        self.assertIn(': "Mercury Profile"', self.js)
        self.assertIn("${possessiveLabel(name)} profile", self.js)
        self.assertIn('subjectTail = "your profile"', self.js)
        self.assertIn('subjectTail = "this profile"', self.js)
        self.assertIn("parts of ${subjectTail}:", self.js)
        self.assertIn("humanFactorLabelFromSource", self.js)
        self.assertIn("factorCardTitle", self.js)
        # Recurring block: meaning first; provenance only in disclosure.
        self.assertIn("Key recurring patterns", self.js)
        self.assertNotIn("contributing factors", self.js)
        self.assertNotIn("signal-factors", self.js)
        self.assertNotIn(">Why?<", self.js)
        self.assertNotIn("Fact IDs:", self.js)
        # No gender / score / strongest marketing language for recurring block.
        patterns_fn = self.js.split("function renderStrongestPatterns", 1)[1].split("function renderSynthesisSections", 1)[0].lower()
        audience_helpers = self.js.split("function resolveProfileAudience", 1)[1].split("function showWorkspaceShell", 1)[0].lower()
        for blob in (patterns_fn, audience_helpers):
            self.assertNotIn("he/she", blob)
            self.assertNotIn("his/her", blob)
            self.assertNotIn("gender", blob)
            self.assertNotIn("proven skill", blob)
            self.assertNotIn("proven ability", blob)
            self.assertNotIn("strongest traits", blob)
            self.assertNotIn("top skills", blob)
            self.assertNotIn("candidate score", blob)
            self.assertNotIn("fit score", blob)
        self.assertNotIn("strongest pattern", patterns_fn.replace("strongest_patterns", ""))
        # Quick-fill + Build a Team preserved.
        self.assertIn('data-self-demo="avdey"', self.html)
        self.assertIn("Build a Team", self.html)
        self.assertIn("self-build-team", self.html)

    def test_self_profile_synthesis_contract(self):
        self.assertIn("No repeated pattern stands out across multiple Mercury factors", self.js)
        self.assertIn("Condition not resolved", self.js)
        self.assertIn("Compensation (source material / detail)", self.js)
        self.assertIn("profile.limitations", self.js)
        self.assertIn("conditional_details", self.js)
        self.assertIn("section.preview_fact_ids", self.js)
        self.assertIn("sectionDisplayTitle", self.js)
        self.assertIn("if (!section.resolved_fact_count) return \"\"", self.js)
        self.assertIn("Explore all", self.js)
        self.assertIn("Show less", self.js)
        self.assertIn("section-factor-explore", self.js)
        self.assertIn("groupSectionFactsByFactor", self.js)
        self.assertNotIn("section-remaining-facts", self.js)
        self.assertNotIn(">View all<", self.js)
        self.assertNotIn("View all", self.js)
        # Page-level title only — calculated card has no duplicate profile title.
        self.assertIn("setBrandTitleForProfile", self.js)
        self.assertIn("profileHeaderTitle", self.js)
        self.assertNotIn("<h2>${escapeHtml(headerTitle)}</h2>", self.js)
        self.assertIn("self-calc-line", self.js)
        self.assertIn("self-aspect-list", self.js)
        self.assertIn("formatAspectChip", self.js)
        # Explore-all does not re-fetch; uses local synthesis facts.
        explore_block = self.js.split("function renderSectionBody", 1)[1].split(
            "function renderSynthesisSections", 1
        )[0]
        self.assertIn("Explore all", explore_block)
        self.assertIn("renderSectionFactorExplore", explore_block)
        self.assertNotIn("apiPost", explore_block)
        self.assertNotIn("mercury-source-profile", explore_block)
        self.assertIn("data-self-demo=\"avdey\"", self.html)
        self.assertIn("data-self-demo=\"vlad\"", self.html)
        self.assertIn("data-self-demo=\"dzmitry\"", self.html)
        self.assertIn("SELF_DEMOS", self.js)

    def test_progressive_section_factor_disclosure(self):
        body_fn = self.js.split("function renderSectionBody", 1)[1].split(
            "function renderSynthesisSections", 1
        )[0]
        explore_fn = self.js.split("function renderSectionFactorExplore", 1)[1].split(
            "function renderSectionBody", 1
        )[0]
        group_fn = self.js.split("function groupSectionFactsByFactor", 1)[1].split(
            "function renderSectionFactorExplore", 1
        )[0]
        grouped_item_fn = self.js.split("function renderGroupedFactItem", 1)[1].split(
            "function factorTypeRank", 1
        )[0]
        # Flat View-all wall removed.
        self.assertNotIn("section-remaining-facts", self.js)
        self.assertNotIn("section-view-all", self.js)
        self.assertNotIn("View all", self.js)
        # Explore control with dynamic N.
        self.assertIn("Explore all ${total} observations", body_fn)
        self.assertIn("Explore all 1 observation", body_fn)
        self.assertIn("hasMore = total > previewIds.length", body_fn)
        # Show less after factor groups (single bottom control).
        self.assertIn("section-show-less", body_fn)
        self.assertIn("Show less", body_fn)
        self.assertEqual(body_fn.count("Show less"), 1)
        self.assertGreater(
            body_fn.find("section-show-less"),
            body_fn.find("renderSectionFactorExplore"),
        )
        self.assertNotIn("show-less-label", body_fn)
        # Factor groups, not flat fact list.
        self.assertIn("Profile factors behind this section", explore_fn)
        self.assertIn("section-factor-group", explore_fn)
        self.assertIn("section-factor-chevron", explore_fn)
        self.assertIn("factorCardTitle", explore_fn)
        self.assertIn("factor_type", group_fn)
        self.assertIn("factor_key", group_fn)
        self.assertIn("factorTypeRank", group_fn)
        self.assertIn("sign: 0", self.js)
        self.assertIn("house: 1", self.js)
        self.assertIn("motion: 2", self.js)
        self.assertIn("aspect: 3", self.js)
        # Counts use observation wording; groups collapsed by default.
        self.assertIn("1 observation", explore_fn)
        self.assertIn("observations", explore_fn)
        self.assertNotIn('class="section-factor-group" open', self.js)
        # Expanded rows omit repeated provenance; risk preserved; human copy preferred.
        self.assertNotIn("fact-provenance", grouped_item_fn)
        self.assertIn("risk-mark", grouped_item_fn)
        self.assertIn("humanFactText(fact, presentationMap)", grouped_item_fn)
        self.assertIn("escapeHtml(text)", grouped_item_fn)
        # Preview prefers presentation copy when available.
        preview_fn = self.js.split("function renderPreviewFactItem", 1)[1].split(
            "function renderStrongestPatterns", 1
        )[0]
        self.assertIn("humanFactText(fact, presentationMap)", preview_fn)
        self.assertIn("function humanFactText", self.js)
        self.assertIn("presentationTextMap", self.js)
        self.assertIn("presentation_text_by_fact_id", self.js)
        # Full source evidence still uses RAW canonical text.
        evidence_fn = self.js.split("function renderFactItem", 1)[1].split(
            "function ", 1
        )[0]
        self.assertIn("escapeHtml(fact.text)", evidence_fn)
        self.assertNotIn("humanFactText", evidence_fn)
        # Preview hidden while explore open (no duplicate visible IDs).
        self.assertIn(".section-body:has(> .section-explore[open]) > .section-preview", self.css)
        self.assertIn(".section-factor-group", self.css)
        # Chevron open/closed + hover/focus affordances.
        self.assertIn(".section-factor-chevron", self.css)
        self.assertIn(".section-factor-group[open] > summary .section-factor-chevron", self.css)
        self.assertIn(".section-factor-group > summary:hover", self.css)
        self.assertIn(".section-factor-group > summary:focus-visible", self.css)
        self.assertIn(".section-explore[open] > .section-show-less", self.css)
        self.assertIn(".section-explore[open] > summary.section-explore-summary", self.css)
        # Full source evidence still available in methodology.
        self.assertIn("Explore full source evidence", self.js)
        self.assertIn("details-methodology", self.js)

    def test_self_profile_partial_coverage_shows_calculated_factors(self):
        self.assertIn("factor-unsupported", self.js)
        self.assertIn("Source interpretation not yet available in this prototype.", self.js)
        self.assertIn("Not yet available", self.js)
        self.assertIn("Source coverage: partial", self.js)
        self.assertIn("House not calculated — birth time required.", self.js)
        self.assertIn("self-house-note", self.js)
        self.assertIn("self-coverage-meta", self.js)
        # Calculated factors drive layer list, not only active source packs.
        self.assertIn("calc.mercury_sign", self.js)
        self.assertIn("calc.birth_time_known", self.js)
        self.assertIn('motion.toLowerCase() !== "direct"', self.js)
        # No invented interpretation for unsupported packs.
        self.assertNotIn("inventedInterpretation", self.js)
        self.assertNotIn("guessSourceText", self.js)
        # Supported factors still render statement counts / full texts.
        self.assertIn("source statements", self.js)
        self.assertIn("escapeHtml(fact.text)", self.js)
        self.assertIn("factor-unsupported", self.css)

    def test_edit_team_data_action_exists(self):
        self.assertIn("Edit Team Data", self.html)
        self.assertIn("Apply &amp; Analyze", self.html)

    def test_load_demo_scenario_exists(self):
        self.assertIn("Load Demo Scenario", self.html)
        self.assertIn("loadDemoAndAnalyze", self.js)
        self.assertIn("AI Platform Team", self.js)

    def test_workflow_stage_ui_contains_lifecycle(self):
        blob = f"{self.html}\n{self.js}\n{self.css}"
        for stage in ("Explore", "Validate", "Productionize", "Connect"):
            self.assertIn(stage, blob)
        self.assertIn("workflow-strip", self.html)
        self.assertIn("workflow-strip", self.css)
        self.assertIn("renderWorkflowStrip", self.js)

    def test_candidate_impact_preview_calls_existing_endpoint(self):
        self.assertIn("loadImpactPreviews", self.js)
        self.assertIn('/api/v1/candidate-team-impact', self.js)
        self.assertIn("closed_missing_functions", self.js)
        self.assertIn("CLOSES CURRENT GAP", self.js)
        self.assertNotIn("inferTeamFunction", self.js)
        self.assertNotIn("calculateGap", self.js)

    def test_full_before_after_is_secondary(self):
        self.assertIn("View Full Before / After", self.js)
        self.assertIn("<details", self.js)
        self.assertIn("ba-table", self.js)

    def test_no_score_ranking_or_hire_ui(self):
        lowered = self.blob.lower()
        forbidden = [
            "impact_score",
            "fit_score",
            "match_percentage",
            "coverage_percentage",
            "recommended_candidate",
            "best candidate",
            "hire recommendation",
            "reject candidate",
            "rank #",
            "candidate_rank",
        ]
        for term in forbidden:
            self.assertNotIn(term, lowered, term)

    def test_no_astrology_engine_terms_in_main_workspace(self):
        workspace_html = self.html.split("id=\"workspace\"", 1)[1].split("id=\"setup-overlay\"", 1)[0].lower()
        empty_html = self.html.split("id=\"empty-state\"", 1)[1].split("id=\"self-profile\"", 1)[0].lower()
        for term in ("mercury", "zodiac", "aspect", "dispositor", "retrograde", "longitude", "house"):
            self.assertNotIn(term, workspace_html, term)
            self.assertNotIn(term, empty_html, term)
        # Self-exploration may show calculated Mercury factor names; keep it outside empty/workspace shells.
        self.assertIn('id="self-profile"', self.html)
        self.assertLess(self.html.find('id="empty-state"'), self.html.find('id="self-profile"'))
        self.assertLess(self.html.find('id="self-profile"'), self.html.find('id="workspace"'))
        self.assertIn("Mercury in", self.js)
        self.assertIn("formatAspectChip", self.js)

    def test_workspace_header_is_single_compact_context(self):
        self.assertIn('id="workspace-context"', self.html)
        self.assertNotIn('id="workspace-summary"', self.html)
        self.assertIn("renderWorkspaceHeader", self.js)
        self.assertIn("shortlisted candidate", self.js)
        self.assertNotIn("Target role:", self.js)

    def test_workflow_gap_appears_once_under_coverage_strip(self):
        self.assertEqual(self.html.count('id="gap-priority"'), 1)
        self.assertIn("gap-priority", self.html.split('id="workflow-strip"', 1)[1])
        self.assertNotIn("summary-gap", self.js)

    def test_impact_delta_uses_before_after_labels_without_duplicate_status_text(self):
        self.assertIn("statusTransitionHtml", self.js)
        self.assertIn("delta-label", self.js)
        self.assertIn(">Before<", self.js)
        self.assertIn(">After<", self.js)
        # Chips carry the status wording; do not repeat it as sibling strong text.
        self.assertNotIn("${statusChip(\"missing\")}<strong>Missing</strong>", self.js)
        self.assertNotIn("${statusChip(\"single_coverage\")}<strong>Single Coverage</strong>", self.js)

    def test_saved_workspaces_actions_exist_without_form_first_ux(self):
        self.assertIn("Saved Workspaces", self.html)
        self.assertIn("Save Workspace", self.html)
        self.assertIn('id="workspaces-overlay"', self.html)
        self.assertIn("hidden", self.html.split('id="workspaces-overlay"', 1)[1].split(">", 1)[0])
        self.assertLess(self.html.find('id="empty-state"'), self.html.find('id="workspaces-overlay"'))

    def test_workspace_persistence_api_usage_in_js(self):
        self.assertIn('"/api/v1/workspaces"', self.js)
        self.assertIn("`/api/v1/workspaces/${activeWorkspaceId}`", self.js)
        self.assertIn("`/api/v1/workspaces/${workspaceId}`", self.js)
        self.assertIn("method: \"POST\"", self.js)
        self.assertIn("method: \"PUT\"", self.js)
        self.assertIn("method: \"DELETE\"", self.js)
        self.assertIn("method: \"GET\"", self.js)
        self.assertIn("openWorkspace", self.js)
        self.assertIn("analyzeTeam", self.js)
        self.assertIn("Persist INPUT STATE only", self.js)
        self.assertNotIn("team_map", self.js.split("collectWorkspacePayload", 1)[1].split("function ", 1)[0])
        self.assertNotIn("closed_missing_functions", self.js.split("collectWorkspacePayload", 1)[1].split("function ", 1)[0])
        self.assertNotIn("missing_required_functions", self.js.split("collectWorkspacePayload", 1)[1].split("function ", 1)[0])


if __name__ == "__main__":
    unittest.main()
