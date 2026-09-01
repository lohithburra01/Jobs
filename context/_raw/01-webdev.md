# Web_Dev content pipeline - capability notes

Source: a production repository containing a multi-tenant SEO content generation, quality-gate, preview, approval and publishing pipeline for a portfolio of law-firm clients on WordPress, plus a model benchmark harness and a security audit trail. Client names, domains, person names and secrets are deliberately omitted. Numbers are cited to the kind of file they came from.

## Systems built

### 1. The publishing engine (multi-tenant, config-driven, HTTP-exposed)

Problem: an agency was hand-converting approved Google Docs into WordPress posts for a portfolio of law-firm clients. Each conversion meant running a manual JSON-import routine, eyeballing SEO fields, uploading a featured image, setting the SEO plugin's focus keyword, choosing a category, and emailing the client for approval. It did not scale, and the recurring defects (focus keyword not reflected in the page, missing featured image, wrong template) were caught by a human looking at an already-live page.

Architecture end to end:

- **Config layer.** One `clients.json` holds every per-client setting. It stores only environment variable NAMES, never secret values; a loader resolves each name against the process environment first and a local dotenv file second, so the same code runs on a laptop and in a container with no secrets in the image. It raises loudly at load time when a secret required by the client's chosen publish method is absent, rather than failing deep inside a network call.
- **Source/trigger layer.** An Airtable module lists rows that should fire the pipeline for a client, filtered by client, content level, row type and status, with cursor pagination, and maps each row into a uniform item dict the rest of the pipeline understands.
- **Generation stage.** An LLM call converts approved document text into a flat ACF field object (SEO fields, H1, overview bullets, body, up to 15 FAQ pairs). The document is first cut into sections, because one client document carries the website blog post plus a lawyer-directory article plus sometimes a business-profile post; only the blog section is sent to the model and the rest is kept as a sidecar for the client dashboard.
- **QA stage.** A deterministic validator (no model involved) runs ten check families and classifies findings as ERROR or WARN. Any ERROR halts the item.
- **Assemble stage.** Renders a preview that looks like the client's own website by cloning a saved shell of one of their real published articles: their head and theme CSS, header, nav and footer are kept, all scripts stripped so tracking never fires on a review page, a base href injected so nav and logo assets resolve, lazy-loaded theme images de-lazified, and the post-content region replaced with the generated article in that client's brand tokens. The featured image is embedded as a data URI so the injected base href cannot hijack it.
- **Publish stage.** Two routed publish methods behind one interface: standard WordPress REST with application-password Basic auth, and a custom WordPress plugin bridge that carries the secret in the request body (needed because some hosts strip the Authorization header, so REST auth returns a not-logged-in error). Both upload the featured image, create or update the post, set the SEO plugin's focus keyword, title and meta description, attach a category, and for ACF clients write the template's ACF fields plus the taxonomy term that triggers the styled blog template.
- **State store.** One JSON record per (client, item) holding status, per-stage results, WordPress post and media ids, the Airtable record id, approval gate state and notification timestamps. Written atomically (temp file in the same directory, fsync, rename) under a re-entrant process lock.
- **HTTP surface.** A standard-library-only HTTP server exposes every stage as an endpoint so a hosted n8n instance can drive the engine over HTTP. Token-authenticated for internal routes; HMAC-signed per-item links for client-facing routes.

Triggering: an hourly n8n schedule for the prepare workflow, an n8n webhook for the client-decision workflow, a manual run for the already-approved backfill workflow. Every stage is also a CLI subcommand for operator use. Produces: a live WordPress post on the client's own site with SEO meta, featured image, category and correct template, plus a branded preview page, plus an updated Airtable row.

### 2. The three-workflow approval choreography (n8n plus engine)

Problem: the first design parked an n8n Wait node inside the per-post batch loop, so a client with four pending pages received one preview email and pages two to four were never generated until page one was decided. The requirement was that a client receives all their pending pages at once. Parked executions also consume the hosted n8n concurrency allowance.

- **Workflow A, prepare and ask** (scheduled): read trigger rows; per item generate, QA, assemble, arm an approval gate on the engine. After the loop, group by client and send one summary email per client linking to that client's dashboard. It never changes the Airtable status; the row stays waiting until the client acts. 19 nodes.
- **Workflow B, the client decided** (webhook): on approve, flip the Airtable status, publish, run post-publish housekeeping, send a "your page is live" email, flip the status again. On reject, internal email only. 16 nodes.
- **Workflow C, already approved** (manual): reads rows a human already marked approved, then generates, QA-checks, assembles, publishes, emails. No gate is ever armed, and that absence is the fingerprint distinguishing this route. 20 nodes.

The engine replaced n8n's per-execution resume URL with a stored static webhook URL, because a frozen execution can only hold one pending approval while the dashboard design needed several open at once. Made backward compatible on purpose: a caller still sending a per-execution resume URL is honoured exactly as before, so rollback is an n8n-side toggle rather than a redeploy.

### 3. Quality gate (deterministic, model-agnostic)

