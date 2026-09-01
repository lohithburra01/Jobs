# Tailoring sheet

The working file. Read this at the start of every session, not
`context/corominas-systems.md`, which is 38k tokens and exists for depth on demand.

Flow: match the JD against the index, pick two or three capabilities, write the bullets
from the one-liners below. Open `context/corominas-systems.md` and read ONLY the relevant
section when a bullet needs architecture detail or an exact number that is not here.

Binding rules that do not fit on this sheet and must not be forgotten:
- Lead with the pattern, never the domain. PART 4 rules 9 and 10.
- Scale is a pilot: 16 articles, 5 clients, 7 active configs. Lead with depth, not volume.
- No uptime, throughput, success rate, per-item cost or end-to-end latency exists
  anywhere. Never claim them.
- The SEO content pipeline runtime is largely the domain lead's. His lane is the
  automation, transport and cost work, the diagnoses, and automation inside the skills.
- Security is response and hardening, never prevention that pre-empted the breach.
- The full FLAGGED section lives at the end of `corominas-systems.md`. Read it before
  writing any bullet that quotes a number not on this sheet.

## Capabilities

### Making nondeterministic model output safe to ship
**Problem:** a language model produces plausible output that is wrong in ways a human reviewer will not reliably catch at volume, and the cost of one bad item reaching a customer is high. Prompt-tuning does not solve it, because a prompt is a request.
**Proof:** the label-honesty check exposed 77 percent of one proposal class (48 of 62) as fabricated sentences mislabelled as verbatim wraps, a defect rate nobody had a number for before the check existed. A frozen regression case records a model returning 7 decisions with 7 evidence-accounting rows while zero evidence shards had been delivered.

### Deciding what a model decides and what code decides, and enforcing the split
**Problem:** work gets routed to a model because that is the fast way to make it work at all, and the resulting system cannot be explained, reproduced, costed or tested.
**Proof:** 3 model-touching stages out of 11; a deterministic transformation preferred over a second model call, with a losslessness assertion that reconstructs the original input from the transformed output.

### Human-in-the-loop approval as an architectural component
**Problem:** approval bolted on as an email produces duplicate sends, lost decisions, double-submits, and pipelines that stall because one item is waiting on a person.
**Proof:** decision memory holding 218 rejected and 311 accepted decisions as an accumulating per-tenant asset; a version-4 measurement showing 0 of 129 previously rejected combinations re-proposed and 119 of 122 accepted items preserved.

### Multi-tenant systems where behaviour is configuration, not code
**Problem:** a system built and proven on one tenant silently promotes that tenant's every value to a universal default, and the failures are invisible rather than loud.
**Proof:** 10 tenant entries with 7 active, per-tenant behaviour as config rather than code branches; a 49-row configuration matrix in which every setting is classified as dies-with-the-content-plan, constant-for-everyone, discoverable-in-code, or genuinely per-tenant, with a stated target of reducing 14 human-answered questions per tenant to 5.

### Reliability engineering for unattended pipelines
**Problem:** an automation that runs while nobody is watching fails in ways that look like success, and a naive retry turns a transient error into a duplicate side effect.
**Proof:** 3 tries, 5000 ms apart, 300000 ms timeout across 137 service-facing HTTP nodes in 26 workflow definitions; serialising a read-modify-write took a concurrency test from 58 raised writes to 0.

### Measuring model quality and cost instead of guessing
**Problem:** model choice is usually made on vibes or on the vendor's benchmark, and cost is estimated rather than measured, so nobody can defend a swap.
**Proof:** 9 models over 40 items; reference model $1.149 at 3.12 s mean latency and 0.525 accuracy against a cheapest contender at $0.0109, 3.77 s and 0.500 accuracy for the identical run. The result is also the demonstration of judgment: every model landed between 0.375 and 0.525 accuracy with accept recall at or near zero, close to a degenerate always-reject classifier on a class-imbalanced set, and the recorded conclusion is that the case was badly posed, not that a model won.

