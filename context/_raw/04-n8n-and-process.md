# n8n orchestration and working process - capability notes

Source: a production automation repo for a marketing agency serving law-firm and
professional-services clients. All client, firm, person and host names are omitted
deliberately. Every number below was read out of the repository, not estimated.

## n8n workflow inventory

**Files.** A content scan for the n8n node schema marker across the whole repository
returns **26 JSON files** that are valid n8n workflow definitions (top-level `nodes`,
`connections`, `settings.executionOrder = v1`). They live in two project areas: a
social-media monthly-mail track (3 files) and a web-content publishing pipeline
(23 files).

**Nodes.** Those 26 files contain **490 nodes in total**, of which **137 are HTTP
request nodes** and **40 are Gmail send nodes**. Individual workflows range from
**4 nodes** (a deliberate smoke-test workflow) to **28 nodes** (the original
end-to-end monolith).

**Distinct shapes.** The 26 files are not 26 independent designs. Grouping by
structure gives roughly **twelve distinct workflow shapes**, with the remainder being
generated per-client instances, versioned iterations (v1 / v2 / v3), and mechanically
post-processed variants (`.ready`, `.retry`). The classes:

1. **Monthly social-media client mail** (14 nodes). Schedule trigger plus a manual
   test trigger, five Code nodes, one HTTP node reading a published spreadsheet CSV,
   two native Google Drive nodes, one Gmail node, one no-op branch for skipped
   clients. This is the fully generated workflow.
2. **Drive discovery probe** (5 nodes). Manual trigger, a Set node for parameters,
   one HTTP node, one Code node. A throwaway exploration workflow used to work out
   how the shared-drive tree was actually shaped before committing to node choices.
3. **Drive folder resolver** (6 nodes). Manual trigger plus three native Google Drive
   nodes and one large Code node that rebuilds the folder tree in memory and matches
   every client name from the client sheet to its folder. Nothing is guessed: names
   that cannot be resolved with certainty are emitted under an explicit
   "not found" list.
4. **Workflow A, "prepare and ask"** (18 nodes per client, 19 nodes for the
   all-clients build). Hourly schedule trigger plus manual trigger, two IF nodes,
   split-out plus a batch loop, six HTTP calls into the content engine, one Code
   node, one Gmail node. Reads rows awaiting client approval, generates the page,
   runs a QA stage, assembles a preview, arms an approval gate per page, then sends
   one summary mail per client. **Seven generated per-client instances exist in the
   repo**, plus the consolidated all-clients build.
5. **Workflow B, "the client decided"** (16 nodes). Production **webhook trigger**
   (POST, single shared path, response from last node), three IF nodes, six HTTP
   calls, three Gmail nodes. Publishes exactly the one page the client acted on,
   flips the record status, mails the client that the page is live, and routes a
   rejection to an internal-only mail instead.
6. **Workflow C, "already approved"** (20 nodes). Manual trigger, seven HTTP calls,
   three IF nodes, a batch loop, one Gmail node. Publishes rows that were approved
   outside the dashboard, with no approval gate armed anywhere in it. The absence of
   the gate calls is the deliberate fingerprint that proves the two publish routes
   cannot interfere.
7. **The original monolith** (28 nodes) and its retry-stamped twin. Schedule plus
   manual trigger, seven HTTP calls, four IF nodes, three Gmail nodes, a batch loop
   and a **Wait node resuming on webhook**. This is the shape that A and B were later
   split out of.
8. **Pipeline v1** (20 nodes). Schedule trigger driving five `executeCommand` nodes
   and two Wait nodes. The pre-cloud, shell-out design, kept as history.
9. **Pipeline cloud v1 / v2 / v3** (22, 24 and 25 nodes). The migration from
   spreadsheet-driven and shell-driven steps to HTTP calls against a hosted engine,
   preserved as separate files rather than overwritten.
10. **A dedicated smoke-test workflow** (4 nodes): manual trigger, one HTTP call to
    the engine's QA endpoint, one Gmail node with a sticky note explaining the run.
11. **`.ready` variants.** A mechanical pass over an exported workflow to make it
    importable, kept as a distinct file so the source and the import artefact are
    both auditable.
12. **`.retry` variants.** The same workflow after a script stamped a retry policy
    onto every HTTP node (see Reliability patterns).

**Trigger types actually present in the JSON:** schedule trigger (hourly, and daily
at a fixed hour), manual trigger, production webhook, and a Wait node resuming on
webhook. Several workflows carry a schedule trigger and a manual trigger wired into
the same downstream node, which is the dual-trigger design described below.

## Workflow generation from code

