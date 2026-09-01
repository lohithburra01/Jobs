# Job sourcing and application-material pipeline - design

Date: 2026-09-01
Status: approved for planning
Supersedes: nothing

## 1. Purpose

Replace the manual front half of the application process. Today: find a posting, copy
the description, paste it into an LLM with the instruction and evidence files, get a fit
call and a JSON back, paste the JSON into VS Code, run `scripts/build_resume.py`. Five to
ten minutes per application, and sourcing is the slowest part.

Target: a daily batch that sources postings, scores them twice, generates tailored
application material for the ones worth it, renders the PDFs, and hands back one
spreadsheet row per posting carrying everything needed to apply.

The renderer does not change. `scripts/build_resume.py` and the JSON schema it consumes
are frozen inputs to this design.

## 2. Scope

In scope, version 1:

- Stage 1 fetch from discovery-tier sources plus manual URL injection
- Stage 2 deep evaluation with a measured feedback loop back into Stage 1
- Stage 3 generation of a tailoring brief and a schema-conforming application JSON
- Stage 4 batch render through the existing builder
- Append-only stage state, resumable, idempotent
- Two validation gates, one pre-render and one post-render
- Three-level tracing, prompt caching, per-run token budget, regression set

Out of scope, version 1, and nothing in this design blocks them:

- Direct submission through Workday or Greenhouse (version 2)
- A curated company seed list with ATS slugs (revisit at week three; see 6.1)
- Google Sheets. The spreadsheet is a local `.xlsx`
- Any cross-posting memory or conversational state (see section 14)

## 3. Architecture

### 3.1 The structural decision

The spreadsheet is not the state store. It cannot hold append-only history, it has no
transaction, and a human editing a cell mid-run corrupts the run.

**SQLite is the ledger. The spreadsheet is a rendered view plus one input channel.**

Every run re-renders the sheet from SQLite. Exactly two things are read back as input:
the `decision` column (blank / apply / skip / force) and the `INBOX` tab, which is the
manual URL injection path. Every other cell is overwritten without asking. That rule is
what stops the sheet becoming a second source of truth.

### 3.2 Layout

```
config/
  constraints.yaml        geography, languages, visa, salary floor, company size, titles
  sources.yaml            source registry: adapter, endpoint, query templates, rate limits
  scoring.yaml            Stage 1 feature weights, thresholds
  tuning_state.yaml       written by `pipeline tune apply`, never by a run
  budget.yaml             per-run token and dollar ceilings
  facts_curated.yaml      forbidden strings, domain tokens, claude_md_sha256
  prompts/                versioned prompt templates, hashed into every trace
pipeline/
  models/                 Pydantic boundary objects
  store/                  SQLite access, append-only event log
  sources/                one adapter per source, one interface
  stages/                 fetch, evaluate, generate, render
  gates/                  Gate A (pre-render), Gate B (post-render)
  llm/                    the single traced call wrapper
  tuning/                 divergence metrics, tuner policy
  cli.py
store/pipeline.db
artifacts/<posting_id>/   raw JD text, evaluation.json, brief.md
exports/run-<run_id>.xlsx
applications/<date>_<company>_<role>/   existing convention, unchanged
docs/superpowers/specs/
tests/regression/
```

Nothing that a config file could carry lives in code: geography, languages, salary floor,
company size, target titles, source list, query templates, feature weights, thresholds,
budgets. Adding Portugal or moving the floor to 68,000 is a YAML edit.

### 3.3 Data flow

```
sources -> PostingStub -> [dedupe] -> postings table
                                          |
                                          v
                              PostingDetail -> Stage 2 LLM -> EvaluationResult
                                          |                        |
                                          |                        v
                                          |                  FetchQualityReport -> tuning proposal
                                          v
                              above threshold -> TailoringBrief -> ApplicationDocument
                                                                         |
                                                                    Gate A (pre-render)
                                                                         |
                                                                    build_resume.py
                                                                         |
                                                                    Gate B (post-render)
                                                                         |
                                                                    RenderResult -> xlsx
```

Stages never call each other. Each reads from and writes to the store and is
independently runnable against whatever the store already holds.

## 4. Data model

### 4.1 Boundary objects

Pydantic v2. No dict crosses a stage boundary.

