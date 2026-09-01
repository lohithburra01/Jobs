# SEO Content Workflow - raw capability notes

Source: a private two-person repository for the SEO strategy and article generation half of a
production content pipeline serving a law-firm client portfolio. Two snapshots were present: a
`main` snapshot and a feature-branch snapshot. They are treated here as one codebase plus one
branch. Line counts are never summed across the two.

**Attribution warning, read before using any of this.** The repository has two owners with a
formally separated lane. An SEO domain owner owns the SEO architecture, the decision methodology,
the stage semantics and most of the Python runtime. The candidate owns the technical automation
lane around it: running skills out of chat, transport and cost work, diagnosis, environment and
test infrastructure, and an internal-linking application that consumes the same run data. The
repository's own handoff documents state the boundary explicitly ("the SEO architecture is not to
be redesigned"). Several of the strongest systems below were authored by the SEO owner, not the
candidate. Every claim in this file is a claim about a system the candidate worked on, read and
can explain, not automatically a claim of authorship. See "Flag for verification".

## Systems built

### Bounded evidence-sharded strategy pipeline (feature branch, sole production flow)

**Problem.** The product is one document per client: for every page a law-firm site already has, a
decision to keep, expand, merge, redirect or delete, plus which new pages to create and in what
order. Doing that with a language model over a whole site does not fit in one context window, and
doing it conversationally in a CLI meant runs died mid-way and lost their state.

**Architecture.** A single entry point exposes `fresh`, `resume`, `status`, `execute-pass1` and
`accept`. The chain is fixed: canonical evidence bundle plus sealed manifest, bounded Pass 1,
AI-authored Planning, bounded per-domain units, Arbitration when conflicts are registered, Root
Closure, portfolio transaction, then journal, technical reconciliation, finalizer, internal-link
projection, validator and renderer. The design rule is a hard split of authority: Python may
partition, bind, hash, count, validate, persist, resume and render, but may not invent subjects,
evidence relevance, domain membership, ownership, conflicts, decisions or closure. Everything
semantic is model-authored and must be provable against a contract. The last five stages call no
provider at all.

**Inputs and outputs.** Input is a canonical evidence bundle assembled from sitemap inventory,
crawl and content snapshots, search-console evidence, an internal-link graph and an authorized
business-constraints record. Output is an immutable final strategy master plus a current-to-target
internal-link implementation matrix and a rendered human-readable projection. Stages hand off
through sealed files on disk, never conversation state: every artifact carries a `*_hash` over its
own canonical bytes, re-verified on read. Run state is append-only or write-once, transitions are
numbered event files, and a resume reloads the sealed artifacts, re-validates hash bindings and
republishes only genuinely ready units. The stated invariant is that conversation memory is never
runtime authority.

### Evidence sharding and manifest layer

The canonical bundle is decomposed into immutable evidence shards: one GLOBAL shard, one SUBJECT
shard per search subject, one PAGE shard per existing page, plus segmented full-text shards for
page content. Each shard records `source_accounting`, a list of JSON pointers back into the bundle
with a per-value hash and a `primary` flag, and the builder refuses to let two shards claim
primary ownership of the same source path. That is what makes "did the model actually use the data
I gave it" answerable after the fact. Every subject, page, evidence row and shard also gets an
opaque handle derived from a hash of its identifier plus the bundle hash, so the model only ever
sees handles, never real identifiers or client URLs; the runner translates back after validation.

### Retrieval-driven Pass 1 (the feature branch's headline system)

Rather than pushing the whole site into one prompt, Pass 1 partitions subjects into deterministic
work units of at most three subjects, ordered by stable identifier. Each unit starts with only its
own bootstrap subject shards delivered. The model returns exactly one of two outcomes: a
`DECISION` covering every subject in the unit exactly once, or a `RETRIEVAL_REQUEST` naming
additional shard handles and stating why. The runner delivers those shards byte-for-byte into a
fresh context and asks again. At most two retrieval rounds and three provider calls per unit. On
the final call retrieval is structurally removed from the schema, so the model must decide from
what it has or record an explicit limitation with calibrated confidence.

This is agent-style retrieval where the model chooses its own context, but the choice is
constrained to an enumerated set the runner controls, and the runner performs no selection of its
own. That separation is the point: the runner may not decide what evidence is relevant, because
relevance is an SEO judgement.

