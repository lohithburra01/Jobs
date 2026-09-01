# Internal Linking Automation (capability notes)

Scope: an internal-linking automation system built for an SEO agency's portfolio of German law-firm websites.
Two instances were read: the original pilot instance, and a second per-client instance that generalised the same
method into a numbered, deterministic Python pipeline. All client names, firm names, domains, URLs and reviewer
names are deliberately omitted. Where the source repo names a client, this document says "a law-firm client
instance".

## The problem

The spec states the business problem directly: law-firm sites have dozens of pages each, split into commercial
"money pages" (broad practice-area service pages), sub money pages (specific case types) and informational blog
articles. These pages are under-linked to each other. Internal links tell a search engine how pages relate and
which are important, pass link equity from strong pages to weak ones, and help readers navigate. The agency did
this linking by hand, page by page, and it did not scale across roughly a dozen clients. The stated job was to
automate it "with quality high enough that a human only approves or rejects, never rewrites".

The hard constraint named in the spec: this is YMYL legal content in German. "Precision matters more than
coverage. A wrong link is worse than a missing link."

The spec explicitly rejects the original framing it inherited. The client brief blamed context-window size ("the
model works from fragments and guesses from URL slugs"). The spec argues that framing is outdated at this scale,
since a whole law-firm site fits in a modern context window, and re-frames the real challenges as:

- Similarity is not relevance. Two topically near pages do not imply one should link to the other. Linking is
  about relationships (sub-area-of, cites-statute, is-the-money-page-for), not raw similarity.
- Exact-match terms matter. Statute citations and legally protected professional titles must match precisely,
  which pure embedding search is bad at.
- Hallucination risk is unacceptable. The system must be able to say "no good target exists" and must ground
  every decision in actual page text.
- Quality must be verifiable, not merely generated. The bottleneck is retrieval precision and verification, not
  text generation.

The spec also fixes a sequencing rule taken from the client brief and treated as inviolable: **understand first,
map second, place links third.** Deliverable shape, per page: the exact existing passage where a link goes, the
proposed anchor text, the target URL, and a one-sentence justification; plus a link matrix, plus orphan flags
for any money page with zero incoming internal links.

## Pipeline architecture

The second client instance is the clean form: eleven numbered stage scripts plus a config module and an LLM call
layer, run in order from one folder. Only two stages call a model. Everything else is deterministic Python.

**Stage 1, fetch (no model).** Paginates the CMS public REST API for all published posts and pages, writes clean
text per page, and separately captures every existing `<a>` tag into an existing-links file mapping source slug
to {href, target slug, anchor}. That capture is the safety fix: the engine knows what is already linked and
cannot re-propose a live link. Two non-obvious pieces live here. A page-builder fallback re-fetches rendered
HTML and takes the largest article container when REST `content.rendered` comes back effectively empty. And
structural component stripping removes CTA boxes, nav menus, author bylines, tables of contents, social bars,
contact forms and promo widgets from the DOM before text extraction, so the linker can never place a link in a
conversion component. Selectors are per-client config; the mechanism is fixed. Existing links are read from the
full HTML before stripping, so dedupe awareness is unaffected.

**Stage 2, inventory and assignment (no model).** Classifies every page by practice area and by role (money,
tool, regional, excluded, or source). Emits three files: a full inventory, an assignment file that gives each
source page exactly one money page, and a target directory listing the only slugs the model is allowed to link
to. Area and role come from a content-based classification handoff where available; slug regex and hardcoded
sets are only a fallback. This is where the practice-area wall is established: only one practice area is kept as
Phase 1, so cross-area links are impossible by construction rather than by prompt.

**Stage 3, embeddings (local, no API cost).** A small multilingual sentence-transformer model embeds each
in-scope page by chunking at 380 words, encoding, mean-pooling and L2-normalising. A cosine similarity matrix
over the page vectors yields the top 8 nearest pages per source as blog-link candidates. Only in-scope pages are
embedded, so the practice-area wall holds here too. This is explicitly a candidate suggester, not the decision
maker.

**Stage 4, draft (LLM, one call per source page).** Each call receives: the assigned money page, the full target
directory, the semantic neighbour candidates, the list of links already live on that page, and the page text.
Long pages are sent head plus tail (60/40 of a 13,000 character budget) rather than truncated, because
truncating to the first few thousand characters hid the closing advice section where money links belong and
silently killed money links. Output is strict JSON per link: target, target type, anchor, suggestion type,
original text, passage, section and reason. Runs in a fixed thread pool of six workers; per-call token usage and
cost are accounted.

**Stage 5, aggregate (no model, deterministic cleanup).** Enforces the wrap-only policy at source: blog links
must be `existing_anchor`, money and tool links must be `existing_anchor` or a light `rewrite`; anything else is
dropped as fabricated. Then dedupes against live links, drops duplicate targets within a page, de-crowds to at
most one internal link per sentence, caps links per page while protecting the money link, and adds statute links
deterministically by regexing every unique paragraph-and-code citation and mapping it to a deep link on the
official federal statute portal via an abbreviation-to-path table.

**Stage 6, review and rectify (LLM, one call per page).** A second pass over the aggregated set. The reviewer
receives the page text, the proposed links, and, if a prior gate run exists, that page's exact gate findings. It
returns a cleaned set: mechanical issues fixed, links with no natural home dropped, at most one money link kept.
If the model returns unparseable output the page falls back to its aggregated set, so a page is never lost.

**Stage 6b, finalize (no model).** Repairs three mechanical defects the review pass leaves: snaps an anchor in
base form to its exact inflected substring in the passage (German prefix stem match), drops links to targets
already live, drops anchors genuinely absent from the passage. Re-applies zone stripping, dedupe, de-crowd, cap
and money accounting.

**Stage 6c, money placement (deterministic, with a narrowly scoped model call).** Money link is optional (zero
or one). If a real service link is already live, none is added. If a valid model wrap already exists in the
latter part of the page, the best one is kept. Otherwise the closing advice paragraph is detected
deterministically by cue regex plus position, and the model is given **only that paragraph** and the target
topic, and must either wrap a phrase verbatim present in it or lightly rewrite one sentence from it, or return
"none". Then a scrub drops anything that is not a clean wrap.

**Stage 7, the gate (no model). Nothing reaches the human reviewer unless this is green.** A single pass, each
link graded ok / warn / error; any page with an error fails the whole page; the exit code is the number of
failing pages, so zero means green and nothing ships otherwise. It checks, among others: target integrity and
validity, cross-practice-area wall breach, already-live dedupe misses, blog wrap-only, anchor word count, anchor
verbatim in its passage, **label honesty** (an `existing_anchor` passage must exist verbatim in the source; a
`rewrite` original text must exist in the source), banned anchors, the banned "lawyer-for-X" anchor pattern,
weak or dangling or bare-generic anchors, exact tool anchor, leaked placeholders, doubled auxiliary verbs,
link-referential filler phrasing, legal absolutes, a specific legal-term error, decision-memory re-proposal of
previously rejected combinations and of previously rejected source-to-target pairs, FAQ-question-heading
anchors, byline anchors, CTA-component anchors, broken-grammar rewrites, a click test comparing anchor content
words against target slug and title, cross-page anchor reuse (templating detector), no-link zones, per-sentence
crowding, statute completeness, and low coverage. It also emits an orphan report: incoming link counts per money
page, flagging any below the configured minimum.

**Stage 8, report (no model).** Builds the local review package: a machine-readable summary (page and link
counts, breakdown by type, money coverage, orphans, incoming-link ranking, gate error page count) and a human
review HTML page.

**Stage 9, dashboard (no model).** Rebuilds the same reviewer dashboard used for the first client by importing
the first instance's render modules and patching only client-specific bits, so the reviewer sees a UI they
already know: in-context preview, accept/reject, per-link comment box, JSON export. A separate converter then
turns the reviewer's exported decisions into a decision-memory file holding both exact (source, target, anchor)
rejections and (source, target) pair rejections, which the gate and the money placer enforce on the next run.

**Where the human gate sits:** nothing is injected live by this pipeline. It emits a review package only, and
human approval is a hard gate in front of any write. The first client instance had a separate set of injection
scripts (see Technical decisions) which are the only code that writes to a live site, dry-run by default with
snapshot-before-write and revert.

## Scale and numbers

All numbers below were found in the repo. Source kind is cited for each.

**Second client instance, Phase 1 run (stage output JSON and summary.json):**
- 211 pages fetched and classified from the CMS REST API; 119 in the in-scope practice area, 85 in the
  out-of-scope area, 6 excluded, 1 other.
- In-scope roles: 88 source pages, 26 money pages, 4 regional pages, 1 tool page.
- 566 existing internal links captured at fetch time across the site.
- 20 pages required the rendered-HTML fallback because REST content was empty (stage-1 source comment).
- Draft stage: 88 pages, 332 proposed links. After aggregation plus deterministic statute links: 502. Final
  after review, finalize and money repair: 347.
- Final link mix: 193 statute, 130 blog, 24 money.
- Money coverage: 66 pages covered, of which 24 got a new money link and 42 already had one live; 22 pages
  intentionally left without one.
- Gate on the final set: 88 pages, 0 error pages (green), 106 warnings.
- Orphan report: 10 money, regional or tool pages below the 3-incoming minimum. Highest incoming count for a
  single target: 27.
- Reviewer feedback export for the earlier Phase 1 batch: 370 decisions, 128 accept, 24 reject, 218 undecided.
- Config observation: 44 of 88 pages carried a generic hub link; treating that hub as an existing CTA had
  suppressed 17 legitimate money links (config source comment).

**First (pilot) client instance, version history (links_v*.json on disk plus handoff docs):**
- v3: 42 pages, 251 links. Reviewer export: 251 decisions, 129 reject, 122 accept, 149 written reasons.
- v4: 42 pages, 227 links. Reviewer export: 227 decisions, 61 reject, 166 accept.
- v5: 42 pages, 192 links. v6: 42 pages, 238 links. v7: 44 pages, 223 links.
- v8: 38 pages, 173 links. v9: 38 pages, 146 links.
- v4 measured deltas (handoff doc): generic "lawyer-for-X" anchors 36 to 0; over-links to the single main money
  page 22 to 0; 0 of 129 previously rejected combinations re-proposed; 119 of 122 accepted links preserved.
- v4 suggestion-type mix: 115 existing_anchor, 37 integrate, 22 rewrite, 53 new_sentence.
- v9 link-aware filter (audit markdown): dropped 27, kept 146; 7 money links flagged as not verifiable through
  the API and escalated for manual check.
- Site read scale: 74 URLs discovered from the public sitemap (go-live plan doc).
- Decision memory currently on disk: 218 rejected, 311 accepted. The v6 handoff records it at 360 decisions (170
  accept, 190 reject) at that point in time.

**Quality measurement of the automated reviewer (handoff memos and a comparison report):**
- Reviewer rejections in one round were segregated into 32 common-sense, 27 taste, 2 unknown. The blind reviewer
  bots caught 12 of 32 common-sense (38%), 15 of 27 taste (56%), 27 of 61 overall (44%). The team's own memo
  flags that the loosely quoted "44%" is the overall number and the honest common-sense figure is 38%.
- On a 107-link overlap set: raw agreement 81 of 107 (76%), bot recall on rejects 12%, bot precision 5%.
- v6: blind bots flagged 39 of 238 links (7 high, 32 medium severity).

**Parity-spec defect measurements that triggered a rebuild (V8 parity spec):**
- 77% of money links (48 of 62) were fabricated sentences mislabeled as wraps.
- 48% of "integrate" links (119 of 249) did not exist in the source text at all.
- The no-link-zone detector fired on only 59 of 105 pages.

**Gate and config thresholds (config.py and stage scripts):**
- Max anchor words 5. Max links per page 6. Min incoming links per money page 3.
- Money position minimum 0.45 (a money wrap should sit in the latter 55% of the page, soft check).
- Page text budget to the drafting model 13,000 characters, split 60% head / 40% tail; review pass sees 5,500
  characters.
- Top 8 semantic neighbours per source; embedding chunk size 380 words.
- Six concurrent worker threads; four retries with exponential backoff on API errors.
- Anchor reuse across 3 or more pages raises a templating warning.
- A CTA container is treated as a whole promo box only if under 400 characters, otherwise only the button widget
  is removed.
- The framework document enumerates 18 numbered gate items; the pipeline README describes the gate as "17
  checks". This discrepancy is real and is flagged below.

**Cost (README, benchmark harness, handoff docs):**
- Whole Phase 1 run for the second client: "a few cents to ~$1" (pipeline README).
- Model registry prices two tiers at $0.09/$0.18 and $0.43/$0.87 per million input/output tokens.
- A four-case, four-model benchmark run was estimated at about $4.
- Planning estimate for a per-client run on a frontier model: about $2, about $1.15 on a mid-tier model, roughly
  $15 to $25 for the full portfolio of about 12 clients.
- One recorded cost incident: an uncapped agent fan-out consumed 6.9M tokens across 359 agents, which is why the
  standing rule is fixed-count, non-spawning workers.

**Model benchmark (results.json, 2026-07-10):** 9 models, 40 items each, one case (accept/reject verdict on a
candidate link, graded against real reviewer labels). Accuracy ranged 0.375 to 0.525; the frontier reference
model scored 0.525 accuracy with 1.0 reject recall and 0.05 accept recall; the selected cheaper model scored 0.5
accuracy at $0.05 for the run versus $1.15 for the frontier model. Parse rates ranged 0.70 to 1.0; mean latency
2.95s to 26.62s per call.

**Run times:** not found in repo (only per-call latency from the benchmark, above). No end-to-end wall-clock
timing was recorded. **Acceptance rate of the second client's final set:** not found in repo, because that batch
had not been re-reviewed at the point the repo was captured.

## Technical decisions and tradeoffs

- **Deterministic pipeline over chat agent.** The second instance is explicitly "a deterministic Python pipeline
  that calls a model, not a chat agent". Two model calls per page total; everything else is code. That is what
  put a full run under a dollar and made results reproducible.
- **Rules in one place, embedded into every prompt.** The canonical linking rules are a single string constant
  in config, embedded verbatim by the drafting, review and money-placement stages. The source comment names the
  failure mode this ends: "one rule hand-copied into 5 places, drifting apart".
- **Wrap-only as the anti-hallucination primitive.** Rather than judging whether an invented sentence is good,
  the system restricts blog links to wrapping text that already exists verbatim and money links to wrapping or
  lightly rewriting one existing sentence. Anything else is dropped mechanically, and the `original_text` field
  on a rewrite makes the claim checkable.
- **Label honesty as a gate check.** The model must declare a suggestion type and the gate verifies that
  declaration against the source text, catching the specific failure where a fabricated sentence is labeled an
  existing anchor. That single check turned an unquantified quality problem into a measurable one (48% of one
  category were label lies).
- **Optional money link.** The pre-rebuild design forced a money link onto every page, which produced fabricated
  CTA sentences and got a whole batch rejected. The rebuilt rule is zero or one, and "a missing money link is
  better than a generic one".
- **Practice-area wall by construction, not by instruction.** Out-of-scope pages are never embedded and never
  enter the target directory, so a cross-area link is structurally impossible; the gate check for it is a
  backstop, not the mechanism.
- **Deterministic statute linking.** Citations are extracted by regex and mapped to deep links through a fixed
  abbreviation table, never generated by a model. The gate checks completeness (every cited paragraph linked
  once), and the aggregator and gate deliberately share the identical law set so they cannot disagree.
- **Component stripping at fetch instead of prompt instruction.** "A link cannot be placed where there is no
  text." The no-link-zone rule for conversion components is enforced by deleting those nodes before extraction.
  The 400-character container heuristic exists to avoid over-stripping an article column that merely contains a
  button.
- **Local embeddings for candidates, paid model for judgement.** Candidate generation runs on a free local
  multilingual model; only drafting and review pay per token.
- **Reasoning mode forced off.** The call layer disables the provider's reasoning parameter as a documented cost
  guard: leaving it on burned five to ten times the output tokens on hidden thinking and could return empty
  content, which the benchmark hit directly.
- **Cheap model selection driven by measurement.** The benchmark harness grades candidate models against real
  reviewer labels and a ported gate, measures cost rather than guessing, and is safe by default (dry-run
  estimate unless an explicit spend flag is passed). Its own README states the honest limit: only one case has
  objective labels, the rest measure agreement with a reference model, not truth.
- **Not relying on model reviewers as the gate.** After measuring blind reviewer bots at 38% recall on the
  problems that mattered, the documented conclusion was to fix problems at generation time and convert every
  objectively checkable rule into a deterministic gate check, because those catch 100% rather than a third.
  Raising bot recall was ranked third.
- **Read is safe, write is gated.** Reading a site is public, read-only and credential-free. Writing is a
  separate per-client-gated path with snapshot-before-write and revert.
- **Injection is CMS-storage-specific.** Three storage shapes were identified (plain CMS body, page-builder JSON
  tree in a hidden meta field, custom fields) and injectors were written for two. The page-builder injector only
  modifies text inside text blocks, wraps the first anchor occurrence that sits outside an existing anchor tag
  and outside headings, prefers the block containing the link's recorded passage, and snapshots raw content to a
  timestamped file before any write, with a revert command that re-uploads the snapshot.

## Hard debugging

- **The blind-to-newer-feedback bug.** One version was built from an older feedback export only and re-proposed
  8 link combinations the reviewer had already rejected in a newer round. Root cause: the decision-memory
  builder read a single feedback file rather than merging all of them. Fix: merge every export oldest to newest,
  later winning on conflict. The handoff doc marks this explicitly as a regression not to reintroduce.
- **Fabricated sentences labeled as existing anchors.** A whole batch was rejected. Root cause traced in the
  parity spec: 77% of money links were invented sentences carrying an `integrate` or `new_sentence` label, and
  48% of `integrate` links did not exist in the source at all. Two fixes: restrict allowed suggestion types at
  aggregation, and add the label-honesty check that verifies the declared type against the source text.
- **No-link-zone detector defeated by fabricated text.** It fired on only 59 of 105 pages, because a fabricated
  passage cannot be located in the real page and so cannot be found inside a zone either. The fix was upstream:
  once passages are guaranteed real, it works.
- **Money links disappearing on long pages.** Truncating to the first few thousand characters removed the
  closing advice section, which is exactly where money links belong. Fix: send head plus tail with an explicit
  elision marker.
- **Empty CMS bodies on page-builder pages.** Twenty pages returned effectively empty REST content because the
  body lived in builder widgets. Fix: detect short extractions and fall back to the rendered page, taking the
  largest article container, with a last-resort concatenation of text and heading widgets.
- **Generic hub link mistaken for an existing CTA.** Treating a site-wide practice-area hub link as an existing
  money CTA suppressed 17 legitimate money links across 44 pages. Fix: a configured hub set excluded from the
  "already has a CTA" test.
- **Anchor inflection mismatch.** German inflects the anchor in context, so a model-returned base-form anchor
  failed the verbatim check. Fix: a prefix-stem snap that finds the exact contiguous inflected substring in the
  passage, and drops the link if none exists.
- **Reasoning-mode token burn and empty completions.** Diagnosed on the benchmark, fixed by disabling reasoning
  in the call layer.
- **Agent fan-out runaway.** 6.9M tokens across 359 agents from spawnable general-purpose workers. Fix and
  standing rule: fixed-count workers that cannot spawn sub-agents, plus a hard token budget per run.
- **Worker output reliability.** Read-only planning agents asked to return large JSON inline fragmented or
  hallucinated it; one returned an entirely unrelated artifact. Fix: workers restricted to read and write that
  save JSON to numbered files, no spawning, followed by re-aggregation and a re-run of the gate.
- **False "done" claims.** One version was declared production-ready without evidence and was rejected. The
  resulting standing rule is that no completion claim is made without showing the gate exit code and counts.
- **A reviewer data-quality finding.** One combination was exported as a reject but its attached written note
  approved it, almost certainly a mis-click. The literal reject was honoured, the item logged to a
  dropped-combos file, and the discrepancy raised rather than silently overridden.
- **Console encoding.** Comparison scripts crashed printing certain glyphs to a legacy Windows code page;
  numbers printed first so the failure was cosmetic. Logged, not yet fixed.

## Reusability

The method is templated as "everything above the client config is fixed; the client config is the steering
wheel". The second client instance is a direct application of that split.

**Fixed across clients:** the stage sequence and its file contracts (raw inventory, existing links, inventory,
assignment, target directory, neighbours, draft, aggregated, final, gate report, summary); the linking rules
text; the suggestion-type vocabulary and the wrap-only policy; the gate checks; the statute-linking mechanism;
the review dashboard renderer, which the second instance imports from the first rather than reimplementing, so
the reviewer sees an identical UI; the LLM call layer with its cost accounting.

**Per-client config (one Python module):** client id and phase; base URL; max anchor words; max links per page;
minimum incoming links per money page; the practice-area classification regexes; the exclusion set; the
money-page, regional-page and tool-page sets; the hub set; priority money pages; banned anchors; client-specific
anchor-quality guards (CTA phrasing, byline pattern, broken-rewrite patterns); the sub-cluster-to-money-page
routing table with a keyword fallback and a default; the tool trigger regex; the no-link zone labels; and the
component selector dictionary that tells the fetch stage which widgets to strip.

**What varies in practice:** the page-builder family drives the component selectors and the injection method
(three storage shapes identified, two injectors written); the money-page inventory and the topic-to-money-page
routing are entirely client-specific; the practice-area wall exists only for a client with two unrelated
practice areas; the certified-title rule is per-lawyer and must be confirmed per site.

**Per-page profiles.** The first instance generated one structured JSON profile per page into a profiles
directory, which is the persistent "understanding" store the spec asks for: read each page once, write a compact
profile, never re-read full text. The second instance compresses this into the inventory plus embeddings instead
of standalone profiles.

**Feedback as a per-client asset.** Each client accumulates a decision-memory file from that client's reviewer
exports, storing both exact rejected triples and rejected source-to-target pairs, and the gate enforces it. The
second instance shipped its first batch with no decision memory at all and consequently re-proposed
already-rejected links; the converter script exists specifically to close that.

## Technology inventory

- Python 3.10 and 3.11, standard library first: `urllib.request` for all HTTP (no requests dependency), `json`,
  `re`, `concurrent.futures.ThreadPoolExecutor` for bounded parallelism.
- BeautifulSoup for HTML parsing, DOM component stripping and existing-link extraction.
- sentence-transformers with a small multilingual E5 embedding model, run locally; numpy for vector
  mean-pooling, normalisation and the cosine similarity matrix.
- An LLM router API (OpenRouter) reached over plain HTTP, with a small model registry holding per-million input
  and output prices, a cost function, retry with exponential backoff, and a tolerant JSON extractor that strips
  code fences and falls back to the widest brace span.
- Anthropic SDK usage in the benchmark harness (a frontier model as reference and as judge).
- WordPress REST API for reads; WordPress application passwords and a custom bridge plugin endpoint for gated
  writes; two PHP bridge plugins present in the repo for custom-field and token-authenticated access.
- pytest for the dashboard and data-layer unit tests (16 tests at one milestone, 30 at a later one).
- Plain HTML plus vanilla JS for the reviewer dashboard, with browser localStorage for in-progress decisions and
  a JSON export as the feedback contract.
- Git for versioning and for storing pre-write snapshots.

## Flag for verification

- **"17 checks" vs 18.** The pipeline README and the gate docstring say the gate is 17 checks; the framework
  document enumerates 18 numbered gate items and the gate source implements more individual conditions than
  either number. Do not quote a check count without recounting the source.
- **Benchmark accuracy figures are weak and should not be presented as a win.** The single objectively-labelled
  case scored 0.375 to 0.525 accuracy across nine models, with accept recall of 0.0 to 0.15. That is close to a
  "reject everything" baseline. The honest claim is "we built the harness and measured that cheap models matched
  the frontier model on this task, which is what justified the model swap on cost", not "the model judges links
  well". The benchmark's own README says the other three cases use a reference model as judge and measure
  agreement, not truth.
- **Model names in the repo (a "V4 Pro/Flash" tier and an "Opus 4.8" reference) should be described
  generically** unless the candidate can confirm them. Describe as "a cheap open-weight tier via a router" and
  "a frontier reference model".
- **Acceptance rate for the second client's final 347-link set is not in the repo.** Do not claim the reviewer
  accepted it. What is in the repo is the earlier batch's 370-decision export (128 accept, 24 reject, 218
  undecided) and the fact that an earlier batch was rejected outright.
