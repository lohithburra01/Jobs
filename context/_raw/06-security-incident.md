# 06 - Security incident (reconstructed from the repo record)

The narrative record does exist: a dedicated `SECURITY.md` incident log, a project memory file, the
running `NOW.md` session journal, and a set of drafted escalation messages. The earlier pass that
concluded "not caused or fixed by this code" was reading code only. All names, domains and
identifiers are redacted below.

---

## What happened

A **law-firm client site running WordPress was taken over by an external attacker** in late July
2026, while the author's content-publishing automation was actively being built against that same
site. That coincidence is the whole shape of the incident.

**How it surfaced.** It came in as a support question, not an alert. On the afternoon of
2026-07-27 the agency's web-dev lead asked in the shared channel whether an unfamiliar WordPress
admin user had been created by the automation pipeline (recorded at roughly 15:50 CET). About
twenty minutes later (roughly 16:14) he escalated: the site was down, it might be a hack, and he
had to leave for the day. There is no monitoring alert in the record and no attacker-side clock.

**What was observed on the site.**
- A rogue WordPress administrator account existed that nobody on the team had created. Its
  username and its email address both carried a signature string associated with the exploit
  family, which is what identified the attack.
- The legitimate administrator account had **lost its capabilities** - it could no longer edit
  content or open the page-builder and caching plugins. Demoting real admins is a documented
  fingerprint of this exploit.
- The **entire site was returning HTTP 403 "Access denied"** - homepage, contact page, imprint,
  and the REST API alike. The response headers showed this was a host or edge security shield
  lockdown sitting above WordPress, not a WordPress-level failure and not anything the author's
  tooling had done.
- The documented indicators for this exploit family also include PHP web shells dropped into the
  WordPress cache directory under random names. The record lists this as an expected indicator and
  as something to ask the host to sweep for; it does **not** record one being found here.

**Dates recorded.**
- ~2026-07-17/18: the underlying WordPress core vulnerability is disclosed and a global
  mass-exploitation wave begins within hours of the patch.
- 2026-07-22 to 2026-07-24: the author's own work on this client site (admin account created for
  the automation by the web-dev lead, a token-gated publish plugin built and installed, live
  behaviour proved with a self-cleaning create-verify-delete test, then a smoke test that created
  a real draft plus a media item and force-deleted both).
- 2026-07-27: the compromise surfaces (see above). Same day, unrelated, the pipeline engine had
  been deployed to a public host.
- 2026-07-28 morning: the web-dev team independently confirms in Slack that the site "really has
  been hacked through the WP security vulnerability" and that they have lost WordPress editing
  rights. A manual restore from the hosting account fails; they escalate to the host for a backup
  restore. Management instructs that the end client be informed.
- 2026-07-28 09:14: the host completes the restore and the web-dev lead patches WordPress core to
  the fixed release, in the same pass.
- 2026-07-28 09:15: the restore is confirmed to have rolled back past the automation's own setup,
  so a new WordPress user for the automation has to be issued.

**Scope of effect as recorded:** one client site, fully down for at least part of 2026-07-27 into
the morning of 2026-07-28, restored from backup and patched by mid-morning 2026-07-28. The rogue
admin account was removed by the restore. Two other client sites in the same portfolio were found
to be running exploitable WordPress versions but were not reported as compromised.

---

## His response

Ordered, with the distinction between record and inference marked.

**RECORDED - 2026-07-27, same afternoon and evening (within hours of the 16:14 escalation):**

1. **Independently reproduced the symptom from outside.** Fetched the client site's public pages
   himself and confirmed the 403 was site-wide rather than scoped to one page, and read the
   response headers to attribute the block to a host security shield rather than to WordPress or
   to the pipeline.
2. **Identified the attack.** Matched the rogue admin account's naming pattern, the demoted real
   admin, and the lockdown to a specific, publicly-known WordPress **core** pre-authentication RCE
   chain that was under active global mass exploitation, and recorded which version ranges are
   fully exploitable, which are partially affected, and which releases fix it.
3. **Ran a full adversarial self-audit of his own attack surface** - the record's phrase is that he
   deliberately attacked his own system from the inside. Six touchpoints, each with a written
   verdict: the web-server config lines he had suggested (no deny directive, cannot change WordPress
   roles, measurably inert anyway); the publish bridge plugin (re-read line by line - constant-time
   token check on every route, no unauthenticated path, creates no users, registers its own
   namespace rather than the core route the exploit abuses); the automation's admin account and
   application password; the hosted engine and the workflow tool (neither can create users or change
   roles); a secret-leak hunt confirming the token and app password existed only in the local env
   file and never in git history or workflow files; and a **control case** - the client site where
   his team had done roughly ten times more work was patched and completely clean, so the volume of
   his work was not the differentiator.