| Object | Produced by | Key fields |
|---|---|---|
| `PostingStub` | Stage 1 | posting_id, canonical_url, source, company_raw, title_raw, location_raw, language, remote_flag, salary_raw, posted_at, prelim_score, prelim_subscores, identity_key |
| `PostingDetail` | Stage 1 or a single fetch | posting_id, jd_text, jd_text_sha256, jd_text_source, fetched_at |
| `EvaluationResult` | Stage 2 | posting_id, refined_score, refined_subscores, hard_pass (bool + reason), company_size, company_size_confidence, salary_min/max, jd_vocabulary[], capabilities_bought[], proof_systems[], red_flags[], rationale |
| `TailoringBrief` | Stage 3a | posting_id, capabilities[], jd_nouns[], systems_to_lead[], projects_to_include[], carry_formula_dream (bool), notes |
| `ApplicationDocument` | Stage 3b | company_name, resume{summary, skills[], experience[], projects[], education[]}, cover_letter{date, company_address, salutation, paragraphs[]} |
| `RenderResult` | Stage 4 | posting_id, resume_pdf, cover_pdf, page_count, gate_b_status |
| `FetchQualityReport` | Stage 2 | run_id, n, mae, bias, spearman, precision_at_threshold, per_source[], per_query_term[], per_feature_divergence[], jd_text_coverage[] |

`ApplicationDocument` mirrors `context/schema-example.json` exactly. No added fields, no
reordering. Pipeline metadata (scores, verdict, trace ids, run id) never enters
`application.json`; it goes to `evaluation.json` in the same employer folder.

Stage 2 and Stage 3b use structured outputs (`output_config.format`) with
`client.messages.parse()` against these models, so schema conformance is enforced at the
API boundary rather than by parsing prose.

**`refined_subscores` uses the same named axes as `prelim_subscores`.** This is what makes
divergence attributable per axis instead of a single mystery number. If the axes drift
apart the feedback loop silently stops meaning anything, so a startup assertion compares
the two axis lists and fails the run on mismatch.

### 4.2 Store schema

Five tables.

`postings` - identity only.
```
posting_id TEXT PRIMARY KEY      -- sha256(canonical_url)
identity_key TEXT NOT NULL       -- sha256(company_norm|title_norm|country)
canonical_url TEXT NOT NULL
duplicate_of TEXT                -- posting_id of the cluster canonical, or NULL
first_seen_run TEXT
source TEXT
company_raw, title_raw, location_raw, language, remote_flag, salary_raw, posted_at
```

`stage_events` - **append-only. No UPDATE, no DELETE, ever.**
```
event_id INTEGER PRIMARY KEY
posting_id TEXT
stage TEXT                       -- fetch | evaluate | generate | gate_a | render | gate_b
run_id TEXT
input_hash TEXT
status TEXT                      -- ok | transient_fail | permanent_fail | gate_failed | skipped
started_at, finished_at
artifact_ref TEXT
error_class, error_detail
```
Current state is a view: the latest event per `(posting_id, stage)`. There is no status
column on `postings`. Retries and manual fixes append rows like everything else.

`runs` - run_id, started_at, finished_at, config_hash, source stats, batch metrics,
tokens_used, usd_spent, halted_reason.

`llm_calls` - local mirror of every call: langfuse_trace_id, posting_id, stage, model,
prompt_hash, input_tokens, output_tokens, cache_creation_input_tokens,
cache_read_input_tokens, cost_usd, latency_ms. Local so cost and cache-hit queries work
without an API round trip, and so a Langfuse outage never blocks a run.

`applied` - identity_key, employer_folder, applied_at. Keyed on `identity_key`, not
`posting_id`. This is what prevents a second board listing producing a second application.

## 5. Identity, dedupe and idempotency

### 5.1 One mechanism, not two

The result cache and the skip rule are the same thing. There is no separate cache layer.

```
input_hash = sha256(
    stage_id
  | prompt_template_hash
  | model_id
  | config_slice_hash        # only the config keys that stage actually reads
  | upstream_artifact_hash   # for evaluate: jd_text_sha256
)
```

**Skip rule:** a stage does work for a posting only if there is no `status=ok` event for
`(posting_id, stage, input_hash)`.