### Semantic reuse layer

A semantic-input binding hashes only meaning-bearing inputs and contracts per stage, deliberately
excluding implementation and wiring. If that hash is unchanged a completed unit result is reused
with zero provider calls; if it changes, only that unit and its real descendants are re-authorized.
This is what makes re-running after a code refactor cheap instead of a full re-spend.

### Article generation and briefing skills (both snapshots)

Two downstream Claude Skills sit at the end of the chain. A content-briefing generator turns an
approved keyword master into a structured brief for exactly one article, with its own outline
rules, quality check and review workflow, plus two helper Python scripts for inspecting and
extracting candidates from keyword files. A German legal-article skill then writes the article
from that brief as a 17-phase gated workflow across three macro-phases: planning (evaluate the
brief, produce a writing plan, get approval), writing (section by section with running quality
control), then derivation and closure. It writes the body first and the introduction last, then
automatically derives two secondary assets (a piece for a third-party legal directory and a short
business-profile post capped at 1,500 characters) and pushes all three through a single combined
expert legal review loop. After the first full handover it is forbidden from re-emitting full text
and must return search-and-replace pairs only, which is a direct token-cost control.

Both are skills, meaning structured instruction sets with routed reference files, not services.
They are substantial prompt engineering artifacts, roughly 7,300 lines of Markdown and Python
across the two, but they are not distributed systems and should not be described as such.

## Prompting and LLM engineering

**Prompt construction is code, not a template string.** Pass 1 prompts are assembled by a
dedicated module returning a list of named sections so each section's byte cost can be attributed
to a budget line: the task, one block per normative reference, then the bounded view split into
canonical global context, work unit context, bootstrap evidence, retrieved evidence and retrieval
state, each rendered as fenced canonical JSON, plus a repair-context section when present.
Assembly is fail-closed: the builder asserts the bounded view has exactly the expected field set,
that bootstrap shard handles are unique, that every bootstrap handle appears in the delivered
evidence, and that the task is prefixed by exactly one leading reference so the same normative text
is never duplicated. Any deviation raises before a call is made.

**Prompts are versioned by content hash.** Every reference file and the task text is loaded from
disk and wrapped with an id, a version and a sha256 of its bytes. The completed model attempt
record stores those hashes, so any output traces to the exact prompt revision that produced it. A
separate lock file freezes an evaluation set together with the sha256 of the reference files it was
written against, with the explicit rule that cases must not be adapted to observed model output
after the fact.

**Structured output is enforced twice.** First the output schema is narrowed per call: allowed
subject handles, page handles and citable evidence handles are rewritten into enums containing
only what was actually delivered, and when retrieval is exhausted the retrieval branch of the
`oneOf` is deleted outright so the model physically cannot ask for more. Second, after the
response, a hand-written validator re-checks totality, handle membership, non-overlap, delivery
provenance and forbidden legacy fields, because schema validity is treated as necessary but not
sufficient.

**A provider-schema projection layer exists because provider structured output is a strict subset
of JSON Schema.** It inlines local `$ref`s recursively, strips `$schema` and `$id`, detects
reference cycles, and audits the projected schema against the documented Anthropic
structured-output subset: allowlists of supported keywords, types and string formats, a
requirement that every object sets `additionalProperties: false`, and caps on optional parameters,
union parameters and enum values. Keywords the provider defers rather than enforces (`minLength`,
`maxItems`, `uniqueItems`, numeric bounds) are tracked separately so the local validator knows it
cannot rely on the provider for them.

**Model routing is a sealed capability registry, not configuration.** A provider capability module
holds the technical profile for the model family in use, marked `customer_configurable: False`,
and computes the safe single-call input ceiling as `floor(context_window * safety_fraction) -
reserved_output - protocol_reserve`. A frozen capability with the same contract is used for
provider-free tests so no test can accidentally traverse a real profile. A completion-budget
preflight then measures actual rendered prompt bytes plus schema bytes, converts to estimated
tokens using a conservative bytes-per-token ratio, adds an output reserve computed as a base plus a
per-subject amount, and raises distinct errors if the reserve exceeds the provider output limit or
if input plus reserve exceeds the context window. Config that raises any ceiling or lowers any
reserve is rejected with a dedicated relaxation-forbidden error, so budgets can only be tightened.
The preflight result is hashed and bound into the execution authority.

