# Landing page generation pipeline (client onboarding automation)

Source: a private repo containing n8n workflow exports, a Next.js 16 application, prompt
files, an Airtable schema document, a presentation deck in two languages, speaker notes,
and a briefing transcript. Built as a live case study during an interview process for a
DACH marketing agency serving law firm clients, and demoed to a Managing Director.

All client identifiers, credentials, webhook URLs and raw prompt text are deliberately
excluded from these notes. Findings below are drawn from reading the code.

## The system (end to end architecture)

**Trigger layer.** A single n8n webhook node listens on a POST path for questionnaire
submissions. The exported workflows are configured for a Tally form as the source, with
response mode set to "last node finishes" in the generation workflows so the caller
receives the workflow output synchronously. A second, separate workflow exposes a lead
capture webhook that responds immediately on receipt.

**Normalisation.** The first Code node after the webhook flattens the form payload into a
flat questionnaire object. The most developed version of this node handles three input
shapes in one branch: a Typeform answers array keyed by field ref, a Tally fields array
keyed by label, and a plain flat JSON body. It maps German questionnaire labels to
English-ish schema keys, splits multi-line text fields into arrays, coerces yes/no answers
to booleans, parses an integer for years of experience, and builds a URL slug from the firm
name. The slug builder transliterates German umlauts and the sharp s before stripping
non-alphanumerics and truncating to 60 characters, which is the detail that makes the
route work for real German firm names.

**State creation.** An Airtable node (or an equivalent HTTP request to the Airtable REST
API in the import-ready variant) creates one row in a `Firms` table with the firm name,
slug, practice area, city, phone, email, and status set to `Generating`. The record id
returned here is referenced by later nodes through n8n's node-reference expressions.

**Generation.** One HTTP request node calls an LLM with a German system prompt and the
questionnaire JSON as the user message. Timeout is set to 120000 ms. This is a single call
that produces the entire page content, not one call per section.

**Response parsing and validation.** A second Code node pulls the text out of the provider
response envelope, attempts `JSON.parse`, and on failure retries after stripping markdown
code fences (a defensive step for the case where the model wraps output despite the
instruction not to). It then checks the parsed object against a hard-coded list of eleven
required top-level keys and throws if any are missing, which surfaces in n8n as a failed
execution rather than a silently broken page. The import-ready variant additionally
back-fills two optional presentation-only blocks (a hero image and a gallery/reviews block)
with placeholder values if the model did not emit them, so the demo page never renders
half-empty.

**State update.** The parsed content is stringified and written back to the same Airtable
row into a long-text `content` field, and the status flips to `In Review`.

**Notification.** The two labelled generation workflows end with a Gmail node that emails
an internal reviewer an HTML message containing a button linking to the preview URL for
that slug. The import-ready variant replaces that node with a Code node that returns a
JSON body containing the firm name, slug, Airtable record id, preview URL and prospective
live URL, so a curl or PowerShell caller receives the link directly in the HTTP response.

**Rendering.** The Next.js application is a single deployed codebase with two dynamic
routes: `/[slug]` for the public page and `/preview/[slug]` for the review copy. Both are
async server components that call a slug lookup helper. That helper queries Airtable with
a `filterByFormula` on the slug, caps the query at one record, maps the row into a typed
record, and JSON-parses the stored content blob inside a try/catch. If Airtable is not
configured or the row is absent, it falls back to an offline sample record for one known
demo slug, so the demo URL cannot break during a presentation. The public route additionally
gates on status and returns a 404 unless the record is `Live` or `Approved`. The public
route also implements `generateMetadata`, pulling the model-generated page title and meta
description into the document head.

**Page composition.** A single `LandingPage` component composes fourteen section components
in fixed order: top bar, hero, why-choose-us, reviews, services, process, expertise, local
factors, team, gallery, success stories, FAQs, contact, footer. Two of those (reviews and
gallery) render only when the corresponding optional key is present and non-empty, so a
sparse record degrades gracefully instead of rendering an empty band.

**Review actions.** The preview route mounts a client-side review bar above the page. It
holds local state for idle, submitting, approved, changes-requested and error, and posts to
an internal API route with either an approve action or a request-changes action carrying a
free-text feedback string.