"Result caching keyed on posting URL plus a content hash of the posting body" is exactly
`(posting_id, stage=evaluate, input_hash containing jd_text_sha256)`. A posting whose
text has not changed is never re-evaluated, and that falls out of the skip rule rather
than being implemented beside it.

Consequences, and they are the right ones:

- Raising the salary floor re-runs evaluation but not fetch
- Swapping the generation model re-runs generation but not evaluation
- Editing a prompt re-runs only that stage
- A rerun with nothing changed does nothing and costs nothing
- `--resume` is not a feature; it is the default behaviour of every stage

`config_slice_hash` is per stage, not global, or every config edit would invalidate
everything. Each stage declares the config keys it reads.

### 5.2 Canonical URL

Lowercase scheme and host, strip fragment, strip query params matching a configured
denylist (`utm_*`, `gh_src`, `ref`, `source`, `trk`, session ids), preserve the rest.
`posting_id = sha256(canonical_url)`.

### 5.3 Duplicate detection

Two boards listing the same job must not produce two generation calls or two
applications. Dedupe is in version 1.

```
identity_key = sha256(company_norm | title_norm | country)
```

- `company_norm`: lowercase, strip legal suffixes (GmbH, mbH, AG, Inc, Ltd, LLC, B.V.,
  N.V., AB, A/S, Oy, SAS, S.A.), collapse whitespace and punctuation
- `title_norm`: lowercase, strip gender markers common in German postings
  (`(m/w/d)`, `(f/m/x)`, `(all genders)`), strip trailing location suffixes, collapse
  punctuation and whitespace
- `country`: resolved from location text against a country alias table; remote-only
  postings normalise to `remote`

Exact `identity_key` match auto-merges into a cluster. The canonical member is the first
seen, or on a tie the one from the higher-priority source in `sources.yaml`. Others get
`duplicate_of` set and never advance past Stage 1.

Fuzzy near-misses (same company and country, title token Jaccard >= 0.8) are **flagged in
the sheet for review, never auto-merged.** Auto-merging on fuzzy title match would
silently drop a genuinely different role at the same company, which is a worse failure
than a duplicate row.

`applied` is keyed on `identity_key`, so once an application exists for a cluster, a
later posting joining that cluster is marked `already_applied` and stops at Stage 1.

## 6. Stage 1, Fetch

### 6.1 Adapters

One interface, `fetch(query, since) -> list[PostingStub]`. Adapter tiers:

**Discovery tier** - aggregator APIs and feeds whose terms permit programmatic access.
Candidate set: Adzuna, Arbeitnow, Remotive, Jobicy, The Muse, Himalayas, HN
Who-Is-Hiring via the Algolia API, plus RSS from EU boards. **Terms, auth requirements
and rate limits are verified per source during implementation and the result written into
`sources.yaml` as a comment. This is a build task, not an assumption.** A source that
fails verification is removed rather than shipped with a guess.

**Manual tier** - the `INBOX` sheet tab and `config/manual_urls.txt`. The URL is fetched
once, canonicalised, given `source=manual`, `prelim_score=null` and
`bypass_prelim_threshold=true`, and flows through Stages 2 to 4 identically. Manual rows
are excluded from tuning metrics, since they have no prelim score to diverge from. This
is the only path by which a LinkedIn, Indeed, StepStone or Xing posting reaches the
pipeline.

**Company tier** - deferred. Building 200 to 400 companies with ATS slugs is days of work
before the pipeline produces a single row. The company list instead grows as a byproduct:
every posting that surfaces records its company and, where detectable, its ATS vendor and
slug, into a `companies` view. Revisit at week three when there is real data to seed from.

Excluded by design, with a reason string in `sources.yaml`: LinkedIn, Indeed, Glassdoor,
StepStone, Xing. Never fetched programmatically.

Career-page fetches, where they occur, respect robots.txt, run at one request per host
per two seconds, and use ETag and Last-Modified conditional requests.

### 6.2 Preliminary scoring is deterministic

No model call. A weighted feature vector over: title match against the target-title
vocabulary, seniority tokens, location and country, working language, remote flag,
source priority, salary metadata when present, and company record when known.

Rationale, and this is the load-bearing reason: the feedback loop has to tune something
machine-adjustable. A weighted feature vector can have its weights moved and the change
read afterwards. A prompt cannot. If both scorers were model calls, divergence would
measure noise between two models rather than fetch quality.

