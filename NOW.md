# NOW - resume state

Last updated: 2026-08-26

## Start every session with this

Two messages. First, to initialise:

    Read NOW.md and context/tailoring-sheet.md. Confirm what you have loaded and what
    the open items are, then wait for my JD.

Then, once it confirms:

    /apply

    <paste the JD>

Cheaper one-shot alternative when there is no need to check state first: put
`Read NOW.md and context/tailoring-sheet.md, then /apply:` and the JD in a single message.

`CLAUDE.md` loads by itself. Those two extra files are the ones that are not automatic:
`NOW.md` is the resume state (~1.3k tokens), `context/tailoring-sheet.md` is the
capability layer plus the JD index (~4k). Nothing else is read up front.

Never read whole: `context/corominas-systems.md` (~38k) and `context/_raw/*` (~48k). Open
a single section of the systems file only when a bullet needs detail the sheet lacks.
One application per session, then `/clear`.

Everything lives under `C:\Users\91910\Downloads\jobs`. One root, no exceptions.
`applications/_archive_pre-system/` holds the 587 files from the old `german resumes`
folder, which is now gone. History only, never source material.

## Where things stand
PART 0 is complete. The system is ready to apply. Nothing has been applied to yet.

- [x] 0.1 Structure: `scripts/`, `context/`, `applications/`, `tracker.md`, `context/answers.md`
- [x] 0.2 Build script rewired:
      `python scripts/build_resume.py <application.json> <output-dir>`
      Outputs `Lohith_Burra_<Company>.pdf` and `Lohith_Burra_<Company>_CoverLetter.pdf`.
      Layout, styles, fonts, margins and page size untouched. Test build off
      `context/schema-example.json` passed: 1 page, 0 em dashes, 0 en dashes.
- [x] 0.3 Corominas mined, then restructured capability-first. `context/corominas-
      systems.md`, 628 lines: how-to-use, a 14-capability layer that leads the file, a
      26-row JD index keyed on capability language, systems with pattern-first headings
      and the domain in parentheses, safe-to-quote numbers with domain-neutral
      restatements, engineering judgment, tech inventory, working method, and a binding
      FLAGGED section. Includes the July 2026 security incident reconstruction.
      Per-folder research in `context/_raw/01..06`.
      Verified: zero em and en dashes, zero client names, domains, emails or credentials
      across every context file.
      Mined: `Downloads\New folder (4)\Guttler` and `Downloads\coronimas`.
      Excluded: `Downloads\New folder (4)\ai video`, a scrapped project. Never cite it.
- [x] 0.4 All four questions answered and written into PART 1 and PART 3, along with the
      authorship boundary and the employment framing.

## What changed in CLAUDE.md this session
- PART 1: the audience number is settled at 10M+ views (Formulytics, his own page).
  176K and 50K+ are retired as belonging to the main brand account.
- PART 1: added "How he builds" as the through-line to sell. Not a fixed stack.
- PART 2 Corominas: dates Jun 2026 to Sep 2026, employment-type label removed, bullets
  rebuilt on verified numbers, SEO co-ownership stated correctly, security bullets now
  incident response plus the hardening that followed.
- PART 2 Formula Neon: renamed to AI Automation Developer, labelled Contract.
- PART 2 Think Round: Remote, US.
- PART 3: "The Corominas ending" replaces "The termination". It is a Probezeit exit on an
  open-ended contract, NOT befristet. The old "fixed-term contract concluded" form answer
  is banned.
- PART 3: "Dates and overlap" added. Never alter dates, handle overlap by selection.
- PART 3: "Formula Dream, what not to say" added. Contract name settled as Formula Dream.
- PART 3: "3D is secondary" added.

## Open, non-blocking
1. The incident log names two CVE identifiers. Verify before quoting either.
2. Rotate the live Airtable token and Google API key hard-coded inline in a workflow JSON
   in `Downloads\coronimas`.
3. He says the Web_Dev pipeline scales to the full client list in his last two weeks. If
   that lands, update the scale numbers in `context/corominas-systems.md`.

## The framing rule that outranks everything
Lead with the automation pattern, never the domain. He is not an SEO, WordPress, content
or social media person. Encoded as PART 4 rules 9 and 10 and as PART 5 step 0. Tailor from
the capability layer at the top of `context/corominas-systems.md`, not from the systems
section. Ship test: if a reader could guess the employer's industry from the bullets
alone, it is not tailored yet.

## Employer folders
Scaffolded by `python scripts/new_application.py "<Company>" "<Role>"`, never by hand.
Produces `jd.md`, `application.json`, `log.md`, `notes/`, `out/`. Verified end to end
2026-08-26: scaffold plus build into `out/` both work. `notes/` is the catch-all for
recruiter mail, call notes, briefs, anything pasted mid-process, one dated file per thing.
PART 5 now also documents what happens after they reply: `/answer`, `/log`, `/prep`.

## Standing constraints when applying
- Scale is a pilot, not mass production: 16 articles, 5 clients, 7 active configs. Lead
  with engineering depth, not volume.
- No operational metrics exist anywhere in the repo: no uptime, throughput, success rate,
  per-article cost or end-to-end latency. Never claim them.
- The SEO content pipeline runtime is largely the domain lead's. His lane is the
  automation, the transport and cost work, the diagnoses, and the automation inside the
  skills.
- Security is response and hardening, never prevention that pre-empted the breach.

## Next session
`/apply` with a pasted JD. Read this file, `CLAUDE.md`, and
`context/corominas-systems.md`. Nothing else is needed.