4. **Swept the client portfolio for the same exposure** the same day - an ad-hoc sample of roughly
   27 of about 85 sites, scored by actual exploitability rather than by patch age, which surfaced
   one further site on an exploitable version.
5. **Flagged a separate finding** discovered in the process: a shared cloud spreadsheet holding
   client WordPress logins in plaintext, called out as a live exposure during an active breach and
   recommended for rotation and access-locking.
6. **Wrote the communications**: a direct reply to the web-dev lead (what was checked, what the
   automation can and cannot technically do, and what to ask the host for - rogue-user creation
   timestamp, lockdown status, security plugin logs, restore from a pre-incident backup, admin
   password resets, malware scan), a channel escalation message, and a follow-up audit update, all
   drafted bilingually.
7. **Volunteered a precautionary rollback of his own access** - stated he would rotate the
   automation token and deactivate his plugin on that site so nothing of his was live during the
   investigation.
8. **Refused to assert cause from correlation.** The record repeatedly states that the definitive
   proof is the host's access log plus the rogue user's creation timestamp, that this was formally
   requested, and that until it arrives the attribution is evidence-backed inference rather than
   proof. This is written into the standing principles as "attribution needs server evidence".

**RECORDED - 2026-07-28, the following day:**

9. **Independently verified the fix rather than taking the report.** After the web-dev lead said he
   had patched, the author externally re-measured the site's WordPress version and confirmed the
   patched release.
10. **Turned the ad-hoc sweep into a reproducible tool.** The 07-27 sweep had saved its results but
    not its method. He wrote a passive, credential-free WordPress version scanner (reads only the
    version the site publishes about itself, no logins, no admin-endpoint probing, no writes) with
    the exploitability scoring for this specific chain built in.
11. **Scanned 44 client domains with it**, building the domain list from an SEO tool's project list
    plus the earlier sweep, and deliberately *not* opening the plaintext credentials spreadsheet to
    get the domain list. Result: two sites exploitable (one still unpatched a full day after being
    flagged, and one **new find that had never appeared in any sample or in the escalation
    thread**), three very old but not affected by this chain, seventeen confirmed patched, and
    twenty-two whose version is hidden from outside. The record is explicit that hidden does not
    mean patched and that coverage was 44 of about 85.
12. **Wrote the operational guidance for the restore window**: publish nothing until the site is
    confirmed clean and patched; a backup restore will likely bring core back on a vulnerable
    version and must be patched immediately after; the automation's plugin may be removed by the
    restore; the bridge token must be treated as exposed because the attacker had database access
    and the token lives in the WordPress options table, and must be rotated *after* the restore,
    not before; and the restore point must predate the rogue account's creation.
13. **Verified by measurement, not assumption, that the restore had deleted his plugin** (its REST
    route returned 404 and its namespace was gone), and used that to make a single consolidated ask
    for the replacement WordPress account, specifying that it needs plugin-install rights once and
    should be downgraded to posts-and-media afterwards.
14. **Audited his own pipeline API on his own initiative** the same day and found five real issues,
    all fixed, deployed and re-verified live that day (see below).
15. **Created the standing record and mandate**: a permanent append-only incident log with a mandate
    dated 2026-07-27 and twelve numbered security principles, made mandatory reading before any
    live-site or credential work.
16. **Stayed in his lane on client comms.** When management raised selling a maintenance package to
    affected clients, the record rules that client-facing vulnerability communication is a
    commercial decision owned by the account side and technical patching is the web-dev lead's; his
    contribution is the scan data and the tooling.

**INFERENCE, not stated in the records:** that the self-audit was completed the same evening rather
than spread over both days (the record dates the audit 2026-07-27 and the messages are dated the
same window, but no completion timestamp is given); that his reply to the web-dev lead was actually
sent and when; and that the precautionary token rotation and plugin deactivation he offered were
actually carried out - they remain **unchecked** action items in the log.

---

## Root cause

The records identify the vector clearly and consistently across three independent sources.

The cause was a **pre-authentication remote code execution chain in WordPress core**, not in any
plugin, theme, or the author's code: a route-confusion flaw in the WordPress REST API batch endpoint
chained with an SQL injection in a query parameter, requiring no login, no credentials and no token.
The vulnerable code shipped in a WordPress major release and the client site's core had been on an
exploitable version the entire time the author worked on it. Public disclosure was followed within
hours by a global automated mass-exploitation wave scanning the internet indiscriminately.

The security log and the drafted messages name two CVE identifiers for the chain. **Confirm those
CVE numbers against a public advisory before quoting them in an interview.** The defensible
statement without them is "a WordPress core pre-auth RCE in the REST batch endpoint, chained with an
SQL injection, under global mass exploitation".

Corroboration is genuinely independent: the web-dev team reached the same conclusion the next
morning without seeing the audit. The control-case argument points the same way. The one gap never
closed is the host's access log and the rogue account's creation timestamp, requested and still an
open action item.