**API routes.** Two route handlers exist, both pinned to the Node runtime. The approve
route validates the JSON body and the presence of a firm id, then branches: on approve it
sets the Airtable status to `Live` and, if a publish webhook URL env var is present, fires
a POST to n8n with the firm id and an approval timestamp, with the fetch error caught and
logged rather than thrown. On request-changes it requires non-empty feedback, sets status
back to `Generating`, and posts the firm id plus feedback to a regenerate webhook URL if
configured, otherwise logging to console. The lead route validates required fields and
forwards the submission plus a server-side timestamp to a lead webhook, returning a
log-only mode response when no webhook is configured and a 502 when the forward fails.

**Lead loop.** The lead capture workflow in n8n receives that forward, creates a row in a
`Leads` table linked to the firm record, reads the firm row back to get its contact email,
and sends the firm an HTML notification containing the enquirer's details.

## Claim verification

**Questionnaire submitted: CONFIRMED IN CODE.** A webhook trigger node exists in three of
the four workflow exports, with a parser that handles Tally, Typeform and flat JSON shapes.
A dummy submission payload with 18 labelled fields is committed for testing, plus a
PowerShell one-liner that posts it. Caveat: the form itself is not in the repo, and every
workflow export is saved with `active` set to false, so the exports alone do not prove a
live production trigger.

**Eleven sections generated by the LLM: CONFIRMED IN CODE.** The validation array in the
parse node lists exactly eleven required top-level keys (meta, header, why choose us,
services list, services detailed, process, expertise, local factors, team, success stories,
FAQs), and a missing key throws. The same eleven keys appear in the TypeScript content type,
in the prompt file's schema block, and as the top-level keys of a committed real generation
output. Worth stating precisely in interview: eleven content keys from the model, fourteen
rendered section components, because the top bar and footer are derived and the reviews and
gallery blocks are not model-generated.

**Next.js page deploys to Vercel: PARTIAL.** The app is a Next.js 16 / React 19 project
with Tailwind 4, targeted at Vercel, and the workflows build preview and live URLs on a
Vercel domain. But there is no per-client deploy anywhere in the repo: no Vercel deploy hook
call, no Vercel API node, no CI config, no `generateStaticParams`. One pre-deployed app
serves every client through a dynamic route that reads Airtable at request time. The
accurate claim is "a new page becomes reachable as soon as the row exists", not "a page is
deployed per client". That is a stronger architectural story anyway, and it is what the deck
argues for against the prior WordPress-per-client approach.

**Preview link reaches the client inbox within 30 seconds: NOT FOUND.** Two things do not
hold. First, no 30 second figure appears anywhere in the repo. The deck claims about 40
seconds from webhook to finished preview URL and describes it as measured in the live
prototype; the n8n setup guide and the deck's demo walkthrough both say about 60 seconds;
the speaker notes and the AI explainer document say 60 to 90 seconds. There is no timing
instrumentation in any code path, so no figure in the repo is substantiated by code. The
only hard timing constant is the 120000 ms HTTP timeout on the model call. Second, the
recipient is an internal reviewer address, not the end client: the Gmail node in the
generation workflows sends the preview link to a reviewer placeholder, and the copy is
written for the internal team. Safe phrasing: "generation to reviewable preview link in
under a minute in the demo run".

**Feedback form routes to Airtable: PARTIAL.** Two feedback-ish flows exist and only one
reaches Airtable. Lead form submissions from a live page do reach Airtable, through the API
route into the n8n lead workflow into a `Leads` table, and that path is fully wired.
Reviewer change requests do not reach Airtable in the committed code: the approve route sets
status back to `Generating` and forwards the feedback text to an n8n webhook, but the only
Airtable write helper exported by the data layer updates status. The Airtable schema document
defines a `feedback` field, and a comment in the route says feedback is written to Airtable,
but no code writes it. This is a real gap and worth owning directly rather than glossing.