**Two transports, one boundary.** Pass 1 runs through the Claude CLI in a deliberately stripped
isolation mode: no tools, no session persistence, no setting sources, strict MCP config, JSON
output, explicit model flag, projected schema passed as a JSON-schema argument, and the environment
reduced to a six-variable allowlist. Pass 2 stages run through the Messages API directly, declared
as a frozen boundary descriptor: one message, one provider turn, one structured-output attempt,
zero re-authoring retries, zero transport retries, no tools, no system prompt, adaptive thinking,
an explicitly required effort level (provider defaults forbidden), and JSON-schema output format.
TLS is centralized rather than left to defaults: a dedicated module resolves exactly one readable
CA bundle (environment variable, then certifi, then OpenSSL default file), refuses to fall back to
an empty default store, asserts `CERT_REQUIRED` and hostname checking, hashes the CA bytes into a
readiness record, and offers a handshake-only probe that sends no HTTP request, no credential and
no customer bytes.

**Retries on malformed output are deliberately absent, and that is the design.** The recorded
policy is no automatic retry, no semantic repair, no re-authoring. A malformed or incomplete
response is captured immutably and terminally rejects that attempt. Re-execution requires a
separate, explicitly authorized retry preparation that must first prove from the immutable capture
exactly which technical failure occurred. A deliberate position with a real cost, not an oversight.

**Skills and agent patterns.** The repository is organized as Claude Skills: a `SKILL.md`
dispatcher with YAML front matter per capability, plus routed reference files the skill tells the
agent to read only when the requested operation needs them. That routing is the context-budget
strategy at the agent layer. A repository-level agent instruction file requires reading the current
official Agent Skills best-practice documentation before editing any skill file, and refusing to
edit if that documentation cannot be reached.

## Scale and numbers

All figures below were read out of the repository. The kind of file each came from is named.

**Codebase size** (measured directly by line count over `.py` files)

- Feature branch total: 62,427 lines of Python; the production pipeline module alone is 24,452.
- `main` snapshot total: 173,454 lines of Python. The branch represents a large deliberate
  reduction, not a separate smaller project. Do not add these together.
- 44 JSON Schema files in the pipeline module; 29 versioned contract families on `main`.
- Article and briefing skills: roughly 7,300 lines of Markdown and Python combined.

**Test and audit evidence** (audit markdown and sealed acceptance JSON in `docs/`)
- 264 provider-free tests passed, 3 skipped because a validation dependency was absent.
- A later sealed acceptance record: 188 tests run, 0 failures, 0 errors, 0 skips, on Python 3.14
  with jsonschema 4.26.0, recording optional-dependency skips going from 10 to 0.
- 110 tracked Python files compiled; 24 CLI entry points checked.
- 0 provider calls and 0 paid-data-source calls during the whole audit.
- On the older `main` snapshot the candidate's own diagnostic note records 106 tests, 105 passing,
  the single failure being a line-ending issue.

**Scale acceptance** (sealed scale-acceptance JSON plus audit markdown)
- Bounded-tree acceptance passed at 50, 500, 1,000 and 3,718 subjects with zero provider calls.
- Corresponding work-unit counts: 8, 62, 123 and 454 units.
- Fixed artifact bounds regardless of scale: tree fanout 4, leaf records 12, catalogue entries 12,
  node conflicts 4, string length 2,048, semantic payload 18,000 bytes. Stated growth invariant:
  only unit count or tree depth may grow with project size.

**Token and call budgets** (source code constants)
- Model capability profile: 1,000,000 token context window, 64,000 max output tokens, 0.80 context
  safety fraction, 4,096 tokens reserved for provider protocol overhead.
- Per-stage call caps: 256,000 input tokens, 256,000 prompt bytes, 56,000 provider-schema bytes,
  64,000 output tokens; delivered-evidence byte caps 72,000 (planning), 96,000 (Pass 1 catalogue
  and closure), 120,000 (domain and arbitration).
- Pass 1 retrieval: max 2 retrieval rounds, 3 provider calls per work unit, 3 subjects per work
  unit, 12 requested shards per round. Subprocess timeout 1,800 seconds.