Cost per row: zero.

### 6.3 Stage 1 filters

Filters that can be decided from posting metadata run here and never cost a call:

- Geography, from location and remote metadata
- Salary floor, when the posting carries a salary range
- Working language, when declared in metadata
- Already applied (`identity_key` in `applied`)
- Duplicate of an existing cluster

**Reject only on positive evidence.** A missing field never rejects a row; it defers the
decision to Stage 2. A posting with no salary metadata is not below the floor, it is
unknown.

Filters needing the body (language requirement level, Microsoft-only stack, working
student, C++ engine internals, UX writing) run at Stage 2. See section 7.3.

## 7. Stage 2, Deep evaluation and the feedback loop

### 7.1 Per row

Fetch full JD text (adapter payload where it carries one, otherwise a single page fetch),
one traced LLM call, produce `EvaluationResult`. Full text, never truncated.

Rows where text cannot be retrieved are marked `unfetchable` and never reach Stage 2.
**What fraction of adapter payloads carry full JD text is unknown until the adapters
exist. It is measured, not assumed:** `jd_text_coverage` is reported per source in every
`FetchQualityReport`.

Model: **Claude Sonnet 5** (`claude-sonnet-5`), `output_config: {effort: "low"}`. Chosen
over Haiku 4.5 for two concrete reasons: Haiku's minimum cacheable prefix is 4096 tokens
against Sonnet 5's 512, and the Stage 2 static block is likely to sit under 4096 tokens,
which would silently disable the largest cost lever in the system; and Sonnet 5 has a 1M
context window, so full JD text never forces a truncation decision. Model id is a config
value.

### 7.2 The loop, made explicit

**Metric artifact.** `FetchQualityReport`, written per run into `artifacts/runs/`,
versioned, never overwritten:

- MAE between prelim and refined score
- Signed bias, which distinguishes "prelim is systematically optimistic" from "prelim is
  noisy". Those need different fixes
- Spearman rank correlation, since ordering matters more than absolute score
- Precision at threshold: of rows prelim ranked in the top N, what fraction cleared the
  deep threshold
- All four broken down per source and per query term, which is the granularity the tuner
  acts on
- Per-feature signed divergence, which is the granularity the weights act on
- `jd_text_coverage` per source

**Tuner.** A deterministic policy, not a model call. Reads the report, emits a **diff**
against `tuning_state.yaml`:

- Source weights adjusted by precision at threshold
- Query terms retired when their rows consistently underperform
- Feature weights nudged by per-feature signed divergence
- Threshold shifted to hold a target yield of rows-above-threshold per run

**The tuner never writes config.** It writes a proposal to
`config/tuning_proposals/<run_id>.yaml`. Applying one requires
`pipeline tune apply <run_id>`, run deliberately. `auto_apply` defaults to false and
stays false. Structurally, the tuner module has no write path to `scoring.yaml` or
`tuning_state.yaml`; only the apply command does.

Rationale, affirmed as a design constraint rather than a default: the tuner has no ground
truth. Divergence measures agreement between two of our own scorers, not correctness. The
only real signal is which applications got replies, and that is weeks delayed and low
volume. The tuner stays advisory.

**Guardrails**, because a feedback loop that eats itself is the standard failure here:

- No adjustment below 20 scored rows in the batch
- Per-run weight delta clamped
- A fixed exploration quota, so a down-weighted source still gets sampled and can recover.
  Without it the loop converges on whichever source happened to win in week one

### 7.3 Hard passes

PART 3 hard passes are evaluated at Stage 2 and terminate the row before Stage 3, so a
hard pass never costs a generation call. The company filter (100-plus employees, or
Series B and above) is resolved per company, cached 30 days, and when size cannot be
determined the row is flagged `size_unknown` and surfaced rather than dropped, per the
standing rule that a good role failing the filter is flagged and never silently dropped.

## 8. Stage 3, Generation

Two calls, for rows above threshold. Model: **Claude Opus 5** (`claude-opus-5`),
`output_config: {effort: "high"}`.

**3a, tailoring brief.** Short, human-readable, cheap. Names the two or three
capabilities the JD is buying, the JD's own nouns, which systems prove them, which
projects appear, whether Formula Dream is carried or dropped. This artifact is where
PART 4 rules 9 and 10 are enforced, and it is what gets read when output comes out wrong.
Regenerating documents does not redo it.

