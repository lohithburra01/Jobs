# 02 - EVIDENCE

Everything that may appear in a resume, a cover letter or an interview answer. Nothing may be
claimed that is not in this file. The FLAGGED section at the end is binding and overrides
every other section in this file.

---

# PART A - IDENTITY

**Positioning:** AI & Automation Engineer. Takes a manual, judgment-heavy, repetitive process
and makes it run reliably without a human in the loop, whatever stack it has to run on.

**The line:** Most AI work stops at generation. The interesting problem is everything around
it: what triggers the run, what validates the output, what happens when a node fails at 3am,
and how it stays reproducible across a hundred clients.

**The domain is never the identity.** He has automated SEO content, internal linking, social
publishing, client onboarding and security scanning. Different subject matter, one job: find
the manual process, model it, build the system that runs it unattended, and handle the failure
modes. The employer's domain and the employer's stack were both inherited. Working well inside
a stack he did not choose is itself a selling point, not a limitation. Never write him as an
SEO person, a WordPress person, a content person or a social media person.

**Target titles:** AI Engineer, Automation Engineer, AI Automation Engineer, Agentic AI
Developer, Forward Deployed Engineer, Solutions Engineer, GTM Engineer, Head of Automation.

**How he builds (the through-line, sell this):** His capability is not a fixed stack, it is
build-as-he-goes. New tools, APIs, endpoints, MCPs and platforms get researched at the moment a
problem needs them and implemented properly the same day. At Corominas he ran internal linking,
web dev and social media automation in parallel and shipped systems, protocols and repeatable
workflows, not one-off scripts, plus his own working protocols on top: handoff docs, session
memory, conventions so work survives across sessions. A JD listing a tool he has not touched is
not a gap to hide. That is the thing he is good at. Never write him as a single-stack
specialist.

**Contact**

    burralohith01@gmail.com
    +49 1573 7742759
    linkedin.com/in/lohithburra
    lohithburra.framer.website
    github.com/lohithburra01

**Work authorisation:** EU Chancenkarte visa. Authorised to work in Germany and the EU
immediately, no sponsorship required. Based in Heilbronn, Germany.

**Languages:** English C2, Telugu native, German beginner.

**Audience number (settled, use this one everywhere):** 10M+ views. It is the Formulytics
social presence he built and ran himself, so he can defend every part of it cold: 10M+
cumulative views on Instagram, roughly 20M views per month on Facebook at peak, 26K Instagram
followers. The old 176K followers and 50K+ cumulative figures belong to the main brand account,
not to his page. They are retired. Do not use them again.

**Education**

- MS, Data Science - Stevens Institute of Technology, USA, 2025
- BTech, Mechanical Engineering - JNTU K, India, 2022

---

# PART B - EXPERIENCE

Everything on a resume must trace back to this part or to the capability, systems and numbers
parts below. Never invent. Only reframe.

## Manager, AI & Automation - Corominas Consulting

**Remote, Germany | Jun 2026 - Sep 2026**

No employment-type label on the resume, ever.

Owned the automation layer across a portfolio of roughly 85 client sites. Four parallel
workstreams. The subject matter was legal content marketing and the CMS was inherited legacy;
neither is the point. Reframe every bullet below into the JD's own language.

- Built a multi-tenant engine in Python that turned a manual editorial process into an
  unattended pipeline: event-triggered generation, deterministic quality gating, client preview
  with versioned in-page edits, and dual publish paths behind an atomic state store, with
  per-tenant behaviour carried in config rather than code
- Built the deterministic gate that makes model output safe to ship: 18 automated checks across
  10 families, model-agnostic by design, every AI proposal passing it before a human ever sees
  it
- Rebuilt a judgment-heavy manual task as a 9-stage pipeline alternating model passes with
  deterministic enforcement, after measuring that unconstrained model output fabricated 77% of
  one decision class and omitted 48% of another. 211 pages classified, 566 existing
  relationships captured, 347 decisions shipped through a gate that exits green at zero error
  pages
- Treated orchestration as generated infrastructure rather than hand-built UI state: 26
  workflow definitions totalling 490 nodes, the production ones emitted by Python generators,
  so onboarding a tenant is a config change and not a rebuild
- Replaced opinion with measurement on model selection: benchmarked 40 items across 9 models
  and moved production onto a model costing $0.0109 against a $1.149 reference where it held
  parity on the decisions that mattered
- Co-owned a shared repository with the domain lead: the lead authored the domain skills,
  Lohith built the automation that runs them, then built automation inside the skills themselves
  so each skill self-encapsulates and the outer workflow consumes it as one unit. Two layers of
  automation, one wrapping the other
- Led the technical response when a client WordPress site was taken over mid-engagement:
  identified the vector as a WordPress core pre-authentication RCE, ran a same-day adversarial
  audit across six touchpoints to rule the automation out with evidence rather than assertion,
  and swept roughly 27 client sites for the same exposure that afternoon
- Turned that sweep into a passive credential-free version scanner covering 44 client domains,
  surfacing 2 exploitable sites including one nobody had flagged and 22 leaking version
  information, then audited his own API and closed 5 findings in a single day verified by 22 of
  22 checks, and authored the team's standing security policy

Also built the client onboarding pipeline as a live case study during the interview process and
demoed it to the Managing Director: questionnaire submitted, Claude generates full German law
firm landing page copy across 11 sections, Next.js page deploys to Vercel, preview link in the
client inbox within 30 seconds, feedback form routes to Airtable, Claude regenerates changed
sections, auto-publishes on approval. This directly won the offer. **Caveat, binding: several
parts of that sentence are weaker than they sound. See FLAGGED before repeating any of it. The
30-second figure does not exist; safe phrasing is "generation to reviewable preview link in
under a minute in the demo run", attributed to the demo.**

Stack: Python, Claude API, n8n, WordPress REST API, Airtable, Next.js, Vercel

## AI Automation Developer - Formula Dream

**Remote | Aug 2025 - Jun 2026 | Contract**

Title flexes to "AI Content Pipeline Developer" when the JD is content-shaped. Never split this
pipeline across multiple entries; it is one integrated system.

- Built the Formulytics pipeline end to end. Producer half: GitHub Actions running
  self-scheduling Python render jobs against F1 static livetiming endpoints, writing MP4 output
  to Google Drive under a filename contract
- Poster half: 21-node n8n workflow with dual-trigger reliability, a Drive event trigger firing
  within a minute plus an hourly sweep as safety net, so nothing is missed and nothing fails
  silently
- OpenF1 API chain pulls sessions, meetings, results and drivers to build a factual race
  summary; Gemini with Google Search grounding generates captions as strict JSON
- Auto-publishes to Instagram and YouTube, marks files posted via Drive custom properties for
  idempotent dedup, every HTTP node retries 3x with backoff, failures email with the exact node
  and execution link
- Built a meta-system on top of n8n: Claude generates complete importable workflow JSON
  pre-configured for his credential setup, idea to running workflow in under 10 minutes. 23+
  workflows built total
- Built and ran Formulytics, the social presence the pipeline publishes to: 10M+ cumulative
  Instagram views, roughly 20M views per month on Facebook at peak, 26K Instagram followers

## AI Engineer - Think Round Inc

**Remote, US | Apr 2025 - Mar 2026**

- Built Zoe, a production trauma-informed AI companion with ACE assessment integration, crisis
  detection and multi-layered safety controls
- Designed a context-aware LLM conversation system with memory persistence and confidence
  scoring
- Developed multi-agent platform architecture (ThinkLife) supporting parallel agent development
  across healing, onboarding and FAQ use cases
- Implemented harmful content filtering, crisis resource routing and professional boundary
  enforcement for vulnerable user populations
- Stack: Python, TypeScript, LLM orchestration, API integrations

**Second role held concurrently, 3D Visualization Developer. Gated: use only for 3D or
real-time roles, never alongside the AI Engineer framing on the same resume.** Unity real-time
walkthroughs 15 FPS to 45+ FPS via LOD and light baking; GIS, LiDAR and photogrammetry pipeline
through RealityCapture cutting terrain correction 30%; asset version control cutting engine
mismatch errors 40%.

Reference contact: Heidi, heidi@thinkround.org

## Program Analyst - Cognizant Technology Solutions

**India | Feb 2022 - Aug 2023**

- Built automated data ingestion pipelines in Python and Apache Spark processing 50M+ rows
  daily
- Cut data-to-KPI latency from 48 hours to 2 hours
- Optimised ETL workflows on AWS (S3, Lambda, Glue), measurably reducing infrastructure cost

Reframes, settled, do not re-litigate: QA roles become data validation and pipeline testing.
Databricks roles use "Apache Spark, PySpark (Databricks-compatible)".

## SceneAgent - Project

**Apr 2026 | github.com/lohithburra01/sceneagent**

Built in 48 hours. Input-agnostic 3D scene intelligence pipeline: video, photos, point cloud,
BIM or pre-trained splat in, semantically queryable scene out.

- Gaussian splat to SAM 3 segmentation to backprojection to DBSCAN clustering, 151 objects
  detected in the demo scene
- LangGraph agent with MCP scene tools: move camera, find objects by natural language, measure
  distances, plan guided tours, render views on demand
- Agent does not carry the scene in its context window, it queries the backend via MCP
- FastAPI, Next.js, pgvector, Docker Compose, Kubernetes
- Pluggable LLM through three env vars, any OpenAI-compatible endpoint

Default project for AI, agentic and automation roles.

## Skills

**AI / LLM:** Claude API, Gemini, LangGraph, MCP tools, RAG, pgvector, prompt engineering, LLM
evaluation and benchmarking, agent orchestration

**Automation:** n8n (23+ workflows, 2 production systems), UiPath, REST API integration,
webhooks, GitHub Actions CI/CD

**Engineering:** Python, FastAPI, Docker, Kubernetes, PostgreSQL, TypeScript, WordPress REST
API, Airtable API, Google Drive API

**Data:** Apache Spark, PySpark (Databricks-compatible), ETL pipelines, AWS (S3, Lambda, Glue),
MySQL

**Platform:** Vercel, Next.js, application security review

**3D / real-time (only when the JD asks):** Unity, Blender and bpy addon development, HLSL,
GLSL, ComfyUI, After Effects scripting, Godot 4

---

# PART C - THE 14 CAPABILITIES

Each capability names the general engineering problem, how he solved it, and one concrete
instance with a number as proof. Lead resume bullets from here, then cite the system as the
setting.

## C1. Making nondeterministic model output safe to ship

**Problem:** a language model produces plausible output that is wrong in ways a human reviewer
will not reliably catch at volume, and the cost of one bad item reaching a customer is high.
Prompt-tuning does not solve it, because a prompt is a request.

**How he solved it, at two ends of the same call.** Before the call, the space of expressible
wrong answers is narrowed structurally rather than instructed away in prose: allowed identifiers
are rewritten into per-call enums containing only what was actually delivered to that call; when
a retrieval budget is exhausted the retrieval branch is deleted from the response schema
outright, so the model physically cannot ask for more; and the permitted operation itself is
restricted, so a proposal may only wrap text that already exists verbatim, or lightly rewrite
exactly one existing sentence while recording the original in a field that makes the claim
mechanically checkable. After the call, output passes a deterministic checker written against
the artefact rather than against the generator, so swapping the model does not invalidate the
gate. Findings are classified ERROR or WARN, any ERROR halts the item, and the checker's exit
code gates the surrounding workflow branch directly. The principle underneath both ends is that
schema validity is necessary but not sufficient, and the captures prove it: one response of
entirely empty arrays passed the provider schema cleanly, and another carried serialized JSON
inside a field typed as an untyped string. Malformed output is captured immutably and terminally
rejected rather than silently retried, and re-execution requires a separate authorized step that
must first prove from the capture which technical failure occurred.

**Proof:** the label-honesty check exposed 77 percent of one proposal class (48 of 62) as
fabricated sentences mislabelled as verbatim wraps, a defect rate nobody had a number for before
the check existed. A frozen regression case records a model returning 7 decisions with 7
evidence-accounting rows while zero evidence shards had been delivered.

## C2. Deciding what a model decides and what code decides, and enforcing the split

**Problem:** work gets routed to a model because that is the fast way to make it work at all,
and the resulting system cannot be explained, reproduced, costed or tested.

**How he solved it.** The model/code boundary is an architectural decision that is written down,
enumerated per stage, and enforced. In one eleven-stage pipeline exactly three stages call a
provider; classification, candidate generation, aggregation, gating and packaging are all code,
and every reference-citation link is extracted by regex and mapped through a fixed lookup table,
never generated. In the publishing engine one stage of eight is model-driven; sectioning,
validation, assembly, asset matching, publishing, state and routing are deterministic Python. In
the strategy pipeline the split is written as a rule of authority: code may partition, bind,
hash, count, validate, persist, resume and render, but may not invent subjects, evidence
relevance, membership, ownership, conflicts, decisions or closure, and the final five stages
call no provider at all.

**Proof:** 3 model-touching stages out of 11; a deterministic transformation preferred over a
second model call, with a losslessness assertion that reconstructs the original input from the
transformed output.

## C3. Human-in-the-loop approval as an architectural component

**Problem:** approval bolted on as an email produces duplicate sends, lost decisions,
double-submits, and pipelines that stall because one item is waiting on a person.

**How he solved it.** Approval is modelled as first-class state. Three state machines are kept
deliberately separate: the customer-facing record status, the internal pipeline status, and the
approval-gate state. Exactly-once notification is a per-item notification timestamp, with the
summary endpoint counting only unstamped items, stamping opt-in per call so the endpoint stays a
pure read when opened by hand, and a matching unmark for the case where the mail step fails
after stamping. The double-decision race is handled by a compare-and-set that moves the gate
from pending to deciding under a lock and returns true only for the winner. The blocking wait
was removed from inside the batch loop, because parking an execution per item meant a customer
with four pending items got one email and items two to four were never built; the fix replaced a
per-execution resume URL with a stored static callback URL, kept backward compatible so rollback
is a toggle rather than a redeploy. Reviewer decisions are not discarded after use: they are
converted into a per-tenant decision-memory file that the gate enforces on the next run, so
review effort compounds.

**Proof:** decision memory holding 218 rejected and 311 accepted decisions as an accumulating
per-tenant asset; a version-4 measurement showing 0 of 129 previously rejected combinations
re-proposed and 119 of 122 accepted items preserved.

## C4. Multi-tenant systems where behaviour is configuration, not code

**Problem:** a system built and proven on one tenant silently promotes that tenant's every value
to a universal default, and the failures are invisible rather than loud.

**How he solved it.** The recorded consequence on the first build was exactly that: wrong
template taxonomy, wrong category, wrong asset tagging, wrong slot count, and five code routes
that fell back to the first tenant whenever none was named. The replacement rule, stated
repeatedly in the source, is that a value we do not have is a STOP, not a default, implemented
as a readiness gate that names each missing item per tenant and is enforced at both the trigger
and the write, rather than as a defaults table. One config file holds every per-tenant setting
and stores only environment variable NAMES, never values, resolved against the process
environment first and a dotenv file second, raising at load time when a secret that tenant's
chosen path requires is absent. In the linking pipeline the split is explicit: everything above
the tenant config is fixed (stage sequence and file contracts, rule text, vocabulary, gate
checks, reference mechanism, renderer, call layer with its cost accounting) and the tenant
config is the steering wheel (caps, thresholds, category regexes, exclusion sets, routing
tables, no-write zones, and the selector dictionary telling the fetch stage which page
components to strip).

**Proof:** 10 tenant entries with 7 active, per-tenant behaviour as config rather than code
branches; a 49-row configuration matrix in which every setting is classified as
dies-with-the-content-plan, constant-for-everyone, discoverable-in-code, or genuinely
per-tenant, with a stated target of reducing 14 human-answered questions per tenant to 5.

## C5. Reliability engineering for unattended pipelines

**Problem:** an automation that runs while nobody is watching fails in ways that look like
success, and a naive retry turns a transient error into a duplicate side effect.