Ten check families: required fields present; SEO length rules; focus keyword actually reflected in H1 and SEO title; leftover un-converted markdown (bold, headings, links); whitespace junk; FAQ question/answer pairing; blog variant A/B consistency; soft-hyphen misuse in body and SEO fields; encoding artifacts from document export; and an output-language check. Exit code 0 on no errors, 1 otherwise, so it gates a workflow branch. It validates the JSON, not how it was generated, so swapping the model does not invalidate the gate.

### 4. Layered write-safety around a shared live business system

The agency's Airtable base is the operational heart of the business and is hand-edited daily by
several people, so the pipeline's write surface was designed as a perimeter and then documented as
one in a plain-English memo written for the non-technical stakeholder. Six guards stand in front of
the single write function, in order: a kill-switch environment variable (read-only by default); a
per-client field allow-list; a per-field value allow-list; a provenance check requiring the record
id to have been read by this run's own trigger query or to be stored on one of this client's own
status records; a per-run write cap; and an audit entry recording old value to new value. The audit
is verified writable BEFORE the change is made, on the reasoning that a write that cannot be
recorded must not happen. There is deliberately no code path that can create a record, delete a
record, or touch schema, and the recommended token scope has no schema permission, so structural
damage is impossible at the API level rather than merely unlikely.

Three further content-level guards sit on the same chokepoint. Transactional landing pages are
identified by row type and refused at every entry point including the publish call, because those
are built by hand and must never reach WordPress. An unrecognised or blank row type is a stop, not
a default, because guessing there means publishing a landing page as a blog post on a law firm's
site; a one-directional environment variable can add new blog-like types without a deploy, and
cannot turn a landing page into a publishable one. A post with no resolvable category is refused
rather than allowed to land in the site's default category, because on several of these sites the
default archive is one the blog listing does not read from, which produces an article that is live
and invisible. The exemption is explicit and per client, never inferred.

The client-facing dashboard reads through an explicit field whitelist rather than a raw row, and
asks Airtable for only those fields, so internal staff names, internal deadlines, document URLs and
project links are never sent over the wire at all.

### 5. Mail-once semantics

The prepare workflow runs hourly and the Airtable status does not move while the client is
deciding, so without a memory every run would email every client again. The memory is a per-item
notification timestamp, and the summary endpoint counts only items that lack it. A client whose
pages have all been announced drops out of the result entirely, so the run writes to nobody rather
than repeating the list. A page that is already live is additionally excluded from the count, on
the rule that the page's own status is the authority on whether anything is still open. The
stamping is opt-in per call, so the endpoint stays a pure read when opened by hand, and there is a
matching unmark for the case where the mail node fails after stamping.

### 6. Client-facing preview, edit and approval dashboard

Server-rendered, no client-side scripting required because the page is opened from an email and screenshotted. Lists the client's pending pieces rather than dropping them straight into a preview; approved pieces move to a completed section with a link to the live page. The preview carries an action bar: approve, edit in page, save. Save posts back to the engine, which versions the pre-edit state, applies only fields that already exist in the JSON (a client can change content, not inject new keys), and re-renders immediately. Edit revisions are capped per item.

### 7. Site self-discovery and readiness gating

Rather than hand-configuring each new client, the engine asks the client's own public WordPress REST API what it has: registered taxonomies, the term that triggers the styled blog template, and the real category list. Explicit configuration always wins; discovery only fills gaps and reports "nothing found" rather than guessing. Cached per client with a 24-hour TTL so it stays off the critical path, and a failed probe never blocks a publish.

A separate pre-publish prober talks to each client's site to measure facts only a real publish used to reveal: the maximum upload size their host actually accepts (by uploading a real JPEG at a target size and deleting it again), and whether the intended slug is taken. A readiness gate then refuses any client whose setup is incomplete, naming each blocker, enforced at both the trigger and the publish call. It reuses the existing preflight checker rather than defining a second list of checks, on the reasoning that two lists drift and the pipeline ends up enforcing the one nobody maintains.

### 8. Image pipeline (vision tagging plus deterministic matching)

A shared licensed image library is vision-tagged once into a controlled topic vocabulary, cached by file id. Matching a new post is then pure text work over cached captions, so no vision call per article and only the chosen file is downloaded. A relevance floor rejects weak matches outright rather than attaching a wrong picture. An append-only ledger records which image went to which site, enforcing the rule that an image may appear on two different clients' sites but never twice on the same site. Per-client image treatment (grayscale for one client) and per-client upload limits are applied in one shared function used by both the preview and the upload, so the two cannot drift.

### 9. Content plan reader

Reads each client's plan spreadsheet to fill in the document link and WordPress category per row, replacing hand-typed document ids. Handles four real-world messes: the document address exists only as the cell's hyperlink (so the workbook is opened with hyperlinks available rather than parsed as CSV, which drops them); the header row is row 2, 3 or 4 under a merged title and an instruction blob that itself contains the header word (so headers are matched on whole normalised cells against a known-name list, not substring); no two clients name columns or tabs the same; and the join key is an unheaded column at a different index per client, found by cell shape then confirmed against record ids actually read from Airtable. Enrichment runs before the has-a-document filter, never guesses a missing column, and swallows its own errors so a plan problem cannot stop a run.