**The claim "20+ n8n workflow definitions orchestrating the pipeline end to end,
generated FROM CODE so they stay reproducible across client configurations" holds,
with one honest qualification.** The file count is real: 26 workflow definitions exist,
comfortably over 20. The generation is real: there are **four Python generators and
one post-processor** that emit or rewrite workflow JSON. The qualification is that not
all 26 files were generated. The earliest pipeline versions were hand-built and
exported, and the generators were written afterwards, explicitly because hand-building
had started to drift. The accurate phrasing is: **the workflows in production use are
generated from code; the repo also retains the hand-built ancestors they were derived
from.**

**How generation works.** Two different strategies are used, and the candidate should
be able to name both.

*Strategy 1: emit the workflow from a tested Python package.* The social-media mail
workflow is built by a generator that imports the same rendering and signature modules
the local tooling uses. The mail templates and the signature HTML are read out of the
real source files at build time and inlined into the workflow's Code nodes, so the
workflow and the local package cannot say different things. The generator's own
docstring states the reason: writing the German copy, the signature blocks and the
date rules a second time by hand into a JSON blob is how the two copies start
diverging. The date logic embedded in the generated Code node computes the send day as
the 25th of the previous month, advanced past weekends **and past regional public
holidays** including the movable Easter-derived ones, with the Easter computation
written out in the emitted JavaScript.

*Strategy 2: transform a proven workflow.* The web-content generators do not build
from nothing. They load a workflow file that has been proven end to end in production,
then transform it. One generator rewrites every engine call for a different client,
adds the approval-arming node in the one position where the resume URL exists, swaps
both client-facing mails to HTML templates, and adds the "your page is live" mail. A
second generator performs the structural split: it takes the monolith and emits two
files, moving a named list of thirteen downstream nodes out of the prepare workflow
and into the publish workflow. A third generator builds the third route by copying
engine-facing nodes **verbatim** out of the two live workflows, so the engine URL, the
auth header name, and the client mail template cannot drift from what is already
running.

**What is parameterised per client.** The client identifier in every engine call, in
both the query string and the JSON body; the engine base URL; the webhook path (either
one path per client or a single shared path serving all clients); the recipient address,
which is resolved at runtime from the engine response rather than baked in, so a
central email allow-list stays in control; the content-plan source (a fixed demo
document, or the live records source); and the batch limit. The generator exposes
`--client <id>`, `--all-clients`, `--generic-b`, `--engine-base`, `--airtable` and
`--demo-doc` flags, and refuses mutually exclusive combinations.

**Guards inside the generator.** Two are worth citing in an interview because they
show the failure they were written against.

- The generator refuses to write a file if the resulting workflow references more than
  one engine host. The reasoning is recorded in the code: a workflow that talks to two
  engines is worse than one that talks to the wrong engine, because half the run writes
  state the other half cannot read. Rewriting only the newly built nodes had previously
  left inherited nodes pointing at a retired host.
- A default engine URL was **removed** after it silently pointed generated workflows at
  a decommissioned engine. The generator now requires the base URL to be supplied and
  rejects any value that is not HTTPS, because the engine mints signed links and every
  call carries an API token.

**Why this matters versus hand-building in the n8n UI.** The repo answers this
directly rather than in the abstract. Onboarding a new client is one command instead of
a manual clone-and-edit of an eighteen-node canvas. A change to the retry policy, the
mail template or the engine host is applied by re-running a script across every client
rather than by opening N workflows. The workflow becomes reviewable in version control
as a diff of the generator, not as a 48 KB JSON blob. And the generator prints, after
each build, the node count, whether the Wait node is absent as intended, and the exact
list of Gmail nodes that still need a credential attached by hand, because credentials
are the one thing that cannot be generated.

## Reliability patterns

**Retry policy.** Every engine-facing HTTP node carries `retryOnFail: true`,
`maxTries: 3` and `waitBetweenTries: 5000` milliseconds, with a request timeout of
300000 milliseconds. This is applied at build time by the generators and also by a
standalone patcher script for workflow files that already exist and should not be
regenerated. The patcher supports a `--check` mode that reports without writing, skips
any JSON that is not an n8n workflow, and prints the count of engine calls plus the
names of the nodes it changed.

The reasoning is written into the code and is defensible: not one HTTP node in the
originally shipped workflows had a retry set, so a single transient failure aborted the
execution **and abandoned every remaining item in the batch loop**. A specific incident
is cited where a generate call returned a server error once and succeeded on a manual
retry, with nothing retrying it automatically.