**Section-level regeneration: PARTIAL.** The mechanism is designed but not implemented as a
workflow. The prompt file contains an explicit clause instructing the model, when reviewer
feedback is supplied alongside the questionnaire, to apply it precisely without needlessly
altering other sections, and to return the complete updated JSON. The setup guide documents
a third workflow that reads the prior generation back from Airtable, sends it with the
feedback as context, and re-parses. No JSON export for that workflow exists in the repo, and
the return contract is the whole document rather than only the changed sections. Accurate
phrasing: "feedback-conditioned regeneration of the full content object, with the prompt
constraining the model to leave untouched sections alone".

**Auto-publish on approval: PARTIAL.** Approval is a single reviewer click and it does make
the page publicly reachable, because the public route refuses to render anything not marked
`Approved` or `Live` and the approve handler flips the status to `Live`. That is a status
gate flip against the shared renderer, not a publish or deploy job. An optional publish
webhook POST fires if the env var is set, but no publishing workflow JSON exists in the repo.

## Model routing

Two providers are wired, in parallel variants of the same workflow, differing only in the
generation node and its response parser. Everything upstream and downstream is identical.

The Anthropic variant posts to the Messages API with a versioned API header, authenticating
through an n8n generic header-auth credential rather than an inline key. It sets an Opus
class model, an 8000 token output cap, and temperature 0.4. Its parser reads the text from
the first content block.

The Google variant posts to the Generative Language v1beta generateContent endpoint with a
Flash class model. It splits the prompt into a `system_instruction` block and a user content
part, sets temperature 0.4, a 16384 token output cap, and critically sets the response MIME
type to `application/json`, which is provider-level enforcement of JSON output rather than
prompt-level pleading. Its parser reads the text from the first candidate's first part.

Why two variants: the setup guide states the split plainly. The Flash model is the demo path
because it runs on a free tier and needs no Anthropic key, and the Anthropic path is the
production recommendation for German legal copy quality. The prompt file's parameter table
argues the same tradeoff, and the deck carries a cost-per-generation table putting the demo
model at effectively zero and the production model in the single-digit-euro-cents range.
Those cost figures are estimates in a document, not measured spend.

Structured-output enforcement operates at three layers, which is the interesting part:

1. **Prompt level.** The system prompt ends with an explicit instruction to answer with
   valid JSON only, no markdown, no fences, no preamble, starting at the opening brace. It
   then inlines the full target schema with per-field type and length annotations. It also
   carries hard cardinality rules (exactly three trust bullets, four to six advantages, five
   to eight detailed services, exactly three process steps, four to five local factors,
   exactly three success stories, eight to ten FAQs) and hard character limits on the SEO
   title, meta description, headline, trust bullets and CTA label.
2. **API level.** The Google path additionally sets a JSON response MIME type. The prompt
   file notes deliberately that a structured-output parameter is not used on the Anthropic
   path because prompt-level instruction was sufficient.
3. **Post-parse level.** The Code node strips fences as a fallback, then validates presence
   of all eleven required keys and throws on any miss, so a malformed generation fails the
   execution loudly instead of writing a broken record.

The prompt also encodes domain safety rules that matter for legal marketing: never invent
credentials, awards, case outcomes or years of experience; emit a bracketed placeholder
token for missing mandatory data instead of guessing; never use unproven superlatives; and
if no real case studies were supplied, generate exactly three illustrative ones each flagged
with a boolean. That boolean is honoured downstream: the success stories component checks
whether any story carries the flag and renders accordingly, so the disclosure survives from
prompt to rendered page. There is also a rule forbidding the model from emitting any image,
logo or video paths, because asset URLs come from questionnaire uploads and not from text
generation. That is a sound separation of concerns and easy to defend.

## Scale and numbers

Only figures actually present in the repo, with the kind of file each came from.

- **4** n8n workflow JSON exports (repo file listing): two generation variants, one
  import-ready generation variant, one lead capture.
- **7** nodes each in the three generation workflow exports; **4** nodes in the lead capture
  export (workflow JSON).
- All four workflow exports have `active` set to **false** (workflow JSON).
- **11** required top-level content keys, validated by a hard-coded array (workflow Code
  node, TypeScript type file, prompt file).
- **14** section components composed by the page container, two of them conditional
  (component source).