### 10. WordPress publish bridge plugin (PHP)

A custom plugin, roughly 560 lines at v1.5, exposing token-authenticated REST routes for ping, media upload, publish/update, find by slug, read back, delete, taxonomy terms, ACF field listing, host limits, and a signed time-limited preview link. The token is generated on activation from cryptographically random bytes, compared in constant time on every route, and rotatable from an admin settings page. Version history is in the plugin header: scheduling, ACF field writing plus template taxonomy plus author assignment, a read-only verification endpoint, then category attachment plus the signed preview link. That signed link is what lets the client approve the real page rendered by their own theme rather than an imitation of it.

### 11. Model benchmark harness (`_Benchmark`)

Purpose: measure whether a cheap model matches an expensive reference model on the exact tasks the expensive one did, so the winner can be wired into production. Four cases built from real project data rather than synthetic tests: link accept/reject classification graded against a human reviewer's real labelled decisions; link generation graded by a ported deterministic gate plus an LLM judge; whole-page link review graded by judge against the reference model; and keyword selection. All models route through one aggregator so a single key runs the comparison. Cost is measured from reported token usage against a per-model price table, not estimated. Dry-run mode prints the estimate and spends nothing; a real run requires an explicit confirmation flag. Output is a results JSON plus a generated HTML scorecard of quality versus cost versus latency. A second harness reproduces the full page-level review task with the real reviewer guideline as system prompt and the real review package as input, scored with the same recall method as the production comparison scripts, running calls concurrently through a thread pool.

### 12. Security audit and portfolio scan (`security`, `SECURITY.md`)

Two tracks. A credential-free WordPress version scanner passively fetches each managed site's public homepage (readme as fallback), reads the version WordPress itself publishes via generator meta and asset query strings, and scores it against a known exploit chain into exploitable, partially affected, old-but-unaffected, and patched. Written explicitly to make an earlier ad-hoc sweep reproducible, because that sweep's results were recorded but its method was not. Separately, a self-initiated adversarial audit of the team's own engine, written up as an incident record with findings, fixes and live re-probe evidence (see Hard debugging).

### 13. Operator tooling (scripts, honestly labelled)

Scripts, not systems, but the difference between a pipeline that can be tested and one that cannot: a ground-zero reset that per article permanently deletes the live page and its featured image, puts the Airtable row back to the status it came FROM (not one blanket value), clears the post id, and purges the record so the trigger stops treating the article as done, with the order documented as the safety property; an Airtable row snapshot/restore tool so a test run against the agency's live content plan is revertible; a ledger reader answering "was this firm ever told about this article" after a reset has deliberately cleared the live field; a per-client email allow-list editor that only writes config and never sends; a workflow patcher stamping a retry policy onto every engine HTTP node in an already-built n8n file while deliberately skipping email nodes; plus onboarding scaffolding, client matrix generation, shell scraping and WordPress capability probes.

## Scale and numbers

Only figures actually present in the repository, with the kind of source cited.

**Portfolio and volume**
- 10 client entries in the client config, 7 marked active (from `clients.json`).
- Defaults of 4 posts per client per month on a weekly cadence (from `clients.json` defaults).
- 671 content rows measured across nine Airtable bases, of which 140 are transactional landing pages that must never be auto-published (from a dated code comment in the Airtable source module).
- 193 client records in the accounts table, 178 carrying a main contact address (same module).
- 16 articles published across 5 clients as of one dated status file, with 3 more held back by slug collisions (from a published-pages status text file).
- 6 articles published in one dated test run through the already-approved workflow (test publish log).
- One client had 126 rows at the trigger status while the run cap was 5 (from a docstring describing a cap-ordering bug).
- 2,919 ledger event lines on the local volume copy, the large majority from one client's repeated test runs (counted from `events.jsonl`); 25 lines in the Airtable write audit log (counted).

**Caps, limits and tuned constants** (all from pipeline source)
- Max items per client per run: 10 default, 5 in production; a rehearsal at 1 exposed a cap defect.
- Airtable write cap per run: 25 records, environment-overridable. Airtable rate limit noted as 5 requests per second per base; client dashboard listing cached per client for 300 seconds.
- Edit revision retention 200 per item (disk-exhaustion guard). HTTP body cap 512 KB.
- Item id validation: lowercase alphanumeric plus hyphen and underscore, maximum 120 characters.
- Link signature: HMAC-SHA256 over `client:item` keyed by the API token, truncated to 20 hex chars.
- Featured image upload target 900,000 bytes; probe size 850,000 bytes; downscale ladder of widths 1600/1400/1200/1000/800 and JPEG qualities 82/74/66/58. Two client hosts measured returning HTTP 413 above roughly 1 MB while a third accepted a 1.2 MB file.
- Image relevance floor 1.5, chosen from the observed spread where accepted articles scored 1.5 and 6.5 and rejected ones 0.5 to 1.5, with the comment stating openly there is no clean separation at that sample size.
- Body textblock slots 10 by default, 20 for one client; up to 15 FAQ pairs; up to 5 overview bullets.
- SEO targets enforced as warnings: title 45 to 62 chars (target 50 to 60), meta description 95 to 130 (target 100 to 125), focus keyword 1 to 4 words, excerpt 30 to 75 words (target ~50).
- Site profile cache TTL 24 hours; signed WordPress preview link default lifetime 14 days.
- n8n HTTP retry policy applied by the patcher: 3 tries, 5000 ms between tries.
- Renderer version counter at 6, used so a stale cached preview re-renders itself.