- **Run times are not recorded anywhere.** Only per-call latency from the benchmark exists.
- **"System" vs "scripts".** This is a set of numbered scripts run by hand from a folder, plus a static HTML
  review dashboard, plus separately-run injection scripts. There is no service, no scheduler, no queue and no
  self-serve UI. The productisation objectives document lists the self-serve app, multi-client setup, safety and
  recovery, cost guardrails and security as not started. Claim "a repeatable per-client pipeline templated to a
  second client", not "a platform".
- **Portfolio size.** The spec says roughly 12 law firms are the target. Two client instances exist in the repo.
  Do not imply the pipeline ran across the portfolio.
- **The 38% vs 44% bot recall figure.** The repo itself corrects the looser 44%. Quote 38% for common-sense
  problems and be ready to explain the bucket split.
- **Whether the candidate can explain the German-language checks.** Several gate checks (inflection snapping,
  modal-hosted infinitives, genitive after a preposition, ASCII-umlaut leakage detection, a specific legal-term
  misuse) require explaining German grammar and German employment-law terminology. The repo's own memory notes
  record that the owner does not read German and relied on the reviewer for that layer. Frame these as "encoded
  the reviewer's rules as deterministic checks", not as personal language expertise.
- **Live injection.** Injection scripts exist and are dry-run by default with snapshot and revert, and one
  instance has recorded snapshot files. Confirm before claiming links were actually pushed live to a client
  site.