**How he solved it.** His ordering is idempotency first, retries second, and the claim is
written down rather than assumed: generate overwrites, publish updates a tracked object id
rather than creating a new one, init returns the existing record. Only then is a retry policy
applied to every service-facing HTTP node, and deliberately withheld from mail nodes, because
re-sending a message that already went out is worse than surfacing the error. Batch nodes carry
continue-on-error selectively rather than globally, so one bad item does not abandon the batch.
Cross-execution idempotency is keyed by period in orchestrator static data, with the operational
consequence (re-importing the workflow wipes it) recorded next to the code. Every trigger has a
twin: a schedule trigger and a manual trigger wired into the same first node, the manual path
passing through a parameter node so a full run can be exercised against real data with side
effects diverted to an internal address and the real recipient printed in the body, and a test
run explicitly not recorded as having been sent. State is written atomically (temp file, fsync,
rename) under a re-entrant process lock, with the scaling limit written down in two places
rather than discovered later. Degradation is designed rather than accidental: when a model
review pass returns unparseable output for one item, that item falls back to its previously
aggregated set rather than being dropped from the batch. Where a gap remains, it is written down
with its consequence rather than left implicit: one workflow is recorded as having a mail node
with no error handling, alongside the exact failure sequence that would follow. A resolver that
cannot resolve a name emits it to a named not-found list rather than fuzzy-matching.

**Proof:** 3 tries, 5000 ms apart, 300000 ms timeout across 137 service-facing HTTP nodes in 26
workflow definitions; serialising a read-modify-write took a concurrency test from 58 raised
writes to 0.

## C6. Measuring model quality and cost instead of guessing

**Problem:** model choice is usually made on vibes or on the vendor's benchmark, and cost is
estimated rather than measured, so nobody can defend a swap.

**How he solved it.** He built a harness that grades candidate models on the exact tasks the
expensive model was doing, using real project data rather than synthetic prompts: one case
graded against a human reviewer's actual labelled accept/reject decisions, one graded by a
ported copy of the production deterministic gate, and two graded by a reference model acting as
judge. All candidates route through one aggregator so a single key runs the comparison. Cost is
computed from reported token usage against a per-model price table, not estimated. Dry-run mode
prints the estimate and spends nothing; a real run requires an explicit confirmation flag.
Output is a results JSON plus a generated scorecard over quality versus cost versus latency. The
honesty is built into the artefact: its own README separates the objectively-labelled case from
the judge-scored ones and instructs the reader to treat the latter as directional agreement with
a reference model, not truth, and records that every model ran in plain configuration with no
extended thinking so the comparison is like for like.

**Proof:** 9 models over 40 items; reference model $1.149 at 3.12 s mean latency and 0.525
accuracy against a cheapest contender at $0.0109, 3.77 s and 0.500 accuracy for the identical
run. The result is also the demonstration of judgment: every model landed between 0.375 and
0.525 accuracy with accept recall at or near zero, close to a degenerate always-reject
classifier on a class-imbalanced set, and the recorded conclusion is that the case was badly
posed, not that a model won.

## C7. Bounded context and budget control for LLM systems at scale

**Problem:** an LLM system whose prompt grows with its input works in development and fails at
the provider boundary in production, and the failure arrives as a truncated response rather than
as an error.

**How he solved it.** The bound is a property of the architecture rather than of the input. Work
is partitioned into deterministic units of fixed maximum size, ordered by stable identifier,
each starting from only its own bootstrap context. Artifact shapes carry fixed caps regardless
of scale. Budget is computed before the call, not discovered by it: a preflight measures actual
rendered prompt bytes plus schema bytes, converts to estimated tokens with a deliberately
conservative bytes-per-token ratio, adds an output reserve computed as a base plus a per-item
amount, and raises distinct errors if the reserve exceeds the provider output limit or if input
plus reserve exceeds the context window. Configuration that would raise a ceiling or lower a
reserve is rejected with a dedicated relaxation-forbidden error, so budgets can only ever be
tightened, and the preflight result is hashed into the execution authority so a run cannot
proceed under a budget it did not pass. A semantic reuse layer hashes only meaning-bearing
inputs and contracts per stage, excluding implementation and wiring, so a completed unit is
reused with zero provider calls after a refactor and only genuinely affected units are
re-authorised.

**The part that is unambiguously his own:** he measured that the six rulebooks a multi-stage
workflow needed came to roughly 139,000 tokens, about 70 percent of a single chat window, before
any actual input, and re-architected around the measurement rather than around a guess: three of
the six stages were moved out of chat entirely into isolated sub-runs, each reading its input
from a file and writing its output to a file, so peak context per stage is bounded by that
stage's own needs instead of by the union of all of them.

**Proof:** bounded-tree acceptance passed at 50, 500, 1,000 and 3,718 subjects with zero
provider calls, producing 8, 62, 123 and 454 work units, with artifact bounds fixed at fanout 4,
leaf records 12, catalogue entries 12, conflicts 4, string length 2,048 and semantic payload
18,000 bytes regardless of scale. Per-stage isolation measured at 16K, 31K and 23K peak context
for 56K, 87K and 100K total tokens across three real runs, against the 139K baseline the
unisolated design would have carried. On the cost side: disabling provider reasoning cut
hidden-thinking output tokens by 5x to 10x, and a 6.9 million token fan-out across 359 agents is
the recorded incident that set the budget rule.

## C8. Integrating with an inherited stack rather than requiring a rewrite

**Problem:** the interesting automation almost always has to land on a platform somebody else
chose, that predates the engineer, and that will not be replaced. Insisting on a rewrite is not
an engineering answer.

**How he solved it.** He argued for a modern stack and did not get it, then delivered inside the
constraint at three levels. At the protocol level: two publish paths behind one interface,
standard REST with header auth where the host passes the Authorization header and a custom
bridge carrying the secret in the request body where the host strips it. At the platform level:
a bridge plugin written in the legacy platform's own language, roughly 560 lines at v1.5,
exposing 10 token-authenticated routes (ping, media upload, publish/update, find by identifier,
read back, delete, taxonomy terms, custom-field listing, host limits, signed time-limited
preview link), with the token generated on activation from cryptographically random bytes,
compared in constant time on every route, and rotatable from an admin page. Some of that plugin
exists purely because the platform silently drops unregistered metadata keys over its own REST
API, a failure mode you only find by measuring. At the environment level: rather than
hand-configuring each new tenant, the engine interrogates the tenant's own API for its registered
taxonomies, its template-triggering term and its real category list, with explicit configuration
always winning and discovery reporting "nothing found" rather than guessing; and a pre-publish
prober measures facts only a real write used to reveal, including the maximum upload size the
host actually accepts, by uploading a real file at a target size and deleting it again. A
separate constraint drove the whole architecture: choosing a managed orchestrator as a company
tool removed local-file and command execution, which is precisely why every pipeline stage had
to be exposed as an HTTP endpoint.

**Proof:** three different names observed for the same template-triggering taxonomy across
tenant sites plus one site with none; two hosts measured returning HTTP 413 above roughly 1 MB
while a third accepted a 1.2 MB file; three distinct content storage shapes discovered across
installs of the same platform, with writers implemented for two.

## C9. Write perimeters around shared live systems of record

**Problem:** an automation that writes into a database humans edit by hand all day can destroy
work silently, and "we were careful" is not a control.

**How he solved it.** He designs the write surface as a perimeter and documents it as one, in
plain English, for the non-technical owner of the data. Six guards stand in front of a single
write function, in order: a kill-switch environment variable leaving the system read-only by
default; a per-tenant field allow-list; a per-field value allow-list; a provenance check
requiring the record id to have been read by this run's own query or to be recorded on one of
this tenant's own status records; a per-run write cap; and an audit entry recording old value to
new value, verified writable BEFORE the change is made, on the reasoning that a write that
cannot be recorded must not happen. There is deliberately no code path that can create a record,
delete a record or touch schema, and the recommended token scope carries no schema permission,
so structural damage is impossible at the API level rather than merely unlikely. The read side
is a perimeter too: the customer-facing dashboard projects an explicit field whitelist and asks
the API for only those fields, so internal staff names, deadlines and internal links never
travel over the wire. The failure policy is asymmetric and reasoned: fail closed on customer
data, fail open on the checker, because an unanswered question about a tenant is a stop but a
broken question-asker is an alarm, and refusing every tenant on an import error turns a small
deployment fault into a full outage.

**Proof:** 6 ordered guards, a write cap of 25 records per run, and two append-only logs with
deliberately opposite policies (the write audit refuses the write when it cannot log; the event
ledger swallows every error and never blocks).

## C10. Infrastructure as generated artefacts rather than hand-built console state

**Problem:** low-code and console-configured infrastructure drifts across tenants, cannot be
reviewed as a diff, and duplicates logic that already exists in a tested package.

**How he solved it.** Four generators plus one post-processor emit or rewrite workflow JSON. Two
strategies are used. One emits a workflow from a tested Python package, reading templates and
computed logic out of the real source files at build time and inlining them into the workflow's
code nodes, so the orchestrator and the package cannot say different things. The other
transforms a proven workflow: one generator rewrites every service call for a different tenant
and inserts the approval-arming node at the one position where the callback exists, a second
performs a structural split, a third builds a third route by copying service-facing nodes
verbatim out of two live workflows so the host, the auth header name and the message template
cannot drift. The generators carry guards of their own: a build is refused if the resulting
workflow references more than one service host, on the recorded reasoning that a workflow
talking to two hosts is worse than one talking to the wrong host because half the run writes
state the other half cannot read; a default base URL was removed after it silently pointed
generated workflows at a decommissioned host, and non-HTTPS values are now rejected; and after
each build the generator prints the node count, whether the blocking node is absent as intended,
and the exact list of nodes still needing a credential attached by hand. Generated artefacts are
validated before import by a Node script (connections point at nodes that exist, no orphans,
unique names and ids, every embedded script parses, no banned node type), and a second harness
extracts the embedded JavaScript, runs it against a fake context, and compares its month-by-month
answers against the Python implementation of the same rules.

**Proof:** 26 workflow definitions, 490 nodes, roughly 12 distinct shapes, 7 generated
per-tenant instances; onboarding a tenant is one command instead of a manual clone-and-edit of
an eighteen-node canvas, and a policy change becomes a reviewable diff of a generator rather
than of a 48 KB JSON blob.

## C11. Operator tooling and reversible destructive operations

**Problem:** a pipeline nobody can safely test against real data is a pipeline that only gets
tested in production, by a customer.

**How he solved it.** Every destructive operation he wrote is dry-run by default, requires an
explicit apply flag, and can be undone. A ground-zero reset per item deletes the live artefact
and its attachment, returns the source record to the status it came FROM rather than to a
blanket value, clears the tracked object id, and purges the state record so the trigger stops
treating the item as done, with the ORDER of those steps documented as the safety property, and
any tenant whose system is not responding skipped entirely. Any script that mutates a live
external system snapshots the prior state to a timestamped file first and ships a revert command
that re-uploads the snapshot. A row snapshot and restore tool makes a test run against live
operational data revertible. A ledger reader answers "was this customer ever told about this
item" after a reset has deliberately cleared the field that used to answer it. A self-cleaning
smoke test exercises the real write path against a live external system, verifies the result
including attachment and metadata, then deletes what it created so the system is left exactly as
it was. Alongside these sit onboarding scaffolding, tenant matrix generation, capability probes,
a one-shot run script that prints a section-by-section validation summary with token usage, a
seeding script, and an allow-list editor that only writes config and never sends.

**Proof:** both publish entry points build the payload and write nothing without an explicit
commit flag, with going live requiring a second flag on top; injection scripts are dry-run by
default with snapshot-before-write and a revert command.

## C12. Adversarial self-audit and security review of one's own surface

**Problem:** engineers audit other people's code. The systems that get compromised are usually
the ones whose author never attacked them.

**How he solved it.** He ran a self-initiated adversarial audit of his own service and wrote it
up as an incident record with findings, fixes and live re-probe evidence rather than as a
checklist. The root cause he named is the transferable part: all five findings were safe while
the service ran on loopback behind a temporary tunnel, and deploying to a permanent public URL
changed the threat model while the endpoint design did not change with it. The critical finding
was a chain rather than a single bug: an intentionally unauthenticated edit endpoint, combined
with a write path that inserted HTML verbatim with platform filtering disabled, meant that
guessing an identifier let an attacker rewrite the body of an item awaiting approval so that a
human would approve arbitrary HTML onto a live customer site, and identifiers are not secret
because they are keyword phrases that travel inside preview links in customer inboxes. Fixes
were designed to close classes rather than instances: strict identifier validation enforced at
the HTTP layer AND inside the function that actually writes, so the CLI and any future caller
are covered; HMAC-signed per-item links replacing open-by-identifier access, derived from the
existing API token so there is no new secret to manage and one leaked link never exposes another
item; refusing to start at all when bound to a non-loopback address without a token; a body size
cap and a revision count cap; and a pinned public base URL so a spoofed Host header cannot
redirect a reviewer's emailed link.

**Proof:** 5 findings (1 critical, 1 high, 2 medium, 1 low), all fixed and deployed the same
day, verified by a 22-of-22 local suite in a throwaway data directory including a re-run of the
proven traversal exploit, plus a live re-probe of every original exploit showing
previously-succeeding requests refused while the legitimate reviewer flow still returned 200.

## C13. Incident response, and turning a lived incident into permanent tooling and policy

**Problem:** most teams handle an incident, write a postmortem nobody reads, and keep the same
blind spot.

**How he solved it.** A customer site he was actively building automation against was taken over
by an external attacker mid-engagement. It surfaced as a support question rather than an alert.
His response the same afternoon was to reproduce the outage externally, identify the vector, and
run a six-touchpoint adversarial self-audit of everything he had touched on that system,
covering config, the bridge plugin, the admin account, the hosted service and a secret-leak
hunt, plus a control-case comparison against a sibling tenant where he had done far more work
and which was clean. That is the discipline worth naming: rule your own system in or out with
evidence rather than assertion, quickly, while the incident is still live. He then swept roughly
27 tenant systems for the same exposure, flagged one exploitable system and a spreadsheet
holding plaintext credentials, and drafted the reply and escalation.

Two pieces worth telling on their own. **Ordering of operations under incident conditions:** he
wrote down that a backup restore would likely reinstate the vulnerable core and must be patched
immediately after, that the restore point must predate the rogue account's creation, that
nothing should be published until the system was confirmed clean, and that his own integration
token must be treated as exposed because it lived in a database table the attacker had access
to, so rotation had to happen after the restore and not before. **Operational discipline during
the sweep:** he deliberately did not open the spreadsheet of plaintext credentials he had just
flagged, sourcing his domain list from a tooling export instead.

The permanent-tooling half is the stronger half. The next day he independently re-measured the
affected system to verify someone else's patch rather than taking it on trust, confirming by
measurement that a REST route now 404ed and the namespace was gone, converted the ad-hoc sweep
into a passive credential-free scanner so the method was reproducible and not just its results,
ran it across the portfolio, and audited his own API. The scanner reads the version a platform
publishes about itself from public surfaces and scores it against a known exploit chain into
exploitable, partially affected, old-but-unaffected and patched, and the write-up states plainly
that hidden is not patched and that coverage, not detection, is the limiting factor. The policy
half is twelve numbered security principles plus an append-only incident log, made mandatory
reading before any live-system or credential work, four of the principles written straight out
of that week: re-audit whenever exposure changes; every write endpoint needs an authenticator
even where it must be token-free for its users; authentication fails closed; never treat your
own content as pre-sanitised.

**Proof:** 44 domains scanned out of an estimated 85 managed systems, returning 2 exploitable
(one never previously flagged), 3 very old but unaffected, 17 confirmed patched and 22 with the
version hidden and unverifiable from outside. **Ordering matters and must be stated honestly:
the audit work followed the incident and is response and hardening, never prevention.**

## C14. Root-cause diagnosis of silent failures in automated systems

**Problem:** the dangerous defects in an unattended system are the ones that look identical to
success. Nothing errors, a log line reads zero, and the pipeline reports green.

**How he solved it.** He is unusually good at the class of bug where the evidence is an absence.
A per-tenant run cap applied to candidates instead of to work: a tenant with 126 rows at trigger
status and a cap of 5 handed over the first five rows, the caller recognised all five as already
built, and the run produced nothing, not once but forever, because the same five come back first
every run and the log reads "0 items", indistinguishable from a tenant with nothing waiting. A
shared namespace mistaken for a shared matcher: item ids were slugified titles and therefore not
unique across tenants, so two tenants with an item on the same topic wrote to the same output and
preview file, and one tenant opened a link in their own inbox and read another tenant's content
inside their own branding, while status records stayed separate so nothing looked wrong. A guard
that could not run: a preflight checker imported inside a stdout redirect raised at import time,
and because the readiness gate treats an import failure as "the checker is broken, allow and
shout", the publish-time gate had been silently inert on every API call since it was built. A
guard that could not see: a rename check compared a requested identifier against a response
field that does not exist, compared None, concluded nothing was wrong, and let two tenants
publish at the wrong address one deploy after the guard was written. And a proof of provenance:
an intermittent JSON parse failure was proven to be the model rather than the input because the
same input failed at a different character offset on two runs minutes apart, and deterministic
code cannot do that.