---

## What changed afterwards

- **A standing security mandate**, dated to the day of the incident: anything touching a client
  site, credential or live system must be careful, logged, reversible and least-privilege.
- **A permanent, append-only incident log** with a fixed per-incident structure (vulnerability,
  symptoms, timeline, audit, verdict, action items with status). Reading it is a precondition for
  live-site or credential work.
- **Twelve numbered security principles**, four written directly out of that week's two findings:
  re-audit whenever exposure changes; every endpoint that writes needs an authenticator even if it
  must be token-free; auth fails closed; never treat your own content as pre-sanitised.
- **A reusable credential-free portfolio scanner** with exploitability scoring for the specific
  chain, replacing the unrepeatable manual sweep, plus a maintained domain list file.
- **Code and deployment hardening** of the author's own API: strict slug validation at both the HTTP
  layer and inside the write function, HMAC-signed per-resource links replacing guessable slugs,
  fail-closed startup, body and revision caps, and a pinned public base URL so a spoofed Host header
  cannot redirect an emailed link.
- **A credential-hygiene push**: rotate anything that lived on a compromised system, no plaintext
  secrets in shared drives, chat or git, scoped rather than org-wide tokens, deactivate plugins when
  idle, and downgrade privileged accounts after one-time admin tasks.
- **A lane boundary**: vulnerability communication to end clients is a commercial decision, not the
  engineer's to initiate.
- **An unresolved process gap logged honestly**: the code that publishes to client sites was
  entirely untracked in git at the time, so no history and no rollback for exactly the code that
  touches live sites. It went into git on 2026-07-29.

---

## The pre-existing audit work - precise ordering

This determines whether the resume can present this work as prevention or as response. The answer
is mostly **response**, with one genuine prevention element.

- **The standing security policy came out of the incident, not before it.** The mandate at the top
  of `SECURITY.md` is dated 2026-07-27, the day the compromise surfaced, and the memory file states
  outright that this is "the incident that set this". The twelve principles were written in the
  same window. Presenting the policy as pre-existing would be false.
- **The credential-free scanner is response, and second-generation response at that.** The ad-hoc
  portfolio sweep happened on 2026-07-27, the day of the incident, after it surfaced. The scanner
  script was written on 2026-07-28, the day after, explicitly because the 07-27 sweep had saved its
  results but not its method. Its own docstring names the incident as its reason for existing.
  It is a good bullet, but it is "built the tool during the response", not "had the tool in place".
- **The unauthenticated write path finding is self-initiated, one day after the incident, and is
  prevention with respect to that specific hole.** Logged separately, found 2026-07-28 by a
  self-directed audit of his own attack surface, with no external report and no evidence of
  exploitation. Five findings: a critical unauthenticated write endpoint that, combined with a
  publish path inserting HTML verbatim with WordPress filtering removed, let anyone on the internet
  rewrite a post awaiting approval and get arbitrary HTML or JavaScript published to a live client
  site once a reviewer approved it; a read-and-write path traversal via an unsanitised parameter
  (read proven live, write proven in a throwaway directory); auth that failed **open** when no token
  was configured; unbounded writes with no body cap on the single-copy data volume; and unpublished
  client content readable by guessing a slug. All five fixed, deployed and re-verified against the
  live URL the same day, 22 of 22 local tests passing and the original exploits re-probed live and
  refused. Stated cause: the engine moved from localhost behind a temporary tunnel to a permanent
  public URL on 2026-07-27 without the endpoint design changing with it. So: found before anyone
  exploited it (prevention), but found because the client incident had just made security top
  priority and the exposure change was fresh (response-driven).
- **The one genuine "before" element** is the working discipline that predated the incident:
  token-gated routes with constant-time comparison and no unauthenticated path in the publish
  plugin, secrets confined to the local env file and never committed, live writes held back, and
  self-cleaning create-verify-delete tests, all dated 2026-07-22 to 2026-07-24. The record credits
  exactly this for why the self-audit could be completed quickly and come back clean. That is a
  defensible "built it carefully beforehand, which is why I could clear it fast" claim, and it is
  distinct from claiming a security programme existed beforehand.

**Safe framing:** responded to the incident, cleared his own systems with evidence, then converted
the response into durable tooling and policy, and used the same momentum to find and close real
holes in his own API before anyone touched them.

---

## Evidence map