### Bounded context and budget control for LLM systems at scale
**Problem:** an LLM system whose prompt grows with its input works in development and fails at the provider boundary in production, and the failure arrives as a truncated response rather than as an error.
**Proof:** bounded-tree acceptance passed at 50, 500, 1,000 and 3,718 subjects with zero provider calls, producing 8, 62, 123 and 454 work units, with artifact bounds fixed at fanout 4, leaf records 12, catalogue entries 12, conflicts 4, string length 2,048 and semantic payload 18,000 bytes regardless of scale. Per-stage isolation measured at 16K, 31K and 23K peak context for 56K, 87K and 100K total tokens across three real runs, against the 139K baseline the unisolated design would have carried. On the cost side: disabling provider reasoning cut hidden-thinking output tokens by 5x to 10x, and a 6.9 million token fan-out across 359 agents is the recorded incident that set the budget rule.

### Integrating with an inherited stack rather than requiring a rewrite
**Problem:** the interesting automation almost always has to land on a platform somebody else chose, that predates the engineer, and that will not be replaced. Insisting on a rewrite is not an engineering answer.
**Proof:** three different names observed for the same template-triggering taxonomy across tenant sites plus one site with none; two hosts measured returning HTTP 413 above roughly 1 MB while a third accepted a 1.2 MB file; three distinct content storage shapes discovered across installs of the same platform, with writers implemented for two.

### Write perimeters around shared live systems of record
**Problem:** an automation that writes into a database humans edit by hand all day can destroy work silently, and "we were careful" is not a control.
**Proof:** 6 ordered guards, a write cap of 25 records per run, and two append-only logs with deliberately opposite policies (the write audit refuses the write when it cannot log; the event ledger swallows every error and never blocks).

### Infrastructure as generated artefacts rather than hand-built console state
**Problem:** low-code and console-configured infrastructure drifts across tenants, cannot be reviewed as a diff, and duplicates logic that already exists in a tested package.
**Proof:** 26 workflow definitions, 490 nodes, roughly 12 distinct shapes, 7 generated per-tenant instances; onboarding a tenant is one command instead of a manual clone-and-edit of an eighteen-node canvas, and a policy change becomes a reviewable diff of a generator rather than of a 48 KB JSON blob.

### Operator tooling and reversible destructive operations
**Problem:** a pipeline nobody can safely test against real data is a pipeline that only gets tested in production, by a customer.
**Proof:** both publish entry points build the payload and write nothing without an explicit commit flag, with going live requiring a second flag on top; injection scripts are dry-run by default with snapshot-before-write and a revert command.

### Adversarial self-audit and security review of one's own surface
**Problem:** engineers audit other people's code. The systems that get compromised are usually the ones whose author never attacked them.
**Proof:** 5 findings (1 critical, 1 high, 2 medium, 1 low), all fixed and deployed the same day, verified by a 22-of-22 local suite in a throwaway data directory including a re-run of the proven traversal exploit, plus a live re-probe of every original exploit showing previously-succeeding requests refused while the legitimate reviewer flow still returned 200.

### Incident response, and turning a lived incident into permanent tooling and policy
**Problem:** most teams handle an incident, write a postmortem nobody reads, and keep the same blind spot.
**Proof:** 44 domains scanned out of an estimated 85 managed systems, returning 2 exploitable (one never previously flagged), 3 very old but unaffected, 17 confirmed patched and 22 with the version hidden and unverifiable from outside. Ordering matters and must be stated honestly: the audit work followed the incident and is response and hardening, never prevention.

### Root-cause diagnosis of silent failures in automated systems
**Problem:** the dangerous defects in an unattended system are the ones that look identical to success. Nothing errors, a log line reads zero, and the pipeline reports green.
**Proof:** 126 rows against a cap of 5 producing 0 items forever, found during a rehearsal at cap 1 where it silently zeroed four tenants; the resulting rule, recorded in source, that the cap always meant "do not build more than N in one run" and never "do not look further down the list".

## Quick index for JD matching
Rows are capability signals, not domains. Find the JD's language on the left, lead with the capability, cite the system as the setting.

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