- Output reserve: 8,000 base plus 6,000 per subject; Pass 2 reserve 60,000; single-message reserve
  48,000. Input estimate constrained to 1.0 to 2.0 bytes per token.
- Provider structured-output limits encoded from the docs: 16 enum values, 24 optional parameters,
  16 union parameters.

**A real observed provider call** (sealed canary JSON)
- Wall-clock duration approximately 52 seconds. Requested model `claude-sonnet-5`, reached; CLI
  version 2.1.224; 1 provider call started, 0 retry calls, status success; raw response 11,546
  bytes.
- Target-model usage: 3 input tokens, 36,405 cache-creation, 33,700 cache-read, 4,768 output.
  Whole-tree totals across the CLI's internal 3 turns: 18,702 input, 36,405 cache creation, 33,700
  cache read, 4,784 output. An auxiliary model (`claude-haiku-4-5-20251001`) accounted for 18,699
  of the input tokens and 16 output tokens.

**Business and workload context** (candidate handoff notes, not code)
- Roughly 40 SEO clients, 4 blog posts per month each. The internal-linking application targets
  roughly 12 clients.
- One CLI call measured burning over 200,000 output tokens because the CLI ran extra internal
  rewriting rounds. This is the observation that motivated moving to a direct one-request Messages
  API call. A separate runaway on the linking side reached 6.9 million tokens, which is why the
  linking spec mandates a hard per-run token cap and no agent fan-out.