**3b, document generation.** Emits `ApplicationDocument` via structured outputs.

Output lands in the existing employer folder. Stage 3 shells out to
`scripts/new_application.py` to create it, reusing that script's `slug()` convention
rather than reimplementing it, so folder names stay identical to hand-created ones and
`/apply`, `/log`, `/answer` and `/prep` keep working unchanged.

## 9. Validation gates

Two gates, and the distinction matters.

### 9.1 Gate A, pre-render, against the JSON artifact

Pydantic model, then deterministic checks. Each returns a field path and a reason. All
checks run; the gate reports every failure rather than stopping at the first.

1. **Dash check.** No U+2012, U+2013, U+2014, U+2015 or U+2212 anywhere, at byte level
2. **Facts check.** Every company, title and date range matches the canonical record
   exactly. Hard fail. This is the anti-fabrication check and the highest-value check in
   the system
3. **Claims check.** Every number appearing in a bullet is in the allowed-numbers set
4. **Forbidden strings.** "fixed-term", "befristet", the retired 176K and 50K figures,
   client names
5. **Rule 9 lead check.** No bullet opens with a domain token (SEO, WordPress, law firm,
   content marketing, social media) unless that token appears in the JD
6. **Length budget.** Character and line model estimating one page

### 9.2 Gate B, post-render, against the PDF

Extract text from the produced PDF. Assert page count is exactly 1. Re-run checks 1 and 4
on what actually rendered.

Gate B is the check that survives both a model swap and a renderer change, because it
never touches the generator and never touches the JSON. Neither gate imports anything
from the generation module.

A gate failure quarantines that row with `status=gate_failed` and names the field. The
batch continues.

## 10. Facts integrity

`config/facts_curated.yaml` carrying a hand-maintained copy of the employment record
would let the anti-fabrication gate silently validate against stale facts. That is
unacceptable for the highest-value check in the system, so facts are derived, not stored.

**Derived block, regenerated in memory on every run.** A deterministic parser (no model
call) reads PART 1 and PART 2 of `CLAUDE.md` and extracts: company names, role titles,
period strings, education entries, contact fields, and the set of every numeric token
appearing in PART 1 and PART 2. That numeric set is the allowed-numbers list for Gate A
check 3. There is no stored file to go stale.

**Curated block, `config/facts_curated.yaml`.** Only what cannot be derived: forbidden
strings, retired figures, the rule 9 domain-token list, and number normalisation rules
(so `10M+`, `10 million` and `10M` compare equal). It carries `claude_md_sha256`.

**Hard fail on divergence.** Every run recomputes the SHA-256 of `CLAUDE.md`. If it does
not match `claude_md_sha256`, the run halts before any LLM call with a non-zero exit and
a message naming the mismatch. Not a warning. Clearing it requires
`pipeline facts sync`, which re-derives the derived block, prints a diff of what changed,
and rewrites the hash on confirmation.

The derived block means the run is always validating against current CLAUDE.md content.
The hash gate means an edit to CLAUDE.md forces a deliberate look at whether the curated
block still holds.

## 11. Observability

Three levels, because "which stage consumed the most tokens today" has to be answerable.

| Level | Langfuse object | Carries |
|---|---|---|
| Posting | `session_id = posting_id` | The full decision chain for one application, replayable end to end |
| Stage | `trace`, one per `(posting_id, stage)`, tagged `run_id` and `stage` | Stage inputs, outputs, duration, status |
| Call | `generation`, one per LLM call | Prompt, response, model, tokens, cache read and write tokens, cost, latency, prompt hash |
| Run | tag `run_id` on every trace, plus the `runs` row | Aggregation key for per-day, per-stage token and cost queries |

Beyond that:

- **Scores on the trace.** Every trace carries prelim, refined, divergence, verdict and
  gate status as Langfuse scores, so all documents below threshold can be queried without
  opening a single artifact
- **Deterministic checks on the same trace as the model call that produced the artifact.**
  Each Gate A check emits a span and a score attached to the generation trace, not to a
  separate log. A failing check is inspectable directly beside the prompt and response
  that caused it, with no correlation by hand
- **Local mirror.** Every field also lands in `llm_calls`, so cost and cache queries work
  offline and a Langfuse outage degrades to local-only logging without blocking the run