**Models and cost** (generation module, tagger, benchmark results JSON)
- Production generation model: a DeepSeek Pro tier model via OpenRouter, temperature 0, reasoning explicitly disabled as a cost guard, 180 second timeout, 3 parse retries.
- Vision tagging: a Gemini Flash tier model, chosen because the text model has no vision.
- Full library vision-tagged: 213 images, 0 failures, approximately $0.20 total (project state doc; the 213 count independently confirmed by entry counts in the image index and library JSON).
- Benchmark registry of 9 models with per-million input/output prices from $0.09/$0.10 at the cheapest to $5.00/$25.00 for the reference model (`models.py`).
- Recorded run over 40 items on the link-verdict case (`results.json`): reference model $1.149 at 3.12 s mean latency and 0.525 accuracy; cheapest contender $0.0109 at 3.77 s and 0.500 accuracy; slowest contender 26.62 s mean. Structured-output parse rate 0.70 to 1.00. Accuracy across all nine models 0.375 to 0.525, reject recall 0.75 to 1.00, accept recall 0.00 to 0.15.
- Estimated cost of the full four-case, four-model benchmark: approximately $4 (benchmark README).
- Judge overhead on that run: $0.00 over 0 judge calls, because only the label-graded case was run.

**Measured agent quality on the sibling linking project** (handoff memory document)
- Reviewer decision corpus of 360 real accept/reject decisions. Automated reviewer recall against the human reviewer on the category it was built for: 12 of 32, about 38 percent. Overall including subjective calls: 27 of 61, about 44 percent. The document explicitly records that 44 percent had been quoted casually, that 38 percent is the honest number, and that the automated reviewer is not good enough to be a gate on its own.

**Security scan** (`SECURITY.md`, scanner script)
- 44 domains scanned out of an estimated 85 managed sites; list assembled from an SEO tool's project list plus extras from an earlier sweep; 54 lines in the domain file.
- Result: 2 exploitable, 3 very old but not affected by that chain, 17 confirmed patched, 22 with the version hidden and unverifiable from outside. The write-up states plainly that hidden is not patched and that coverage, not detection, is the limiting factor.
- Engine self-audit: 5 findings (1 critical, 1 high, 2 medium, 1 low), all fixed and deployed the same day, verified by a 22-of-22 local suite plus a live re-probe of each original exploit.

**Test suite**
- 33 test scripts under the QA gate directory plus 1 at the parent level, containing 715 assertion calls in total (counted). They are hand-rolled runner scripts with a shared `check()` helper and a pass/fail summary, not pytest test functions, although a pytest cache directory is present.

**Onboarding cost model** (design document)
- 49 configuration matrix rows enumerated, each classified as dies-with-the-content-plan, constant-for-everyone, already-discovered-in-code, or genuinely per-client. Stated target: roughly 14 human-answered questions per client today, reducible to 5.

## Technical decisions and tradeoffs

**Standard library over frameworks.** The HTTP engine is built on Python's `http.server` with a threading server and every HTTP client call uses `urllib`. The only third-party runtime dependencies are BeautifulSoup plus lxml (cloning the client's page shell), openpyxl (plan spreadsheets, chosen over CSV specifically because CSV export drops the cell hyperlink holding the document address), and Pillow (image treatment and downscaling). Stated reason: deployability, a small image, and identical behaviour on a laptop and in the container.

**Config over code branches, and stop over default.** The pipeline was built and proven on one client, and the recorded consequence is that everything true of that client silently became a universal default: wrong template taxonomy, wrong category, wrong image tagging, wrong textblock count, and five routes that fell back to that client when none was named. The replacement rule, stated repeatedly, is "a value we do not have is a STOP, not a default", implemented as a readiness gate rather than as defaults.

**Discovery over configuration where the site can answer.** The template-triggering taxonomy is not even named the same on every client site (three variants observed plus one site with none). The recorded reasoning is that typing per-client values does not survive client eight and the failure is silent, so the engine asks the site; configuration still wins where present.

**Two publish paths rather than one.** REST where the host passes the Authorization header, a plugin bridge with the token in the request body where it does not. The bridge also sets SEO meta server-side, so bridge clients need no extra plugin, whereas the REST path requires a must-use plugin to register the SEO meta keys (WordPress silently drops unregistered meta keys).

**Native post content, not ACF-only.** Content is assembled into editable HTML post content rather than locked exclusively into ACF fields, so later editing is ordinary WordPress editing. ACF fields are additionally written for clients whose template renders them. The consequence, handled explicitly, is that a client whose template renders both would print the FAQ twice.

**Dry run by default everywhere.** Both publish entry points build the payload and write nothing unless an explicit commit flag is passed, and going live requires a second flag on top. Write test scripts are self-cleaning (create draft plus media, verify, delete).