**Retry is only safe because the stages are idempotent, and this is stated explicitly.**
Generate overwrites, publish updates the tracked post id rather than creating a new
post, and init returns the existing record. Gmail nodes are **deliberately excluded**
from the retry policy: re-sending a mail that already went out is treated as worse than
surfacing the error.

**Dual-trigger design.** Several workflows wire a schedule trigger and a manual trigger
into the same first processing node. The scheduled path is the production path; the
manual path passes through a Set node holding test parameters (a redirect address and a
month override) so a full run can be exercised against real data with every mail
diverted to one internal address and the real recipient shown inside the message body.
A test run is explicitly **not** recorded as sent.

**Idempotency and dedup.** Two independent mechanisms.

- The social workflow's already-sent guard uses n8n's **workflow static data**, keyed by
  month, holding the set of client ids already mailed. It survives executions, so
  repeated manual runs on the send day still deliver exactly one mail per client. The
  repo also records the operational consequence: re-importing the workflow wipes that
  static data, so a re-import after a live run would mail everyone a second time. That
  is written down as a hard rule rather than left to be rediscovered.
- The content pipeline uses a **three-state model** kept independent on purpose: the
  client-facing record status, the internal pipeline status, and the approval-gate
  state. A separate `notified_at` timestamp enforces "a client is mailed about a page
  exactly once", which is what allowed the hourly schedule to be switched on at all.
  The two publish routes are separated by record status alone, and that constraint is
  documented as the fault line to watch.

**Rate-limit handling.** One Google Drive node carries `executeOnce: true`, with the
reason recorded on the node: without it the node runs once per shared drive and each
run rescans the whole drive, which produced a documented rate-limit rejection from the
provider on a specific date.

**Error routing.** Selected nodes carry `onError: continueRegularOutput` so that a
failure in one item does not abandon the batch. This is applied selectively, not
globally. One workflow in the repo is flagged in the resume notes as having a Gmail
node **without** error handling, with the consequence spelled out: the page would
already be live, the status write would never run, and the rest of the batch would be
dropped. That the gap is written down and named is itself part of the pattern.

**Node choices made to avoid known runtime failures.** The IF/Filter/Switch node family
is banned from the generated social workflow and replaced with two one-line Code nodes,
because the IF node type-checks the empty right-hand field of a boolean condition and
failed at import twice. Native Google Drive nodes are used rather than generic HTTP
nodes because the hosted n8n refuses Google credentials inside an HTTP request node.
A month name is produced from a literal array rather than a locale call, because the
locale data may not be present in the hosted runtime and the mail would silently render
in the wrong language.

**Pre-import validation.** A Node script validates the generated workflow before anyone
imports it. It checks that every connection points at a node that exists, that no node
is orphaned, that node names and node ids are unique, that every Code node's JavaScript
parses, and that no banned node type is present. A second Node test harness **extracts
the JavaScript out of the generated workflow and executes it against a fake n8n
context**, comparing its month-by-month answers against the Python implementation of
the same rules. The stated reason is that the Python is tested but the JavaScript is
what actually sends the mail, and a generated artefact nobody runs is a guess.

## Working protocols and process

**A single resume-state document.** The repository root holds a `NOW.md` that is the
designated first read for any new session. It is **308 KB with 145 second-level
headings** and is structured newest-first: a "where we are in one line" block, a table
of current state per client, then an ordered next-steps list with warnings, then dated
history below. A project sub-track keeps its own `NOW.md` and states explicitly that
nothing is shared between the two tracks except the hosting. A dated backup of the
root file is kept alongside it.

**An explicit memory index.** A handoff directory holds a `MEMORY.md` that is an index
of named memory documents, each one line, each linking to a fuller file. The entries
are durable facts rather than task state: a prime objective, a communication
constraint, a rule against unverified "done" claims, a measured finding about tool
recall, an architecture decision, a technical state document. Individual memory files
carry YAML front matter with a name, a description and a node type, and cross-reference
each other with wiki-style links.

**A session handoff document** written for a cold restart in a fresh terminal. It
carries the version history of a deliverable, the reviewer's actual reactions version
by version, an honest record of where trust was broken and why, the current state with
its verification status, the diagnosis, and the roadmap. It names the two companion
documents to read with it.

**A written protocol file with numbered rules.** A `PROTOCOL.md` exists alongside a
`FLOW.md`. The split is deliberate and stated: `FLOW.md` says what the machine does,
`PROTOCOL.md` says how it is allowed to be touched. The rules include: do not change
the logic to make a test pass; a test is undone by a documented clean-sweep script and
never by editing behaviour; nothing reaches a client without two independent locks
(a global switch and a per-client flag, both defaulting to no); and a prompt is a
request, so the output must be checked. Each rule cites the specific incident that
produced it, including a case where a change that was correct in isolation would have
emptied a two-month backlog of un-announced items into real client inboxes on its
first scheduled run.