## 12. Caching

### 12.1 Prompt caching

The instruction and evidence context is identical across every call within a stage in a
run and is the dominant token cost. This is the largest cost lever in the system.

Prompt layout, per stage:

```
[ static block ]  system: role instructions, constraints, capability layer,
                  facts, scoring rubric, few-shot examples
                  <- explicit cache_control breakpoint HERE, end of shared portion
[ varying tail ]  user: this posting's JD text, this posting's metadata
```

Explicit breakpoint, not top-level automatic caching. Automatic placement lands after the
per-posting tail, so every request would pay the write premium on bytes never read back.
The correct pattern is shared prefix, varying suffix, with the marker at the end of the
shared portion.

TTL: 5 minutes (the default). Rows in a batch run back to back, so the start-to-start gap
between requests sharing a prefix stays under the TTL and a read refreshes the timer at
no cost. The 1-hour TTL doubles the write price and buys nothing here. If per-row latency
is measured above 5 minutes, that is the trigger to switch, not a guess up front.

Caches are model-scoped, so Stage 2 and Stage 3 have separate cache namespaces. They have
different static blocks anyway.

**Silent invalidators to keep out of the static block:** the current date, `run_id`,
`posting_id`, unsorted JSON, anything derived from `datetime.now()`. The cover letter date
belongs in the varying tail.

**Verification is not optional.** Every run reports cache hit ratio from
`cache_read_input_tokens` and `cache_creation_input_tokens`. A ratio at or near zero
across a batch means an invalidator is present and is reported as a run warning, because
the failure mode is silent: no error, just a cost multiple.

Minimum cacheable prefix is model-dependent and silently skips below it (512 tokens on
Sonnet 5 and Opus 5). The static blocks are well above this, but a startup check counts
static block tokens with `messages.count_tokens` and warns if a stage's block is below its
model's minimum.

### 12.2 Result caching

Covered entirely by the skip rule in 5.1. There is no second mechanism.

### 12.3 What is deliberately not cached, and why

| Not cached | Why |
|---|---|
| JD page fetches, beyond HTTP ETag and Last-Modified | Postings change and get pulled. Serving a stale body costs an application, which is worth more than the fetch |
| Rendered PDFs | Regeneration is cents of CPU, and the skip rule already prevents redundant renders. A PDF cache would be a second state store to keep consistent |
| The tuning state | Always read fresh at run start, so an applied proposal takes effect on the next run with no invalidation step |
| Langfuse writes | Buffered, not cached. Losing a trace on crash is acceptable; the local mirror is the durable copy |
| Company size and funding lookups | Cached, but with a 30-day TTL rather than indefinitely. Company size is the input to a hard filter and it changes |
| Anything across runs at the model level | No conversational cache, no shared context between postings. See section 14 |

## 13. Cost and safety

### 13.1 Budget

`config/budget.yaml` carries `max_usd_per_run`, `max_tokens_per_run`, and optional
per-stage sub-budgets. The LLM wrapper keeps a running tally and, before each call,
estimates that call's cost with `messages.count_tokens`. If the projected total would
exceed the ceiling, **the run halts** rather than overrunning: completed stages stay
committed, the in-flight row gets no `ok` event so the next run picks it up, the `runs`
row records `halted_reason`, the report is written, and the process exits non-zero.

Halting is the correct behaviour rather than degrading, because a partial run resumes for
free under the skip rule.

Honest estimate at the stated volume of 100 evaluations and 10 generations per day:

| Stage | Model | Per call | Per day |
|---|---|---|---|
| 2, evaluate | Sonnet 5, effort low | ~$0.013 | ~$1.30 |
| 3a + 3b, generate | Opus 5, effort high | ~$0.10 to $0.15 combined | ~$1.00 to $1.50 |

That lands between $2.30 and $2.80, so **the stated $2.00 per day ceiling is tight and
will bind on full-volume days.** The budget halt is therefore a live mechanism, not a
theoretical guard. The levers if it binds too often, in order of preference: reduce Stage
2 output size (the rationale field is the bulk of it), lower the Stage 3 threshold so
fewer rows generate, then move Stage 2 to the Message Batches API for 50 percent off.
Batches fit Stage 2 exactly, since it is a non-latency-sensitive daily batch, but they add
async polling and interact with prompt caching in ways that need measuring, so this is
deferred until the cost data justifies it rather than assumed into version 1.