**Fail closed on client data, fail open on the checker.** The Airtable write path is read-only unless a kill switch env var is set, refuses any field not on a per-client allow-list, refuses any value not on that field's value list, refuses any record id the run did not itself read, caps writes per run, and refuses the write entirely if the audit log cannot be written. In contrast the readiness checker fails OPEN if the checker itself cannot run, with the reasoning written out: an unanswered question about a client is a stop, but a broken question-asker is an alarm, and refusing every client on an ImportError turns a small deployment fault into a full outage. A strict-mode env var inverts it.

**Blocking audit versus non-blocking ledger.** Two append-only logs with deliberately opposite policies. The Airtable write audit refuses the write when it cannot log, because it guards changes to a shared live business system. The event ledger swallows every error and never blocks, because a record-keeper that can stop the work is worse than none. Both write to the mounted volume as well as the code directory, after two separate incidents where a deploy discarded the code-directory copy.

**Volume-backed state over a database.** State written by one stage is read by a later stage and by a reviewer days later from an emailed link, across separate requests and redeploys. The choice was a mounted persistent volume with atomic file writes plus a process lock, with the limitation written down in two places: the lock is sufficient only because the engine is one process on one machine with one volume, and scaling to two machines requires an exclusive-create lockfile or a real database.

**Hosted n8n over self-hosted, which forced the HTTP engine.** Deciding n8n should be a managed company tool made the Execute Command and local-file nodes unavailable, which is precisely why the stages had to be exposed as an HTTP API. Recorded as a deliberate consequence, not an accident.

**Refuse a renamed slug rather than accept it, with a per-client override.** WordPress silently appends a numeric suffix when a slug is held by an invisible post (a draft or a trashed post) and reports success. Default policy: delete the page just created and hold the row with the reason recorded, because a live page at the wrong address while the client's own link points at the right one is worse than no page. A per-client `suffix` policy accepts the rename where the client does not mind. A third option, taking over the existing post, is documented as impossible with the current plugin capability rather than faked.

**An image must never cost the article, but must never be invisible either.** A failed image upload was originally fatal to the publish; changed to skip and continue, since the featured image is the easiest part to add by hand. When a client noticed a published page with no picture and the only trace was a log line, the failure was additionally recorded on the item's status record and returned in the API response.

**Same treatment code for preview and upload.** Every time the preview and the published page computed anything separately they drifted, and a preview that disagrees with the published page is described in the code as the worst version of the bug because it is invisible until a client is already looking at their live site. Image treatment, duplicate-block removal and FAQ suppression are each applied in exactly one shared place for this reason.

**Deterministic transformation over a second model call.** The variant A to variant B body split (one field versus split heading/text pairs) is done deterministically on the heading boundaries the generator already emits, with a losslessness assertion that reconstructs the original, rather than asking the model again. Sections beyond the available slots merge into the last slot with headings kept inline, because silently losing sections would be invisible content loss on a live page.

**Benchmark honesty.** The README separates the objectively-labelled case from the judge-scored cases and instructs the reader to treat the latter as directional agreement with the reference model, not truth. It records that all models run in plain configuration with no extended thinking so the comparison is apples to apples, and flags that as a limitation.

## Hard debugging

**Cross-client namespace collision.** Item ids are slugified article titles, so they are not unique across clients. Generated JSON and rendered previews were keyed by item id alone while only status records were client-scoped. Two firms with an article on the same common legal topic wrote to the same output file and the same preview file: one client's generation silently overwrote the other's, and the first client would open the link in their own email and read another firm's content inside their own site shell, while status records stayed separate so nothing looked wrong. Root cause: a shared namespace, not a shared matcher. Writes became client-scoped while reads fall back to the legacy flat path so earlier artefacts keep resolving. The same root cause had earlier produced one client's licensed stock photo appearing on another client's article, which had been fixed by gating the image matcher per client and leaving the namespace shared; the write-up says so explicitly.

**Cap applied to candidates instead of to work.** The per-client run cap was applied inside the trigger function, before the caller dropped rows already built. A client with 126 rows at the trigger status and a cap of 5 handed over the first five rows in Airtable order, the caller recognised all five as done, and the run produced nothing. Not nothing once: nothing ever, because the same five come back first on every run, and the log reads "0 items", indistinguishable from a client with nothing waiting. Found during a rehearsal with the cap at 1, where it silently zeroed four clients. Fix: split the cap into a separate function the caller invokes after filtering, with the reasoning recorded that the cap always meant "do not build more than N pages in one run", never "do not look further down the list".

**Non-deterministic JSON from the model.** Generation intermittently returned text containing a raw control character inside a JSON string value, which is illegal in JSON. Proof it was the model and not the input: the same document produced a parse failure at a different character offset on two runs minutes apart, and deterministic code cannot do that. Three-layer fix: tolerate code fences and surrounding prose when extracting the array; a targeted repair pass escaping only characters already illegal inside a string and only while inside a string, so it cannot alter document structure; and a three-attempt retry loop, because a hard failure here surfaced to a client as a generic service error and had already cost a live demo. The write-up names the real mistake as having previously logged an intermittent failure as a curiosity instead of fixing it.