- **~1,066** lines of landing section component TSX across 15 files (line count over the
  component directory).
- **18** questionnaire fields in the committed test submission payload (test fixture JSON).
- **16** fields defined for the firms table and **7** for the leads table (Airtable schema
  markdown).
- **5** workflow status values: generating, in review, approved, live, error (schema markdown
  and TypeScript union type).
- **124** flat field keys in the legacy WordPress custom-fields export kept as the reference
  target output (a sample law-firm landing page JSON in the repo root). This is the number
  that shows what the manual process used to hand-assemble.
- Prompt hard limits: SEO title **60** characters, meta description **155**, headline **90**,
  exactly **3** trust bullets at **60** characters each, CTA label **50** (prompt markdown).
- Prompt cardinality: advantages **4-6**, detailed services **5-8**, process steps exactly
  **3**, local factors **4-5**, success stories exactly **3**, FAQs **8-10** (prompt markdown).
- One committed real generation output produced: **8** listed services, **6** detailed
  services, **3** process steps, **4** local factors, **2** team members, **3** success
  stories, **9** FAQs (test output JSON). All within the prompt's stated bands.
- Model call parameters: temperature **0.4** on both providers; output cap **8000** tokens
  on the Anthropic path and **16384** on the Google path; HTTP timeout **120000** ms
  (workflow JSON).