**Earlier out-of-chat skill runs** (candidate's own migration findings document)
- 3 of 6 skills run fully out of chat on real client data, each an isolated sub-run reading input
  from a file and writing output to a file.
- Peak context per run approximately 16K, 31K and 23K tokens; total tokens per run approximately
  56K, 87K and 100K. 74 URLs classified in the first stage; 39 items self-flagged provisional in
  the second.
- The six skills' rulebooks alone totalled approximately 139K tokens, about 70 percent of a single
  chat window: the measurement that justified isolated per-stage execution.

**Not found in repo.** Cost figures: no per-run currency cost, no per-client spend, no price table
anywhere in either snapshot; cost appears only as a stated objective and as token counts. Article
throughput: the 4-posts-per-month figure is a business target from a handoff note, with no run log
recording articles actually produced. End-to-end pipeline latency: only the single ~52 second
canary call is timed, and the audit states no full live end-to-end run has been completed.

## Technical decisions and tradeoffs

**Split authority between Python and the model, and write it down as a contract.** Python
partitions, binds, hashes, counts and validates; the model decides. The cost is a large amount of
contract and schema machinery. The benefit is that when output is wrong you can tell whether the
runner mis-fed the model or the model reasoned badly, otherwise the hardest question in this kind
of system.

**No automatic retries, anywhere.** Rejected attempts are captured and terminated rather than
silently re-rolled. Operators see more failures, but every accepted result corresponds to exactly
one auditable model call. Given the traceability requirement ("I want to know why this decision was
made, and whether all the data was used"), silent retries would destroy the property the system
exists to provide.

**Model sees opaque handles, never real identifiers.** Costs a translation layer in both
directions. Buys two things: the model cannot invent a plausible-looking identifier that does not
exist, and constrained handle enums make the schema itself enforce scope. Relatedly, constrain the
schema per call rather than instructing in prose: deleting the retrieval branch when rounds are
exhausted is structurally stronger than telling the model not to ask again, at the cost of
rebuilding and re-hashing the schema on every call.

**Conservative byte-based token estimation instead of a tokenizer.** The preflight uses a
bytes-per-token ratio bounded between 1.0 and 2.0 rather than counting exactly: pessimistic and
provider-independent. The code is explicit that structured output adds provider-managed prompt
tokens not observable before the request, so the declared payload is documented as a bound and
never as an exact total-input proof, with a 20 percent context safety margin held for that
unobservable contribution.

**One request, one model, no tools, no retries, hard limit.** Chosen after measuring a CLI call
that internally fanned out and burned over 200,000 output tokens. The CLI transport remains for
Pass 1 where it was already proven; new stages went to the Messages API. Keeping both costs surface
area, justified by not re-proving a working path.

**Bound every call by construction so scale changes unit count, never call size.** This is why the
acceptance suite runs 50 through 3,718 subjects and asserts the byte and token caps hold. A large
client produces more calls, not longer ones, which is the tractable direction.

**Fail closed on unknown contract versions, hash mismatches and open gates**, combined with
write-once outputs and atomic publishing into fresh directories; the stated rule is never to
silently overwrite, migrate or normalize an existing run. Relatedly, tests must not skip: the
clean-room runner treats a skipped test as a failure and stops at the first failing suite, which
surfaced a missing validation dependency as a real gap rather than a green run.

**The known architectural weakness, stated honestly.** The pipeline splits a site into bounded
domains, decides each independently, then has to referee contradictions that exist only because it
split. A human strategist holds the whole site at once and is consistent by construction. At the
observed client size the data is small enough not to require splitting at all. The candidate's
diagnosis is to keep sharding at genuinely large scale but make the ordering and merge decision
once over a compact summary rather than stitching blind parts together. This is a diagnosis
recorded in a handoff document, not a change that was implemented.

## Hard debugging

**Long structured output silently under-delivering.** Root Closure computes the exact set of
cross-domain conflicts and requires exactly one decision per conflict: same count, no duplicates,
no unknown keys, every row carrying a directive and a rationale. A mismatch raises
`CLOSURE_ROOT_CONFLICT_TOTALITY` and rejects the whole run. In practice the model returned fewer
rows than requested, merged two conflicts, or renamed a key: the classic failure of asking for one
long exhaustive structured list in a single shot. Recorded against a real client run and the top
open blocker at handoff. The candidate's proposed fix was to batch the conflicts, then diff
returned against expected and re-ask only for the missing keys and merge, rather than rejecting and
retrying everything, and explicitly not to weaken the totality gate, because the gate is the
traceability requirement.

**Extended thinking eating the JSON output budget.** A retry-preparation routine exists purely to
prove this from an immutable capture: it reads the sealed provider envelope, checks `stop_reason ==
"max_tokens"`, checks `output_tokens` exactly equals the configured `max_tokens`, extracts
`thinking_tokens` from usage details and computes the remaining output budget. If thinking consumed
enough that less than a minimum structured-output reserve remained, the failure is classified
`BOUNDED_RESPONSE_TRUNCATED` with authority `PROVEN_MAX_TOKENS_THINKING_EXHAUSTION`, and only then
is re-execution authorized. Root cause: adaptive thinking and structured output share one output
budget, so a reserve adequate for the JSON alone was not adequate overall.

**Provider schema grammar-compilation rejection with no model turn.** An earlier closure schema
encoded totality directly in the schema shape: one required named property per conflict key and per
selection slot, with `additionalProperties: false`. For a real client that is a large generated
object, and the provider rejected it at grammar-compilation time before any model turn. The fix was
a grammar-light wire contract carrying only four AI-authored fields as generic arrays, with the
concrete conflict keys, selection identifiers and candidate identifiers living in the sealed request
and checked locally after capture. Schema-encoded totality does not scale, so totality moved from
the schema into post-capture validation while remaining just as strict.

**A schema that permitted the empty answer.** Another proof routine covers a captured response
containing empty arrays that nonetheless satisfied the provider schema then in force: the model
returned nothing useful and the provider accepted it. A permissive schema turns a semantic failure
into a silent success, which is why the current validator checks totality against sealed
requirements rather than trusting schema validity. A further routine handles a version where the
outer schema validated but a field carried an untyped JSON string that failed local parsing,
producing `CLOSURE_ROOT_DECISION_MANIFEST_MALFORMED`: nesting serialized JSON inside a
structured-output field defeats the point of structured output.

**Undelivered evidence cited in output.** A frozen regression case records a real attempt where the
model returned 7 subject decisions with 7 accounting rows while zero shards had been delivered; the
run was rejected with `PASS2_EVIDENCE_HANDLE_INVALID` on the first evidence handle. The model cited
evidence it had never been shown. The structural fix is the constrained-enum approach: only
delivered handles are representable in the schema.

**Cross-platform hash breakage that looked like fifty real defects.** Every artifact is bound to a
sha256 of its file bytes. Running the repository on Windows converted line endings on write, so
every hash mismatched and the pipeline failed with roughly fifty of its own contract errors that
read as genuine architectural defects but were not; the same suite was green on macOS. This cost a
full working session and is now a documented hard environment constraint. A related genuine
finding: a test compared raw file bytes against a fixture instead of parsed JSON, exactly the
fragile pattern that makes this class of bug reappear.

**Checks that validate form rather than answer.** The most consequential finding is a diagnosis
rather than a code fix. On the older snapshot a run produced a finished strategy with 65 page
profiles, every one marked priority `high`, every one ranked equally first, 36 cannibalisation
assessments recorded `NOT_ASSESSABLE`, and the document stamped `READY` with the test suite green.
Root cause: validators asked whether every field was populated, never whether the answer was
sensible; "high" is a valid priority and "not assessable" is a valid value, so everything passed.
The deeper cause is that nothing ever compared all 65 profiles together, so no ordering could
exist. The recorded recommendation was to define acceptance criteria for the finished document
first and wire those as pass or fail checks.

## What the feature branch added

The branch is not a small feature addition. It adds an entire new production module and
decommissions the previous runtime.

- **A new `seo-pipeline` module, 24,452 lines of Python, present only on the branch.** 396 files
  exist only on the branch, 385 inside this module. It becomes the sole executable production flow,
  a single entry point replacing the previous multi-dispatcher arrangement.
- **The AI-directed retrieval Pass 1 the branch is named for**: bounded work units of at most three
  subjects, a two-outcome model contract (decide or request evidence), at most two retrieval rounds
  and three calls per unit, and a per-call schema narrowed to handles actually delivered.
- **The evidence shard and manifest layer** retrieval needs: opaque handles, per-shard source
  accounting with single-primary-owner enforcement, byte-verified shard loading, and sealed delivery
  manifests recording exactly which shards were handed over in which round.
- **Direct Anthropic Messages API transport** alongside the existing CLI transport, with the
  centralized verified-TLS module, the one-turn no-tools no-retry boundary descriptor, and required
  explicit effort selection.
- **The provider-schema projection and compatibility auditor**, encoding the provider's strict
  structured-output subset and separating provider-deferred from provider-enforced keywords.
- **The sealed provider capability registry and completion-budget preflight**, including the
  relaxation-forbidden rule that ceilings may only be tightened.
- **The semantic reuse and invalidation layer**, hashing only meaning-bearing inputs so a code
  change does not trigger a re-spend.
- **Scalability closure and acceptance machinery**, producing sealed evidence at 50, 500, 1,000 and
  3,718 subjects.
- **Explicitly authorized retry preparation for closure and continuation for arbitration**, each
  requiring a proof, drawn from the immutable capture, of which technical failure occurred.
- **New documentation authority**: a target-architecture document, a production-readiness handoff,
  a single authoritative backlog, a historical-data boundary document, and seven sealed acceptance
  JSON records.
- **Decommissioning**: the earlier Track B, Stage 2 and V1 runtimes are declared dead and forbidden
  as recovery, replay or fallback paths. 499 files present on `main` are absent from the branch,
  which is why the Python total drops from 173,454 to 62,427.
- **A stated readiness position rather than a claim of completion**:
  `THEORETICALLY_PRODUCTION_CAPABLE: YES`, `FULLY_PRODUCTION_PROVEN: NO`, with four named remaining
  items and one known open blocker.

## Technology inventory

- **Languages and runtime**: Python 3.10 or newer (an acceptance run recorded on 3.14), Markdown
  as the skill and reference format, JSON and NDJSON as the artifact formats.
- **Standard library only for transport**: `urllib.request`, `ssl`, `socket`, `subprocess`,
  `hashlib`, `json`, `pathlib`, `argparse`, `unittest`. No HTTP client dependency, no LLM SDK, no
  web framework, no database. The Anthropic call is a hand-built POST with `x-api-key` and
  `anthropic-version` headers.
- **Model access**: Anthropic Messages API structured output (`json_schema` output format,
  adaptive thinking, explicit effort) and the Claude CLI in a stripped no-tools isolation mode with
  `--json-schema`.
- **Models referenced**: `claude-sonnet-5` as the configured target; `claude-haiku-4-5-20251001`
  observed as a CLI-internal auxiliary model in a sealed canary record.
- **Third-party dependencies** (a deliberately minimal pinned set): `python-docx`, `openpyxl`,
  `pypdf`, `python-pptx`, `PyYAML`, `jsonschema`, `certifi` as an optional CA source.
- **Contracts, validation and integrity**: JSON Schema (44 schemas in the pipeline module, 29
  versioned contract families on `main`), hand-written cross-artifact semantic validators, sha256
  over canonical JSON bytes, seal-and-verify helpers, append-only state event files, atomic publish
  into fresh directories.
- **Agent tooling**: Claude Skills with YAML front matter and routed reference files; a
  repository-level agent instruction file.
- **Testing**: `unittest` discovery via a custom clean-room runner that treats skips as failures,
  frozen provider envelopes and test transports for provider-free execution, golden fixtures, and
  frozen evaluation case files locked by reference-file hash.
- **Data sources integrated upstream**: sitemap inventory, crawl and content snapshots, Google
  Search Console evidence, an internal-link crawl graph, and a commercial keyword-research provider
  (planned and cost-governed, not invoked by the active runtime).
- **Process**: branch plus reviewed pull request only, never a direct commit to the default branch.

## Flag for verification

**Authorship is the single biggest risk in this file.** The pipeline runtime, the SEO decision
methodology and most of the contract machinery were authored by the SEO domain owner; the candidate
joined to own the automation lane. Before any "Systems built" content goes on a resume, the
candidate must decide system by system what they wrote, what they debugged and what they only read.
Safe framing: "I worked inside a production LLM pipeline of this shape, owned the transport and
cost lane, and diagnosed its central failure mode." Unsafe: "I built a bounded evidence-sharded
strategy pipeline."

**Likely NOT the candidate's authorship**: the retrieval runtime, the evidence shard and manifest
layer, the provider-schema projection auditor, the closure and arbitration machinery, the
scalability closure system, and the SEO decision methodology reference. The handoff notes describe
several in the third person ("he built", "he already has").

**Likely the candidate's own work**: running three skills fully out of chat on real client data
with the measured token figures; the diagnosis that validators check form rather than answer; the
diagnosis that splitting the site manufactures the conflicts that then kill the run; the Windows
line-ending hash-mismatch finding; the byte-comparison test finding; the stale README assertion
finding; and the internal-linking product spec. Confirm each.

**The internal-linking application is a spec, not a shipped system.** Its own document is marked
"vision / north-star (not yet built)". The orchestrator-plus-workers design, the deterministic
gate, the budget governor and the feedback-versioning model are design, not running code. The 6.9
million token runaway that motivated its budget caps is a real measurement and can be cited.

**"Production" needs care.** The repository's own verdict is `FULLY_PRODUCTION_PROVEN: NO`, with no
completed independent live end-to-end run and one open blocker at the last stage. Say
"production-intended pipeline that had passed provider-free acceptance but not a full live
end-to-end" rather than "production pipeline".

**Do not sum the two snapshots.** 173,454 lines on `main` and 62,427 on the branch are the same
project at two points in time; the branch is a large deliberate reduction. The 173k figure was
already reduced by the SEO owner before handoff, so quoting it as current state would be wrong.

**Numbers to source cold.** The 264-test and 3,718-subject figures come from an audit document and
sealed acceptance JSON the candidate did not produce; the 188-test figure comes from a later
acceptance record. If asked "did you run that suite", the honest answer is that the candidate ran
the suite on the older snapshot (106 tests, 105 passing) and read the sealed acceptance evidence for
the branch.

**The 52-second canary is one isolated synthetic planning call, not pipeline latency.** Never
present it as end-to-end runtime. Similarly, cost claims are unsupported: no currency figure exists
anywhere, so token counts and the 200k-output-token CLI observation are citable but converting them
to money or a percentage saving is not.

**The German-language legal article skill.** The candidate does not read German and does not have
SEO domain knowledge, both stated plainly in the handoff. Defensible: the workflow architecture,
the gating, the token-control decision to emit search-and-replace pairs instead of full text, the
input-contract design. Not defensible: the legal-content quality rules or the SEO rules.

**Anything about the model's SEO judgement quality.** There is no scoring, no rubric and no measured
quality baseline. The evaluation files are behavioural expectation cases, several frozen and never
yet run against a model. Do not claim evaluation-driven quality improvement.