**The model translated the article.** One article in roughly twenty came back with its headline, summary box and first four body sections in English on a German law firm's site. The source document was verified fully German. The model started correct, drifted through the middle of a long output, and recovered by the fifth body section, which is why the FAQ underneath was still German. The prompt already carried the rule in capitals. Two fixes: a language check inside the generator comparing source and output and raising, plus an independent check in the QA gate classified as ERROR not WARN, with the reasoning that a warning would have printed into a run log already carrying ten of them and the page would have gone out anyway. The detector is deliberately conservative, scoring on function words unique to one language plus umlauts as a positive signal and excluding words real in both, because a check that cries wolf gets switched off.

**Duplicated content blocks across three surfaces.** The FAQ appeared twice on published pages. Upstream cause: for one body variant the model puts the entire article body, including overview and FAQ, into the single body field, while the structured FAQ fields also carry it and the client's template renders both. It was patched in the preview renderer, then in the ACF publish path, and still reached a live page through the third path (a non-ACF client, where post content is the whole page). Final fix applies a heading-presence check at the source in the generator plus at the single load chokepoint every stage reads through, so pages generated before the fix are cleaned the next time anything touches them, with no regenerate.

**Cross-client link leakage.** A demo page built for one client from another client's source document carried two anchors pointing at the source client's domain inside a page branded as the first client. The other client's name appeared nowhere; only the domain did. A stripper now removes links to any other configured client's site, applied both at generation and at the shared load chokepoint.

**A guard that could not see.** The slug-rename check compared the requested slug against the slug returned by the publish response. The bridge's publish response carries a permalink but not a slug, and its read endpoint returns neither, so the first version compared None, concluded nothing was wrong, and let two clients publish at a suffixed address one deploy after the guard was written. Fix: three fallback sources ending in the site's own public REST API as authoritative, with None meaning "we genuinely could not read it" and reported rather than treated as success. A second bug in the same function was caught within minutes by a test: reading the last path segment of a permalink as the slug produced "p" for a site using query-string permalinks, which then compared unequal and failed a publish that was fine. Final rule: fail only on evidence, specifically only on WordPress's numeric-suffix rename pattern, and allow anything else with a report.

**Tracked post id pointing at a deleted post.** The publish path keeps the WordPress post id so a re-publish updates in place rather than duplicating. If the page was deleted on the WordPress side, which is what happens after a test publish is cleaned up, the update targets a dead id and the site answers a 500 forever for that item. Fix detects that specific error code, drops the stored id and creates fresh, with the reasoning that it cannot duplicate anything because the post it would have duplicated is gone.

**Lost update under a threading HTTP server.** Status mutation functions read a record, mutate it and write it back; two interleaved requests silently discarded the first one's field. An atomic file replace does not fix this, only holding a lock across the whole read-modify-write does. Separately on Windows, concurrent atomic renames onto one destination raise a permission error, and the recorded measurement is that serialising took the test from 58 raised writes to 0. A re-entrant lock was used because the update helper holds it and then calls the writer, which takes it again.

**Approval double-click race.** A compare-and-set helper moves the approval state from pending to deciding under the lock and returns true only for the winner. At the time it was written the race was already absorbed by n8n's per-execution resume URL being single-use, and the docstring records that it becomes the only protection once that is replaced by a static webhook accepting unlimited calls, where two clicks would mean two publishes and two "your page is live" emails to a real client.

**A guard that was inert for weeks.** The engine imports the preflight checker inside a stdout redirect to a string buffer, which has no reconfigure method, so an unguarded encoding call raised an AttributeError at import time. The readiness gate treats an import failure as "the checker is broken, allow and shout", so the publish-time readiness gate had been silently inert on every API call since it was built. Recorded conclusion: a guard that cannot run is worse than none.

**Audit logs discarded by deploys, twice.** Both the image ledger and the Airtable write audit log were written only next to their module, which inside the container image means every deploy threw them away. The cost landed when the pre-publish Airtable statuses of sixteen live pages turned out to be unrecoverable, because the only record of old-to-new had been wiped. Both now write to the mounted volume first and the code directory second, and neither raises on failure.

**Cleared records are not empty records.** Every reset variant cleared fields, but a cleared record is still a record, and the trigger treats any article it has a record for as already built. Fifteen articles built once and never sent were therefore invisible permanently. A purge endpoint deletes the record outright, token-gated, refusing while the record still points at a live page, with the correct order documented: delete the page, clear the id, then purge. Deleting the record first strands the page on the client's site with nothing knowing about it, the next run republishes, WordPress refuses the taken address, and the article is blocked, which is the exact state three articles sat in for over a week.

**Gates left armed on published pages.** Eight pilot pages were published by the backfill workflow while the prepare workflow still had an approval gate armed on them, so the approve button in the client's inbox stayed live on a page already on their website; pressing it would republish and send a second "your page is live" email. Cause fixed at source (a requeue no longer arms a gate), plus a deliberately narrow disarm endpoint that clears the gate and nothing else and refuses a page that is not published, because cancelling a real outstanding client decision is not that endpoint's job.