### 13.2 Regression set

`tests/regression/postings/` holds a fixed set of postings with frozen JD text and
known-good outputs. It runs before any prompt change ships.

Assertions are on deterministic properties, not string equality, because model output is
not deterministic:

- Gate A passes
- Verdict class matches (strong fit / apply with reframe / hard pass)
- `capabilities_bought` overlaps the expected set above a threshold
- Refined score falls inside a tolerance band
- Rule 9 lead check passes on every bullet

Plus a golden-set diff report written for human reading, since a change can pass every
assertion and still be worse.

The set covers, at minimum: one strong automation fit, one AI/agentic fit, one data
engineering fit, one German-language posting without a C1 requirement, one hard pass by
language requirement, one hard pass by Microsoft-only stack, one posting with no salary
metadata, and one duplicate pair across two sources.

## 14. Statelessness

Each posting is an independent unit of work. There is no conversational memory and no
session store between postings. No posting's evaluation sees another posting's text,
score or output.

The only persistent state is:

1. The Stage 2 feedback signal to Stage 1 (`tuning_state.yaml`, applied deliberately)
2. The applied-to record used for idempotency (`applied`, keyed on `identity_key`)
3. `stage_events`, which is the resumability ledger, not memory

Nothing in this design requires more than that, and if a future stage appears to need
cross-posting context, the requirement gets named and justified against statelessness
before any store is added.

## 15. CLI and scheduling

```
pipeline fetch     [--limit N] [--source S] [--dry-run]
pipeline evaluate  [--limit N] [--only <posting_id>]
pipeline generate  [--limit N] [--only <posting_id>]
pipeline render    [--limit N]
pipeline run                              # all four, in order
pipeline report    [--run-id R]           # FetchQualityReport + cost + cache hit ratio
pipeline tune show <run_id>               # the proposed diff
pipeline tune apply <run_id>              # the only write path to scoring config
pipeline facts sync
pipeline export    [--run-id R]           # rewrite the xlsx
```

Global flags: `--force <stage>` bypasses the skip rule for named rows, `--dry-run` makes
no LLM call and no write.

Scheduling is Windows Task Scheduler, daily. Single process, sequential, with a per-source
rate limiter. At 100 rows a day, anything more is cost paid forever for a problem that
does not exist. Missed days are not backfilled; the next run fetches what is currently
posted.

## 16. Error handling

Three failure classes, and none of them aborts a batch:

| Class | Behaviour |
|---|---|
| Transient (network, 429, 5xx) | Retry with backoff, up to 3, within the run. Exhausted retries become permanent |
| Permanent (404, unparseable payload, unfetchable JD) | Dead-letter the row, record the class, continue |
| Gate failure | Quarantine with the failing field named, continue |

The only conditions that halt a run: the facts hash mismatch (section 10), the budget
ceiling (13.1), and a subscore axis mismatch between the two scorers (4.1). All three are
integrity failures where continuing produces confidently wrong output.

## 17. Testing

- Unit tests for every deterministic component: canonicalisation, `identity_key`
  normalisation, the prelim scorer, each Gate A check, the divergence metrics, the tuner
  policy, `input_hash` construction
- Adapter shape tests against recorded fixtures, one per source. A source changing its
  response shape is the most likely silent breakage in Stage 1, so each adapter fails
  loudly on an unexpected shape rather than returning an empty list
- Store tests asserting the append-only invariant and skip-rule behaviour
- Gate B tests against fixture PDFs, including a deliberately two-page one
- The regression set from 13.2, gating prompt changes
- No test makes a live LLM call. The LLM wrapper is injected and stubbed

## 18. Version 2, not designed here, not blocked

Direct submission through Workday and Greenhouse. Version 1 records `apply_url` and the
detected ATS vendor per row, which is the only thing version 2 needs from version 1.

## 19. Known risk

The tuner is the component most likely to be wrong in an interesting way, and section 7.2
constrains it to advisory precisely because it has no ground truth. Company size and
funding resolution is the highest per-row cost and the most likely source of silent
wrongness. The one-page constraint is a render-time property being predicted at
generation time, so a Gate A length failure with a regeneration retry is an expected
path, not an exception.