**Proof:** 126 rows against a cap of 5 producing 0 items forever, found during a rehearsal at
cap 1 where it silently zeroed four tenants; the resulting rule, recorded in source, that the cap
always meant "do not build more than N in one run" and never "do not look further down the
list".

---

# PART D - JD MATCHING INDEX

Rows are capability signals, not domains. Find the JD's language on the left, lead with the
capability, cite the system as the setting.

| JD signal | Capability to lead with | System that proves it | Strongest number |
|---|---|---|---|
| Workflow automation / process automation | Turning a manual judgment-heavy process into an unattended pipeline with a human gate | Multi-tenant processing engine plus three-workflow approval choreography | 8 pipeline stages exposed as both CLI and HTTP; 3 orchestrated routes at 18, 16 and 20 nodes |
| Internal tooling | Operator tooling and reversible destructive operations | Ground-zero reset, snapshot/restore, self-cleaning live smoke test | Every destructive path dry-run by default; going live needs a second explicit flag |
| Agentic systems / agent infrastructure | Bounded, runner-controlled retrieval where the model chooses context from an enumerated set | Retrieval-driven Pass 1 | Max 2 retrieval rounds, 3 provider calls and 3 subjects per unit, 12 requested shards per round |
| LLM evaluation / model benchmarking | Measuring model quality and cost instead of guessing | Model benchmark harness | 9 models over 40 human-labelled items; $1.149 reference vs $0.0109 cheapest for the same run |
| AI reliability / LLM guardrails | Making nondeterministic model output safe to ship | Deterministic quality gate plus deterministic link gate | 715 assertion calls across 33 test scripts; gate green at 0 error pages with 106 warnings over 88 items |
| Human in the loop / review workflows | Approval as a first-class state machine with exactly-once notification | Reviewer preview, edit and approval surface; decision memory | 3 independent state machines; decision memory at 218 rejected and 311 accepted |
| Multi-tenant / platform config | Behaviour as configuration, not code branches | Multi-tenant processing engine | 10 tenant entries, 7 active; 49-row configuration matrix classifying every setting |
| API integration | Integrating heterogeneous external APIs with no HTTP framework dependency | Engine external surface | 5 external API families plus a custom namespace, all over `urllib` with zero HTTP dependencies |
| Legacy system integration / migration-averse stacks | Delivering inside an inherited platform rather than demanding a rewrite | Bridge plugin plus dual publish paths plus environment discovery | Roughly 560-line plugin at v1.5 with 10 token-authenticated routes; 3 storage shapes discovered, writers for 2 |
| Orchestration / low-code / n8n / Airflow-adjacent | Infrastructure as generated artefacts, validated before import | Workflow generators and pre-import validator | 26 definitions, 490 nodes, roughly 12 shapes, 7 generated per-tenant instances |
| Cost optimisation / FinOps for AI | Budget preflight and measured model swap | Benchmark harness plus reasoning-off guard plus budget preflight | Reasoning-off cut hidden output tokens 5x to 10x; budgets can only be tightened, never relaxed |
| Prompt engineering / structured output | Constraining the schema instead of instructing in prose | LLM transport, schema projection and three-layer enforcement | Per-call enum narrowing; retrieval branch deleted from the `oneOf` when rounds are exhausted |
| Data pipelines / ETL | Multi-stage deterministic pipeline with explicit file contracts between stages | Eleven-stage proposal pipeline | 88 sources: 332 drafted, 502 after aggregation, 347 final |
| Reliability / retries / idempotency / concurrency | Idempotency established before retries are enabled; races closed under a threading server | Retry policy across service-facing nodes; lost-update and double-click fixes | 3 tries, 5000 ms apart, 300000 ms timeout on 137 HTTP nodes with mail excluded; 58 raised writes to 0 |
| Forward deployed engineer | Working inside a customer's existing stack, with the operators, shipping to their constraint | Bridge plugin, environment discovery, plain-English perimeter memo for a non-technical owner | 16 items published live across 5 tenants on tenant-owned systems |
| Solutions engineering / technical pre-sales | Building a working end-to-end demo of a manual process, from intake form to reviewable artefact | Questionnaire-to-page onboarding pipeline | 124 flat fields the manual process used to hand-assemble, replaced by one generated object of 11 keys |
| Customer onboarding automation | Intake normalisation across heterogeneous payload shapes plus generated artefact plus review gate | Questionnaire-to-page pipeline; tenant onboarding scaffolding | 3 input payload shapes normalised in one branch; 18 intake fields to a rendered 14-section page |
| Document processing | Structured extraction from unstructured documents with a deterministic validator behind it | Document-to-structured-object generation plus quality gate | Up to 15 question/answer pairs and 10 to 20 body slots per item, validated by 10 check families |
| Content operations / editorial tooling | Multi-tenant production pipeline with a customer approval loop | Publishing engine plus approval choreography | 16 items live across 5 tenants; 4 items per tenant per month on a weekly cadence |
| Platform engineering | Config-driven multi-tenant service with atomic state, health checks and a pinned public surface | Engine deployment and state layer | Persistent mounted volume, auto-stop disabled, health check every 30 s with 5 s timeout |
| Security review / application security | Adversarial self-audit of one's own surface, plus credential-free fleet scanning | Engine self-audit and portfolio scanner | 5 findings (1 critical, 1 high, 2 medium, 1 low) fixed and re-probed live in one day; 44 domains scanned |
| Incident response | Ruling your own system in or out with evidence, then converting the sweep into permanent tooling | Live compromise response and scanner | 6 touchpoints self-audited same day; roughly 27 systems swept; 44 later scanned, 2 exploitable |
| Python backend | Standard-library HTTP service with atomic file state and no framework | Engine HTTP surface | `http.server` with `ThreadingHTTPServer`, every outbound call over `urllib`, 512 KB body cap |
| Next.js / React / TypeScript | Server-component rendering over a record store with a status-gated public route | Intake-to-page rendering app | 14 section components, roughly 1,066 lines of TSX across 15 files, 11 generated content keys |
| RAG / retrieval / context engineering | Bounded evidence shards with runner-controlled delivery and local embeddings for candidates | Retrieval Pass 1 and the embedding candidate stage | Local multilingual embedding model, 380-word chunks, top 8 neighbours per source, zero API cost |
| NLP / localisation / non-English content | Detecting model output drift at two independent layers | Language drift detector | Roughly 1 item in 20 drifted mid-output; detector added in the generator and again in the gate as ERROR |
| Technical writing / handover / process | Resume-state documents, protocol files and contract tests that fail when a rule is traded away | Resume-state and protocol documents | Root resume-state document at 308 KB with 145 second-level headings, newest-first |

---

# PART E - SYSTEMS IN DETAIL

Grouped by the capability they best demonstrate. All architecture detail and all numbers are
retained. Use these when a bullet needs architecture detail or a number the capability section
does not carry.

## E1. Multi-tenant processing engine, config-driven and HTTP-exposed

*(instance: documents to published pages across a client portfolio on a legacy CMS)*

Pattern: a manual per-tenant conversion process, judgment-heavy and repetitive, turned into an
unattended pipeline with a customer approval gate. The manual version meant, per item, a hand
import, eyeballed metadata fields, an attachment upload, a keyword choice, a category choice and
an approval email, with defects (metadata not applied, missing attachment, wrong template) caught
by a human looking at an already-live page.

Architecture: one config file holds every per-tenant setting and stores only environment variable
NAMES, never values; a loader resolves each name against the process environment first and a
dotenv file second, and raises at load time when a secret required by that tenant's chosen write
method is absent. A source layer lists trigger rows filtered by tenant, level, row type and status
with cursor pagination, mapping each into a uniform item dict. Generation converts approved
document text into a flat field object (metadata fields, heading, overview bullets, body, up to 15
question/answer pairs) after cutting the document into sections so only the relevant section
reaches the model. A deterministic validator gates the item. Assembly renders a preview by cloning
a saved shell of one of that tenant's own live pages: their head, CSS, header, nav and footer
kept, all scripts stripped so tracking never fires on a review page, a base href injected so
assets resolve, lazy images de-lazified, and the content region replaced. Publishing routes behind
one interface to either standard REST with application-password auth or a custom plugin bridge
carrying the secret in the request body, needed because some hosts strip the Authorization header.
State is one JSON record per (tenant, item) written atomically (temp file, fsync, rename) under a
re-entrant process lock on a mounted volume. Every stage is exposed both as a CLI subcommand and
as an HTTP endpoint, token-authenticated for internal routes and HMAC-signed per item for
customer-facing ones.

Model/code split: only the document-to-JSON generation call is model-driven. Sectioning,
validation, assembly, asset matching, publishing, state and routing are all deterministic Python.

Numbers: 10 tenant entries, 7 active. Defaults of 4 items per tenant per month on a weekly
cadence. 16 items published across 5 tenants as of one dated status file, 3 more held by
identifier collisions. Max items per tenant per run: 10 default, 5 in production. HTTP body cap
512 KB. Item id validation lowercase alphanumeric plus hyphen and underscore, max 120 characters.
Link signature is HMAC-SHA256 over `tenant:item` keyed by the API token, truncated to 20 hex
characters. Renderer version counter at 6 so stale cached previews re-render.

## E2. Deterministic gate for model output

*(instance: ten check families over a generated content object)*

Pattern: the machine gate that stands between a model proposal and anything a customer sees. Ten
check families run with no model involved: required fields present; length rules; keyword actually
reflected in the heading and title; leftover unconverted markdown; whitespace junk; question/answer
pairing; body variant A/B consistency; soft-hyphen misuse; encoding artifacts from document export;
and an output-language check. Findings are classified ERROR or WARN, any ERROR halts the item, and
the process exits 0 or 1 so it gates a workflow branch directly. It validates the artefact, not how
the artefact was produced, so swapping the generation model does not invalidate the gate.

Numbers: length targets enforced as warnings - title 45 to 62 characters (target 50 to 60),
description 95 to 130 (target 100 to 125), keyword 1 to 4 words, excerpt 30 to 75 words. Body slots
10 by default and 20 for one tenant; up to 15 question/answer pairs; up to 5 overview bullets.

## E3. Write perimeter around a shared live system of record

*(instance: an operational database hand-edited daily by several people)*

Six guards stand in front of a single write function, in order: a kill-switch environment variable
(read-only by default); a per-tenant field allow-list; a per-field value allow-list; a provenance
check requiring the record id to have been read by this run's own trigger query or to be stored on
one of this tenant's status records; a per-run write cap; and an audit entry recording old value to
new value. The audit is verified writable BEFORE the change is made. There is deliberately no code
path that can create a record, delete a record, or touch schema, and the recommended token scope
carries no schema permission. Three content-level guards sit on the same chokepoint: one row type
is refused at every entry point including the write call; an unrecognised or blank row type is a
stop rather than a default; and an item with no resolvable category is refused rather than allowed
to land in a default bucket the listing does not read from. The customer-facing dashboard reads
through an explicit field whitelist and asks the API for only those fields, so internal staff names,
deadlines, document links and project links never travel over the wire.

Numbers: write cap 25 records per run, environment-overridable. Provider rate limit noted as 5
requests per second per base. Dashboard listing cached per tenant for 300 seconds. 25 lines in the
write audit log as counted on disk.

## E4. Reviewer approval surface with exactly-once notification

*(instance: customer sign-off before anything goes live)*

Server-rendered with no client-side scripting required, because the page is opened from an email
and screenshotted. It lists the tenant's pending items rather than dropping them into a preview;
approved items move to a completed section linking to the live artefact. The preview carries an
action bar (approve, edit in page, save); save posts back to the engine, which versions the
pre-edit state, applies only fields already present in the JSON so a reviewer can change content
but not inject keys, and re-renders immediately.

Exactly-once notification: the prepare workflow runs hourly and the record status does not move
while a customer is deciding, so without memory every run would re-notify every tenant. The memory
is a per-item notification timestamp, and the summary endpoint counts only items lacking it. A
tenant whose items have all been announced drops out of the result entirely. An item already live
is additionally excluded, on the rule that the artefact's own status is the authority on whether
anything is open. Stamping is opt-in per call so the endpoint stays a pure read when opened by
hand, with a matching unmark for the case where the mail node fails after stamping.

Numbers: edit revision retention 200 per item as a disk-exhaustion guard.

## E5. Environment self-discovery, capability probing and readiness gating

*(instance: onboarding a new tenant site)*

The engine asks the tenant's own public REST API what it has: registered taxonomies, the term that
triggers the styled template, and the real category list. Explicit configuration always wins;
discovery only fills gaps and reports "nothing found" rather than guessing. A separate pre-publish
prober measures facts only a real write used to reveal: the maximum upload size the host actually
accepts, by uploading a real JPEG at a target size and deleting it again, and whether the intended
identifier is taken. A readiness gate then refuses any tenant whose setup is incomplete, naming
each blocker, enforced at both the trigger and the write call, and reusing the existing preflight
checker rather than defining a second list of checks, on the reasoning that two lists drift and the
pipeline ends up enforcing the one nobody maintains.

Deterministic throughout, no model involved. Numbers: profile cache TTL 24 hours; discovery never
on the critical path and a failed probe never blocks a write. Attachment upload target 900,000
bytes, probe size 850,000 bytes, downscale ladder of widths 1600/1400/1200/1000/800 at JPEG
qualities 82/74/66/58. Two hosts measured returning HTTP 413 above roughly 1 MB while a third
accepted a 1.2 MB file. Three different names observed for the template-triggering taxonomy across
tenant sites, plus one site with none.

## E6. Asset selection: one-time vision pass plus deterministic matching

*(instance: a shared licensed image library)*

Use the expensive model once to build an index, then make every runtime decision with cheap
deterministic code over that index. A shared library is vision-tagged once into a controlled topic
vocabulary and cached by file id. Matching a new item is then pure text work over cached captions,
so there is no vision call per item and only the chosen file is downloaded. A relevance floor
rejects weak matches outright rather than attaching a wrong asset. An append-only ledger records
which asset went to which tenant, enforcing that an asset may appear for two different tenants but
never twice for the same one. Per-tenant treatment and per-tenant upload limits are applied in one
shared function used by both the preview and the upload, so the two cannot drift.

Model-driven: the one-time tagging pass. Deterministic: matching, floor, ledger, treatment,
downscaling. Numbers: 213 assets tagged, 0 failures, approximately $0.20 total. Relevance floor
1.5, chosen from an observed spread where accepted items scored 1.5 and 6.5 and rejected ones 0.5
to 1.5, with a code comment stating openly there is no clean separation at that sample size. 2,919
ledger event lines on the local volume copy, the large majority from one tenant's repeated test
runs.

## E7. Hostile-input ingestion from human-maintained spreadsheets

*(instance: per-tenant plan workbooks)*

Parsing files that humans maintain, where every tenant's file is shaped differently and no
assumption survives. It handles four real-world messes: the document address exists only as the
cell's hyperlink, so the workbook is opened with hyperlinks available rather than parsed as CSV,
which drops them; the header row sits at row 2, 3 or 4 under a merged title and an instruction blob
that itself contains the header word, so headers are matched on whole normalised cells against a
known-name list rather than by substring; no two tenants name columns or tabs the same; and the
join key is an unheaded column at a different index per tenant, found by cell shape then confirmed
against record ids actually read from the record system. Enrichment runs before the has-a-document
filter, never guesses a missing column, and swallows its own errors so a plan problem cannot stop a
run. Fully deterministic.

## E8. Bridge plugin inside an inherited platform

*(instance: a custom REST namespace in PHP)*

Extending someone else's platform in its own language because the platform's stock interface
silently loses data. Roughly 560 lines at v1.5, exposing token-authenticated REST routes for ping,
media upload, publish/update, find by identifier, read back, delete, taxonomy terms, custom-field
listing, host limits, and a signed time-limited preview link. The token is generated on activation
from cryptographically random bytes, compared in constant time on every route, and rotatable from
an admin settings page. Version history in the plugin header records scheduling, then custom-field
writing plus template taxonomy plus author assignment, then a read-only verification endpoint, then
category attachment plus the signed preview link. The signed link is what lets a reviewer approve
the real artefact rendered by their own theme rather than an imitation of it. The bridge also sets
metadata server-side, so bridge tenants need no extra plugin, whereas the REST path requires a
must-use plugin to register the metadata keys because unregistered keys are silently dropped.

## E9. Eleven-stage proposal pipeline with a hard human gate

*(instance: internal link proposals across a professional-services site)*