**Reverted fix nobody recorded.** An audit found that a fix preventing published pages from being counted as "waiting" in the client summary email had been committed and reverted 24 minutes later, with no document anywhere recording the revert or its reason, so the defect existed only in git history. At audit time five live pages still carried the pending flag, and enabling client email would have told a client that seven texts were waiting that were already live on their site. It was restored deliberately, with the two halves of the original commit separated so only the independently-correct half was reinstated.

**Security self-audit (five findings, one day).** Severities as assessed at discovery:
1. Critical. The edit endpoint was intentionally unauthenticated because reviewers open it from an email and hold no token. Combined with a publish path inserting the pipeline's HTML verbatim with WordPress HTML filtering disabled, the chain was: guess a slug, rewrite the body of a post awaiting approval, a human approves a page that looks fine, arbitrary HTML publishes to a live client site. Slugs are not secret: they are SEO keyword phrases that travel in preview links in client inboxes.
2. High. Path traversal, read and write, through an unsanitised item parameter flowing straight into path construction. Proven live read-only against the deployed service; proven write locally in a throwaway directory, never against production. Bounded to files of the right extension and to keys already present in the target, but the client config is such a file and its existing keys include the publish target.
3. Medium. Authentication failed open when no token was configured, so a lost or mistyped secret would have silently made the whole API world-writable with only a startup log line.
4. Medium. Unbounded writes and no body cap, a trivial disk-exhaustion path onto the volume holding the only copy of reviewer edit history.
5. Low. Unpublished client content world-readable by slug guessing.

Stated root cause: all five were safe while the engine ran on loopback behind a temporary tunnel, and deploying to a permanent public URL changed the threat model while the endpoint design did not change with it. Recorded lesson: when something moves from local to public, re-audit its whole surface, because "it was fine yesterday" is a statement about the network, not the code.

Fixes: strict slug validation enforced at the HTTP layer AND inside the function that actually writes, so the CLI and any future caller are covered; HMAC-signed per-item links replacing open-by-slug access, derived from the existing API token so there is no new secret to manage and one leaked link never exposes another post, with the engine minting the links because the workflow cannot compute the signature; refusing to start at all when bound to a non-loopback address without a token; a body size cap and a revision count cap; and a pinned public base URL so a spoofed Host header cannot redirect a reviewer's emailed link. Verified by a 22-check local suite in a throwaway data directory including re-running the proven traversal exploit, and by a live re-probe of every original exploit after deploy showing previously-succeeding requests refused while the legitimate reviewer flow still returns 200. Also verified clean in the same audit, and the reason finding 2 did not escalate: no secrets tracked in git, and the container ignore file excludes the environment file and generated ready-to-import workflow files, so the API token and WordPress credentials are not baked into the image and could not be read via the traversal.

## Technology inventory

**Languages**: Python 3.11 (engine, pipeline, tooling, benchmark), PHP (WordPress plugins), HTML/CSS/JavaScript (server-rendered previews, dashboards, email templates), shell (container entrypoint), JSON and JSONL (config, state, workflow definitions, ledgers), Markdown (specs, runbooks, incident logs).

**Python standard library, used deliberately in place of frameworks**: `http.server` with `ThreadingHTTPServer`; `urllib.request`/`error`/`parse`; `json`; `hmac` and `hashlib` (HMAC-SHA256, constant-time compare); `base64`; `pathlib`; `threading.RLock`; `tempfile` plus `os.replace` and `os.fsync` for atomic writes; `contextlib.redirect_stdout` for per-request log capture; `argparse`; `re`; `datetime`; `concurrent.futures.ThreadPoolExecutor` (benchmark); `mimetypes`.

**Third-party Python**: beautifulsoup4 and lxml (HTML shell cloning and manipulation), openpyxl (spreadsheet reading with hyperlink targets preserved), Pillow (resize, JPEG re-encode, grayscale).

**APIs and external services**: Airtable REST API v0 (filterByFormula, offset pagination, field projection, PATCH single-field updates, personal access tokens scoped to record read/write on one base with no schema scope); WordPress REST API v2 (posts, media, categories, taxonomies, users) with application-password Basic auth; a custom WordPress REST namespace from the in-house bridge plugin; Google Docs public export endpoint (text and HTML); Google Drive anonymous download by file id for the shared image library; Google Sheets via xlsx export; OpenRouter as the LLM aggregator; Gmail nodes in n8n for client and internal email; an SEO analytics tool consumed as an MCP for dashboard snapshots, explicitly snapshot-based because an MCP is not reachable from a server process.

**Models**: a DeepSeek Pro tier text model for document to structured JSON generation; a Gemini Flash tier vision model for image tagging; a Claude Opus tier model as benchmark reference and LLM judge. The benchmark registry additionally covers GLM, Kimi, Qwen and MiniMax families.

**WordPress ecosystem**: ACF field groups and `update_field`; a Rank Math style SEO plugin's post meta; Elementor-based themes (selector-driven content region replacement); an author taxonomy plugin; a must-use plugin registering SEO meta keys for the REST path; `kses_remove_filters`/`kses_init_filters` around content insertion; `hash_equals`; `random_bytes`; signed time-limited preview links.