- Airtable list queries capped at **50** records; slug lookup capped at **1** (data layer).
- Timing claims, none instrumented in code: **~40 seconds** webhook to finished preview URL,
  described as measured in the live prototype (deck); **~60 seconds** (n8n setup guide and
  the deck's demo walkthrough); **60-90 seconds** (speaker notes and the AI explainer doc).
- Business-case figures, all estimates in the deck rather than measurements: **~4 hours** of
  team time per page manually versus **~10 minutes** of review, and **~40 hours** saved per
  ten onboardings.
- Per-generation model cost: an estimate table in the explainer doc, not measured spend.
- Time-to-live end to end: not found in repo as a measured figure.
- Number of real client firms processed in production: not found in repo.

## Technical decisions and tradeoffs

**One codebase, N clients, dynamic routes.** The prior process spun up a WordPress install
with a custom-fields JSON import per client. Replacing that with a slug-routed Next.js app
reading one row per client from Airtable removes per-client infrastructure entirely and makes
a template change a single deploy for every client. The tradeoff, argued explicitly in the
deck, is that the agency gives up per-client CMS autonomy; the deck answers this by noting
the same pipeline could instead POST the finished custom-fields JSON into the existing
WordPress estate, keeping the automation and the incumbent infrastructure.

**Airtable as state machine rather than as database.** One row per client carries the status
enum, the full generated content as a JSON string, contact fields and asset attachments. The
status field is the actual gate on publication, since the public route refuses to render
anything not approved. This makes the audit trail free (Airtable tracks field history) and
makes the reviewer's action a one-field write. The tradeoff is a stringified JSON blob in a
long-text field, which cannot be queried by content and must be parsed defensively on every
read, which the data layer does inside a try/catch with a fallback.

**Preview is the real page, not a document.** The review surface is the production renderer
with a fixed action bar overlaid and search indexing disabled through route metadata,
removing format drift between what a reviewer approves and what ships. That drift was the
failure mode of the previous document-based review step.

**Human gate is structural, not procedural.** Nothing publishes on a model output. The status
check lives in the public route itself, so no code path lets the LLM change status.

**Graceful degradation everywhere.** Optional sections are conditionally rendered rather than
rendered empty; the slug lookup falls back to an offline sample when Airtable is unreachable;
both API routes fall back to console logging when their webhook env vars are unset; the JSON
parse retries after fence-stripping; the content parse falls back to sample content. Every
one of these is a demo-robustness decision, and each is a small liability in production
because a fallback that silently succeeds hides a real outage. That is the honest read.

**Two provider variants kept in parallel rather than one abstracted node.** Duplicating the
whole workflow per provider rather than parameterising it is the pragmatic n8n choice, since
request and response envelopes differ between providers and n8n has no clean interface layer.
It costs drift risk: the two variants must be edited in lockstep, and the repo already shows
that drift, since the import-ready variant gained placeholder back-filling that the labelled
variants never received.

**Inline credentials in the import-ready workflow.** That variant hard-codes an Airtable
token and a Google API key directly into node parameters instead of using n8n's credential
store, which the labelled variants do use correctly. This is a demo-speed shortcut with a
real security consequence, and any reuse of this material must strip and rotate those values
first. Worth raising proactively in an interview rather than being caught by it.

## Technology inventory

- **Orchestration:** n8n (webhook, Code, Airtable, HTTP Request, Gmail nodes; expression
  based cross-node references; execution order v1).
- **LLM providers:** Anthropic Messages API and Google Generative Language generateContent,
  both called as raw HTTP requests rather than through provider nodes.
- **Structured output:** prompt-embedded JSON schema with length and cardinality constraints;
  provider-level JSON response MIME type on the Google path; required-key validation in a
  post-parse Code node.
- **Front end:** Next.js 16 App Router, React 19, TypeScript 5, Tailwind CSS 4, lucide-react
  icons, `next/image` with a remote-pattern allowlist.
- **Server:** Next.js route handlers pinned to the Node runtime; async server components;
  `generateMetadata` for per-client SEO tags.
- **Data:** Airtable via the official JS SDK in the app and via REST in one workflow variant;
  `filterByFormula` queries; typed record mapping.
- **Hosting:** Vercel.
- **Forms:** Tally as the primary questionnaire source, with Typeform payloads supported by
  the same parser.
- **Email:** Gmail nodes in n8n for reviewer notification and lead forwarding.
- **Tooling:** a standalone Node ESM script that fires one generation call and prints a
  section-by-section validation summary plus token usage; a second script that seeds the
  Airtable base from committed sample content; a PowerShell script that fires the demo
  webhook and opens the returned preview URL.
- **Presentation:** Marp markdown decks in German and English with generated PDF and PPTX,
  plus timed speaker notes.

## Flag for verification

- **The 30 second figure does not exist in the repo.** The repo's own numbers are about 40
  seconds (deck, claimed as measured), about 60 seconds (setup guide), and 60 to 90 seconds
  (speaker notes and explainer). Nothing in code measures it. Use "under a minute in the demo
  run" and attribute it to the demo, or drop the number.
- **"Deploys to Vercel" overstates what happens.** No deploy is triggered per client. Say
  "renders at a dynamic route from a shared deployed app".
- **The preview link goes to an internal reviewer, not to the client.** Do not claim client
  inbox delivery.
- **Reviewer feedback is not written to Airtable in the committed code.** Only status is.
  A code comment claims otherwise. If asked, say the feedback field is in the schema and the
  webhook forward is wired, and the Airtable write for it is the missing piece.
- **The regeneration workflow has no JSON export.** It is documented in the setup guide and
  supported by a clause in the prompt, and the app posts to it, but there is no committed
  workflow to demonstrate. Do not claim a working regeneration loop was demonstrated end to
  end unless that can be shown.
- **Regeneration returns the whole document, not only changed sections.** The prompt asks
  for the full updated JSON with untouched sections left alone. "Regenerates the changed
  sections" is not what the contract says.
- **All four workflow exports are saved inactive.** They demonstrate structure, not a running
  production system. Be precise about what was live during the demo versus what was built.
- **Model identifiers in the workflow JSON do not match the deck.** The deck names one Flash
  generation and the workflow calls a different one. Know which was actually executed.
- **The import-ready workflow contains inline secrets.** Know that this is true, know why it
  happened (a demo that had to run without credential setup), and know that the labelled
  variants use the credential store properly.
- **Reviews and gallery content is placeholder-injected, not generated or fetched.** The deck
  describes a daily Places API sync as the production design; no such workflow exists in the
  repo. The demo data is stock imagery and mock reviews, which the deck does disclose.
- **Team member parsing is incomplete.** The questionnaire captures team members as a single
  raw multi-line string and passes it through as-is; no code splits it into structured
  members. The model infers the structure. Be ready to explain that.
- **No automated tests.** The two committed scripts are manual one-shot harnesses, not a
  test suite. No CI configuration exists.