**A contract document with numbered invariants.** `FLOW.md` states the objective, the
three independent state machines, the three workflows, and **six rules that must
hold**, then a section listing every known way the machine breaks, each entry marked
confirmed / fixed / present-today with a date. It closes with an instruction to change
the file in the same commit as the machine. Several invariants are asserted directly by
a contract test file, so trading one rule for another fails in the test suite rather
than on a client's website.

**Reversal and reset as first-class tooling.** A reset script performs four steps per
item in a fixed order, and the order is described as the safety property. It runs as a
dry run by default and requires an explicit apply flag. A client whose site is not
responding is skipped entirely rather than half-reset.

**Readiness gates rather than remembered checklists.** A preflight script answers "is
this client safe to switch on" mechanically, per client, read-only by default, with an
opt-in flag before it touches a client's own site, and a non-zero exit code if any
checked client is not ready. The same principle appears in the client registry code:
an incomplete client is refused **by name** with the missing item stated, and nothing
silently falls back to a default.

**Smoke tests at two levels.** A four-node n8n workflow exists purely to prove the
hosted workflow can reach the engine and send a mail. Separately, a self-cleaning
Python smoke test exercises the real publish path against a live site, verifies the
result including its featured image and SEO metadata, then deletes the post and the
uploaded media so the client site is left exactly as it was.

**An isolated tool evaluation with an honest negative result.** A separate smoke-test
project evaluated an alternative agent runner. Its findings document leads with the
statement that the narrow question is unanswered and that no answer was fabricated,
tabulates what ran versus what did not, resolves every requested model name against the
live provider catalogue, and verifies that no credential leaked into the existing
billing path. Every untested cell in its results table says "not run".

**Naming and file conventions that are consistent enough to be a system.**
Generated workflow files are prefixed by their role and suffixed by their scope.
Post-processing passes get their own suffix rather than overwriting. Dated documents
carry an ISO date in the filename. Backups carry a suffix naming the reason for the
backup, not just a timestamp. Decision and status documents are separated from
reference and architecture documents. Test files are named after the invariant they
protect rather than after the module they exercise.

**Comment discipline.** Throughout the generators and the workflow-shaping code, the
comments record the failure that motivated the line, with a date, and often the
alternative that was rejected and why. This is the single most interview-useful
property of the codebase: nearly every non-obvious decision has its reason attached.

## Scale and numbers

All from the repository. Source type given for each.

- **26 n8n workflow definition files** (content scan of all JSON in the repo for the
  n8n node schema marker).
- **490 nodes in total** across those 26 files; **137 HTTP request nodes**;
  **40 Gmail nodes** (parsed from the workflow JSON).
- **Node counts per workflow: 4 minimum, 28 maximum** (workflow JSON).
- **Roughly 12 distinct workflow shapes**; the remainder are per-client instances and
  versioned or post-processed variants (structural comparison of the workflow JSON).
- **7 generated per-client instances** of the prepare workflow, plus one consolidated
  all-clients build (file listing).
- **Retry policy: 3 attempts, 5000 ms between attempts, 300000 ms request timeout**
  (workflow JSON and the generator source).
- **13 nodes** moved from the monolith into the publish workflow by the split
  generator (named list in the generator source).
- **Execution frequency: hourly** for the content prepare workflow; **daily at a fixed
  hour** for the social mail workflow, which then decides for itself whether that day
  is the send day (schedule trigger rules in the workflow JSON).
- **Test suite: 32 files, 732 checks, green**, at engine version 71; an earlier
  recorded state was 28 files and 682 checks (resume-state document). A single
  contract test in that suite carries **37 checks** for one bug class.
- **91 Python files** within two directory levels of the content pipeline
  (file listing).
- **43 clients** in the social-media client sheet, across 5 columns
  (client sheet CSV).
- **36 clients** identified as in scope for the content pipeline, filtered from
  **197 records**, of which **8 already onboarded and 28 new**; the client setup matrix
  is **46 parameters across 37 clients** (resume-state document).
- **4 pilot clients and 12 articles** in the first live client-facing run
  (resume-state document).
- Model benchmark for a related pipeline stage: cheaper models scored **0.93** on the
  deterministic gate and **90 percent / 83 percent** on review against **59 percent**
  for the expensive baseline, at **5x to 22x lower cost**, total spend about **8 US
  dollars** (resume-state document; a dedicated benchmark package with a results
  scorecard exists in the repo).