**Orchestration and infrastructure**: n8n Cloud (schedule trigger, webhook trigger, HTTP Request, IF, Split Out, Split In Batches, Code, Gmail, NoOp, Sticky Note nodes; workflows generated programmatically from Python builder scripts and patched in place for retry policy); Docker (python:3.11-slim, build context scoped to the app directory, seed-on-first-boot entrypoint, secrets never baked in, dockerignore excluding environment and generated files); Fly.io (Frankfurt region, shared-cpu-1x with 512 MB, persistent mounted volume, auto-stop disabled so in-flight state is never wiped, HTTP health check every 30 s with 5 s timeout, pinned public base URL); Render documented as an alternative via a blueprint file, with the note that the free tier's lack of a disk and its sleeping behaviour make it unusable for a stateful engine; Cloudflare Tunnel or ngrok for the development-time public URL.

**Security tooling and practice**: passive credential-free version fingerprinting via generator meta tags, asset version query strings and readme fallback; CVE-chain exploitability scoring; HMAC-SHA256 link signing; constant-time comparison; strict input allow-listing by regex; host allow-listing with exact-or-dot-suffix matching (explicitly not substring); fail-closed authentication; append-only audit logging with pre-write verification; kill-switch environment variables; per-field and per-value write allow-lists; provenance checks binding writes to records the run actually read.

**Testing**: 33 hand-rolled runner scripts with a shared assertion helper, exercising the real selection and state code against fake network layers and a temporary data directory. Fakes stand in for the network only, never for the project's own logic, stated as a design rule. Coverage includes concurrency (racing writers, racing approval claims), namespace isolation, path traversal refusal, permutations of hand-editable Airtable states, mail-once behaviour, category guards, page type guards, language gating, image floor reassignment, ledger persistence, and a flow contract test.

## Flag for verification

1. **Ownership boundary.** Much of this repository is written in a distinctly reflective, post-mortem voice with dated attributions to named colleagues, and it contains an agent-workflow specs directory and session artefacts. Before claiming sole authorship, confirm which parts were hand-written versus produced with heavy AI assistance. The defensible framing is likely "designed, directed and verified" rather than "hand-wrote every line".
2. **"Production" scale is modest.** The strongest volume evidence is 16 published articles across 5 clients, 7 active client configurations, and a default of 4 posts per client per month. Do not let "portfolio of law-firm clients" imply thousands of articles. The 671-row and 193-client figures describe the agency's Airtable, not what the pipeline processed.
3. **The 1000-client design document is a design, not a system.** The 49-row matrix and the "5 questions per client" target are a written plan. Claim it as architecture thinking, not delivered scale.
4. **Benchmark results are weak and were run narrowly.** The recorded results JSON covers ONE case at 40 items, and every model including the expensive reference scored between 0.375 and 0.525 accuracy with accept recall at or near zero, which is close to a degenerate always-reject classifier on a class-imbalanced set. The harness design is defensible; the result is not evidence any model performed well. Be ready to say what the numbers actually show and why the case turned out to be badly posed.
5. **The 38 percent reviewer-recall figure belongs to the sibling internal-linking project**, not to this pipeline. Do not attribute it to the publishing engine.
6. **Test suite shape.** These are runner scripts with a `check()` helper, and there is no CI configuration in the repository. "715 assertions across 33 test scripts" is accurate; "a 715-test pytest suite running in CI" is not.
7. **The security incident on a client site was not caused by, or fixed by, this code.** The WordPress core compromise was a third-party vulnerability handled by the web dev team; the contribution here was the credential-free portfolio scanner and the write-up. The engine self-audit IS own work and is the stronger of the two stories.
8. **Path traversal write was proven locally, not in production.** The security log is careful about this; any claim should be too.
9. **Benchmark judge claims** rely on an expensive model as gold standard, which measures agreement, not truth. The README says so; the candidate should too.
10. **Some described behaviour is aspirational or partially wired.** The draft stage explicitly holds rather than performing a live write. The post-publish stage stamps status and delegates the actual search-console indexing, analytics tracking and sheet updates to n8n nodes. The SEO dashboard section is a manually refreshed snapshot, not a live integration, by explicit design. Do not describe these as fully automated integrations.
11. **The client email path had two locks and a documented mark-then-fail gap.** A summary can be marked as sent before the email node fires, with a manual unmark as the remedy. If asked about delivery guarantees, that is the honest answer.
12. **Cost figures.** The approximately $0.20 image tagging figure and approximately $4 full benchmark estimate come from project notes and a README, not metered billing. No per-article generation cost is recorded anywhere. If asked what an article cost to generate: not found in repo, but the model, temperature and disabled-reasoning settings are known and it could be computed from the price table.
13. **Latency and error rate.** No end-to-end pipeline latency measurement and no publish error rate are recorded. The only latency figures are per-model benchmark call latencies. Not found in repo.
14. **Rollout status.** Several documents describe the pipeline as still gated, with client email behind a master switch plus a per-client flag, and several clients pre-staged but inactive. Present it as a pilot that published real articles to real client sites, which is true and strong, rather than as a fully autonomous production system.