A high-precision proposal system for a domain where a wrong output is worse than a missing one,
built so a human only approves or rejects and never rewrites. The stated constraint was precision
over coverage.

The spec rejects the framing it inherited (that the problem is context-window size) and reframes
it: similarity is not relevance, exact-match terms must match precisely, hallucination is
unacceptable so the system must be able to say "no good target exists", and quality must be
verifiable rather than merely generated. The sequencing rule is inviolable: understand first, map
second, act third.

Architecture: eleven numbered stage scripts plus a config module and an LLM call layer, run in
order from one folder. Stage 1 fetches all published pages from the source API, writes clean text
per page, and separately captures every existing anchor into a file mapping source to target, so
the engine cannot re-propose something that already exists; it strips conversion components, nav,
bylines, tables of contents, social bars, forms and promo widgets from the DOM before text
extraction, so a proposal can never land inside a conversion component, and falls back to rendered
HTML when the API returns empty content. Stage 2 classifies every page by category and role and
emits an inventory, a one-target-per-source assignment, and a directory listing the only
identifiers the model may reference. A persistent-understanding layer sits under this: each page is
read once and reduced to a compact structured profile written to disk, and no later stage ever
re-reads the full text, which is context compression precomputed as a deterministic artefact rather
than paid for on every call. Stage 3 embeds in-scope pages locally and produces top-8 nearest
neighbours as candidates. Stage 4 drafts proposals with one model call per source. Stage 5
aggregates deterministically. Stage 6 runs a model review pass, 6b repairs mechanical defects, 6c
places the optional priority proposal. Stage 7 is the gate. Stages 8 and 9 build the review package
and console.

Model/code split: only stages 4, 6 and a narrowly scoped call in 6c touch a model. Everything else,
including all reference-citation linking, is code: citations are extracted by regex and mapped to
deep links through a fixed abbreviation table, never generated.

Numbers (second tenant instance, Phase 1): 211 pages fetched, 119 in scope, 85 out of scope, 6
excluded, 1 other. In-scope roles: 88 source, 26 priority, 4 regional, 1 tool. 566 existing links
captured. 20 pages required the rendered-HTML fallback. Draft stage 88 pages and 332 proposals, 502
after aggregation and citation linking, 347 final. Final mix 193 citation, 130 informational, 24
priority. Priority coverage 66 pages, 24 newly linked and 42 already live, 22 deliberately left
without. Page text budget to the drafting model 13,000 characters split 60 percent head and 40
percent tail; the review pass sees 5,500 characters. Six concurrent worker threads, four retries
with exponential backoff.

## E10. The deterministic gate as the only path to a human

*(instance: the link gate)*