- Related linking pipeline output: **133 links across 34 pages** for one client, and
  **105 pages / 449 links** for another at a total cost of about **0.30 US dollars**
  (resume-state document).
- Tool evaluation: **343 models** in the live provider catalogue, of which
  **27 free** (findings document).
- Root resume-state document: **308 KB, 145 second-level headings** (measured).
- **Execution volume, error rates and runtime per execution: not found in repo.**
  No n8n execution logs or metrics exports are present.
- **n8n instance count, concurrency limits and plan tier: not found in repo**, beyond
  a design note that parked executions count against a concurrency allowance.

## Technology inventory

- **n8n** (self-described as running on a hosted cloud instance): schedule trigger,
  manual trigger, webhook, wait-resume-on-webhook, HTTP request, Code, Set, IF, Filter,
  Split Out, Split In Batches, No-Op, Sticky Note, Gmail, Google Drive, Google Sheets,
  Airtable, Execute Command. Workflow static data used for cross-execution state.
- **Python 3.10** for all workflow generators, the content engine, the readiness and
  reset tooling, and the test suite. `argparse`-driven CLIs throughout; `pytest`.
- **Node.js** for the pre-import workflow validator and for a harness that executes the
  generated workflow JavaScript against a stubbed n8n context.
- **JavaScript** inside n8n Code nodes, generated from Python templates.
- **WordPress** as the publish target, reached through a custom bridge plugin
  (versioned to 1.5 in the repo) plus REST metadata helpers; ACF and a page-builder
  plugin both handled as distinct content shapes.
- **Airtable** as the client-facing record system; **Google Sheets** (published CSV
  export, no credential) and **Google Drive** as content and asset sources;
  **Gmail** for delivery.
- **Fly.io** as the engine host (inferred from the URL pattern the generators validate
  and rewrite).
- **Docker** (a dockerignore file is present at the pipeline root).
- **Git** for version control, with dated and reason-suffixed backup files alongside.
- **OpenRouter** as a multi-model API gateway for the benchmarking and linking work.
- **Markdown** as the documentation substrate throughout, with YAML front matter on
  memory documents.

## Flag for verification

- **"Generated from code" needs the qualification stated above.** The strongest true
  version is: four generators plus one post-processor produce and maintain the
  workflows in production use; the hand-built ancestors they were derived from are
  retained in the repo as history. Claiming all 26 were generated would not survive a
  look at the file dates.
- **"20+ workflow definitions" is literally true but should be paired with the
  distinct-shape count.** An interviewer who opens the directory will see seven
  near-identical per-client files and several `.ready` / `.retry` / `v2` / `v3`
  variants. Leading with "26 definitions, about 12 distinct shapes, 7 of them generated
  per-client instances" is both stronger and safer than the bare count.
- **"Orchestrating the pipeline end to end" is accurate for the content pipeline** but
  the candidate should be ready to say that the heavy lifting is in an HTTP engine and
  n8n is the orchestrator, not the processor. 137 of the 490 nodes are HTTP calls out
  to that engine.
- **The candidate must be able to explain the approval-gate mechanics cold**, because
  it is the most distinctive design decision: why a parked execution holding one resume
  URL made per-client batch approval impossible, and how moving the gate from a running
  process to a stored record on each page solved it. This is the single most likely
  deep-dive question.
- **Idempotency claims should be stated as designed-for, not proven.** The code asserts
  that generate overwrites, publish updates by tracked id, and init returns the existing
  record. There are tests, but there are no execution logs in the repo demonstrating
  retry behaviour under real transient failure.
- **No production execution metrics exist in the repo.** Avoid any claim about uptime,
  executions per day, success rate or volume processed. The only volume evidence is the
  client counts and the first-run article count.
- **The test-suite numbers come from the resume-state document, not from a captured
  test run.** They are consistent across two dated entries in that document, but the
  candidate should be prepared to say they are self-reported figures.
- **Some workflow files are historical and one is described as never having been run.**
  If asked which workflows are live, the honest answer is the prepare workflow, the
  publish-on-decision webhook workflow, and the social monthly mail; the third publish
  route is built and reviewed but had not been executed as of the last resume state.
- **The linking-pipeline and benchmark numbers belong to adjacent projects in the same
  repo, not to the n8n work.** Do not let them migrate into an n8n bullet.
- **The candidate should not claim the retry policy was designed up front.** The code
  says plainly that it was added after an incident in which zero HTTP nodes had retries
  configured. That is a better story told honestly than inflated.
