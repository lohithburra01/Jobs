"""Scaffold an employer folder.

Usage:
    python scripts/new_application.py "Company Name" "Role Title" [--date YYYY-MM-DD]
                                      [--root applications]

Creates applications/<date>_<company-slug>_<role-slug>/ containing:
    jd.md              raw JD as pasted
    application.json   resume + cover letter data, skeleton matching schema-example.json
    log.md             append-only history and every answer given
    notes/             any other context: emails, recruiter messages, call notes, txt
    out/               the built PDFs

Prints the folder path. Refuses to overwrite an existing non-empty folder.
"""

import argparse
import datetime
import json
import os
import re
import sys


def slug(text):
    s = text.lower().strip()
    s = s.replace("&", " and ")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return re.sub(r"-{2,}", "-", s).strip("-")


APPLICATION_SKELETON = {
    "company_name": "",
    "resume": {
        "summary": "",
        "skills": [{"label": "", "value": ""}],
        "experience": [
            {"title": "", "company": "", "period": "", "bullets": [""]}
        ],
        "projects": [{"name": "", "period": "", "bullets": [""]}],
        "education": [
            {
                "degree": "Master of Science - Data Science",
                "school": "Stevens Institute of Technology",
                "year": "2025",
            },
            {
                "degree": "Bachelor of Technology - Mechanical Engineering",
                "school": "JNTU K",
                "year": "2022",
            },
        ],
    },
    "cover_letter": {
        "date": "",
        "company_address": "",
        "salutation": "",
        "paragraphs": [""],
    },
}


LOG_TEMPLATE = """# {company} - {role}
Status: applied
Applied: {date}
Size: <employee count or funding stage>
Source: <where the JD came from>
Contacts:
  - <name, title, email or LinkedIn>

## Capabilities this JD is buying
<the two or three named before any bullet was written, per PART 5 step 0>

## Timeline
### {date} - applied
Submitted via <source>.

## Answers given
<every screening or form answer, verbatim, added by /answer>
"""


NOTES_README = """Anything about this employer that is not the JD, the application data or
the log goes here. Recruiter emails, call notes, take-home briefs, job ads that changed,
screenshots of the posting, LinkedIn threads, salary discussions.

Plain .txt or .md, one file per thing, prefixed with the date: 2026-08-26_recruiter-call.txt

The rule from PART 5 holds: nothing about this employer lives anywhere else.
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("company")
    ap.add_argument("role")
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    ap.add_argument("--root", default="applications")
    a = ap.parse_args()

    name = "{}_{}_{}".format(a.date, slug(a.company), slug(a.role))
    path = os.path.join(a.root, name)

    if os.path.isdir(path) and os.listdir(path):
        print("Refusing to overwrite existing folder: " + path)
        sys.exit(1)

    os.makedirs(os.path.join(path, "notes"), exist_ok=True)
    os.makedirs(os.path.join(path, "out"), exist_ok=True)

    with open(os.path.join(path, "jd.md"), "w", encoding="utf-8") as f:
        f.write("# {} - {}\n\nSource: \nDate pasted: {}\n\n---\n\n".format(
            a.company, a.role, a.date))

    skeleton = json.loads(json.dumps(APPLICATION_SKELETON))
    skeleton["company_name"] = a.company
    with open(os.path.join(path, "application.json"), "w", encoding="utf-8") as f:
        json.dump(skeleton, f, indent=2, ensure_ascii=False)
        f.write("\n")

    with open(os.path.join(path, "log.md"), "w", encoding="utf-8") as f:
        f.write(LOG_TEMPLATE.format(company=a.company, role=a.role, date=a.date))

    with open(os.path.join(path, "notes", "README.md"), "w", encoding="utf-8") as f:
        f.write(NOTES_README)

    print(path)


if __name__ == "__main__":
    main()