Nothing reaches a human reviewer unless a machine says it is worth their attention. A single pass
grades each proposal ok, warn or error; any item with an error fails the whole page; the exit code
is the number of failing pages, so zero means green and nothing ships otherwise. Checks include
target integrity, category-wall breach, already-live dedupe misses, wrap-only policy, anchor word
count, anchor verbatim in its passage, label honesty (a declared verbatim wrap must exist verbatim
in the source and a declared rewrite's original text must exist in the source), banned anchors,
weak or dangling or bare-generic anchors, leaked placeholders, doubled auxiliary verbs,
self-referential filler, absolutist phrasing, decision-memory re-proposal of previously rejected
combinations and pairs, heading anchors, byline anchors, conversion-component anchors,
broken-grammar rewrites, a click test comparing anchor content words against target identifier and
title, cross-page anchor reuse as a templating detector, no-write zones, per-sentence crowding,
citation completeness and low coverage. It also emits an orphan report of incoming counts per
priority target.

Fully deterministic. Numbers: max anchor words 5, max proposals per page 6, minimum incoming per
priority target 3, position minimum 0.45, anchor reuse across 3 or more pages raises a templating
warning, a conversion container is treated as a whole promo box only if under 400 characters. Gate
on the final set: 88 pages, 0 error pages, 106 warnings. Orphan report: 10 pages below the
3-incoming minimum, highest incoming count for a single target 27.

## E11. Reviewer console, accumulating decision memory and gated write-back

Making human review effort compound instead of evaporate, and keeping every write to a live
external system reversible. The console is plain HTML and vanilla JS with in-context preview,
accept/reject, a per-item comment box and JSON export, using browser local storage for in-progress
decisions. The second tenant instance rebuilds it by importing the first instance's render modules
and patching only tenant-specific bits, so the reviewer sees a UI they already know. A converter
turns exported decisions into a decision-memory file holding both exact (source, target, anchor)
rejections and (source, target) pair rejections, which the gate and the placer enforce on the next
run. Nothing is written live by the pipeline: it emits a review package only and human approval is
a hard gate in front of any write. Separate injection scripts are the only code that writes to a
live system, dry-run by default, with snapshot-before-write to a timestamped file and a revert
command that re-uploads the snapshot. Three content storage shapes were identified (plain body,
page-builder JSON tree in a hidden meta field, custom fields) and writers implemented for two; the
page-builder writer only modifies text inside text blocks, wraps the first occurrence outside an
existing anchor tag and outside headings, and prefers the block containing the recorded passage.

Two integrity details worth telling. The decision-memory builder originally read one feedback
export rather than merging all of them, which let 8 already-rejected combinations be re-proposed;
the fix merges every export oldest-to-newest with later decisions winning, and the defect is
recorded as a regression not to reintroduce. And one export contained a reject whose written note
plainly approved the item, an obvious mis-click: the literal reject was honoured, the item was
logged to a dropped file, and the discrepancy was escalated to the human, rather than the code
silently deciding it knew better than the recorded decision.

Numbers: decision memory currently on disk holds 218 rejected and 311 accepted; a version-6 handoff
recorded it at 360 decisions (170 accept, 190 reject) at that time. Reviewer export for one Phase 1
batch: 370 decisions, 128 accept, 24 reject, 218 undecided. Pilot instance version history spans v3
(42 pages, 251 proposals) to v9 (38 pages, 146 proposals). Version 4 measured deltas: generic
templated anchors 36 to 0, over-links to a single target 22 to 0, 0 of 129 previously rejected
combinations re-proposed, 119 of 122 accepted items preserved.

## E12. Bounded, sharded, resumable long-horizon pipeline

*(instance: a whole-site strategy document. Authorship is shared and much of this runtime is the
domain lead's. Read FLAGGED before claiming any of it.)*

A long-running LLM workload that does not fit in one context window and must survive being killed
mid-run. The prior approach was conversational in a CLI, so runs died mid-way and lost state.

Architecture: a single entry point exposes fresh, resume, status, execute-pass1 and accept. The
chain is fixed: canonical evidence bundle plus sealed manifest, bounded Pass 1, model-authored
planning, bounded per-domain units, arbitration when conflicts are registered, root closure,
portfolio transaction, then journal, technical reconciliation, finaliser, projection, validator and
renderer. The design rule is a hard split of authority: code may partition, bind, hash, count,
validate, persist, resume and render, but may not invent subjects, evidence relevance, domain
membership, ownership, conflicts, decisions or closure. The last five stages call no provider at
all. Stages hand off through sealed files on disk, never conversation state: every artifact carries
a hash over its own canonical bytes, re-verified on read; run state is append-only or write-once;
transitions are numbered event files; a resume reloads sealed artifacts, re-validates hash bindings
and republishes only genuinely ready units. The canonical bundle is decomposed into immutable
evidence shards (one global, one per subject, one per page, plus segmented full-text shards), each
recording source accounting as JSON pointers back into the bundle with per-value hashes and a
primary flag, with the builder refusing to let two shards claim primary ownership of the same
source path. Every subject, page, evidence row and shard gets an opaque handle derived from a hash
of its identifier plus the bundle hash, so the model only ever sees handles, never real identifiers
or customer URLs.

Retrieval-driven Pass 1: subjects are partitioned into deterministic work units of at most three,
ordered by stable identifier, each starting with only its own bootstrap shards. The model returns
exactly one of two outcomes: a decision covering every subject in the unit exactly once, or a
retrieval request naming additional shard handles and stating why. The runner delivers those shards
byte-for-byte into a fresh context and asks again. On the final call the retrieval branch is
structurally removed from the schema, so the model must decide from what it has or record an
explicit limitation with calibrated confidence. This is agent-style retrieval where the model
chooses its own context, but constrained to an enumerated set the runner controls and where the
runner performs no selection of its own, because relevance is a domain judgement.

A semantic reuse layer hashes only meaning-bearing inputs and contracts per stage, deliberately
excluding implementation and wiring, so a completed unit is reused with zero provider calls after a
code refactor and only genuinely affected units and their real descendants are re-authorised.

Numbers: bounded-tree acceptance passed at 50, 500, 1,000 and 3,718 subjects with zero provider
calls, producing 8, 62, 123 and 454 work units. Fixed artifact bounds regardless of scale: tree
fanout 4, leaf records 12, catalogue entries 12, node conflicts 4, string length 2,048, semantic
payload 18,000 bytes. Pass 1 retrieval: max 2 rounds, 3 provider calls and 3 subjects per unit, 12
requested shards per round, subprocess timeout 1,800 seconds. 44 JSON Schema files in the pipeline
module. Feature branch total 62,427 lines of Python, of which the production pipeline module is
24,452.

## E13. LLM transport, schema projection and budget preflight

Treating the provider call as an engineered boundary with a measured budget, a versioned prompt and
a validated contract, rather than as a string sent hopefully.

Prompt construction is code, not a template string: a dedicated module returns a list of named
sections so each section's byte cost is attributable to a budget line, and assembly is fail-closed,
asserting the bounded view has exactly the expected field set, that bootstrap handles are unique,
that every bootstrap handle appears in delivered evidence, and that the task is prefixed by exactly
one leading reference so normative text is never duplicated. Prompts are versioned by content hash:
every reference file and the task text is loaded from disk and wrapped with an id, a version and a
sha256, and the model attempt record stores those hashes so any output traces to the exact prompt
revision. Structured output is enforced twice: the schema is narrowed per call so only delivered
handles are representable, and after the response a hand-written validator re-checks totality,
handle membership, non-overlap, delivery provenance and forbidden legacy fields, because schema
validity is treated as necessary but not sufficient.

A provider-schema projection layer exists because provider structured output is a strict subset of
JSON Schema: it inlines local references recursively, strips schema and id keywords, detects
reference cycles, and audits the projected schema against the documented provider subset with
allowlists of supported keywords, types and string formats, a requirement that every object sets
`additionalProperties: false`, and caps on optional, union and enum parameters. Keywords the
provider defers rather than enforces are tracked separately so the local validator knows it cannot
rely on them.

Model routing is a sealed capability registry marked not customer-configurable, computing the safe
single-call input ceiling as floor(context window times safety fraction) minus reserved output
minus protocol reserve. A completion-budget preflight measures actual rendered prompt bytes plus
schema bytes, converts to estimated tokens using a conservative bytes-per-token ratio, adds an
output reserve computed as a base plus a per-subject amount, and raises distinct errors if the
reserve exceeds the provider output limit or if input plus reserve exceeds the context window.
Configuration that raises a ceiling or lowers a reserve is rejected with a dedicated
relaxation-forbidden error, so budgets can only be tightened, and the preflight result is hashed
into the execution authority.

Two transports share one boundary. Pass 1 runs through a stripped CLI isolation mode: no tools, no
session persistence, no setting sources, strict MCP config, JSON output, explicit model flag,
projected schema passed as a JSON-schema argument, environment reduced to a six-variable allowlist.
Later stages run through the Messages API directly, declared as a frozen boundary descriptor: one
message, one provider turn, one structured-output attempt, zero re-authoring retries, zero
transport retries, no tools, no system prompt, adaptive thinking, an explicitly required effort
level with provider defaults forbidden. TLS is centralised: one module resolves exactly one
readable CA bundle by environment variable, then certifi, then the OpenSSL default file, refuses to
fall back to an empty store, asserts certificate requirement and hostname checking, hashes the CA
bytes into a readiness record, and offers a handshake-only probe that sends no HTTP request, no
credential and no customer bytes.

Numbers: capability profile 1,000,000 token context window, 64,000 max output, 0.80 safety
fraction, 4,096 tokens reserved for protocol overhead. Per-stage caps 256,000 input tokens, 256,000
prompt bytes, 56,000 provider-schema bytes, 64,000 output tokens; delivered-evidence byte caps
72,000, 96,000 and 120,000 by stage. Output reserve 8,000 base plus 6,000 per subject. Input
estimate constrained to 1.0 to 2.0 bytes per token with a 20 percent context safety margin held for
provider-managed tokens not observable before the request. Provider structured-output limits
encoded from documentation: 16 enum values, 24 optional parameters, 16 union parameters. One sealed
canary call: approximately 52 seconds wall clock, 1 provider call, 0 retries, 11,546-byte raw
response, target-model usage 3 input, 36,405 cache creation, 33,700 cache read and 4,768 output
tokens.

## E14. Structured instruction sets as versioned artefacts

*(instance: a briefing generator and a long-form generation workflow)*

Prompt engineering treated as a maintained artefact with phases, gates and a token-cost control,
not as a text box. A briefing generator turns an approved input master into a structured brief for
exactly one output item with its own outline rules, quality check and review workflow, plus two
helper scripts for inspecting and extracting candidates from input files. A generation skill then
produces the item from that brief as a 17-phase gated workflow across three macro-phases: planning
(evaluate the brief, produce a plan, get approval), writing (section by section with running
quality control), then derivation and closure. It writes the body first and the introduction last,
then automatically derives two secondary assets (one of them capped at 1,500 characters) and pushes
all three through a single combined review loop. After the first full handover it is forbidden from
re-emitting full text and must return search-and-replace pairs only, which is a direct token-cost
control.

These are structured instruction sets with routed reference files, roughly 7,300 lines of Markdown
and Python across the two. They are prompt engineering artifacts, not services, and must not be
described as distributed systems.

## E15. Three-workflow approval choreography

*(instance: prepare, decide, backfill)*

Decomposing an orchestration so that a human decision never blocks unrelated work. The first design
parked a Wait node inside the per-item batch loop, so a tenant with four pending items received one
email and items two to four were never generated until item one was decided. Parked executions also
consume the hosted concurrency allowance.

Workflow A, prepare and ask (hourly schedule): read trigger rows, generate, gate, assemble and arm
an approval gate per item; after the loop, group by tenant and send one summary per tenant linking
to that tenant's dashboard. It never changes the record status, so the row stays waiting until the
customer acts. Workflow B, the customer decided (production webhook): on approve, flip the status,
publish, run post-write housekeeping, send a confirmation, flip the status again; on reject,
internal notification only. Workflow C, already approved (manual): reads rows a human already
marked approved, then generates, gates, assembles, publishes and notifies, with no gate armed
anywhere, and that absence is the deliberate fingerprint proving the two write routes cannot
interfere.

The engine replaced the per-execution resume URL with a stored static webhook URL, because a frozen
execution can only hold one pending approval while the dashboard design needed several open at
once. It was made backward compatible on purpose: a caller still sending a per-execution resume URL
is honoured exactly as before, so rollback is a toggle rather than a redeploy. Three independent
state machines are kept separate on purpose: the customer-facing record status, the internal
pipeline status, and the approval-gate state, with a separate notification timestamp enforcing
exactly-once notification.

Numbers: 18 nodes per tenant for A and 19 for the all-tenants build, 16 for B, 20 for C. The
original monolith they were split out of had 28 nodes; the split generator moved a named list of 13
nodes from prepare into publish.

## E16. Workflow generation from code, with reliability patterns applied at build time

Four Python generators plus one post-processor emit or rewrite workflow JSON. Strategy one emits
the workflow from a tested Python package: templates and signature markup are read out of the real
source files at build time and inlined into the workflow's Code nodes, so the workflow and the
local package cannot say different things; the embedded date logic computes a send day as the 25th
of the previous month advanced past weekends and past regional public holidays including movable
Easter-derived ones, with the Easter computation written out in the emitted JavaScript. Strategy
two transforms a proven workflow: one generator rewrites every service call for a different tenant
and adds the approval-arming node in the one position where the callback exists; a second performs
the structural split; a third builds the third route by copying service-facing nodes verbatim out
of the two live workflows so the host, auth header name and template cannot drift.

Guards inside the generator: it refuses to write a file if the resulting workflow references more
than one service host, on the recorded reasoning that a workflow talking to two hosts is worse than
one talking to the wrong host because half the run writes state the other half cannot read. A
default base URL was removed after it silently pointed generated workflows at a decommissioned
host; the base URL is now required and any non-HTTPS value is rejected. After each build the
generator prints the node count, whether the blocking node is absent as intended, and the exact
list of nodes still needing a credential attached by hand.

Reliability: every service-facing HTTP node carries retry-on-fail with 3 tries, 5000 ms between
tries and a 300000 ms request timeout, applied both at build time and by a standalone patcher with
a check-only mode. Retry is only safe because the stages are idempotent, and this is stated
explicitly: generate overwrites, publish updates the tracked object id rather than creating a new
one, init returns the existing record. Mail nodes are deliberately excluded from retry because
re-sending a message that already went out is worse than surfacing the error. Dual-trigger design
wires a schedule trigger and a manual trigger into the same first node, with the manual path
passing through a Set node holding test parameters so a full run can be exercised against real data
with side effects diverted to one internal address and the real recipient shown in the body, and a
test run explicitly not recorded as sent. Idempotency uses workflow static data keyed by month for
one track, with the operational consequence written down that re-importing the workflow wipes that
data. Selected nodes carry continue-on-error so one failing item does not abandon a batch, applied
selectively rather than globally. Node choices avoid known runtime failures: the IF/Filter/Switch
family is banned from one generated workflow and replaced with two one-line Code nodes because the
IF node type-checks the empty right-hand field of a boolean condition and failed at import twice;
native provider nodes are used because the hosted runtime refuses those credentials inside a
generic HTTP node; a month name comes from a literal array rather than a locale call because locale
data may be absent in the hosted runtime. A Node script validates every generated workflow before
import (connections point at nodes that exist, no orphans, unique names and ids, every Code node's
JavaScript parses, no banned node type), and a second harness extracts the JavaScript out of the
generated workflow and executes it against a fake context, comparing its month-by-month answers
against the Python implementation of the same rules.

Numbers: 26 workflow definition files, 490 nodes total, 137 HTTP request nodes, 40 mail nodes, node
counts from 4 to 28, roughly 12 distinct shapes, 7 generated per-tenant instances of the prepare
workflow plus one consolidated build. Execution frequency hourly for the content prepare workflow
and daily at a fixed hour for the monthly-mail workflow, which then decides for itself whether that
day is the send day. One provider node carries execute-once with the reason recorded, after a
documented rate-limit rejection on a specific date.

## E17. Intake-to-rendered-artefact onboarding pipeline

*(instance: a questionnaire to a live customer page. Several claims about this system are weaker
than they sound. Read FLAGGED before using any of it.)*

Customer onboarding automation end to end: a form submission becomes a normalised record, a
generated content object, a reviewable preview and a status-gated public artefact, with no human
assembly step. The manual version meant standing up a fresh CMS install with a bespoke field import
per customer, hand-assembling a large flat field set.

Architecture: a webhook node receives a questionnaire submission. A normalisation Code node
flattens three input shapes in one branch (an answers array keyed by field ref, a fields array
keyed by label, and plain flat JSON), maps localised labels to schema keys, splits multi-line
fields into arrays, coerces yes/no to booleans, parses an integer for a numeric field, and builds a
URL slug that transliterates locale-specific characters before stripping non-alphanumerics and
truncating to 60 characters. A row is created with status Generating. One HTTP node calls an LLM
with a localised system prompt and the questionnaire JSON, producing the entire page content in a
single call rather than one call per section. A parse node extracts the text, attempts JSON parse,
retries after stripping code fences, then validates against a hard-coded list of eleven required
top-level keys and throws if any is missing, so a malformed generation fails the execution loudly
rather than writing a broken record. The content is stringified back into the row and status flips
to In Review. A notification goes to an internal reviewer with a link to the preview URL.

One design decision carries beyond this project: the review surface is the production renderer with
an action bar overlaid and indexing disabled, not a separate preview format. The previous process
reviewed a document and shipped a page, so reviewers approved something that was not what shipped;
making the reviewed artefact and the shipped artefact literally the same render removes that drift
by construction. The same principle appears in the publishing engine, where preview and published
output are computed by one shared function because every time they were computed separately they
diverged, and a preview that disagrees with the live page is described in the source as the worst
version of the bug, because it is invisible until a customer is already looking at their own site.

Rendering is a single deployed Next.js app with two dynamic routes, public and preview, both async
server components calling a slug lookup that queries the record store with a filter formula capped
at one record, maps into a typed record, and JSON-parses the stored blob inside a try/catch with an
offline sample fallback. The public route gates on status and returns 404 unless Approved or Live,
and implements per-tenant metadata from the model-generated title and description. A single page
container composes fourteen section components in fixed order, two of them conditional so a sparse
record degrades gracefully. The preview route mounts a client-side review bar posting to internal
API route handlers: approve sets status Live and optionally fires a publish webhook;
request-changes requires non-empty feedback, sets status back to Generating and forwards the
feedback. A separate lead-capture flow forwards enquiries into a second table linked to the first
record and notifies the customer.

Structured output is enforced at three layers: prompt level (answer with valid JSON only, full
target schema inlined with per-field type and length annotations, hard cardinality rules and hard
character limits), API level (a JSON response MIME type on one provider path, which is
provider-level enforcement rather than prompt-level pleading), and post-parse level (fence
stripping then required-key validation that throws). The prompt encodes safety rules that matter
for regulated marketing: never invent credentials, awards, outcomes or years of experience; emit a
bracketed placeholder token for missing mandatory data instead of guessing; never use unproven
superlatives; and if no real examples were supplied, generate exactly three illustrative ones each
flagged with a boolean. That boolean is honoured downstream, so the disclosure survives from prompt
to rendered page. A further rule forbids the model emitting any asset path, because asset URLs come
from questionnaire uploads and not from text generation.

Numbers: 4 workflow exports, 7 nodes each in the three generation variants and 4 in the lead
capture. 11 required content keys, 14 rendered section components, roughly 1,066 lines of section
TSX across 15 files. 18 questionnaire fields in the committed test payload. 16 fields on the
primary table and 7 on the secondary. 5 status values. 124 flat field keys in the legacy export
kept as the reference target output, which is the figure showing what the manual process used to
hand-assemble. Prompt hard limits: title 60 characters, description 155, headline 90, exactly 3
trust bullets at 60 characters each, CTA label 50. Cardinality: advantages 4 to 6, detailed
services 5 to 8, process steps exactly 3, local factors 4 to 5, examples exactly 3, question/answer
pairs 8 to 10. Temperature 0.4 on both provider paths, output cap 8000 tokens on one and 16384 on
the other, HTTP timeout 120000 ms. List queries capped at 50 records, slug lookup capped at 1.

## E18. Model benchmark harness

Making a model choice defensible with measured quality and measured cost on the real task, so the
swap survives review. Four cases built from real project data rather than synthetic tests:
accept/reject classification graded against a human reviewer's real labelled decisions; generation
graded by a ported deterministic gate plus a model judge; whole-item review graded by judge against
the reference model; and a selection task. All models route through one aggregator so a single key
runs the comparison. Cost is measured from reported token usage against a per-model price table,
not estimated. Dry-run mode prints the estimate and spends nothing; a real run requires an explicit
confirmation flag. Output is a results JSON plus a generated HTML scorecard of quality versus cost
versus latency. A second harness reproduces the full item-level review task with the real reviewer
guideline as system prompt and the real review package as input, scored with the same recall method
as the production comparison scripts, running calls concurrently through a thread pool. The README
separates the objectively-labelled case from the judge-scored cases and instructs the reader to
treat the latter as directional agreement with the reference model, not truth, and records that all
models run in plain configuration with no extended thinking so the comparison is like for like.

Numbers: registry of 9 models priced from $0.09/$0.10 per million input/output at the cheapest to
$5.00/$25.00 for the reference model. Recorded run over 40 items on the verdict case: reference
model $1.149 at 3.12 s mean latency and 0.525 accuracy; cheapest contender $0.0109 at 3.77 s and
0.500 accuracy; slowest contender 26.62 s mean. Structured-output parse rate 0.70 to 1.00. Accuracy
across all nine models 0.375 to 0.525, reject recall 0.75 to 1.00, accept recall 0.00 to 0.15.
Estimated cost of the full four-case, four-model benchmark approximately $4. Judge overhead on that
run $0.00 over 0 judge calls because only the label-graded case was run.

## E19. Operator tooling

Scripts rather than systems, but the difference between a pipeline that can be tested and one that
cannot. A ground-zero reset that per item permanently deletes the live artefact and its attachment,
puts the record back to the status it came FROM rather than a blanket value, clears the object id,
and purges the state record so the trigger stops treating the item as done, with the order
documented as the safety property, dry-run by default and requiring an apply flag, skipping
entirely any tenant whose system is not responding. A row snapshot and restore tool so a test run
against live content is revertible. A ledger reader answering whether a customer was ever told
about an item after a reset cleared the live field. A per-tenant notification allow-list editor
that only writes config and never sends. A workflow patcher stamping a retry policy onto every
service-facing HTTP node in an already-built workflow file while deliberately skipping mail nodes.
A self-cleaning smoke test exercising the real write path against a live system, verifying the
result including attachment and metadata, then deleting both so the system is left exactly as it
was. Plus onboarding scaffolding, tenant matrix generation, capability probes, a one-shot
generation script that prints a section-by-section validation summary with token usage, a seeding
script, and a script that fires the demo webhook and opens the returned preview URL.

---

# PART F - NUMBERS THAT ARE SAFE TO QUOTE

The third column is the domain-neutral restatement to use in a bullet when the JD is not about
that domain. The fourth column is where the number came from, which is what he says if an
interviewer asks how he knows.

| Number | What it measures | Domain-neutral restatement | Source kind |
|---|---|---|---|
| 10 client entries, 7 active | Tenant configurations in the publishing engine | 10 tenant configurations, 7 active, behaviour driven by config not code | Config file |
| 16 articles across 5 clients, 3 held by slug collisions | Live items published by the engine at one dated point | 16 items published live across 5 tenants, 3 held by identifier collisions | Status text file |
| 4 posts per client per month, weekly cadence | Configured default | 4 items per tenant per month on a weekly cadence | Config file defaults |
| 213 images, 0 failures, approximately $0.20 | One-time vision tagging of a shared library | 213 assets indexed by one vision pass at 0 failures and about $0.20, then matched deterministically forever after | Project state doc, count confirmed against two index files |
| 715 assertion calls across 33 test scripts (plus 1 at parent level) | Gate test suite size | 715 assertions across 33 test scripts covering a deterministic validation layer | Counted in the repository |
| 32 test files, 732 checks, green, at engine version 71 | Same suite, later state, self-reported | Same, quoted from the self-reported state document rather than counted | Resume-state document |
| 22 of 22 local checks passing | Verification suite for the security self-audit fixes | 22 of 22 verification checks including a re-run of the proven exploit | Security write-up |
| 5 findings: 1 critical, 1 high, 2 medium, 1 low | Adversarial self-audit of own service, all fixed same day | 5 findings across 4 severities in a self-initiated audit, all fixed and re-probed the same day | Security doc |
| 44 domains scanned; 2 exploitable, 3 old-unaffected, 17 patched, 22 unverifiable | Credential-free fleet version scan | 44 systems fleet-scanned without credentials, 2 exploitable surfaced | Security doc plus scanner script |
| 26 workflow files, 490 nodes, 137 HTTP nodes, 40 mail nodes | Orchestration inventory | 26 orchestration definitions totalling 490 nodes, 137 of them service calls | Content scan of workflow JSON |
| Roughly 12 distinct shapes; 7 generated per-client instances | Structural grouping of those 26 files | 12 distinct workflow shapes, 7 of them generated per-tenant from code | Structural comparison plus file listing |
| 4 to 28 nodes per workflow | Range across the inventory | Same | Workflow JSON |
| 3 tries, 5000 ms apart, 300000 ms timeout | Retry policy on service-facing nodes | Uniform retry policy applied by a generator across every service call | Workflow JSON and generator source |
| 13 nodes moved from monolith to publish workflow | Scope of the structural split | A 28-node monolith split into three routes by moving a named list of 13 nodes | Named list in generator source |
| 25 records per run write cap; 5 requests/second/base rate limit | Write perimeter limits on a shared system of record | Per-run write cap of 25 records against a shared operational database | Pipeline source |
| 200 edit revisions retained per item; 512 KB HTTP body cap | Disk-exhaustion guards added after the self-audit | Resource caps added as remediation for a disk-exhaustion finding | Pipeline source |
| 900,000 byte upload target, 850,000 byte probe, 1600/1400/1200/1000/800 widths at quality 82/74/66/58 | Downscale ladder | Adaptive payload downscaling against measured per-host limits | Pipeline source |
| HTTP 413 above roughly 1 MB on two hosts, 1.2 MB accepted on a third | Measured host upload limits | Three hosts measured, two rejecting above roughly 1 MB, one accepting 1.2 MB | Code comment |
| Relevance floor 1.5, accepted 1.5 and 6.5, rejected 0.5 to 1.5 | Match threshold and its observed spread | Threshold set from an observed score spread, with the weak separation recorded openly | Code comment |
| 2,919 ledger event lines; 25 write-audit lines | Append-only log volume | Two append-only logs with deliberately opposite failure policies | Counted from files |
| 211 pages fetched, 119 in scope, 566 existing links captured, 20 needing HTML fallback | Crawl and classification stage | 211 source documents fetched and classified, 566 existing relations captured, 20 needing a rendered fallback | Stage output JSON plus stage-1 comment |
| 332 drafted, 502 after aggregation, 347 final; mix 193 statute, 130 blog, 24 money | Proposal funnel | 332 model proposals expanded to 502 by deterministic enrichment and reduced to 347 by gating | Stage output JSON and summary JSON |
| 88 pages, 0 error pages, 106 warnings | Gate result on the final set | A deterministic gate green at 0 blocking errors and 106 warnings over 88 items | Gate report |
| 10 pages below the 3-incoming minimum, highest incoming count 27 | Coverage report | Coverage report naming 10 under-served targets against a minimum of 3 | Gate report |
| 370 decisions: 128 accept, 24 reject, 218 undecided | Reviewer export for an earlier batch | 370 human decisions captured as structured data | Reviewer export JSON |
| 218 rejected and 311 accepted in decision memory | Accumulated per-tenant feedback asset | 529 human decisions persisted as a machine-enforced per-tenant memory | Decision-memory file on disk |
| 36 to 0 generic anchors; 22 to 0 over-links; 0 of 129 rejected combinations re-proposed; 119 of 122 accepted links preserved | Measured version deltas | Measured regression deltas after a rebuild, including 0 of 129 previously rejected outputs re-proposed | Handoff doc |
| 77 percent of money links (48 of 62) fabricated and mislabelled; 48 percent of one link category (119 of 249) absent from source | Defect rates that triggered a rebuild | 77 percent of one output class provably fabricated, found by a machine label-honesty check | Parity spec |
| No-link-zone detector fired on only 59 of 105 pages | Downstream consequence of fabricated passages | Downstream detector coverage collapse caused by upstream fabrication | Parity spec |
| 12 of 32 common-sense (38 percent); 27 of 61 overall (44 percent) | Automated reviewer recall against a human reviewer | An LLM reviewer measured at 38 percent recall against human labels, which is why it was not made a gate | Handoff memo and comparison report |
| 81 of 107 raw agreement (76 percent), reject recall 12 percent, precision 5 percent | Same comparison on an overlap set | Same | Comparison report |
| 9 models, 40 items, accuracy 0.375 to 0.525, accept recall 0.00 to 0.15 | Objectively-labelled benchmark case | 9 models graded on 40 human-labelled items | Results JSON |
| $1.149 reference vs $0.0109 cheapest for the same 40-item run | Measured benchmark cost | Roughly a 100x cost spread measured from token usage for statistically indistinguishable quality | Results JSON |
| A few cents to about $1 per full client linking run | Cost of one full pipeline run | Full pipeline run costed in cents | Pipeline README |
| 105 pages and 449 links at approximately $0.30 total for one instance; 133 links across 34 pages for another | Per-instance run scale and cost | Two full per-tenant runs at 449 and 133 outputs, one of them costed at about $0.30 | Resume-state document |
| Roughly $2 per tenant run on a frontier model, $1.15 mid-tier, $15 to $25 for a roughly 12-tenant portfolio | Portfolio cost planning, an estimate not a bill | Portfolio-level cost model built from measured per-run costs | Planning note, estimate |
| Roughly 139,000 tokens of rulebooks, about 70 percent of one chat window | The measurement that justified moving stages out of chat | Measured that static instructions alone consumed 70 percent of the available context, then re-architected around it | Context accounting, his own measurement |
| Peak context 16K, 31K and 23K; totals 56K, 87K and 100K across three isolated stage runs | Per-stage isolation, measured | Per-stage isolation cut peak context to a fraction of the monolithic design | Run records, his own runs |
| 74 URLs classified in one out-of-chat stage; 39 items self-flagged provisional in another | Output volume of two isolated stage runs | Same | Run records |
| 110 tracked Python files compiled, 24 CLI entry points checked, 0 provider calls and 0 paid-data-source calls | Audit sweep run entirely without spending | A full static audit of a codebase with zero provider and zero paid-data spend | Audit markdown |
| Optional-dependency test skips 10 to 0 between acceptance records | Effect of a runner that treats a skip as a failure | Eliminated silently skipped tests by making a skip a failure | Acceptance records |
| 46 parameters across 37 clients in the setup matrix | Tenant configuration surface, distinct from the 49-row onboarding design matrix | 46 configuration parameters tracked across 37 tenants | Client setup matrix |
| 4 pilot clients and 12 articles in the first live customer-facing run | First live run, distinct from the 16-across-5 status file | 12 items to 4 tenants in the first live customer-facing run | Resume-state document |
| 26 workflow files split 3 social and 23 content | Composition of the orchestration inventory | Same | File listing |
| 17 legitimate priority links suppressed across 44 of 88 pages by one misclassification | Blast radius of a single classifier defect | A single misclassification suppressed 17 valid outputs across half the corpus | Version notes |
| 343 models in the live provider catalogue, 27 free | Catalogue resolution during a tool evaluation | Every requested model name resolved against the live catalogue rather than assumed | Tool evaluation findings |
| 6.9 million tokens across 359 agents | Uncapped fan-out incident that set the budget rule | An uncapped agent fan-out consuming 6.9 million tokens, which is why budget caps exist | Handoff notes |
| Over 200,000 output tokens on one CLI call | Fan-out observation motivating a direct one-request transport | Same | Handoff notes |
| 264 provider-free tests passed, 3 skipped; later 188 run, 0 failures | Sealed acceptance evidence | Provider-free acceptance suite, so the pipeline is testable without spending | Audit markdown and sealed acceptance JSON |
| 106 tests, 105 passing (single failure a line-ending issue) | Suite he personally ran on the older snapshot | Same | His own diagnostic note |
| Acceptance at 50, 500, 1,000 and 3,718 subjects producing 8, 62, 123 and 454 units | Scale closure with zero provider calls | Bounded partitioning proven from 50 to 3,718 inputs with zero provider spend | Sealed scale-acceptance JSON |
| 62,427 lines of Python on the branch, 24,452 in the production module, 44 JSON schemas | Codebase size at one snapshot | Same | Direct line count |
| 1,000,000 context window, 64,000 max output, 0.80 safety fraction, 4,096 protocol reserve | Sealed model capability profile | Budget preflight constants, enforced so budgets can only be tightened | Source constants |
| Approximately 52 seconds, 11,546-byte response, 1 call, 0 retries | One isolated canary provider call | One synthetic canary call, never to be presented as pipeline latency | Sealed canary JSON |
| 58 raised writes to 0 | Effect of serialising concurrent atomic renames | A lost-update race taken from 58 failures to 0 by serialising a read-modify-write | Code comment on the concurrency fix |
| 126 rows at trigger status against a run cap of 5 | The cap-ordering defect | A cap applied to candidates instead of to work, producing a permanent silent zero | Docstring |
| 11 required content keys, 14 section components, roughly 1,066 lines of TSX | Front-end composition | A 14-component rendered page driven by an 11-key generated object | Code node, TypeScript type, component directory count |
| 124 flat field keys in the legacy export | What the manual process used to hand-assemble | 124 fields previously hand-assembled per customer, replaced by one generated object | Sample JSON in repo root |
| 43 clients in the social sheet; 36 in scope for the content pipeline from 197 records (8 onboarded, 28 new) | Agency-side counts, not pipeline throughput | Organisation-side counts only, never pipeline throughput | Client sheet CSV and resume-state document |
| 308 KB, 145 second-level headings | Root resume-state document | A 308 KB structured handover document as the designated first read for any new session | Measured |
| 49 configuration matrix rows; target of 14 questions per client reduced to 5 | Onboarding cost model, a design artefact | A 49-row configuration matrix classifying every setting, targeting a cut from 14 onboarding questions to 5 | Design document |

---

# PART G - ENGINEERING JUDGMENT (the interview stories)

Each is a decision a senior engineer in any domain would recognise.

**Deterministic gates over model judgment, decided by measurement.** After measuring blind model
reviewers at 38 percent recall on the problems that mattered, the recorded conclusion was to fix
problems at generation time and convert every objectively checkable rule into a deterministic gate
check, because those catch 100 percent rather than a third. Raising model-reviewer recall was
ranked third in priority. This is the rare case of an engineer measuring their own LLM feature,
finding it inadequate, and redesigning around determinism rather than prompt-tuning it.

**Restricting the operation is stronger than judging the output.** Rather than judging whether an
invented sentence is good, the system restricts the model to wrapping text that already exists
verbatim, or lightly rewriting exactly one existing sentence with the original recorded in a
checkable field. Anything else is dropped mechanically. The gate then verifies the model's own
declared operation type against the source text, which converted an unquantified quality problem
into a measured one: 77 percent of one output class were fabricated sentences mislabelled as
verbatim wraps, and 48 percent of another class did not exist in the source at all.

**Constrain the schema, do not instruct in prose.** Allowed identifiers are rewritten into per-call
enums containing only what was actually delivered, and when retrieval rounds are exhausted the
retrieval branch is deleted from the schema outright, so the model physically cannot ask for more.
A frozen regression case records the failure this prevents: a real attempt returned 7 decisions
with 7 accounting rows while zero evidence shards had been delivered, meaning the model cited
evidence it had never been shown.

**Extended thinking and structured output share one output budget.** A retry-preparation routine
exists purely to prove this from an immutable capture: it reads the sealed envelope, checks the
stop reason is max tokens, checks output tokens exactly equals the configured max, extracts
thinking tokens from usage details, and computes the remaining output budget. Only when thinking
consumed enough that less than a minimum structured-output reserve remained is the failure
classified as truncation and re-execution authorised. A reserve adequate for the JSON alone was not
adequate overall.

**Schema-encoded totality does not scale.** An earlier closure schema encoded totality directly in
its shape, one required named property per key with additional properties forbidden. For a real
tenant that generated a large object and the provider rejected it at grammar-compilation time,
before any model turn. The fix moved totality out of the schema into post-capture validation
against sealed requirements while keeping it just as strict, with a grammar-light wire contract
carrying only generic arrays.

**Validators that check form rather than answer.** The most consequential finding in that work was
a diagnosis, not a code fix. A run produced a finished deliverable with 65 profiles, every one
marked priority high, every one ranked equally first, 36 assessments recorded as not assessable,
and the document stamped ready with the test suite green. The validators asked whether every field
was populated, never whether the answer was sensible, and nothing ever compared all 65 profiles
together so no ordering could exist. The recorded recommendation was to define acceptance criteria
for the finished deliverable first and wire those as pass-or-fail checks.

**The architectural weakness stated against his own system.** The pipeline splits a problem into
bounded domains, decides each independently, then has to referee contradictions that exist only
because it split. A human holds the whole problem at once and is consistent by construction, and at
the observed input size the data is small enough not to require splitting at all. The diagnosis was
to keep sharding at genuinely large scale but make the ordering and merge decision once over a
compact summary rather than stitching blind parts together. This is a recorded diagnosis, not an
implemented change.

**Cost-parity benchmarking against real labels, not synthetic tests.** The harness grades candidate
models against a human reviewer's actual decisions and a ported deterministic gate, measures cost
from reported token usage against a price table rather than estimating, and is dry-run by default
so a real spend requires an explicit flag. Its own README separates the one objectively-labelled
case from the judge-scored cases and instructs the reader to treat the latter as agreement with a
reference model, not truth. Its result also has to be reported honestly: every model including the
expensive reference scored between 0.375 and 0.525 accuracy with accept recall at or near zero,
which is close to a degenerate always-reject classifier on a class-imbalanced set. The harness
design is defensible; the result is not evidence any model performed well.

**A cap applied to candidates instead of to work produces silent zeroes.** The per-tenant run cap
was applied inside the trigger function, before the caller dropped rows already built. A tenant
with 126 rows at the trigger status and a cap of 5 handed over the first five rows, the caller
recognised all five as done, and the run produced nothing, not once but forever, because the same
five come back first every run and the log reads "0 items", indistinguishable from a tenant with
nothing waiting. Found during a rehearsal with the cap at 1, where it silently zeroed four tenants.
The fix split the cap into a function the caller invokes after filtering, on the recorded reasoning
that the cap always meant "do not build more than N in one run", never "do not look further down
the list".

**A shared namespace is not the same problem as a shared matcher.** Item ids are slugified titles
and are therefore not unique across tenants. Generated JSON and rendered previews were keyed by
item id alone while status records were tenant-scoped, so two tenants with an item on the same
topic wrote to the same output and preview file: one tenant's generation silently overwrote the
other's, and the first tenant would open the link in their own email and read another tenant's
content inside their own branding, while status records stayed separate so nothing looked wrong.
The same root cause had earlier produced one tenant's licensed asset on another tenant's page,
which had been fixed by gating the matcher per tenant and leaving the namespace shared. Writes
became tenant-scoped while reads fall back to the legacy flat path so earlier artefacts keep
resolving.

**Fail closed on customer data, fail open on the checker.** The write path is read-only unless a
kill switch is set, refuses unlisted fields and values, refuses record ids the run did not itself
read, caps writes and refuses entirely if the audit cannot be written. The readiness checker
deliberately does the opposite and fails open if the checker itself cannot run, with the reasoning
written out: an unanswered question about a tenant is a stop, but a broken question-asker is an
alarm, and refusing every tenant on an import error turns a small deployment fault into a full
outage. A strict-mode variable inverts it. The same asymmetry governs two append-only logs: the
write audit refuses the write when it cannot log because it guards a shared live business system,
while the event ledger swallows every error and never blocks because a record-keeper that can stop
the work is worse than none.

**A guard that cannot run is worse than none.** The engine imported the preflight checker inside a
stdout redirect to a string buffer, which has no reconfigure method, so an unguarded encoding call
raised at import time. Because the readiness gate treats an import failure as "the checker is
broken, allow and shout", the write-time readiness gate had been silently inert on every API call
since it was built. Separately, a rename guard compared the requested identifier against a response
that carries a permalink but not an identifier, so it compared None, concluded nothing was wrong,
and let two tenants publish at a suffixed address one deploy after the guard was written. The final
rule there was to fail only on evidence, specifically only on the numeric-suffix rename pattern,
with None meaning "we genuinely could not read it" and being reported rather than treated as
success.

**Threat model changes when the network changes.** All five findings in the self-audit were safe
while the service ran on loopback behind a temporary tunnel; deploying to a permanent public URL
changed the threat model while the endpoint design did not change with it. The critical finding was
a chain, not a single bug: an intentionally unauthenticated edit endpoint, combined with a write
path inserting HTML verbatim with platform filtering disabled, meant guessing an identifier let an
attacker rewrite the body of an item awaiting approval so a human would approve arbitrary HTML onto
a live customer system. Identifiers are not secret, because they are keyword phrases that travel in
preview links inside customer inboxes. Recorded lesson: when something moves from local to public,
re-audit its whole surface, because "it was fine yesterday" is a statement about the network, not
the code.

**A cross-platform integrity failure that read as an architectural defect.** Line-ending conversion
on write broke every sha256 artefact binding in a hash-sealed pipeline, surfacing roughly 50 of the
pipeline's own contract errors that looked like design failures, while the same code was green on
another operating system. It cost a full working session and ended as a documented hard environment
constraint rather than a code change. A related finding in the same sweep: a test compared raw file
bytes instead of parsed JSON, so it was asserting a serialisation detail rather than the contract
it claimed to protect.

**Bounding what a worker agent may do, after watching unbounded ones fail.** Read-only planning
agents asked to return large JSON inline fragmented their output, hallucinated, and in one case
returned an entirely unrelated artefact. The fix was a contract rather than a better prompt:
workers restricted to read and write, required to save JSON to numbered files instead of returning
it inline, and forbidden from spawning further workers, followed by deterministic re-aggregation
and a re-run of the gate over the merged result. This is the multi-agent reliability lesson,
separate from the token-budget one.

**Proving a failure is the model's, not the input's.** Generation intermittently returned a raw
control character inside a JSON string value. The proof it was the model rather than the input was
that the same input produced a parse failure at a different character offset on two runs minutes
apart, and deterministic code cannot do that. The three-layer fix tolerated code fences and
surrounding prose, applied a targeted repair pass escaping only characters already illegal inside a
string and only while inside a string so it cannot alter document structure, and added a
three-attempt retry. The write-up names the real mistake as having previously logged an intermittent
failure as a curiosity instead of fixing it.

**A drifting model output caught at two independent layers.** Roughly one item in twenty came back
with its headline, summary and first four sections in the wrong language, with the source input
verified correct. The model started correct, drifted through the middle of a long output, and
recovered by the fifth section, which is why the tail was still correct. The prompt already carried
the rule in capitals. Two fixes: a language check inside the generator comparing input and output,
plus an independent check in the gate classified ERROR not WARN, with the reasoning that a warning
would have printed into a run log already carrying ten of them and the item would have gone out
anyway. The detector is deliberately conservative, scoring on function words unique to one language
plus diacritics as a positive signal and excluding words real in both, because a check that cries
wolf gets switched off.

**Retry is a claim about idempotency.** Adding a retry policy to every service-facing HTTP node was
only safe because generate overwrites, publish updates a tracked object id rather than creating,
and init returns the existing record. Mail nodes are excluded on purpose. The retry policy itself
was added after an incident in which not one HTTP node had a retry configured and a single
transient failure aborted an execution and abandoned every remaining item in the batch loop; this
should be told as a response to an incident, not as up-front design.

---

# PART H - THE SECURITY INCIDENT (July 2026)

## What happened

A customer system he was actively building automation against was taken over by an external
attacker mid-engagement. It surfaced as a support question rather than an alert: the platform lead
asked whether an unfamiliar admin account belonged to the pipeline, then escalated that the system
was down. Symptoms were a rogue admin account carrying the exploit family's signature, the real
admin stripped of capabilities, and the whole system returning 403 behind the host's security
shield.

## Root cause

A platform-core pre-authentication RCE: a REST batch route confusion chained with SQL injection,
requiring no login, under global mass exploitation for roughly ten days beforehand. **The core was
vulnerable before he ever touched the system, and the team independently reached the same
conclusion the next morning.** The incident log names two CVE identifiers; verify them before
quoting either.

## His response

Same afternoon: reproduced the outage externally, identified the vector, and ran a six-touchpoint
adversarial self-audit of everything he had touched, covering config lines, the bridge plugin, the
admin account, the hosted engine and a secret-leak hunt, plus a control-case comparison against a
sibling tenant where he had done far more work and which was clean. He swept roughly 27 tenant
systems for the same exposure, flagged one exploitable system and a spreadsheet holding plaintext
credentials, drafted the reply and escalation, and offered to rotate his token and deactivate his
plugin.

Ordering of operations he wrote down under incident conditions: a backup restore would likely
reinstate the vulnerable core and must be patched immediately after; the restore point must predate
the rogue account's creation; nothing should be published until the system was confirmed clean; and
his own integration token must be treated as exposed because it lived in a database table the
attacker had access to, so rotation had to happen after the restore and not before. Operational
discipline during the sweep: he deliberately did not open the spreadsheet of plaintext credentials
he had just flagged, sourcing his domain list from a tooling export instead.

The following day he independently re-measured the system to verify the team's patch rather than
taking it on trust, confirming by measurement that a REST route now 404ed and the namespace was
gone; turned the ad-hoc sweep into a passive credential-free scanner; scanned 44 domains finding two
exploitable including one never previously flagged; and audited his own API, fixing five findings
the same day. He also authored the team's standing security policy: twelve numbered principles plus
an append-only incident log, made mandatory reading before any live-system or credential work.

## The ordering caveat (binding)

**The audit work followed the incident.** The standing policy is dated the incident day, the scanner
was written the day after, and the unauthenticated write path was found in a self-initiated audit a
day later. Present this as incident response and the hardening that came out of it, **never as
prevention that pre-empted the breach**. The one genuine before-element is his pre-incident
discipline (token-gated routes, secrets never committed, self-cleaning live tests), which is why the
self-audit cleared him quickly.

## What is NOT recorded and must never be claimed

- Detection time, dwell time, downtime, data scope or exfiltration.
- A confirmed web shell. A web shell is an expected indicator for that exploit family and was never
  confirmed on this system; do not let the expectation become a finding.
- Host access logs.
- He did **not** remediate the client site himself and must not imply he did.
- Self-audit completion timing is inference, not record. The audit is dated the incident day but
  carries no completion timestamp, so "same evening" is unsupported. "Same day" is what the record
  shows.
- There is no statement anywhere on data scope, exfiltration, or whether breach notification was
  considered. For a law-firm client that absence is conspicuous. The honest answer if asked: this
  was handled by the platform team and he has no record of it. Never improvise here.

## Open items an interviewer may reasonably probe

The precautionary token rotation and plugin deactivation he offered are unchecked action items and
were never confirmed carried out. It is unconfirmed whether his reply to the platform lead was
actually sent, and when. Neither of the two exploitable systems is confirmed patched, one of them
still unpatched a full day after being flagged, and the plaintext-credentials spreadsheet is not
confirmed rotated or locked. Two further portfolio systems were found on exploitable versions but
were not reported compromised. **Say "flagged and escalated", never "resolved".**

## The safe bullet (use this wording)

Led the technical response to a client CMS compromise during a live engagement, identified the
vector as a platform-core pre-authentication RCE, ran a same-day adversarial audit of every
automation touchpoint to rule his own systems out with evidence rather than assertion, then built a
passive credential-free version scanner covering 44 client domains that surfaced two exploitable
systems, one of which nobody had previously flagged.

## Note on which security story is stronger

The client-site compromise was a third-party vulnerability handled by the web dev team; his
contribution was the credential-free portfolio scanner and the write-up. **The engine self-audit IS
his own work and is the stronger of the two stories.** Prefer it for security-shaped roles.

---

# PART I - TECHNOLOGY INVENTORY

Note on framing: parts of this stack were inherited rather than chosen. The legacy CMS, the hosted
orchestrator and the record store were the employer's existing choices; he argued for a modern
stack and did not win that argument. Adapting to an existing stack, extending it in its own
language where necessary, and measuring what it actually does rather than what its documentation
claims, is itself one of the capabilities being demonstrated. The freely chosen parts (standard
library over frameworks, generation over hand-configuration, deterministic gates, provider-free
test paths) are where his own taste shows.

**Languages and runtimes:** Python 3.10 and 3.11 (engines, pipelines, generators, tooling,
benchmarks; one acceptance run recorded on 3.14), PHP (CMS bridge plugins), TypeScript 5 and
JavaScript (Next.js app, orchestrator Code nodes, reviewer dashboards, validators), Node.js
(pre-import workflow validation and a JS-against-fake-context harness), HTML and CSS
(server-rendered previews, dashboards, email templates), shell (container entrypoint), PowerShell
(demo harness scripts), Markdown, JSON, NDJSON and JSONL.

**Standard library used deliberately in place of frameworks:** `http.server` with
`ThreadingHTTPServer`; `urllib.request`/`error`/`parse` for every outbound HTTP call, with no HTTP
client dependency anywhere; `json`; `hmac` and `hashlib` for HMAC-SHA256 and constant-time
comparison; `ssl` and `socket` for a centralised verified-TLS module; `subprocess`; `base64`;
`pathlib`; `threading.RLock`; `tempfile` plus `os.replace` and `os.fsync` for atomic writes;
`contextlib.redirect_stdout`; `argparse`; `re`; `datetime`;
`concurrent.futures.ThreadPoolExecutor`; `mimetypes`; `unittest`.

**Third-party Python (deliberately minimal):** beautifulsoup4 and lxml (HTML shell cloning, DOM
component stripping, existing-link extraction), openpyxl (spreadsheets read with hyperlink targets
preserved), Pillow (resize, JPEG re-encode, grayscale), sentence-transformers with a small
multilingual embedding model, numpy, jsonschema, certifi as an optional CA source, python-docx,
pypdf, python-pptx, PyYAML, pytest.

**LLM and model access:** Anthropic Messages API called as hand-built POSTs with explicit version
headers and JSON-schema output format, adaptive thinking and explicit effort; the Claude CLI in a
stripped no-tools isolation mode with a JSON-schema argument; Google Generative Language
generateContent with a JSON response MIME type; OpenRouter as a multi-model router; a local
sentence-transformer for embeddings. Model roles across the projects: a cheap router-hosted tier
for production generation with temperature 0 and reasoning explicitly disabled as a cost guard, a
Flash-tier vision model for asset tagging, a Flash-tier model as a free demo generation path, an
Opus-class model as production recommendation for regulated copy and as benchmark reference and
judge, and a benchmark registry covering nine models across several families.

**Front end:** Next.js 16 App Router with React 19, TypeScript, Tailwind CSS 4, lucide-react,
`next/image` with a remote-pattern allowlist, async server components, route handlers pinned to the
Node runtime, `generateMetadata` for per-tenant metadata; plus plain HTML and vanilla JS reviewer
dashboards using browser local storage with a JSON export as the feedback contract.

**Inherited CMS ecosystem:** WordPress REST API v2 (posts, media, categories, taxonomies, users)
with application-password Basic auth; a custom REST namespace from an in-house bridge plugin; ACF
field groups and `update_field`; a Rank Math style SEO plugin's post meta; Elementor-based themes
handled by selector-driven content-region replacement; an author taxonomy plugin; a must-use plugin
registering meta keys for the REST path; `kses` filter toggling around content insertion;
`hash_equals`; `random_bytes`; signed time-limited preview links.

**Data and external services:** Airtable REST v0 (filter formulas, offset pagination, field
projection, single-field PATCH, personal access tokens scoped to record read/write on one base with
no schema scope) plus the official JS SDK in the Next.js app; Google Docs public export endpoints;
Google Drive anonymous download by file id and native Drive nodes; Google Sheets via published CSV
export and xlsx export; Google Search Console evidence; sitemap inventory and crawl snapshots; a
commercial research provider (cost-governed, not invoked by the active runtime); an analytics tool
consumed as an MCP for manually refreshed dashboard snapshots; Tally as the primary questionnaire
source with Typeform payloads supported by the same parser; Gmail for delivery.

**Orchestration and infrastructure:** n8n Cloud (schedule, manual, webhook and
wait-resume-on-webhook triggers; HTTP Request, Code, Set, IF, Filter, Split Out, Split In Batches,
No-Op, Sticky Note, Gmail, Google Drive, Google Sheets, Airtable and Execute Command nodes; workflow
static data for cross-execution state; workflows generated programmatically from Python builders and
patched in place); Docker (slim Python base, build context scoped to the app directory,
seed-on-first-boot entrypoint, secrets never baked in, a dockerignore excluding environment and
generated files); Fly.io (regional deployment, shared CPU with 512 MB, persistent mounted volume,
auto-stop disabled so in-flight state is never wiped, HTTP health check every 30 s with 5 s timeout,
pinned public base URL); Render documented as an alternative with the note that a free tier's lack of
a disk makes it unusable for a stateful engine; Cloudflare Tunnel or ngrok for development-time
public URLs; Vercel for the front-end app; Git with dated and reason-suffixed backups.

**Contracts, validation and integrity:** JSON Schema (44 schemas in one pipeline module, 29
versioned contract families on an earlier snapshot); hand-written cross-artifact semantic
validators; sha256 over canonical JSON bytes; seal-and-verify helpers; append-only state event
files; atomic publish into fresh directories; content-hash-versioned prompts; frozen evaluation
cases locked by reference-file hash; golden fixtures and frozen provider envelopes for provider-free
execution.

**Security tooling and practice:** passive credential-free version fingerprinting via generator meta
tags, asset version query strings and readme fallback; exploit-chain exploitability scoring;
HMAC-SHA256 link signing; constant-time comparison; strict input allow-listing by regex; host
allow-listing with exact-or-dot-suffix matching, explicitly not substring; fail-closed
authentication; append-only audit logging with pre-write verification; kill-switch environment
variables; per-field and per-value write allow-lists; provenance checks binding writes to records
the run actually read; snapshot-before-write with revert on any live mutation.

**Testing:** 33 hand-rolled runner scripts with a shared assertion helper exercising real selection
and state code against fake network layers and a temporary data directory, with the stated design
rule that fakes stand in for the network only and never for the project's own logic; a custom
clean-room `unittest` runner that treats a skipped test as a failure and stops at the first failing
suite; pytest for dashboard and data-layer units; a Node harness that executes generated workflow
JavaScript against a stubbed context and compares its answers against the Python implementation of
the same rules; contract tests asserting named invariants; self-cleaning live smoke tests.

---

# PART J - WORKING METHOD AND PROCESS DISCIPLINE

**Parallel workstreams under one memory system.** Five workstreams ran concurrently across separate
repositories with different owners, different stacks and different maturity levels: a multi-tenant
processing engine, a proposal-and-gate pipeline, a bounded LLM strategy pipeline owned by someone
else, an orchestration and generation layer, and a demo onboarding pipeline. They were kept coherent
not by holding it all in his head but by a written state layer that any new session reads first.

**A single resume-state document as the designated first read.** The repository root holds a
resume-state file that is the first thing any new session reads: 308 KB with 145 second-level
headings, structured newest-first with a one-line "where we are" block, a table of current state per
tenant, an ordered next-steps list with warnings, then dated history below. A project sub-track
keeps its own and states explicitly that nothing is shared between the two tracks except hosting. A
dated backup is kept alongside.

**An explicit memory index.** A handoff directory holds an index of named memory documents, one line
each, linking to fuller files. The entries are durable facts rather than task state: a prime
objective, a communication constraint, a rule against unverified "done" claims, a measured finding
about tool recall, an architecture decision, a technical state document. Individual memory files
carry YAML front matter with a name, description and node type, and cross-reference each other with
wiki-style links.

**Separated contract and protocol documents.** One file says what the machine does, stating the
objective, the three independent state machines, the three workflows, six rules that must hold, and
then every known way the machine breaks with each entry marked confirmed, fixed or present-today
with a date; it closes with an instruction to change the file in the same commit as the machine, and
several of its invariants are asserted directly by a contract test file so trading one rule for
another fails in the test suite rather than on a customer's system. A second file says how the
machine is allowed to be touched, with numbered rules each citing the specific incident that
produced it: do not change logic to make a test pass; a test is undone by a documented clean-sweep
script and never by editing behaviour; nothing reaches a customer without two independent locks, a
global switch and a per-tenant flag, both defaulting to no; and a prompt is a request, so the output
must be checked.

**Learning tools on demand rather than staying inside the known stack.** The work required picking
up, in situ, a low-code orchestrator's node semantics and its hosted-runtime quirks, a legacy CMS
plugin API in a language he does not otherwise write, a record-store REST dialect with its own
filter grammar, a spreadsheet library chosen specifically because the obvious one drops the data he
needed, a local embedding model, a provider structured-output subset that differs from JSON Schema,
and a front-end framework version with server components. In each case the recorded pattern is the
same: measure what the tool actually does rather than trust its documentation, then encode the
measured behaviour as a constant or a guard with the measurement in a comment.

**Generation from code rather than hand-editing artefacts.** Workflow JSON is emitted or transformed
by generators that import the same modules the local tooling uses, so templates and logic cannot
diverge between the orchestrator and the package. The stated reasons are concrete: onboarding a
tenant is one command instead of a manual clone-and-edit of an eighteen-node canvas, a change to
retry policy or message template is one script run across every tenant, and the change becomes
reviewable in version control as a diff of the generator rather than as a 48 KB JSON blob.

**Templating across tenants as an explicit split.** The proposal pipeline is templated as "everything
above the tenant config is fixed, the tenant config is the steering wheel". Fixed across tenants: the
stage sequence and its file contracts, the rules text, the operation vocabulary and wrap-only policy,
the gate checks, the citation mechanism, the console renderer, and the call layer with its cost
accounting. Per tenant, in one Python module: tenant id and phase, base URL, caps, minimum incoming
links, category regexes, exclusion and priority page sets, hub set, banned anchors, tenant-specific
quality guards, the routing table, no-write zone labels, and the component selector dictionary
telling the fetch stage which widgets to strip.

**Smoke tests at two levels and readiness gates instead of remembered checklists.** A four-node
workflow exists purely to prove the hosted orchestrator can reach the engine and send mail. A
self-cleaning Python smoke test exercises the real write path against a live system and leaves it
exactly as it was. A preflight script answers "is this tenant safe to switch on" mechanically, per
tenant, read-only by default with an opt-in flag before it touches a tenant's own system, and a
non-zero exit code if any tenant is not ready; the registry refuses an incomplete tenant by name with
the missing item stated, and nothing silently falls back to a default.

**Naming and comment conventions consistent enough to be a system.** Generated workflow files are
prefixed by role and suffixed by scope; post-processing passes get their own suffix rather than
overwriting; dated documents carry an ISO date in the filename; backups carry a suffix naming the
reason rather than just a timestamp; decision and status documents are separated from reference and
architecture documents; test files are named after the invariant they protect rather than the module
they exercise. Throughout the generators and workflow-shaping code, comments record the failure that
motivated the line, with a date, and often the alternative that was rejected and why.

**Honest negative results are written down.** A separate tool evaluation leads its findings document
with the statement that the narrow question is unanswered and that no answer was fabricated,
tabulates what ran versus what did not with every untested cell saying "not run", resolves every
requested model name against the live provider catalogue, and verifies that no credential leaked into
the existing billing path. Similarly, a standing rule from a rejected release is that no completion
claim is made without showing the gate exit code and counts.

**Branch and review discipline.** One repository's process is branch plus reviewed pull request only,
never a direct commit to the default branch. (See FLAGGED: this does not apply to the repository
holding the code that publishes to client sites.)

---

# PART K - FLAGGED: DO NOT CLAIM WITHOUT CHECKING

**This section is binding and overrides every other section of this file.** Several of the
strongest systems described above were authored by a domain owner, not by Lohith. Several
attractive numbers (uptime, throughput, per-item cost, end-to-end latency, acceptance rates) do not
exist anywhere. Nothing marked unsupported here goes on a resume, in a cover letter, or into an
interview answer. When FLAGGED contradicts a claim above, FLAGGED wins. Reframing changes the
angle, never the facts.

## K1. Capability framing must not become domain claiming

**Applies to every reframed bullet.** The reframing in this file is about the angle, never about
the facts. The patterns transfer; the industry experience does not. He has not worked in fintech,
healthtech, devtools, logistics, e-commerce operations, insurance, or any other vertical, and no
bullet, cover letter or interview answer may imply otherwise. "Built multi-tenant workflow
automation with a human-in-the-loop approval gate" is true and portable. "Built multi-tenant
workflow automation for financial services" is a lie.

Likewise, do not silently upgrade domain nouns: a client portfolio is not "enterprise customers", a
marketing agency is not "a SaaS platform", 7 active tenants is not "at scale", a hand-run set of
numbered scripts is not "a platform", and an internal reviewer is not "the customer" where this
file says otherwise. If a JD asks for domain experience he does not have, say the pattern transfers
and name the closest real constraint he worked under (regulated professional-services copy, a
shared live operational database, a legacy CMS he could not replace), rather than borrowing the
JD's vertical.

## K2. Authorship uncertain (which code may not be his)

**The SEO content pipeline is the single biggest authorship risk.** That repository has two owners
with a formally separated lane. A domain owner owns the SEO architecture, the decision methodology,
the stage semantics and most of the Python runtime; Lohith owns the automation lane around it:
running skills out of chat, transport and cost work, diagnosis, environment and test
infrastructure, and the internal-linking application that consumes the same run data. The
repository's own handoff documents state the boundary explicitly and say the SEO architecture is
not to be redesigned.

**Likely NOT his:** the retrieval runtime, the evidence shard and manifest layer, the
provider-schema projection auditor, the closure and arbitration machinery, the scalability closure
and acceptance system, and the SEO decision methodology reference. Handoff notes describe several
of these in the third person.

**Likely his, each to be confirmed individually:** running three skills fully out of chat on real
client data with the measured token figures; the diagnosis that validators check form rather than
answer; the diagnosis that splitting the site manufactures the conflicts that then kill the run;
the Windows line-ending hash-mismatch finding; the byte-comparison test finding; a stale README
assertion finding; and the internal-linking product spec.

**Safe framing for the SEO pipeline:** "I worked inside a production-intended LLM pipeline of this
shape, owned the transport and cost lane, and diagnosed its central failure mode." **Unsafe:** "I
built a bounded evidence-sharded strategy pipeline."

**The publishing engine repository is written in a reflective post-mortem voice with dated
attributions to named colleagues, and contains an agent-workflow specs directory and session
artefacts.** Before claiming sole authorship, confirm which parts were hand-written versus produced
with heavy AI assistance. The defensible framing is likely "designed, directed and verified" rather
than "hand-wrote every line".

**The German-language layer is not his expertise.** The handoff notes state plainly that he does not
read German and relied on the reviewer for that layer. Several internal-linking gate checks require
explaining German grammar and German employment-law terminology, and the article skill encodes
legal-content quality rules. Defensible: the workflow architecture, the gating, the token-control
decision to emit search-and-replace pairs instead of full text, the input-contract design, and
"encoded the reviewer's rules as deterministic checks". Not defensible: personal language expertise,
legal-content quality rules, or SEO domain rules.

**The client-site security incident was not caused by, or fixed by, this code.** A CMS core
compromise on a client site was a third-party vulnerability handled by the web dev team. His
contribution was the credential-free portfolio scanner and the write-up. The engine self-audit IS his
own work and is the stronger of the two stories.

**Not all 26 n8n workflows were generated from code.** The earliest pipeline versions were hand-built
and exported, and the generators were written afterwards because hand-building had started to drift.
The strongest true version: four generators plus one post-processor produce and maintain the
workflows in production use, and the hand-built ancestors they were derived from are retained as
history.

## K3. Numbers that do not exist

Do not use any of the following. None of them are recorded anywhere.

- **Uptime.** No uptime figure, no availability measurement, no monitoring export exists in any
  repository.
- **Execution volume and throughput.** No orchestrator execution logs or metrics exports are
  present. No executions-per-day, no jobs-processed, no requests-served figure exists. The only
  volume evidence anywhere is client counts and the 16-article first-run count.
- **Success and error rates.** No publish error rate, no workflow success rate, no failure rate of
  any kind is recorded. Idempotency is asserted in code and covered by tests, but there are no
  execution logs demonstrating retry behaviour under a real transient failure, so idempotency must
  be stated as designed-for, not proven.
- **Per-article generation cost.** Not found in any repository. The model, temperature and
  disabled-reasoning settings are known and it could be computed from a price table, but no such
  figure was computed or recorded. The approximately $0.20 image-tagging total and the approximately
  $4 full-benchmark estimate come from project notes and a README, not metered billing.
- **Any currency cost for the SEO pipeline.** No per-run cost, no per-client spend, no price table
  exists in either snapshot of that repository. Cost appears only as a stated objective and as token
  counts. Converting those token counts to money or to a percentage saving is not supported.
- **End-to-end latency.** No end-to-end pipeline latency measurement exists for the publishing
  engine, the SEO pipeline or the linking pipeline. The only latency figures anywhere are per-model
  benchmark call latencies and one isolated 52-second canary call, which is a single synthetic
  planning call and must never be presented as pipeline latency. Internal linking run times are
  explicitly not recorded.
- **The 30-second preview-link figure in the landing page work does not exist.** The repository's own
  figures are approximately 40 seconds in the deck (claimed as measured in a live prototype),
  approximately 60 seconds in the setup guide and demo walkthrough, and 60 to 90 seconds in the
  speaker notes and explainer document. **These three disagree with each other**, nothing in code
  measures it, and the only hard timing constant is a 120000 ms HTTP timeout. Safe phrasing:
  "generation to reviewable preview link in under a minute in the demo run", attributed to the demo.
- **Acceptance rate of the internal linking output.** Not in the repository for the second client's
  final 347-link set, because that batch had not been re-reviewed when the repository was captured.
  Do not claim the reviewer accepted it. What exists is the earlier batch's 370-decision export (128
  accept, 24 reject, 218 undecided) and the fact that an earlier batch was rejected outright.
- **Number of real client firms processed by the landing page pipeline in production.** Not found.
  All four workflow exports are saved inactive, so they demonstrate structure, not a running system.
- **Orchestrator instance count, concurrency limits and plan tier.** Not found, beyond a design note
  that parked executions count against a concurrency allowance.

### Where sources disagree, say so

- The publishing-engine test suite is recorded as **33 test scripts with 715 assertion calls**
  (counted directly in the repository) and separately as **32 files with 732 checks at engine version
  71** (from the resume-state document, self-reported, with an earlier entry of 28 files and 682
  checks). **These do not reconcile; quote one and name its source.**
- The internal-linking gate is described as **"17 checks"** in the pipeline README and gate docstring
  while the framework document enumerates **18 numbered items** and the source implements more
  individual conditions than either. **Do not quote a check count without recounting the source.**
- A benchmark summary in the resume-state document reports cheaper models scoring 0.93 on the
  deterministic gate and 90 percent and 83 percent on review against 59 percent for the expensive
  baseline at 5x to 22x lower cost for about $8 total spend; the results JSON for the
  objectively-labelled case reports accuracy of 0.375 to 0.525 across nine models and an
  approximately $4 estimate for the full four-case run. **These are different measurements reported
  in different places and they do not agree; do not blend them.**

## K4. Claims that are weaker than they sound (with the accurate version he CAN say)

**"Production pipeline" for the SEO work.** The repository's own verdict is theoretically production
capable yes, fully production proven no, with four named remaining items, one known open blocker at
the last stage, and no completed independent live end-to-end run. **Accurate version:** "a
production-intended pipeline that had passed provider-free acceptance but not a full live end-to-end
run."

**"Multi-tenant production publishing platform."** Production scale is modest. The strongest volume
evidence is 16 published articles across 5 clients, 7 active client configurations, and a default of
4 posts per client per month. The 671-row and 193-client figures describe the agency's record base,
not what the pipeline processed. Several documents describe the pipeline as still gated, with client
email behind a master switch plus a per-client flag and several clients pre-staged but inactive.
**Accurate version:** "a pilot that published real articles to real client sites through a
multi-tenant, config-driven engine", which is true and strong.

**"Designed for 1,000 clients."** The 49-row configuration matrix and the target of reducing 14
questions per client to 5 are a written design document. **Accurate version:** "architecture thinking
about onboarding cost, written up as a configuration matrix", not delivered scale.

**"Built a benchmark showing the cheap model wins."** The recorded results JSON covers one case at 40
items, and every model including the expensive reference scored between 0.375 and 0.525 accuracy with
accept recall at or near zero, close to a degenerate always-reject classifier on a class-imbalanced
set. **Accurate version:** "built the harness, graded nine models against real reviewer labels and
measured cost from token usage, which is what justified a model swap on cost grounds", plus a ready
explanation of why the case turned out to be badly posed. The other three benchmark cases use an
expensive model as judge, which measures agreement, not truth, and the README says so.

**"38 percent" versus "44 percent" reviewer recall.** The honest common-sense figure is 12 of 32,
about 38 percent; the 44 percent is 27 of 61 overall including subjective calls. The team's own memo
records that 44 percent had been quoted casually and that 38 percent is the honest number. **Quote 38
percent** and be ready to explain the bucket split. This figure belongs to the internal-linking
project and must never be attributed to the publishing engine.

**"A 715-test pytest suite in CI."** These are hand-rolled runner scripts with a shared check helper,
and there is no CI configuration in the repository. **Accurate version:** "715 assertion calls across
33 test scripts". The landing page project has no automated tests at all and no CI; its two committed
scripts are manual one-shot harnesses.

**"An internal linking platform."** It is a set of numbered scripts run by hand from a folder, plus a
static HTML review dashboard, plus separately-run injection scripts. There is no service, no
scheduler, no queue and no self-serve UI, and the productisation objectives document lists the
self-serve app, multi-client setup, safety and recovery, cost guardrails and security as not started.
**Accurate version:** "a repeatable per-client pipeline, templated to a second client". Two client
instances exist; the target portfolio is roughly a dozen firms, so do not imply it ran across the
portfolio. Confirm before claiming links were actually pushed live to a client site; injection scripts
exist, are dry-run by default with snapshot and revert, and one instance has recorded snapshot files.

**"The internal linking orchestrator with budget governor and feedback versioning."** That document is
marked vision and north-star, not yet built. The orchestrator-plus-workers design, the deterministic
gate spec, the budget governor and the feedback-versioning model are design, not running code. The
6.9 million token runaway that motivated its budget caps is a real measurement and can be cited.

**"Deploys a page per client to Vercel."** No deploy is triggered per client: there is no deploy hook,
no deploy API node, no CI config and no static params generation. One pre-deployed app serves every
client through a dynamic route reading the record store at request time. **Accurate version:** "a new
page becomes reachable as soon as the row exists", which is the stronger architectural story anyway.

**"The preview link reaches the client."** It reaches an internal reviewer address. The mail node
sends to a reviewer placeholder and the copy is written for the internal team.

**"Reviewer feedback routes to Airtable."** It does not, in the committed code. The approve route sets
status back to Generating and forwards the feedback text to a webhook, but the only write helper
exported by the data layer updates status. The schema defines a feedback field and a code comment
claims otherwise, but no code writes it. **Accurate version:** the field is in the schema and the
webhook forward is wired, and the Airtable write is the missing piece.

**"Section-level regeneration."** The regeneration workflow has no committed JSON export. It is
documented in the setup guide, supported by a clause in the prompt and posted to by the app, but there
is nothing to demonstrate. Also, the contract returns the whole updated document with untouched
sections left alone, not only the changed sections. **Accurate version:** "feedback-conditioned
regeneration of the full content object, with the prompt constraining the model to leave untouched
sections alone."

**"Auto-publish on approval."** Approval flips a status field against a shared renderer that refuses to
render anything not Approved or Live. That is a status gate, not a publish or deploy job. An optional
publish webhook fires if an environment variable is set, but no publishing workflow exists in the
repository.

**Reviews and gallery content on the landing pages is placeholder-injected, not generated or fetched.**
The deck describes a daily places-API sync as the production design; no such workflow exists. The demo
data is stock imagery and mock reviews, which the deck does disclose. Team member parsing is also
incomplete: the questionnaire captures team members as a single raw multi-line string passed through
as-is, and the model infers the structure.

**The import-ready landing page workflow contains inline secrets.** It hard-codes a record-store token
and a provider API key directly into node parameters instead of using the credential store, which the
labelled variants use correctly. This was a demo-speed shortcut with a real security consequence. Any
reuse of that material must strip and rotate those values first, and it is better raised proactively in
an interview than discovered.

**Path traversal write was proven locally, not in production.** The security log is careful about this;
any claim must be too. The live proof was read-only against the deployed service; the write was proven
locally in a throwaway directory.

**Some described publishing-engine behaviour is aspirational or partially wired.** The draft stage
explicitly holds rather than performing a live write. The post-publish stage stamps status and delegates
the actual indexing, analytics and sheet updates to workflow nodes. The SEO dashboard section is a
manually refreshed snapshot, not a live integration, by explicit design. Do not describe these as fully
automated integrations. The client email path had two locks and a documented mark-then-fail gap where a
summary can be marked as sent before the mail node fires, with a manual unmark as the remedy; that is
the honest answer on delivery guarantees.

**Which workflows are actually live.** The prepare workflow, the publish-on-decision webhook workflow
and the social monthly mail were live; the third publish route was built and reviewed but had not been
executed as of the last resume state. Some workflow files are historical and one is described as never
having been run.

**"20+ workflow definitions" is literally true but weak alone.** Leading with "26 definitions, about 12
distinct shapes, 7 of them generated per-client instances" is both stronger and safer, because an
interviewer who opens the directory will see seven near-identical per-client files and several variant
suffixes. Similarly, "orchestrating end to end" is accurate for the content pipeline, but be ready to
say the heavy lifting is in an HTTP engine and that the orchestrator is the orchestrator, not the
processor: 137 of the 490 nodes are HTTP calls out to that engine.

**Do not sum the two SEO snapshots.** 173,454 lines on the older snapshot and 62,427 on the branch are
the same project at two points in time; the branch is a large deliberate reduction, and the older figure
had already been reduced by the domain owner before handoff, so quoting it as current state would be
wrong.

**Model identifiers must be described generically unless confirmed.** Model names in the linking
repository and mismatches between the landing page deck and its workflow JSON mean the exact identifiers
cannot be asserted. Describe as "a cheap open-weight tier via a router" and "a frontier reference model"
unless the specific identifier can be confirmed from the file.

**Never claim evaluation-driven quality improvement on the SEO pipeline.** There is no scoring, no rubric
and no measured quality baseline for the model's SEO judgement. The evaluation files are behavioural
expectation cases, several frozen and never yet run against a model.

**Retry policy was not designed up front.** The code says plainly it was added after an incident in which
zero HTTP nodes had retries configured. Told honestly it is a better story than inflated.

**The code that publishes to client sites was entirely untracked in git at the time of the incident.** No
history, no rollback, for exactly the code that touches live customer systems. It went into git on
2026-07-29. This is logged honestly in the repository and must not be papered over by any "version control
discipline" claim; the branch-and-reviewed-PR discipline described elsewhere belongs to a different
repository.

**The 4-posts-per-tenant-per-month figure is a business target, not a throughput measurement.** It appears
as a config default and in a handoff note. No run log records items actually produced at that rate. Quote
it as a configured cadence, never as delivered volume.

**Numbers from adjacent projects share a repository and must not migrate.** The linking-pipeline figures
and the benchmark figures live in the same repository as the orchestration work. Do not let a linking
number or a benchmark number appear inside an orchestration bullet, or vice versa.

**The article and briefing skills: quality rules are not his.** The German language layer is not his, and
the same applies specifically to the 17-phase generation skill: he can defend the workflow architecture,
the phase gating, the token-control decision to emit search-and-replace pairs, and the input contracts. He
cannot defend the legal-content quality rules or the domain quality rules encoded inside it.

**Landing page model identity in the demo.** Beyond the general "describe models generically" rule: the
identifiers in the workflow JSON do not match the deck, so he must know which model actually executed in
the demo before describing it at all.

**Two parallel provider workflows in the landing page work have already drifted.** The import-ready
variant gained placeholder back-filling that the labelled variants never received. Do not describe those
exports as a single maintained artefact.

**Graceful degradation in the landing page work is a named liability, not a feature.** The repository's own
honest read is that every silent fallback there (the offline sample record, the console log when the
webhook is unset, the fence-strip retry) is a demo-robustness win and a production liability, because a
fallback that silently succeeds hides an outage. Do not present those as reliability engineering; the
reliability engineering claims belong to the publishing engine and the orchestration layer.

## K5. Security incident, July 2026 - what may and may not be claimed

Restated here because this subsection is binding. Full narrative in PART H.

- The core was vulnerable before he ever touched the site, and the team independently reached the same
  conclusion the next morning. The incident log names two CVE identifiers: **verify them before quoting
  either.**
- **Ordering:** the audit work followed the incident. The standing policy is dated the incident day, the
  scanner was written the day after, and the unauthenticated write path was found in a self-initiated
  audit a day later. Present this as incident response and the hardening that came out of it, **never as
  prevention that pre-empted the breach.** The one genuine before-element is his pre-incident discipline
  (token-gated routes, secrets never committed, self-cleaning live tests), which is why the self-audit
  cleared him quickly.
- **Never claim, because it is not recorded anywhere:** detection time, dwell time, downtime, data scope
  or exfiltration, a confirmed web shell, or host access logs. He also did not remediate the client site
  himself and should not imply he did. A web shell is an expected indicator for that exploit family and
  was never confirmed on this system; do not let the expectation become a finding.
- **Open and unconfirmed items an interviewer may probe:** the precautionary token rotation and plugin
  deactivation he offered are unchecked action items and were never confirmed carried out; it is
  unconfirmed whether his reply to the platform lead was actually sent, and when; neither of the two
  exploitable systems is confirmed patched, one still unpatched a full day after being flagged; the
  plaintext-credentials spreadsheet is not confirmed rotated or locked; two further portfolio systems were
  found on exploitable versions but were not reported compromised. **Say "flagged and escalated", never
  "resolved".**
- **Self-audit completion timing is inference, not record.** The audit is dated the incident day but
  carries no completion timestamp, so "same evening" is not supported. "Same day" is what the record
  shows.
- **There is no statement anywhere on data scope, exfiltration, or whether breach notification was
  considered.** For a law-firm client that absence is conspicuous. Flagged here so it is never improvised
  in an interview: the honest answer is that this was handled by the platform team and he has no record of
  it.
- **Safe bullet:** led the technical response to a client CMS compromise during a live engagement,
  identified the vector as a platform-core pre-authentication RCE, ran a same-day adversarial audit of
  every automation touchpoint to rule his own systems out with evidence rather than assertion, then built
  a passive credential-free version scanner covering 44 client domains that surfaced two exploitable
  systems, one of which nobody had previously flagged.