| Claim | Kind of source |
|---|---|
| Incident narrative, symptoms, version ranges, timeline, verdict, self-audit touchpoints, control case, portfolio scan results, standing mandate and the twelve principles | **Security doc**: a dedicated append-only incident log in the repo root (~385 lines, three entries plus principles) |
| Escalation clock times, the team's independent confirmation next morning, the restore attempt, the patch, the new-user request | **Security doc**, quoting team chat messages with timestamps, transcribed and translated |
| Scanner rationale, passivity guarantees, exploitability scoring, the "results were saved but the method was not" reasoning | **Code comment**: module docstring and inline comments of the scanner script |
| His reply to the web-dev lead, the ask list to the host, the offer to rotate and deactivate, the channel escalation and the honest timing argument | **Handoff/comms drafts**: bilingual message files written to be sent by him |
| Plugin confirmed deleted by the restore, verified rather than assumed | **Handoff doc** (a "notes, do not send" block) plus **session notes** |
| Own-API audit findings, fixes, live re-probe results, test counts; restore-window operating rules; day-by-day sequencing | **Session notes**: the running session journal in the repo root |
| Condensed durable version, behavioural takeaways, lane boundary | **Memory file** for this repo |
| Git history | **Not usable for this window**: the security files were only committed on 2026-07-29 and later, so file dates and the written log are the timeline, not commit dates |

---

## What is NOT recorded

Be blunt about these in any interview.

- **No detection time and no dwell time.** Nobody knows when the site was actually compromised. The
  rogue account's creation timestamp was requested from the host and the action item is still
  **open and unchecked**. Everything before the 15:50 question on 2026-07-27 is unknown.
- **No downtime figure.** The site was down when it surfaced on the afternoon of 2026-07-27 and
  restored at 09:14 on 2026-07-28. No outage duration is stated, and it is not known how long it
  had been failing before anyone looked.
- **No scope of data affected.** No statement about exfiltration, about what was in the database,
  about personal data, or about whether a breach notification was considered. This is a law-firm
  client, so the absence is conspicuous, but inventing it is not an option.
- **No confirmation that a web shell was found.** Web shells in the cache directory are listed as a
  known indicator for this exploit family and as something to ask the host to sweep for. Whether
  one existed on this site is an open question in the log.
- **No proof of attribution.** The host access log was never received in the record. The
  attribution rests on the exploit's fingerprint, the team's independent conclusion, and the
  control case. The author states this limitation himself.
- **No confirmation that the two exploitable sites were ever patched.** Both remain open action
  items, one of them explicitly still unpatched a full day after being flagged.
- **No confirmation that the plaintext credential spreadsheet was rotated or locked.** Open item.
- **No confirmation that the precautionary token rotation and plugin deactivation happened.** Open.
- **Coverage of the portfolio scan was 44 of about 85 sites**, with 22 of those 44 hiding their
  version. The author records this as the real blind spot rather than rounding it up.
- **No client-facing impact, no cost, no SLA, no incident report to the end client** authored by
  him. Client communication was explicitly someone else's lane.
- **He did not remediate the client site.** The restore and the patch were done by the host and the
  agency's web-dev lead. His contributions were the diagnosis, the exoneration evidence, the
  portfolio exposure data, the verification of the fix, and his own systems.

---

## Draftable bullets

Each uses only what the records support. Pick by intensity.

**A. Modest, safest, fully evidenced**
> Responded to a client WordPress compromise mid-engagement: reproduced and scoped the outage
> independently, identified the vector as a WordPress core pre-authentication RCE under global mass
> exploitation, and cleared our automation as the cause with a documented six-point self-audit and a
> control-case comparison, all within hours of escalation.

**B. Response plus the tooling that came out of it (recommended single best)**
> Led the technical response to a client WordPress compromise during a live engagement: identified
> the vector as a WordPress core pre-authentication RCE, ran a same-day adversarial audit of every
> automation touchpoint to rule our pipeline out with evidence rather than assertion, then built a
> passive credential-free version scanner that covered 44 client domains and surfaced two
> exploitable sites, one of which no one had previously flagged.

**C. Response plus own-API hardening (strongest, still honest)**
> Handled a client WordPress compromise end to end within 24 hours: attributed it to a WordPress
> core pre-auth RCE, exonerated our automation with a documented self-audit and independent
> verification of the host's patch, shipped a credential-free portfolio scanner covering 44 domains
> that found two exploitable sites, and used the same pass to audit our own publishing API, closing
> an unauthenticated write path onto live client sites, a read/write path traversal, and fail-open
> authentication, all fixed, deployed and re-verified live the same day.

**D. Security-engineering angle, incident as context**
> Self-audited a content-publishing API after moving it from localhost to a public URL and found
> five issues including an unauthenticated write endpoint that chained into arbitrary HTML
> publishing on live client sites and a read/write path traversal; fixed all five in a day with
> strict input validation, HMAC-signed per-resource links, and fail-closed auth, verified by 22
> passing tests and by re-running the original exploits against production.

**Do not write:** any bullet claiming he prevented the compromise, restored the site, had a security
programme in place beforehand, or knows the dwell time, downtime or data impact. None of that is
supported.
