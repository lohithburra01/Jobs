# Job Sourcing and Application-Material Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a daily batch pipeline that sources job postings, scores them twice with a measured feedback loop between the two scorers, generates tailored resume and cover letter JSON for the ones worth applying to, and renders PDFs through the existing builder.

**Architecture:** Four stages (fetch, evaluate, generate, render) that never call each other. They communicate through a SQLite ledger whose `stage_events` table is append-only, so any run resumes by replaying only the work that has no successful event. A single `input_hash` per `(posting, stage)` serves as both the idempotency key and the result cache. A local `.xlsx` is a rendered view of the ledger plus one input channel.

**Tech Stack:** Python 3.11+, Pydantic v2, SQLite (`sqlite3`, no ORM), `httpx`, `anthropic` SDK, Langfuse, `openpyxl`, `pypdf`, `pytest`, ReportLab (existing, unchanged).

**Spec:** `docs/superpowers/specs/2026-09-01-job-pipeline-design.md`

## Global Constraints

- Python 3.11 or newer. Pydantic v2.
- No dict crosses a stage boundary. Every inter-stage object is a Pydantic model.
- `stage_events` is append-only. No `UPDATE`, no `DELETE`, ever. Current state is a query.
- The renderer `scripts/build_resume.py` and the JSON schema in `context/schema-example.json` are frozen. Do not modify either.
- Generated application text must contain none of U+2012, U+2013, U+2014, U+2015, U+2212.
- Evaluation model: `claude-sonnet-5`, `output_config={"effort": "low"}`. Generation model: `claude-opus-5`, `output_config={"effort": "high"}`. Both are config values, never literals in stage code.
- Prompt caching: one explicit `cache_control` breakpoint at the end of the static system block, TTL 5 minutes. Never place run ids, posting ids, or the current date in the static block.
- Budget ceiling halts a run. It never degrades quality or silently truncates.
- No test makes a live LLM call or a live network call. The LLM client and HTTP client are injected.
- `auto_apply` for the tuner is false and stays false. The tuner has no write path to scoring config.
- Config lives in YAML under `config/`. Adding a geography or changing the salary floor must never require a code change.

---

## File Structure

```
pipeline/
  __init__.py
  config.py            load and validate config/*.yaml into Pydantic settings
  identity.py          canonical URL, posting_id, identity_key normalisation
  hashing.py           input_hash construction
  models.py            all Pydantic boundary objects
  store.py             SQLite schema, append-only events, skip rule
  facts.py             derive facts from CLAUDE.md, hash gate
  llm.py               traced LLM client, budget, prompt caching
  scoring.py           deterministic prelim scorer
  sources/
    base.py            Source protocol, RawPosting
    arbeitnow.py       first discovery adapter
    manual.py          manual URL injection
  stages/
    fetch.py
    evaluate.py
    generate.py
    render.py
  gates/
    gate_a.py          pre-render checks against the JSON artifact
    gate_b.py          post-render checks against the PDF
  tuning/
    metrics.py         divergence metrics, FetchQualityReport
    tuner.py           deterministic proposal policy
  export.py            xlsx render and INBOX read-back
  cli.py
config/
  constraints.yaml  sources.yaml  scoring.yaml  tuning_state.yaml
  budget.yaml  facts_curated.yaml  prompts/
tests/
  test_identity.py  test_hashing.py  test_store.py  test_facts.py
  test_scoring.py  test_llm.py  test_sources.py  test_gate_a.py
  test_gate_b.py  test_metrics.py  test_tuner.py  test_export.py
  test_stages.py
  fixtures/
  regression/
```

---

### Task 1: Project scaffold and config loading

**Files:**
- Create: `pyproject.toml`, `pipeline/__init__.py`, `pipeline/config.py`
- Create: `config/constraints.yaml`, `config/scoring.yaml`, `config/budget.yaml`
- Test: `tests/test_config.py`

**Interfaces:**
- Consumes: nothing
- Produces: `load_config(root: Path) -> Config`; `Config` with `.constraints: Constraints`, `.scoring: Scoring`, `.budget: Budget`; `Config.slice_hash(keys: list[str]) -> str`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_config.py
from pathlib import Path
from pipeline.config import load_config

def test_loads_constraints_from_yaml(tmp_path: Path):
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "constraints.yaml").write_text(
        "salary_floor_eur: 65000\n"
        "countries: [DE, NL, SE, remote]\n"
        "working_languages: [en, de]\n"
        "min_employees: 100\n"
        "target_titles: ['AI Engineer', 'Automation Engineer']\n",
        encoding="utf-8",
    )
    (tmp_path / "config" / "scoring.yaml").write_text(
        "threshold: 60.0\nweights: {title: 0.4, country: 0.3, language: 0.3}\n",
        encoding="utf-8",
    )
    (tmp_path / "config" / "budget.yaml").write_text(
        "max_usd_per_run: 2.0\nmax_tokens_per_run: 3000000\n", encoding="utf-8"
    )
    cfg = load_config(tmp_path)
    assert cfg.constraints.salary_floor_eur == 65000
    assert "remote" in cfg.constraints.countries
    assert cfg.scoring.threshold == 60.0
    assert cfg.budget.max_usd_per_run == 2.0

def test_slice_hash_changes_only_with_named_keys(tmp_path: Path):
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "constraints.yaml").write_text(
        "salary_floor_eur: 65000\ncountries: [DE]\nworking_languages: [en]\n"
        "min_employees: 100\ntarget_titles: ['AI Engineer']\n", encoding="utf-8")
    (tmp_path / "config" / "scoring.yaml").write_text(
        "threshold: 60.0\nweights: {title: 1.0}\n", encoding="utf-8")
    (tmp_path / "config" / "budget.yaml").write_text(
        "max_usd_per_run: 2.0\nmax_tokens_per_run: 100\n", encoding="utf-8")
    cfg = load_config(tmp_path)
    before = cfg.slice_hash(["constraints.salary_floor_eur"])
    cfg.constraints.salary_floor_eur = 68000
    after = cfg.slice_hash(["constraints.salary_floor_eur"])
    unrelated = cfg.slice_hash(["scoring.threshold"])
    assert before != after
    assert unrelated == cfg.slice_hash(["scoring.threshold"])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_config.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'pipeline'`

- [ ] **Step 3: Write minimal implementation**

```toml
# pyproject.toml
[project]
name = "job-pipeline"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
  "pydantic>=2.7", "pyyaml>=6", "httpx>=0.27", "anthropic>=1.0",
  "langfuse>=2.50", "openpyxl>=3.1", "pypdf>=4.2",
]

[project.optional-dependencies]
dev = ["pytest>=8", "pytest-cov"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

```python
# pipeline/config.py
import hashlib
import json
from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class Constraints(BaseModel):
    salary_floor_eur: int
    countries: list[str]
    working_languages: list[str]
    min_employees: int
    target_titles: list[str]
    url_strip_params: list[str] = Field(
        default_factory=lambda: ["gh_src", "ref", "source", "trk"]
    )


class Scoring(BaseModel):
    threshold: float
    weights: dict[str, float]


class Budget(BaseModel):
    max_usd_per_run: float
    max_tokens_per_run: int


class Config(BaseModel):
    constraints: Constraints
    scoring: Scoring
    budget: Budget

    def slice_hash(self, keys: list[str]) -> str:
        """Hash only the named dotted config keys, so a stage is invalidated
        by the config it actually reads and by nothing else."""
        payload = {}
        for key in sorted(keys):
            node: object = self
            for part in key.split("."):
                node = getattr(node, part)
            payload[key] = node
        blob = json.dumps(payload, sort_keys=True, default=str)
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _read(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_config(root: Path) -> Config:
    c = root / "config"
    return Config(
        constraints=Constraints(**_read(c / "constraints.yaml")),
        scoring=Scoring(**_read(c / "scoring.yaml")),
        budget=Budget(**_read(c / "budget.yaml")),
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_config.py -v`
Expected: 2 passed

- [ ] **Step 5: Write the real config files**

```yaml
# config/constraints.yaml
salary_floor_eur: 65000
countries: [remote, NL, SE, DK, FI, NO, AT, DE, CZ, PL]
working_languages: [en, de]
min_employees: 100
target_titles:
  - AI Engineer
  - Automation Engineer
  - AI Automation Engineer
  - Agentic AI Developer
  - Forward Deployed Engineer
  - Solutions Engineer
  - GTM Engineer
  - Head of Automation
url_strip_params: [gh_src, ref, source, trk, sessionid, jobsid]
```

```yaml
# config/scoring.yaml
threshold: 60.0
weights:
  title_match: 0.35
  country: 0.20
  language: 0.15
  remote: 0.10
  seniority: 0.10
  source_priority: 0.10
```

```yaml
# config/budget.yaml
max_usd_per_run: 2.0
max_tokens_per_run: 4000000
```

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml pipeline/ config/ tests/test_config.py
git commit -m "feat: project scaffold and config loading"
```

---

### Task 2: URL canonicalisation and posting_id

**Files:**
- Create: `pipeline/identity.py`
- Test: `tests/test_identity.py`

**Interfaces:**
- Consumes: `Constraints.url_strip_params` from Task 1
- Produces: `canonicalise_url(url: str, strip_params: list[str]) -> str`; `posting_id_for(url: str, strip_params: list[str]) -> str`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_identity.py
from pipeline.identity import canonicalise_url, posting_id_for

STRIP = ["gh_src", "ref", "source", "trk"]

def test_strips_tracking_params_and_fragment():
    url = "HTTPS://Boards.Example.com/jobs/42?utm_source=x&gh_src=abc&team=ai#apply"
    assert canonicalise_url(url, STRIP) == "https://boards.example.com/jobs/42?team=ai"

def test_preserves_meaningful_params_and_is_order_stable():
    a = canonicalise_url("https://e.com/j?b=2&a=1", STRIP)
    b = canonicalise_url("https://e.com/j?a=1&b=2", STRIP)
    assert a == b == "https://e.com/j?a=1&b=2"

def test_posting_id_is_stable_across_tracking_noise():
    one = posting_id_for("https://e.com/j/9?utm_medium=mail", STRIP)
    two = posting_id_for("https://e.com/j/9", STRIP)
    assert one == two
    assert len(one) == 64
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_identity.py -v`
Expected: FAIL with `ImportError: cannot import name 'canonicalise_url'`

- [ ] **Step 3: Write minimal implementation**

```python
# pipeline/identity.py
import hashlib
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


def canonicalise_url(url: str, strip_params: list[str]) -> str:
    """Lowercase scheme and host, drop the fragment, drop tracking params,
    sort the rest so param order never changes the identity."""
    parts = urlsplit(url.strip())
    strip = {p.lower() for p in strip_params}
    kept = [
        (k, v)
        for k, v in parse_qsl(parts.query, keep_blank_values=True)
        if k.lower() not in strip and not k.lower().startswith("utm_")
    ]
    kept.sort()
    return urlunsplit((
        parts.scheme.lower(),
        parts.netloc.lower(),
        parts.path.rstrip("/") or "/",
        urlencode(kept),
        "",
    ))


def posting_id_for(url: str, strip_params: list[str]) -> str:
    canonical = canonicalise_url(url, strip_params)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_identity.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add pipeline/identity.py tests/test_identity.py
git commit -m "feat: canonical URL and posting_id"
```

---

### Task 3: identity_key normalisation and duplicate clustering

**Files:**
- Modify: `pipeline/identity.py`
- Test: `tests/test_identity.py`

**Interfaces:**
- Consumes: nothing new
- Produces: `normalise_company(s: str) -> str`; `normalise_title(s: str) -> str`; `normalise_country(location: str, remote: bool) -> str`; `identity_key_for(company, title, location, remote) -> str`; `title_similarity(a: str, b: str) -> float`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_identity.py  (append)
from pipeline.identity import (
    identity_key_for, normalise_company, normalise_title,
    normalise_country, title_similarity,
)

def test_company_normalisation_drops_legal_suffixes():
    assert normalise_company("Acme Robotics GmbH") == "acme robotics"
    assert normalise_company("ACME  Robotics, Inc.") == "acme robotics"

def test_title_normalisation_drops_german_gender_markers():
    assert normalise_title("AI Engineer (m/w/d)") == "ai engineer"
    assert normalise_title("AI Engineer (f/m/x)") == "ai engineer"
    assert normalise_title("AI Engineer (all genders)") == "ai engineer"

def test_remote_normalises_to_remote_country():
    assert normalise_country("Anywhere in Europe", remote=True) == "remote"
    assert normalise_country("Amsterdam, Netherlands", remote=False) == "NL"

def test_same_job_on_two_boards_shares_identity_key():
    a = identity_key_for("Acme Robotics GmbH", "AI Engineer (m/w/d)", "Berlin, Germany", False)
    b = identity_key_for("ACME Robotics", "AI Engineer", "Berlin, DE", False)
    assert a == b

def test_different_role_same_company_does_not_collide():
    a = identity_key_for("Acme", "AI Engineer", "Berlin, Germany", False)
    b = identity_key_for("Acme", "Data Engineer", "Berlin, Germany", False)
    assert a != b

def test_title_similarity_flags_near_miss_without_merging():
    assert title_similarity("senior ai engineer", "ai engineer") >= 0.6
    assert title_similarity("ai engineer", "ai engineer platform") >= 0.6
    assert title_similarity("ai engineer", "office manager") < 0.3
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_identity.py -v`
Expected: FAIL with `ImportError: cannot import name 'identity_key_for'`

- [ ] **Step 3: Write minimal implementation**

```python
# pipeline/identity.py  (append)
import re

LEGAL_SUFFIXES = (
    "gmbh", "mbh", "ag", "se", "inc", "llc", "ltd", "limited", "corp",
    "corporation", "bv", "nv", "ab", "as", "oy", "sas", "sa", "plc", "co",
)

GENDER_MARKERS = re.compile(
    r"\((?:m\s*/\s*w\s*/\s*d|m\s*/\s*f\s*/\s*d|f\s*/\s*m\s*/\s*x|"
    r"w\s*/\s*m\s*/\s*d|all\s+genders|d\s*/\s*m\s*/\s*w)\)",
    re.IGNORECASE,
)

COUNTRY_ALIASES = {
    "germany": "DE", "deutschland": "DE", "de": "DE",
    "netherlands": "NL", "nederland": "NL", "nl": "NL",
    "sweden": "SE", "se": "SE", "denmark": "DK", "dk": "DK",
    "finland": "FI", "fi": "FI", "norway": "NO", "no": "NO",
    "austria": "AT", "osterreich": "AT", "at": "AT",
    "czechia": "CZ", "czech republic": "CZ", "cz": "CZ",
    "poland": "PL", "polska": "PL", "pl": "PL",
}


def _collapse(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", text.lower())).strip()


def normalise_company(name: str) -> str:
    words = _collapse(name).split()
    while words and words[-1] in LEGAL_SUFFIXES:
        words.pop()
    return " ".join(words)


def normalise_title(title: str) -> str:
    return _collapse(GENDER_MARKERS.sub(" ", title))


def normalise_country(location: str, remote: bool) -> str:
    if remote:
        return "remote"
    for token in reversed(_collapse(location).split(",")):
        pass
    parts = [p.strip() for p in location.lower().replace("/", ",").split(",")]
    for part in reversed(parts):
        key = _collapse(part)
        if key in COUNTRY_ALIASES:
            return COUNTRY_ALIASES[key]
    return "unknown"


def identity_key_for(company: str, title: str, location: str, remote: bool) -> str:
    blob = "|".join((
        normalise_company(company),
        normalise_title(title),
        normalise_country(location, remote),
    ))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def title_similarity(a: str, b: str) -> float:
    """Jaccard over title tokens. Used to flag near-misses for review.
    Never used to auto-merge: dropping a genuinely different role at the
    same company is worse than carrying a duplicate row."""
    sa, sb = set(normalise_title(a).split()), set(normalise_title(b).split())
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)
```

Remove the stray `for token in reversed(...)` loop left in `normalise_country`; it is dead code and the following `parts` loop is the real implementation.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_identity.py -v`
Expected: 9 passed

- [ ] **Step 5: Commit**

```bash
git add pipeline/identity.py tests/test_identity.py
git commit -m "feat: identity_key normalisation and near-miss similarity"
```

---

### Task 4: input_hash construction

**Files:**
- Create: `pipeline/hashing.py`
- Test: `tests/test_hashing.py`

**Interfaces:**
- Consumes: `Config.slice_hash` from Task 1
- Produces: `input_hash(stage: str, prompt_hash: str, model: str, config_slice: str, upstream: str) -> str`; `file_hash(path: Path) -> str`; `text_hash(text: str) -> str`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_hashing.py
from pipeline.hashing import input_hash, text_hash

BASE = dict(stage="evaluate", prompt_hash="p1", model="claude-sonnet-5",
            config_slice="c1", upstream="u1")

def test_identical_inputs_hash_identically():
    assert input_hash(**BASE) == input_hash(**BASE)

def test_each_component_changes_the_hash():
    base = input_hash(**BASE)
    for key, value in [("stage", "generate"), ("prompt_hash", "p2"),
                       ("model", "claude-opus-5"), ("config_slice", "c2"),
                       ("upstream", "u2")]:
        assert input_hash(**{**BASE, key: value}) != base, key

def test_text_hash_is_stable_and_hex():
    assert text_hash("abc") == text_hash("abc")
    assert len(text_hash("abc")) == 64
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_hashing.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'pipeline.hashing'`

- [ ] **Step 3: Write minimal implementation**

```python
# pipeline/hashing.py
import hashlib
from pathlib import Path


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def input_hash(stage: str, prompt_hash: str, model: str,
               config_slice: str, upstream: str) -> str:
    """The single idempotency key. A stage does work for a posting only when
    no ok event exists for (posting_id, stage, input_hash). Because upstream
    carries the JD body hash, this is also the result cache: a posting whose
    text has not changed is never re-evaluated."""
    return text_hash("\x1f".join((stage, prompt_hash, model, config_slice, upstream)))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_hashing.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add pipeline/hashing.py tests/test_hashing.py
git commit -m "feat: input_hash as the single idempotency and cache key"
```

---

### Task 5: Boundary models

**Files:**
- Create: `pipeline/models.py`
- Test: `tests/test_models.py`

**Interfaces:**
- Consumes: nothing
- Produces: `PostingStub`, `PostingDetail`, `EvaluationResult`, `TailoringBrief`, `ApplicationDocument`, `RenderResult`, `FetchQualityReport`, `SUBSCORE_AXES`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_models.py
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from pipeline.models import ApplicationDocument, EvaluationResult, SUBSCORE_AXES

def test_application_document_matches_frozen_schema_example():
    raw = json.loads(Path("context/schema-example.json").read_text(encoding="utf-8"))
    doc = ApplicationDocument(**raw)
    assert doc.model_dump(mode="json").keys() == raw.keys()
    assert doc.resume.experience[0].bullets

def test_application_document_rejects_unknown_field():
    with pytest.raises(ValidationError):
        ApplicationDocument(company_name="X", resume={}, cover_letter={}, score=9)

def test_evaluation_subscores_must_use_the_shared_axes():
    with pytest.raises(ValidationError):
        EvaluationResult(
            posting_id="a" * 64, refined_score=70.0,
            refined_subscores={"made_up_axis": 1.0},
            hard_pass=False, hard_pass_reason=None, rationale="x",
        )
    ok = EvaluationResult(
        posting_id="a" * 64, refined_score=70.0,
        refined_subscores={axis: 1.0 for axis in SUBSCORE_AXES},
        hard_pass=False, hard_pass_reason=None, rationale="x",
    )
    assert ok.refined_score == 70.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_models.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'pipeline.models'`

- [ ] **Step 3: Write minimal implementation**

```python
# pipeline/models.py
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

SUBSCORE_AXES = (
    "title_match", "country", "language", "remote", "seniority", "source_priority",
)


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PostingStub(Strict):
    posting_id: str
    identity_key: str
    canonical_url: str
    source: str
    company_raw: str
    title_raw: str
    location_raw: str = ""
    language: str = "en"
    remote_flag: bool = False
    salary_raw: str | None = None
    posted_at: str | None = None
    prelim_score: float | None = None
    prelim_subscores: dict[str, float] = Field(default_factory=dict)
    bypass_prelim_threshold: bool = False


class PostingDetail(Strict):
    posting_id: str
    jd_text: str
    jd_text_sha256: str
    jd_text_source: Literal["adapter", "page_fetch"]
    fetched_at: str


class EvaluationResult(Strict):
    posting_id: str
    refined_score: float
    refined_subscores: dict[str, float]
    hard_pass: bool
    hard_pass_reason: str | None = None
    company_size: int | None = None
    company_size_confidence: Literal["high", "low", "unknown"] = "unknown"
    salary_min_eur: int | None = None
    salary_max_eur: int | None = None
    jd_vocabulary: list[str] = Field(default_factory=list)
    capabilities_bought: list[str] = Field(default_factory=list)
    proof_systems: list[str] = Field(default_factory=list)
    red_flags: list[str] = Field(default_factory=list)
    rationale: str

    @field_validator("refined_subscores")
    @classmethod
    def _axes_must_match(cls, value: dict[str, float]) -> dict[str, float]:
        if set(value) != set(SUBSCORE_AXES):
            raise ValueError(
                f"refined_subscores axes {sorted(value)} must equal {sorted(SUBSCORE_AXES)}"
            )
        return value


class TailoringBrief(Strict):
    posting_id: str
    capabilities: list[str]
    jd_nouns: list[str]
    systems_to_lead: list[str]
    projects_to_include: list[str]
    carry_formula_dream: bool
    notes: str = ""


class SkillRow(Strict):
    label: str
    value: str


class ExperienceRow(Strict):
    title: str
    company: str
    period: str
    bullets: list[str]


class ProjectRow(Strict):
    name: str
    period: str
    bullets: list[str]


class EducationRow(Strict):
    degree: str
    school: str
    year: str


class ResumeBody(Strict):
    summary: str
    skills: list[SkillRow]
    experience: list[ExperienceRow]
    projects: list[ProjectRow]
    education: list[EducationRow]


class CoverLetterBody(Strict):
    date: str
    company_address: str
    salutation: str
    paragraphs: list[str]


class ApplicationDocument(Strict):
    company_name: str
    resume: ResumeBody
    cover_letter: CoverLetterBody


class RenderResult(Strict):
    posting_id: str
    resume_pdf: str
    cover_pdf: str
    page_count: int
    gate_b_status: Literal["ok", "failed"]


class SourceMetric(Strict):
    source: str
    n: int
    mae: float
    bias: float
    precision_at_threshold: float
    jd_text_coverage: float


class FetchQualityReport(Strict):
    run_id: str
    n: int
    mae: float
    bias: float
    spearman: float
    precision_at_threshold: float
    per_source: list[SourceMetric]
    per_query_term: dict[str, float]
    per_feature_divergence: dict[str, float]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_models.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add pipeline/models.py tests/test_models.py
git commit -m "feat: Pydantic boundary models with shared subscore axes"
```

---

### Task 6: Append-only store and the skip rule

**Files:**
- Create: `pipeline/store.py`
- Test: `tests/test_store.py`

**Interfaces:**
- Consumes: `PostingStub` from Task 5
- Produces: `Store(db_path)` with `.upsert_posting(stub)`, `.append_event(posting_id, stage, run_id, input_hash, status, artifact_ref=None, error_class=None, error_detail=None)`, `.should_run(posting_id, stage, input_hash) -> bool`, `.latest(posting_id, stage) -> Row | None`, `.mark_applied(identity_key, folder)`, `.already_applied(identity_key) -> bool`, `.record_call(...)`, `.stage_token_totals(run_id) -> dict[str, int]`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_store.py
import sqlite3

import pytest

from pipeline.store import Store

def make_store(tmp_path):
    return Store(tmp_path / "p.db")

def test_should_run_is_true_until_an_ok_event_exists(tmp_path):
    s = make_store(tmp_path)
    assert s.should_run("p1", "evaluate", "h1") is True
    s.append_event("p1", "evaluate", "r1", "h1", "ok")
    assert s.should_run("p1", "evaluate", "h1") is False

def test_a_changed_input_hash_reopens_the_work(tmp_path):
    s = make_store(tmp_path)
    s.append_event("p1", "evaluate", "r1", "h1", "ok")
    assert s.should_run("p1", "evaluate", "h2") is True

def test_a_failed_event_does_not_block_a_retry(tmp_path):
    s = make_store(tmp_path)
    s.append_event("p1", "evaluate", "r1", "h1", "permanent_fail")
    assert s.should_run("p1", "evaluate", "h1") is True

def test_events_are_append_only(tmp_path):
    s = make_store(tmp_path)
    s.append_event("p1", "evaluate", "r1", "h1", "transient_fail")
    s.append_event("p1", "evaluate", "r1", "h1", "ok")
    rows = s.all_events("p1", "evaluate")
    assert [r["status"] for r in rows] == ["transient_fail", "ok"]

def test_update_and_delete_on_stage_events_are_refused(tmp_path):
    s = make_store(tmp_path)
    s.append_event("p1", "evaluate", "r1", "h1", "ok")
    with pytest.raises(sqlite3.IntegrityError):
        s.conn.execute("UPDATE stage_events SET status='x' WHERE posting_id='p1'")
    with pytest.raises(sqlite3.IntegrityError):
        s.conn.execute("DELETE FROM stage_events WHERE posting_id='p1'")

def test_applied_is_keyed_on_identity_not_posting(tmp_path):
    s = make_store(tmp_path)
    s.mark_applied("ik1", "applications/2026-09-01_acme_ai-engineer")
    assert s.already_applied("ik1") is True
    assert s.already_applied("ik2") is False

def test_stage_token_totals_aggregates_by_stage(tmp_path):
    s = make_store(tmp_path)
    s.record_call(run_id="r1", posting_id="p1", stage="evaluate", model="m",
                  prompt_hash="p", input_tokens=100, output_tokens=50,
                  cache_creation_input_tokens=0, cache_read_input_tokens=900,
                  cost_usd=0.01, latency_ms=10, trace_id="t1")
    s.record_call(run_id="r1", posting_id="p2", stage="generate", model="m",
                  prompt_hash="p", input_tokens=200, output_tokens=100,
                  cache_creation_input_tokens=0, cache_read_input_tokens=0,
                  cost_usd=0.05, latency_ms=20, trace_id="t2")
    assert s.stage_token_totals("r1") == {"evaluate": 1050, "generate": 300}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_store.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'pipeline.store'`

- [ ] **Step 3: Write minimal implementation**

```python
# pipeline/store.py
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from pipeline.models import PostingStub

SCHEMA = """
CREATE TABLE IF NOT EXISTS postings (
  posting_id TEXT PRIMARY KEY, identity_key TEXT NOT NULL,
  canonical_url TEXT NOT NULL, duplicate_of TEXT, first_seen_run TEXT,
  source TEXT, company_raw TEXT, title_raw TEXT, location_raw TEXT,
  language TEXT, remote_flag INTEGER, salary_raw TEXT, posted_at TEXT,
  prelim_score REAL, prelim_subscores TEXT
);
CREATE TABLE IF NOT EXISTS stage_events (
  event_id INTEGER PRIMARY KEY AUTOINCREMENT,
  posting_id TEXT NOT NULL, stage TEXT NOT NULL, run_id TEXT NOT NULL,
  input_hash TEXT NOT NULL, status TEXT NOT NULL,
  started_at TEXT, finished_at TEXT, artifact_ref TEXT,
  error_class TEXT, error_detail TEXT
);
CREATE INDEX IF NOT EXISTS ix_events ON stage_events(posting_id, stage, input_hash);

-- The append-only invariant is enforced by the database, not by convention.
CREATE TRIGGER IF NOT EXISTS stage_events_no_update
BEFORE UPDATE ON stage_events
BEGIN SELECT RAISE(ABORT, 'stage_events is append-only'); END;
CREATE TRIGGER IF NOT EXISTS stage_events_no_delete
BEFORE DELETE ON stage_events
BEGIN SELECT RAISE(ABORT, 'stage_events is append-only'); END;

CREATE TABLE IF NOT EXISTS runs (
  run_id TEXT PRIMARY KEY, started_at TEXT, finished_at TEXT,
  config_hash TEXT, tokens_used INTEGER DEFAULT 0,
  usd_spent REAL DEFAULT 0, halted_reason TEXT
);
CREATE TABLE IF NOT EXISTS llm_calls (
  call_id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT, posting_id TEXT,
  stage TEXT, model TEXT, prompt_hash TEXT, trace_id TEXT,
  input_tokens INTEGER, output_tokens INTEGER,
  cache_creation_input_tokens INTEGER, cache_read_input_tokens INTEGER,
  cost_usd REAL, latency_ms INTEGER, created_at TEXT
);
CREATE TABLE IF NOT EXISTS applied (
  identity_key TEXT PRIMARY KEY, employer_folder TEXT, applied_at TEXT
);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Store:
    def __init__(self, db_path: Path):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def upsert_posting(self, stub: PostingStub, run_id: str,
                       duplicate_of: str | None = None) -> None:
        import json
        self.conn.execute(
            """INSERT INTO postings (posting_id, identity_key, canonical_url,
                 duplicate_of, first_seen_run, source, company_raw, title_raw,
                 location_raw, language, remote_flag, salary_raw, posted_at,
                 prelim_score, prelim_subscores)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
               ON CONFLICT(posting_id) DO NOTHING""",
            (stub.posting_id, stub.identity_key, stub.canonical_url, duplicate_of,
             run_id, stub.source, stub.company_raw, stub.title_raw,
             stub.location_raw, stub.language, int(stub.remote_flag),
             stub.salary_raw, stub.posted_at, stub.prelim_score,
             json.dumps(stub.prelim_subscores, sort_keys=True)),
        )
        self.conn.commit()

    def append_event(self, posting_id: str, stage: str, run_id: str,
                     input_hash: str, status: str, artifact_ref: str | None = None,
                     error_class: str | None = None,
                     error_detail: str | None = None) -> None:
        self.conn.execute(
            """INSERT INTO stage_events (posting_id, stage, run_id, input_hash,
                 status, started_at, finished_at, artifact_ref, error_class, error_detail)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (posting_id, stage, run_id, input_hash, status, _now(), _now(),
             artifact_ref, error_class, error_detail),
        )
        self.conn.commit()

    def should_run(self, posting_id: str, stage: str, input_hash: str) -> bool:
        row = self.conn.execute(
            """SELECT 1 FROM stage_events
               WHERE posting_id=? AND stage=? AND input_hash=? AND status='ok'
               LIMIT 1""",
            (posting_id, stage, input_hash),
        ).fetchone()
        return row is None

    def latest(self, posting_id: str, stage: str) -> sqlite3.Row | None:
        return self.conn.execute(
            """SELECT * FROM stage_events WHERE posting_id=? AND stage=?
               ORDER BY event_id DESC LIMIT 1""",
            (posting_id, stage),
        ).fetchone()

    def all_events(self, posting_id: str, stage: str) -> list[sqlite3.Row]:
        return list(self.conn.execute(
            "SELECT * FROM stage_events WHERE posting_id=? AND stage=? ORDER BY event_id",
            (posting_id, stage),
        ))

    def mark_applied(self, identity_key: str, folder: str) -> None:
        self.conn.execute(
            "INSERT OR IGNORE INTO applied VALUES (?,?,?)",
            (identity_key, folder, _now()),
        )
        self.conn.commit()

    def already_applied(self, identity_key: str) -> bool:
        return self.conn.execute(
            "SELECT 1 FROM applied WHERE identity_key=?", (identity_key,)
        ).fetchone() is not None

    def record_call(self, **kw) -> None:
        self.conn.execute(
            """INSERT INTO llm_calls (run_id, posting_id, stage, model, prompt_hash,
                 trace_id, input_tokens, output_tokens, cache_creation_input_tokens,
                 cache_read_input_tokens, cost_usd, latency_ms, created_at)
               VALUES (:run_id,:posting_id,:stage,:model,:prompt_hash,:trace_id,
                 :input_tokens,:output_tokens,:cache_creation_input_tokens,
                 :cache_read_input_tokens,:cost_usd,:latency_ms,:created_at)""",
            {**kw, "created_at": _now()},
        )
        self.conn.commit()

    def stage_token_totals(self, run_id: str) -> dict[str, int]:
        rows = self.conn.execute(
            """SELECT stage, SUM(input_tokens + output_tokens
                 + cache_creation_input_tokens + cache_read_input_tokens) AS total
               FROM llm_calls WHERE run_id=? GROUP BY stage""",
            (run_id,),
        )
        return {r["stage"]: int(r["total"]) for r in rows}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_store.py -v`
Expected: 7 passed

- [ ] **Step 5: Commit**

```bash
git add pipeline/store.py tests/test_store.py
git commit -m "feat: append-only store with database-enforced invariant and skip rule"
```

---

### Task 7: Facts derivation from CLAUDE.md and the hash gate

**Files:**
- Create: `pipeline/facts.py`, `config/facts_curated.yaml`
- Test: `tests/test_facts.py`

**Interfaces:**
- Consumes: nothing
- Produces: `derive_facts(claude_md_text: str) -> DerivedFacts`; `DerivedFacts` with `.companies`, `.titles`, `.periods`, `.education`, `.allowed_numbers`; `load_curated(path) -> CuratedFacts`; `assert_facts_current(claude_md_path, curated) -> None` raising `FactsDriftError`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_facts.py
import pytest

from pipeline.facts import (
    CuratedFacts, FactsDriftError, assert_facts_current, derive_facts,
)

SAMPLE = """
# PART 1 - WHO HE IS
**Audience number:** 10M+ views, 26K Instagram followers.

# PART 2 - EXPERIENCE

## Manager, AI & Automation - Corominas Consulting
**Remote, Germany | Jun 2026 - Sep 2026**

- Owned the automation layer across a portfolio of roughly 85 client sites
- Built the deterministic gate: 18 automated checks across 10 families

## AI Engineer - Think Round Inc
**Remote, US | Apr 2025 - Mar 2026**

- Built Zoe, a production trauma-informed AI companion

# PART 3 - JUDGMENT
"""

def test_derives_companies_titles_and_periods():
    facts = derive_facts(SAMPLE)
    assert "Corominas Consulting" in facts.companies
    assert "Manager, AI & Automation" in facts.titles
    assert "Jun 2026 - Sep 2026" in facts.periods

def test_allowed_numbers_come_from_the_source_not_a_stored_list():
    facts = derive_facts(SAMPLE)
    assert "10M+" in facts.allowed_numbers
    assert "26K" in facts.allowed_numbers
    assert "85" in facts.allowed_numbers
    assert "18" in facts.allowed_numbers
    assert "176K" not in facts.allowed_numbers

def test_hash_mismatch_halts_before_any_call(tmp_path):
    md = tmp_path / "CLAUDE.md"
    md.write_text(SAMPLE, encoding="utf-8")
    curated = CuratedFacts(
        claude_md_sha256="0" * 64,
        forbidden_strings=["fixed-term"], domain_tokens=["SEO"],
        number_aliases={},
    )
    with pytest.raises(FactsDriftError) as exc:
        assert_facts_current(md, curated)
    assert "pipeline facts sync" in str(exc.value)

def test_matching_hash_passes(tmp_path):
    import hashlib
    md = tmp_path / "CLAUDE.md"
    md.write_text(SAMPLE, encoding="utf-8")
    digest = hashlib.sha256(md.read_bytes()).hexdigest()
    curated = CuratedFacts(claude_md_sha256=digest, forbidden_strings=[],
                           domain_tokens=[], number_aliases={})
    assert_facts_current(md, curated)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_facts.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'pipeline.facts'`

- [ ] **Step 3: Write minimal implementation**

```python
# pipeline/facts.py
import re
from pathlib import Path

import yaml
from pydantic import BaseModel

from pipeline.hashing import file_hash

ROLE_HEADING = re.compile(r"^##\s+(?P<title>.+?)\s+-\s+(?P<company>.+?)\s*$", re.M)
PERIOD = re.compile(r"\|\s*(?P<period>[A-Z][a-z]{2}\s+\d{4}\s+-\s+(?:[A-Z][a-z]{2}\s+\d{4}|Present))")
NUMBER = re.compile(r"\b\d[\d,.]*\s*(?:M\+|K\+|M|K|%|\+)?\b")


class DerivedFacts(BaseModel):
    companies: list[str]
    titles: list[str]
    periods: list[str]
    education: list[str]
    allowed_numbers: set[str]


class CuratedFacts(BaseModel):
    claude_md_sha256: str
    forbidden_strings: list[str]
    domain_tokens: list[str]
    number_aliases: dict[str, str]


class FactsDriftError(RuntimeError):
    pass


def _part_slice(text: str) -> str:
    """PART 1 and PART 2 only. PART 3 onward is judgment, not claimable fact."""
    start = text.find("# PART 1")
    end = text.find("# PART 3")
    return text[start if start >= 0 else 0: end if end > 0 else len(text)]


def derive_facts(claude_md_text: str) -> DerivedFacts:
    scope = _part_slice(claude_md_text)
    companies, titles = [], []
    for m in ROLE_HEADING.finditer(scope):
        titles.append(m.group("title").strip())
        companies.append(m.group("company").strip())
    periods = [m.group("period").strip() for m in PERIOD.finditer(scope)]
    education = re.findall(r"^-\s+(M\.?S\.?|MS|BTech|Bachelor|Master).*$", scope, re.M)
    numbers = {re.sub(r"\s+", "", n) for n in NUMBER.findall(scope)}
    return DerivedFacts(
        companies=companies, titles=titles, periods=periods,
        education=education, allowed_numbers=numbers,
    )


def load_curated(path: Path) -> CuratedFacts:
    return CuratedFacts(**yaml.safe_load(path.read_text(encoding="utf-8")))


def assert_facts_current(claude_md_path: Path, curated: CuratedFacts) -> None:
    """Halt the run before any LLM call when CLAUDE.md has moved. The derived
    block is always regenerated in memory, so it cannot go stale; this gate
    forces a deliberate look at whether the curated block still holds."""
    actual = file_hash(claude_md_path)
    if actual != curated.claude_md_sha256:
        raise FactsDriftError(
            f"CLAUDE.md hash {actual[:12]} does not match "
            f"facts_curated.yaml {curated.claude_md_sha256[:12]}. "
            f"Run `pipeline facts sync` to review the diff and rewrite the hash."
        )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_facts.py -v`
Expected: 4 passed

- [ ] **Step 5: Write the curated file**

```yaml
# config/facts_curated.yaml
claude_md_sha256: "REPLACE_BY_RUNNING_pipeline_facts_sync"
forbidden_strings:
  - "fixed-term"
  - "befristet"
  - "176K"
  - "50K+"
domain_tokens: [SEO, WordPress, "law firm", "content marketing", "social media", articles]
number_aliases:
  "10 million": "10M"
  "10M+": "10M"
  "26,000": "26K"
```

The `claude_md_sha256` placeholder is written by `pipeline facts sync` in Task 18; until then every run halts, which is the intended default.

- [ ] **Step 6: Commit**

```bash
git add pipeline/facts.py config/facts_curated.yaml tests/test_facts.py
git commit -m "feat: derive facts from CLAUDE.md with a hard-fail drift gate"
```

---

### Task 8: Deterministic preliminary scorer

**Files:**
- Create: `pipeline/scoring.py`
- Test: `tests/test_scoring.py`

**Interfaces:**
- Consumes: `Scoring`, `Constraints` (Task 1), `PostingStub`, `SUBSCORE_AXES` (Task 5)
- Produces: `score_prelim(stub: PostingStub, scoring: Scoring, constraints: Constraints, source_priority: dict[str, float]) -> tuple[float, dict[str, float]]`; `stage_one_filter(stub, constraints, applied_check) -> str | None`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_scoring.py
from pipeline.config import Constraints, Scoring
from pipeline.models import SUBSCORE_AXES, PostingStub
from pipeline.scoring import score_prelim, stage_one_filter

CONSTRAINTS = Constraints(
    salary_floor_eur=65000, countries=["remote", "DE", "NL"],
    working_languages=["en", "de"], min_employees=100,
    target_titles=["AI Engineer", "Automation Engineer"],
)
SCORING = Scoring(threshold=60.0, weights={a: 1 / len(SUBSCORE_AXES) for a in SUBSCORE_AXES})

def stub(**kw) -> PostingStub:
    base = dict(posting_id="p", identity_key="i", canonical_url="u", source="arbeitnow",
                company_raw="Acme", title_raw="AI Engineer", location_raw="Berlin, Germany",
                language="en", remote_flag=True)
    return PostingStub(**{**base, **kw})

def test_score_is_between_0_and_100_and_uses_every_axis():
    score, subs = score_prelim(stub(), SCORING, CONSTRAINTS, {"arbeitnow": 1.0})
    assert 0.0 <= score <= 100.0
    assert set(subs) == set(SUBSCORE_AXES)

def test_matching_title_scores_above_unrelated_title():
    good, _ = score_prelim(stub(title_raw="AI Engineer"), SCORING, CONSTRAINTS, {"arbeitnow": 1.0})
    bad, _ = score_prelim(stub(title_raw="Office Manager"), SCORING, CONSTRAINTS, {"arbeitnow": 1.0})
    assert good > bad

def test_filter_rejects_only_on_positive_evidence():
    # Salary known and below floor: rejected.
    assert stage_one_filter(stub(salary_raw="45000 EUR"), CONSTRAINTS, lambda k: False) == "below_salary_floor"
    # Salary unknown: never rejected here, deferred to Stage 2.
    assert stage_one_filter(stub(salary_raw=None), CONSTRAINTS, lambda k: False) is None

def test_filter_rejects_out_of_scope_country_and_already_applied():
    assert stage_one_filter(
        stub(location_raw="Tokyo, Japan", remote_flag=False), CONSTRAINTS, lambda k: False
    ) == "country_out_of_scope"
    assert stage_one_filter(stub(), CONSTRAINTS, lambda k: True) == "already_applied"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_scoring.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'pipeline.scoring'`

- [ ] **Step 3: Write minimal implementation**

```python
# pipeline/scoring.py
import re
from typing import Callable

from pipeline.config import Constraints, Scoring
from pipeline.identity import normalise_country, normalise_title, title_similarity
from pipeline.models import SUBSCORE_AXES, PostingStub

SENIOR_TOKENS = ("senior", "lead", "staff", "principal")
JUNIOR_TOKENS = ("intern", "working student", "werkstudent", "praktikum")
SALARY = re.compile(r"(\d[\d.,]{3,})")


def _salary_eur(raw: str | None) -> int | None:
    if not raw:
        return None
    hits = [int(h.replace(".", "").replace(",", "")) for h in SALARY.findall(raw)]
    hits = [h for h in hits if 10_000 <= h <= 500_000]
    return min(hits) if hits else None


def score_prelim(stub: PostingStub, scoring: Scoring, constraints: Constraints,
                 source_priority: dict[str, float]) -> tuple[float, dict[str, float]]:
    """Deterministic, zero cost, no model call. The feedback loop needs a
    machine-adjustable scorer: weights can be moved and the change read
    afterwards. A prompt cannot be tuned that way."""
    title = normalise_title(stub.title_raw)
    subs = {
        "title_match": max(
            (title_similarity(title, t) for t in constraints.target_titles), default=0.0
        ),
        "country": 1.0 if normalise_country(stub.location_raw, stub.remote_flag)
        in constraints.countries else 0.0,
        "language": 1.0 if stub.language in constraints.working_languages else 0.0,
        "remote": 1.0 if stub.remote_flag else 0.4,
        "seniority": 0.0 if any(t in title for t in JUNIOR_TOKENS)
        else (1.0 if any(t in title for t in SENIOR_TOKENS) else 0.7),
        "source_priority": source_priority.get(stub.source, 0.5),
    }
    assert set(subs) == set(SUBSCORE_AXES)
    total = sum(scoring.weights.get(axis, 0.0) * value for axis, value in subs.items())
    denom = sum(scoring.weights.get(axis, 0.0) for axis in SUBSCORE_AXES) or 1.0
    return round(100.0 * total / denom, 2), subs


def stage_one_filter(stub: PostingStub, constraints: Constraints,
                     already_applied: Callable[[str], bool]) -> str | None:
    """Reject only on positive evidence. A missing field defers to Stage 2;
    a posting with no salary metadata is not below the floor, it is unknown."""
    if already_applied(stub.identity_key):
        return "already_applied"
    country = normalise_country(stub.location_raw, stub.remote_flag)
    if country != "unknown" and country not in constraints.countries:
        return "country_out_of_scope"
    salary = _salary_eur(stub.salary_raw)
    if salary is not None and salary < constraints.salary_floor_eur:
        return "below_salary_floor"
    if stub.language and stub.language not in constraints.working_languages:
        return "language_out_of_scope"
    return None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_scoring.py -v`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add pipeline/scoring.py tests/test_scoring.py
git commit -m "feat: deterministic prelim scorer and evidence-only Stage 1 filters"
```

---

### Task 9: Traced LLM client with prompt caching and a hard budget

**Files:**
- Create: `pipeline/llm.py`
- Test: `tests/test_llm.py`

**Interfaces:**
- Consumes: `Budget` (Task 1), `Store.record_call` (Task 6)
- Produces: `LLMClient(anthropic_client, store, budget, run_id, langfuse=None)` with `.call(stage, posting_id, static_system, varying_user, response_model, model, effort) -> tuple[BaseModel, CallUsage]`; `BudgetExceeded`; `PRICING`; `cache_hit_ratio(store, run_id) -> float`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_llm.py
import pytest
from pydantic import BaseModel

from pipeline.config import Budget
from pipeline.llm import BudgetExceeded, LLMClient, cache_hit_ratio
from pipeline.store import Store


class Out(BaseModel):
    value: int


class FakeUsage:
    def __init__(self, i=1000, o=100, cc=0, cr=0):
        self.input_tokens, self.output_tokens = i, o
        self.cache_creation_input_tokens, self.cache_read_input_tokens = cc, cr


class FakeParsed:
    def __init__(self, usage):
        self.parsed_output, self.usage = Out(value=1), usage


class FakeMessages:
    def __init__(self, usage):
        self._usage, self.last_kwargs = usage, None

    def parse(self, **kwargs):
        self.last_kwargs = kwargs
        return FakeParsed(self._usage)


class FakeAnthropic:
    def __init__(self, usage):
        self.messages = FakeMessages(usage)


def client(tmp_path, usage, max_usd=10.0):
    store = Store(tmp_path / "p.db")
    fake = FakeAnthropic(usage)
    return LLMClient(fake, store, Budget(max_usd_per_run=max_usd,
                                         max_tokens_per_run=10_000_000), "r1"), store, fake

def test_static_block_carries_the_only_cache_breakpoint(tmp_path):
    llm, _, fake = client(tmp_path, FakeUsage())
    llm.call("evaluate", "p1", "STATIC", "VARYING", Out, "claude-sonnet-5", "low")
    system = fake.messages.last_kwargs["system"]
    assert system[-1]["cache_control"] == {"type": "ephemeral"}
    assert "VARYING" not in str(system)
    assert "VARYING" in str(fake.messages.last_kwargs["messages"])

def test_usage_is_mirrored_locally(tmp_path):
    llm, store, _ = client(tmp_path, FakeUsage(i=1000, o=100, cr=4000))
    llm.call("evaluate", "p1", "S", "V", Out, "claude-sonnet-5", "low")
    row = store.conn.execute("SELECT * FROM llm_calls").fetchone()
    assert row["cache_read_input_tokens"] == 4000
    assert row["cost_usd"] > 0

def test_run_halts_rather_than_overrunning_the_budget(tmp_path):
    llm, _, _ = client(tmp_path, FakeUsage(i=1_000_000, o=1_000_000), max_usd=0.01)
    with pytest.raises(BudgetExceeded):
        for _ in range(5):
            llm.call("evaluate", "p1", "S", "V", Out, "claude-sonnet-5", "low")

def test_cache_hit_ratio_is_reported(tmp_path):
    llm, store, _ = client(tmp_path, FakeUsage(i=100, o=10, cr=900))
    llm.call("evaluate", "p1", "S", "V", Out, "claude-sonnet-5", "low")
    assert cache_hit_ratio(store, "r1") == pytest.approx(0.9, abs=0.01)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_llm.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'pipeline.llm'`

- [ ] **Step 3: Write minimal implementation**

```python
# pipeline/llm.py
import time
from typing import TypeVar

from pydantic import BaseModel

from pipeline.config import Budget
from pipeline.hashing import text_hash
from pipeline.store import Store

T = TypeVar("T", bound=BaseModel)

# USD per million tokens: (input, output). Cache reads bill at 0.1x input.
PRICING = {
    "claude-sonnet-5": (2.00, 10.00),
    "claude-opus-5": (5.00, 25.00),
}


class BudgetExceeded(RuntimeError):
    pass


class CallUsage(BaseModel):
    input_tokens: int
    output_tokens: int
    cache_creation_input_tokens: int
    cache_read_input_tokens: int
    cost_usd: float
    latency_ms: int


def _cost(model: str, u) -> float:
    inp, out = PRICING[model]
    return (
        u.input_tokens * inp
        + u.cache_creation_input_tokens * inp * 1.25
        + u.cache_read_input_tokens * inp * 0.10
        + u.output_tokens * out
    ) / 1_000_000


class LLMClient:
    """The single path every model call takes. Owns tracing, the local usage
    mirror, prompt-cache placement, and the run budget."""

    def __init__(self, anthropic_client, store: Store, budget: Budget,
                 run_id: str, langfuse=None):
        self.client = anthropic_client
        self.store = store
        self.budget = budget
        self.run_id = run_id
        self.langfuse = langfuse
        self.spent_usd = 0.0
        self.spent_tokens = 0

    def _check_budget(self) -> None:
        if self.spent_usd >= self.budget.max_usd_per_run:
            raise BudgetExceeded(
                f"run budget {self.budget.max_usd_per_run} USD reached "
                f"at {self.spent_usd:.4f}; halting so the next run resumes free"
            )
        if self.spent_tokens >= self.budget.max_tokens_per_run:
            raise BudgetExceeded(f"run token budget reached at {self.spent_tokens}")

    def call(self, stage: str, posting_id: str, static_system: str,
             varying_user: str, response_model: type[T], model: str,
             effort: str) -> tuple[T, CallUsage]:
        self._check_budget()
        started = time.monotonic()
        result = self.client.messages.parse(
            model=model,
            max_tokens=16000,
            output_config={"effort": effort, "format": response_model},
            # The breakpoint sits at the end of the shared static portion.
            # Nothing per-posting, no run id, no date, may appear above it.
            system=[{
                "type": "text",
                "text": static_system,
                "cache_control": {"type": "ephemeral"},
            }],
            messages=[{"role": "user", "content": varying_user}],
        )
        latency_ms = int((time.monotonic() - started) * 1000)
        raw = result.usage
        usage = CallUsage(
            input_tokens=raw.input_tokens,
            output_tokens=raw.output_tokens,
            cache_creation_input_tokens=raw.cache_creation_input_tokens,
            cache_read_input_tokens=raw.cache_read_input_tokens,
            cost_usd=_cost(model, raw),
            latency_ms=latency_ms,
        )
        self.spent_usd += usage.cost_usd
        self.spent_tokens += (
            usage.input_tokens + usage.output_tokens
            + usage.cache_creation_input_tokens + usage.cache_read_input_tokens
        )
        trace_id = self._trace(stage, posting_id, static_system, varying_user,
                               result.parsed_output, model, usage)
        self.store.record_call(
            run_id=self.run_id, posting_id=posting_id, stage=stage, model=model,
            prompt_hash=text_hash(static_system), trace_id=trace_id,
            input_tokens=usage.input_tokens, output_tokens=usage.output_tokens,
            cache_creation_input_tokens=usage.cache_creation_input_tokens,
            cache_read_input_tokens=usage.cache_read_input_tokens,
            cost_usd=usage.cost_usd, latency_ms=usage.latency_ms,
        )
        return result.parsed_output, usage

    def _trace(self, stage, posting_id, static_system, varying_user,
               output, model, usage) -> str | None:
        """Three levels: session per posting, trace per stage, generation per
        call. A Langfuse outage degrades to the local mirror, never blocks."""
        if self.langfuse is None:
            return None
        try:
            trace = self.langfuse.trace(
                name=f"{stage}", session_id=posting_id,
                tags=[self.run_id, stage],
                metadata={"run_id": self.run_id},
            )
            trace.generation(
                name=f"{stage}.call", model=model,
                input={"system": static_system, "user": varying_user},
                output=output.model_dump(mode="json"),
                usage={"input": usage.input_tokens, "output": usage.output_tokens},
                metadata={
                    "cost_usd": usage.cost_usd,
                    "cache_read_input_tokens": usage.cache_read_input_tokens,
                    "cache_creation_input_tokens": usage.cache_creation_input_tokens,
                    "prompt_hash": text_hash(static_system),
                },
            )
            return trace.id
        except Exception:
            return None


def cache_hit_ratio(store: Store, run_id: str) -> float:
    """Near zero across a batch means a silent cache invalidator is present.
    The failure mode has no error, only a cost multiple, so it is reported."""
    row = store.conn.execute(
        """SELECT SUM(cache_read_input_tokens) AS reads,
                  SUM(cache_read_input_tokens + cache_creation_input_tokens
                      + input_tokens) AS total
           FROM llm_calls WHERE run_id=?""",
        (run_id,),
    ).fetchone()
    total = row["total"] or 0
    return (row["reads"] or 0) / total if total else 0.0
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_llm.py -v`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add pipeline/llm.py tests/test_llm.py
git commit -m "feat: traced LLM client with cache breakpoint, local mirror and budget halt"
```

---

### Task 10: Source adapter interface, one discovery adapter, manual injection

**Files:**
- Create: `pipeline/sources/__init__.py`, `pipeline/sources/base.py`, `pipeline/sources/arbeitnow.py`, `pipeline/sources/manual.py`, `config/sources.yaml`
- Test: `tests/test_sources.py`, `tests/fixtures/arbeitnow_page.json`

**Interfaces:**
- Consumes: `PostingStub` (Task 5), `canonicalise_url`, `identity_key_for` (Tasks 2 and 3)
- Produces: `RawPosting`; `Source` protocol with `.name`, `.fetch(http, query, since) -> list[RawPosting]`; `to_stub(raw, strip_params) -> PostingStub`; `ArbeitnowSource`; `ManualSource(urls: list[str])`; `ShapeError`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_sources.py
import json
from pathlib import Path

import pytest

from pipeline.sources.arbeitnow import ArbeitnowSource
from pipeline.sources.base import ShapeError, to_stub
from pipeline.sources.manual import ManualSource

FIXTURE = Path("tests/fixtures/arbeitnow_page.json")


class FakeHTTP:
    def __init__(self, payload):
        self.payload = payload

    def get(self, url, **kw):
        class R:
            status_code = 200
            def json(_): return self.payload
            def raise_for_status(_): return None
        return R()


def test_adapter_maps_payload_to_raw_postings():
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    raws = ArbeitnowSource().fetch(FakeHTTP(payload), query="ai engineer", since=None)
    assert len(raws) == 2
    assert raws[0].title and raws[0].company and raws[0].url

def test_adapter_fails_loudly_on_an_unexpected_shape():
    with pytest.raises(ShapeError):
        ArbeitnowSource().fetch(FakeHTTP({"unexpected": []}), query="x", since=None)

def test_to_stub_assigns_identity_and_posting_id():
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    raw = ArbeitnowSource().fetch(FakeHTTP(payload), query="x", since=None)[0]
    stub = to_stub(raw, strip_params=["ref"])
    assert len(stub.posting_id) == 64 and len(stub.identity_key) == 64
    assert stub.source == "arbeitnow"

def test_manual_source_bypasses_the_prelim_threshold():
    raws = ManualSource(["https://careers.example.com/jobs/7"]).fetch(None, None, None)
    stub = to_stub(raws[0], strip_params=[])
    assert stub.source == "manual"
    assert stub.prelim_score is None
    assert stub.bypass_prelim_threshold is True
```

Fixture, written by hand from the documented response shape:

```json
{
  "data": [
    {"slug": "ai-engineer-acme", "company_name": "Acme Robotics GmbH",
     "title": "AI Engineer (m/w/d)", "location": "Berlin, Germany",
     "remote": true, "url": "https://www.arbeitnow.com/jobs/ai-engineer-acme",
     "created_at": 1756684800, "description": "<p>Full description here</p>"},
    {"slug": "automation-engineer-borg", "company_name": "Borg BV",
     "title": "Automation Engineer", "location": "Amsterdam, Netherlands",
     "remote": false, "url": "https://www.arbeitnow.com/jobs/automation-engineer-borg",
     "created_at": 1756684800, "description": "<p>Another description</p>"}
  ]
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_sources.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'pipeline.sources'`

- [ ] **Step 3: Write minimal implementation**

```python
# pipeline/sources/base.py
import re
from typing import Protocol

from pydantic import BaseModel

from pipeline.identity import canonicalise_url, identity_key_for, posting_id_for
from pipeline.models import PostingStub

TAG = re.compile(r"<[^>]+>")


class ShapeError(RuntimeError):
    """A source changed its response shape. Fail loudly: an adapter that
    silently returns an empty list looks identical to a quiet job market."""


class RawPosting(BaseModel):
    source: str
    url: str
    company: str
    title: str
    location: str = ""
    remote: bool = False
    language: str = "en"
    salary_raw: str | None = None
    posted_at: str | None = None
    jd_text: str | None = None
    manual: bool = False


class Source(Protocol):
    name: str

    def fetch(self, http, query: str | None, since) -> list[RawPosting]: ...


def strip_html(text: str | None) -> str | None:
    return None if text is None else TAG.sub(" ", text).strip()


def to_stub(raw: RawPosting, strip_params: list[str]) -> PostingStub:
    return PostingStub(
        posting_id=posting_id_for(raw.url, strip_params),
        identity_key=identity_key_for(raw.company, raw.title, raw.location, raw.remote),
        canonical_url=canonicalise_url(raw.url, strip_params),
        source=raw.source, company_raw=raw.company, title_raw=raw.title,
        location_raw=raw.location, language=raw.language, remote_flag=raw.remote,
        salary_raw=raw.salary_raw, posted_at=raw.posted_at,
        bypass_prelim_threshold=raw.manual,
    )
```

```python
# pipeline/sources/arbeitnow.py
from datetime import datetime, timezone

from pipeline.sources.base import RawPosting, ShapeError, strip_html

ENDPOINT = "https://www.arbeitnow.com/api/job-board-api"


class ArbeitnowSource:
    name = "arbeitnow"

    def fetch(self, http, query: str | None, since) -> list[RawPosting]:
        response = http.get(ENDPOINT, params={"search": query} if query else None)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict) or "data" not in payload:
            raise ShapeError(f"{self.name}: expected a 'data' key, got {list(payload)[:5]}")
        out = []
        for item in payload["data"]:
            try:
                out.append(RawPosting(
                    source=self.name, url=item["url"], company=item["company_name"],
                    title=item["title"], location=item.get("location", ""),
                    remote=bool(item.get("remote", False)),
                    jd_text=strip_html(item.get("description")),
                    posted_at=datetime.fromtimestamp(
                        item["created_at"], tz=timezone.utc).isoformat()
                    if item.get("created_at") else None,
                ))
            except KeyError as exc:
                raise ShapeError(f"{self.name}: missing field {exc}") from exc
        return out
```

```python
# pipeline/sources/manual.py
from urllib.parse import urlsplit

from pipeline.sources.base import RawPosting


class ManualSource:
    """URLs pasted by hand, from the INBOX tab or config/manual_urls.txt.
    The only path by which a platform excluded from programmatic fetching
    reaches the pipeline. No prelim score, so it never enters tuning metrics."""

    name = "manual"

    def __init__(self, urls: list[str]):
        self.urls = [u.strip() for u in urls if u.strip()]

    def fetch(self, http, query, since) -> list[RawPosting]:
        return [
            RawPosting(source=self.name, url=url, manual=True,
                       company=urlsplit(url).netloc, title="unknown")
            for url in self.urls
        ]
```

```yaml
# config/sources.yaml
priority:
  manual: 1.0
  arbeitnow: 0.6

enabled:
  - name: arbeitnow
    adapter: arbeitnow
    queries: ["ai engineer", "automation engineer", "solutions engineer"]
    rate_limit_per_minute: 30
    # Terms verified <date> by <who>: public job-board API, no key required.

excluded:
  - name: linkedin
    reason: terms prohibit automated access; reachable only via manual injection
  - name: indeed
    reason: terms prohibit automated access; reachable only via manual injection
  - name: glassdoor
    reason: terms prohibit automated access; reachable only via manual injection
  - name: stepstone
    reason: terms prohibit automated access; reachable only via manual injection
  - name: xing
    reason: terms prohibit automated access; reachable only via manual injection
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_sources.py -v`
Expected: 4 passed

- [ ] **Step 5: Verify the live source before shipping it**

Run: `python -c "import httpx,json;r=httpx.get('https://www.arbeitnow.com/api/job-board-api',timeout=30);print(r.status_code, list(r.json())[:3])"`

Confirm the shape matches the fixture. Read the source's terms of use and record the verification date and outcome in the `sources.yaml` comment. **If terms do not permit programmatic access, delete the adapter rather than ship it.**

- [ ] **Step 6: Commit**

```bash
git add pipeline/sources/ config/sources.yaml tests/test_sources.py tests/fixtures/
git commit -m "feat: source adapter interface, arbeitnow adapter, manual injection"
```

---

### Task 11: Stage 1 fetch, with dedupe clustering

**Files:**
- Create: `pipeline/stages/__init__.py`, `pipeline/stages/fetch.py`
- Test: `tests/test_stage_fetch.py`

**Interfaces:**
- Consumes: Tasks 1, 2, 3, 5, 6, 8, 10
- Produces: `run_fetch(sources, http, store, config, source_priority, run_id) -> FetchOutcome`; `FetchOutcome` with `.new`, `.duplicates`, `.filtered`, `.near_misses`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_stage_fetch.py
from pipeline.config import Budget, Config, Constraints, Scoring
from pipeline.models import SUBSCORE_AXES
from pipeline.sources.base import RawPosting
from pipeline.stages.fetch import run_fetch
from pipeline.store import Store


class StubSource:
    def __init__(self, name, raws):
        self.name, self._raws = name, raws

    def fetch(self, http, query, since):
        return self._raws


def cfg():
    return Config(
        constraints=Constraints(salary_floor_eur=65000, countries=["DE", "remote"],
                                working_languages=["en"], min_employees=100,
                                target_titles=["AI Engineer"]),
        scoring=Scoring(threshold=60.0,
                        weights={a: 1 / len(SUBSCORE_AXES) for a in SUBSCORE_AXES}),
        budget=Budget(max_usd_per_run=2.0, max_tokens_per_run=100),
    )


def raw(source, url, title="AI Engineer (m/w/d)", company="Acme GmbH"):
    return RawPosting(source=source, url=url, company=company, title=title,
                      location="Berlin, Germany", remote=False)


def test_same_job_from_two_sources_produces_one_live_row(tmp_path):
    store = Store(tmp_path / "p.db")
    sources = [
        StubSource("a", [raw("a", "https://a.com/1")]),
        StubSource("b", [raw("b", "https://b.com/9", title="AI Engineer", company="Acme")]),
    ]
    out = run_fetch(sources, None, store, cfg(), {"a": 1.0, "b": 0.5}, "r1")
    assert len(out.new) == 1
    assert len(out.duplicates) == 1

def test_a_rerun_adds_no_rows(tmp_path):
    store = Store(tmp_path / "p.db")
    sources = [StubSource("a", [raw("a", "https://a.com/1")])]
    run_fetch(sources, None, store, cfg(), {"a": 1.0}, "r1")
    second = run_fetch(sources, None, store, cfg(), {"a": 1.0}, "r2")
    assert second.new == []
    assert store.conn.execute("SELECT COUNT(*) c FROM postings").fetchone()["c"] == 1

def test_out_of_scope_country_is_filtered_with_a_reason(tmp_path):
    store = Store(tmp_path / "p.db")
    far = RawPosting(source="a", url="https://a.com/2", company="Acme",
                     title="AI Engineer", location="Tokyo, Japan", remote=False)
    out = run_fetch([StubSource("a", [far])], None, store, cfg(), {"a": 1.0}, "r1")
    assert out.filtered == [("https://a.com/2", "country_out_of_scope")]

def test_near_miss_titles_are_flagged_not_merged(tmp_path):
    store = Store(tmp_path / "p.db")
    sources = [StubSource("a", [
        raw("a", "https://a.com/1", title="AI Engineer"),
        raw("a", "https://a.com/2", title="Senior AI Engineer"),
    ])]
    out = run_fetch(sources, None, store, cfg(), {"a": 1.0}, "r1")
    assert len(out.new) == 2
    assert len(out.near_misses) == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_stage_fetch.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'pipeline.stages'`

- [ ] **Step 3: Write minimal implementation**

```python
# pipeline/stages/fetch.py
from pydantic import BaseModel

from pipeline.config import Config
from pipeline.hashing import input_hash, text_hash
from pipeline.identity import title_similarity
from pipeline.models import PostingStub
from pipeline.scoring import score_prelim, stage_one_filter
from pipeline.sources.base import to_stub
from pipeline.store import Store

NEAR_MISS = 0.8


class FetchOutcome(BaseModel):
    new: list[PostingStub]
    duplicates: list[tuple[str, str]]
    filtered: list[tuple[str, str]]
    near_misses: list[tuple[str, str]]


def run_fetch(sources, http, store: Store, config: Config,
              source_priority: dict[str, float], run_id: str) -> FetchOutcome:
    new: list[PostingStub] = []
    duplicates: list[tuple[str, str]] = []
    filtered: list[tuple[str, str]] = []
    near_misses: list[tuple[str, str]] = []
    seen_identity: dict[str, PostingStub] = {}

    slice_hash = config.slice_hash(
        ["constraints.target_titles", "constraints.countries",
         "constraints.working_languages", "scoring.weights"]
    )

    for source in sources:
        for query in [None]:
            for rawp in source.fetch(http, query, None):
                stub = to_stub(rawp, config.constraints.url_strip_params)
                ih = input_hash("fetch", "n/a", "n/a", slice_hash,
                                text_hash(stub.canonical_url))
                if not store.should_run(stub.posting_id, "fetch", ih):
                    continue

                reason = stage_one_filter(stub, config.constraints, store.already_applied)
                if reason:
                    store.upsert_posting(stub, run_id)
                    store.append_event(stub.posting_id, "fetch", run_id, ih,
                                       "ok", error_class=reason)
                    filtered.append((stub.canonical_url, reason))
                    continue

                canonical = seen_identity.get(stub.identity_key) or _existing_cluster(
                    store, stub.identity_key)
                if canonical is not None:
                    store.upsert_posting(stub, run_id, duplicate_of=canonical)
                    store.append_event(stub.posting_id, "fetch", run_id, ih,
                                       "ok", error_class="duplicate")
                    duplicates.append((stub.canonical_url, canonical))
                    continue

                if not stub.bypass_prelim_threshold:
                    stub.prelim_score, stub.prelim_subscores = score_prelim(
                        stub, config.scoring, config.constraints, source_priority)

                for other in new:
                    if (other.identity_key != stub.identity_key
                            and title_similarity(other.title_raw, stub.title_raw) >= NEAR_MISS):
                        near_misses.append((stub.canonical_url, other.canonical_url))
                        break

                store.upsert_posting(stub, run_id)
                store.append_event(stub.posting_id, "fetch", run_id, ih, "ok")
                seen_identity[stub.identity_key] = stub.posting_id
                new.append(stub)

    return FetchOutcome(new=new, duplicates=duplicates,
                        filtered=filtered, near_misses=near_misses)


def _existing_cluster(store: Store, identity_key: str) -> str | None:
    row = store.conn.execute(
        """SELECT posting_id FROM postings
           WHERE identity_key=? AND duplicate_of IS NULL ORDER BY rowid LIMIT 1""",
        (identity_key,),
    ).fetchone()
    return row["posting_id"] if row else None
```

Note the `seen_identity` dict stores `posting_id` strings, so its type annotation is `dict[str, str]`. Correct the annotation when implementing.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_stage_fetch.py -v`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add pipeline/stages/ tests/test_stage_fetch.py
git commit -m "feat: Stage 1 fetch with dedupe clustering and near-miss flagging"
```

---

### Task 12: Stage 2 evaluation

**Files:**
- Create: `pipeline/stages/evaluate.py`, `config/prompts/evaluate_static.md`
- Test: `tests/test_stage_evaluate.py`

**Interfaces:**
- Consumes: Tasks 5, 6, 9
- Produces: `run_evaluate(store, llm, config, run_id, jd_loader, static_prompt, model, effort) -> list[EvaluationRow]`; `EvaluationRow` with `.stub`, `.evaluation`, `.divergence`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_stage_evaluate.py
from pipeline.models import SUBSCORE_AXES, EvaluationResult, PostingDetail
from pipeline.stages.evaluate import run_evaluate


class FakeLLM:
    def __init__(self, score=80.0):
        self.calls, self.score = 0, score

    def call(self, stage, posting_id, static_system, varying_user,
             response_model, model, effort):
        self.calls += 1
        return EvaluationResult(
            posting_id=posting_id, refined_score=self.score,
            refined_subscores={a: 0.8 for a in SUBSCORE_AXES},
            hard_pass=False, rationale="ok",
        ), None


def loader(posting_id):
    return PostingDetail(posting_id=posting_id, jd_text="full jd text",
                         jd_text_sha256="h" * 64, jd_text_source="adapter",
                         fetched_at="2026-09-01T00:00:00Z")


def test_evaluation_records_divergence_against_prelim(seeded_store, config):
    llm = FakeLLM(score=80.0)
    rows = run_evaluate(seeded_store, llm, config, "r1", loader,
                        "STATIC", "claude-sonnet-5", "low")
    assert rows[0].divergence == rows[0].evaluation.refined_score - rows[0].stub.prelim_score

def test_a_second_run_makes_no_call_when_nothing_changed(seeded_store, config):
    llm = FakeLLM()
    run_evaluate(seeded_store, llm, config, "r1", loader, "STATIC", "claude-sonnet-5", "low")
    before = llm.calls
    run_evaluate(seeded_store, llm, config, "r2", loader, "STATIC", "claude-sonnet-5", "low")
    assert llm.calls == before

def test_changed_jd_text_forces_re_evaluation(seeded_store, config):
    llm = FakeLLM()
    run_evaluate(seeded_store, llm, config, "r1", loader, "STATIC", "claude-sonnet-5", "low")
    def changed(posting_id):
        d = loader(posting_id)
        return d.model_copy(update={"jd_text_sha256": "z" * 64})
    run_evaluate(seeded_store, llm, config, "r2", changed, "STATIC", "claude-sonnet-5", "low")
    assert llm.calls == 2

def test_manual_rows_are_excluded_from_divergence(seeded_store_manual, config):
    rows = run_evaluate(seeded_store_manual, FakeLLM(), config, "r1", loader,
                        "STATIC", "claude-sonnet-5", "low")
    assert rows[0].divergence is None
```

Add `tests/conftest.py` providing `config`, `seeded_store` (one posting with `prelim_score=65.0`), and `seeded_store_manual` (one posting with `prelim_score=None`, `bypass_prelim_threshold=True`), both built with the `Store` and `PostingStub` constructors from Tasks 5 and 6.

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_stage_evaluate.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'pipeline.stages.evaluate'`

- [ ] **Step 3: Write minimal implementation**

```python
# pipeline/stages/evaluate.py
import json

from pydantic import BaseModel

from pipeline.config import Config
from pipeline.hashing import input_hash, text_hash
from pipeline.models import EvaluationResult, PostingStub

STAGE = "evaluate"
CONFIG_KEYS = ["constraints.salary_floor_eur", "constraints.min_employees",
               "constraints.countries", "constraints.working_languages"]


class EvaluationRow(BaseModel):
    stub: PostingStub
    evaluation: EvaluationResult
    divergence: float | None


def _live_stubs(store) -> list[PostingStub]:
    rows = store.conn.execute(
        """SELECT p.* FROM postings p
           WHERE p.duplicate_of IS NULL
             AND NOT EXISTS (SELECT 1 FROM stage_events e
                             WHERE e.posting_id=p.posting_id AND e.stage='fetch'
                               AND e.error_class IS NOT NULL)"""
    )
    out = []
    for r in rows:
        out.append(PostingStub(
            posting_id=r["posting_id"], identity_key=r["identity_key"],
            canonical_url=r["canonical_url"], source=r["source"],
            company_raw=r["company_raw"], title_raw=r["title_raw"],
            location_raw=r["location_raw"] or "", language=r["language"] or "en",
            remote_flag=bool(r["remote_flag"]), salary_raw=r["salary_raw"],
            posted_at=r["posted_at"], prelim_score=r["prelim_score"],
            prelim_subscores=json.loads(r["prelim_subscores"] or "{}"),
            bypass_prelim_threshold=r["prelim_score"] is None,
        ))
    return out


def run_evaluate(store, llm, config: Config, run_id: str, jd_loader,
                 static_prompt: str, model: str, effort: str) -> list[EvaluationRow]:
    slice_hash = config.slice_hash(CONFIG_KEYS)
    prompt_hash = text_hash(static_prompt)
    rows: list[EvaluationRow] = []

    for stub in _live_stubs(store):
        detail = jd_loader(stub.posting_id)
        if detail is None:
            store.append_event(stub.posting_id, STAGE, run_id, "n/a",
                               "permanent_fail", error_class="unfetchable")
            continue
        ih = input_hash(STAGE, prompt_hash, model, slice_hash, detail.jd_text_sha256)
        if not store.should_run(stub.posting_id, STAGE, ih):
            continue

        varying = (
            f"POSTING\ncompany: {stub.company_raw}\ntitle: {stub.title_raw}\n"
            f"location: {stub.location_raw}\nurl: {stub.canonical_url}\n\n"
            f"JOB DESCRIPTION\n{detail.jd_text}"
        )
        evaluation, _ = llm.call(STAGE, stub.posting_id, static_prompt, varying,
                                 EvaluationResult, model, effort)
        store.append_event(stub.posting_id, STAGE, run_id, ih, "ok")
        divergence = (
            None if stub.prelim_score is None
            else evaluation.refined_score - stub.prelim_score
        )
        rows.append(EvaluationRow(stub=stub, evaluation=evaluation,
                                  divergence=divergence))
    return rows
```

Write `config/prompts/evaluate_static.md` containing, in this order and with nothing per-posting in it: the role of the evaluator, the constraint summary rendered from `constraints.yaml`, the hard-pass list from PART 3 of `CLAUDE.md`, the capability layer summary from `context/tailoring-sheet.md`, the definition of every subscore axis, and two worked examples. No date, no run id, no posting id.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_stage_evaluate.py -v`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add pipeline/stages/evaluate.py config/prompts/ tests/test_stage_evaluate.py tests/conftest.py
git commit -m "feat: Stage 2 evaluation with divergence capture"
```

---

### Task 13: Divergence metrics and the FetchQualityReport

**Files:**
- Create: `pipeline/tuning/__init__.py`, `pipeline/tuning/metrics.py`
- Test: `tests/test_metrics.py`

**Interfaces:**
- Consumes: `EvaluationRow` (Task 12), `FetchQualityReport` (Task 5)
- Produces: `build_report(rows, run_id, threshold, jd_coverage) -> FetchQualityReport`; `spearman(a, b) -> float`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_metrics.py
import pytest

from pipeline.tuning.metrics import build_report, spearman


def row(prelim, refined, source="a", subs_prelim=None, subs_refined=None):
    from pipeline.models import SUBSCORE_AXES, EvaluationResult, PostingStub
    from pipeline.stages.evaluate import EvaluationRow
    stub = PostingStub(posting_id="p" + str(prelim), identity_key="i", canonical_url="u",
                       source=source, company_raw="c", title_raw="t",
                       prelim_score=prelim,
                       prelim_subscores=subs_prelim or {a: 0.5 for a in SUBSCORE_AXES})
    ev = EvaluationResult(posting_id=stub.posting_id, refined_score=refined,
                          refined_subscores=subs_refined or {a: 0.5 for a in SUBSCORE_AXES},
                          hard_pass=False, rationale="r")
    return EvaluationRow(stub=stub, evaluation=ev, divergence=refined - prelim)


def test_mae_and_bias_separate_noise_from_systematic_optimism():
    optimistic = build_report([row(80, 60), row(75, 55)], "r1", 60.0, {"a": 1.0})
    assert optimistic.mae == pytest.approx(20.0)
    assert optimistic.bias == pytest.approx(-20.0)
    noisy = build_report([row(70, 90), row(70, 50)], "r1", 60.0, {"a": 1.0})
    assert noisy.mae == pytest.approx(20.0)
    assert noisy.bias == pytest.approx(0.0)

def test_spearman_measures_ordering_not_magnitude():
    assert spearman([1, 2, 3], [10, 20, 30]) == pytest.approx(1.0)
    assert spearman([1, 2, 3], [30, 20, 10]) == pytest.approx(-1.0)

def test_precision_at_threshold_counts_top_ranked_rows_that_cleared():
    report = build_report([row(90, 70), row(85, 40), row(20, 10)], "r1", 60.0, {"a": 1.0})
    assert report.precision_at_threshold == pytest.approx(0.5)

def test_manual_rows_without_a_prelim_score_are_excluded():
    manual = row(0, 90)
    manual.stub.prelim_score = None
    manual.divergence = None
    report = build_report([manual, row(70, 70)], "r1", 60.0, {"a": 1.0})
    assert report.n == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_metrics.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'pipeline.tuning'`

- [ ] **Step 3: Write minimal implementation**

```python
# pipeline/tuning/metrics.py
from statistics import mean

from pipeline.models import SUBSCORE_AXES, FetchQualityReport, SourceMetric


def _ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    for position, index in enumerate(order):
        ranks[index] = float(position)
    return ranks


def spearman(a: list[float], b: list[float]) -> float:
    if len(a) < 2:
        return 0.0
    ra, rb = _ranks(a), _ranks(b)
    ma, mb = mean(ra), mean(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = (sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb)) ** 0.5
    return num / den if den else 0.0


def build_report(rows, run_id: str, threshold: float,
                 jd_coverage: dict[str, float]) -> FetchQualityReport:
    """Divergence measures agreement between our own two scorers, not
    correctness. Bias separates 'prelim is systematically optimistic' from
    'prelim is noisy'; those need different fixes."""
    scored = [r for r in rows if r.stub.prelim_score is not None]
    if not scored:
        return FetchQualityReport(
            run_id=run_id, n=0, mae=0.0, bias=0.0, spearman=0.0,
            precision_at_threshold=0.0, per_source=[], per_query_term={},
            per_feature_divergence={},
        )

    prelim = [r.stub.prelim_score for r in scored]
    refined = [r.evaluation.refined_score for r in scored]
    diffs = [b - a for a, b in zip(prelim, refined)]

    top_n = max(1, len(scored) // 2)
    top = sorted(scored, key=lambda r: r.stub.prelim_score, reverse=True)[:top_n]
    precision = sum(1 for r in top if r.evaluation.refined_score >= threshold) / len(top)

    per_source = []
    for source in sorted({r.stub.source for r in scored}):
        subset = [r for r in scored if r.stub.source == source]
        sd = [r.evaluation.refined_score - r.stub.prelim_score for r in subset]
        st = sorted(subset, key=lambda r: r.stub.prelim_score, reverse=True)
        st = st[: max(1, len(st) // 2)]
        per_source.append(SourceMetric(
            source=source, n=len(subset),
            mae=mean(abs(d) for d in sd), bias=mean(sd),
            precision_at_threshold=sum(
                1 for r in st if r.evaluation.refined_score >= threshold) / len(st),
            jd_text_coverage=jd_coverage.get(source, 0.0),
        ))

    per_feature = {
        axis: mean(
            r.evaluation.refined_subscores[axis] - r.stub.prelim_subscores.get(axis, 0.0)
            for r in scored
        )
        for axis in SUBSCORE_AXES
    }

    return FetchQualityReport(
        run_id=run_id, n=len(scored),
        mae=mean(abs(d) for d in diffs), bias=mean(diffs),
        spearman=spearman(prelim, refined), precision_at_threshold=precision,
        per_source=per_source, per_query_term={}, per_feature_divergence=per_feature,
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_metrics.py -v`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add pipeline/tuning/ tests/test_metrics.py
git commit -m "feat: divergence metrics and FetchQualityReport"
```

---

### Task 14: Tuner policy, proposals, and the apply command

**Files:**
- Create: `pipeline/tuning/tuner.py`, `config/tuning_state.yaml`
- Test: `tests/test_tuner.py`

**Interfaces:**
- Consumes: `FetchQualityReport` (Task 5), `Scoring` (Task 1)
- Produces: `propose(report, state, scoring, min_rows=20, max_delta=0.05, exploration_quota=0.1) -> TuningProposal`; `TuningProposal` with `.source_weights`, `.feature_weights`, `.threshold`, `.retired_terms`, `.reason`; `apply_proposal(proposal, config_dir)`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_tuner.py
import pytest

from pipeline.config import Scoring
from pipeline.models import SUBSCORE_AXES, FetchQualityReport, SourceMetric
from pipeline.tuning.tuner import apply_proposal, propose

SCORING = Scoring(threshold=60.0, weights={a: 0.2 for a in SUBSCORE_AXES})


def report(n, per_source, bias=0.0, feature=None):
    return FetchQualityReport(
        run_id="r1", n=n, mae=10.0, bias=bias, spearman=0.5,
        precision_at_threshold=0.5, per_source=per_source, per_query_term={},
        per_feature_divergence=feature or {a: 0.0 for a in SUBSCORE_AXES},
    )


def source(name, precision, n=30):
    return SourceMetric(source=name, n=n, mae=10.0, bias=0.0,
                        precision_at_threshold=precision, jd_text_coverage=1.0)


def test_no_proposal_below_the_minimum_row_count():
    p = propose(report(5, [source("a", 0.1)]), {}, SCORING)
    assert p.source_weights == {}
    assert "below minimum" in p.reason

def test_low_precision_source_is_down_weighted_but_never_to_zero():
    p = propose(report(40, [source("a", 0.0)]), {"a": 1.0}, SCORING)
    assert p.source_weights["a"] < 1.0
    assert p.source_weights["a"] >= 0.1, "exploration quota keeps a source samplable"

def test_weight_deltas_are_clamped():
    p = propose(report(40, [source("a", 0.0)]), {"a": 1.0}, SCORING, max_delta=0.05)
    assert 1.0 - p.source_weights["a"] <= 0.05 + 1e-9

def test_feature_divergence_moves_the_matching_feature_weight():
    feature = {a: 0.0 for a in SUBSCORE_AXES}
    feature["title_match"] = 0.4
    p = propose(report(40, [source("a", 0.5)]), {"a": 1.0}, SCORING, feature=None)
    p = propose(report(40, [source("a", 0.5)], feature=feature), {"a": 1.0}, SCORING)
    assert p.feature_weights["title_match"] > SCORING.weights["title_match"]

def test_apply_is_the_only_write_path(tmp_path):
    import inspect

    import pipeline.tuning.tuner as tuner
    src = inspect.getsource(tuner.propose)
    assert "open(" not in src and "write_text" not in src, "propose must not write config"
    (tmp_path / "scoring.yaml").write_text("threshold: 60.0\nweights: {title_match: 0.2}\n",
                                           encoding="utf-8")
    (tmp_path / "tuning_state.yaml").write_text("source_weights: {}\n", encoding="utf-8")
    p = propose(report(40, [source("a", 0.0)]), {"a": 1.0}, SCORING)
    apply_proposal(p, tmp_path)
    assert "a:" in (tmp_path / "tuning_state.yaml").read_text(encoding="utf-8")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_tuner.py -v`
Expected: FAIL with `ImportError: cannot import name 'propose'`

- [ ] **Step 3: Write minimal implementation**

```python
# pipeline/tuning/tuner.py
from pathlib import Path

import yaml
from pydantic import BaseModel

from pipeline.config import Scoring
from pipeline.models import FetchQualityReport

MIN_ROWS = 20
MAX_DELTA = 0.05
EXPLORATION_FLOOR = 0.1


class TuningProposal(BaseModel):
    run_id: str
    source_weights: dict[str, float] = {}
    feature_weights: dict[str, float] = {}
    threshold: float | None = None
    retired_terms: list[str] = []
    reason: str


def propose(report: FetchQualityReport, state: dict[str, float], scoring: Scoring,
            min_rows: int = MIN_ROWS, max_delta: float = MAX_DELTA,
            exploration_quota: float = EXPLORATION_FLOOR) -> TuningProposal:
    """Deterministic policy. Writes nothing: the tuner has no ground truth,
    so its output is a proposal that a human applies with `tune apply`."""
    if report.n < min_rows:
        return TuningProposal(
            run_id=report.run_id,
            reason=f"{report.n} scored rows is below minimum {min_rows}; no adjustment",
        )

    source_weights = {}
    for metric in report.per_source:
        current = state.get(metric.source, 1.0)
        target = max(exploration_quota, metric.precision_at_threshold)
        delta = max(-max_delta, min(max_delta, target - current))
        source_weights[metric.source] = round(
            max(exploration_quota, current + delta), 4)

    feature_weights = {}
    for axis, divergence in report.per_feature_divergence.items():
        current = scoring.weights.get(axis, 0.0)
        delta = max(-max_delta, min(max_delta, divergence * 0.1))
        feature_weights[axis] = round(max(0.0, current + delta), 4)

    return TuningProposal(
        run_id=report.run_id, source_weights=source_weights,
        feature_weights=feature_weights,
        reason=(f"n={report.n} mae={report.mae:.1f} bias={report.bias:+.1f} "
                f"spearman={report.spearman:.2f}"),
    )


def apply_proposal(proposal: TuningProposal, config_dir: Path) -> None:
    """The only write path to scoring configuration. Invoked by
    `pipeline tune apply <run_id>`, never by a run."""
    state_path = Path(config_dir) / "tuning_state.yaml"
    state = yaml.safe_load(state_path.read_text(encoding="utf-8")) or {}
    state.setdefault("source_weights", {}).update(proposal.source_weights)
    state["last_applied_run"] = proposal.run_id
    state_path.write_text(yaml.safe_dump(state, sort_keys=True), encoding="utf-8")

    if proposal.feature_weights:
        scoring_path = Path(config_dir) / "scoring.yaml"
        scoring = yaml.safe_load(scoring_path.read_text(encoding="utf-8"))
        scoring["weights"].update(proposal.feature_weights)
        if proposal.threshold is not None:
            scoring["threshold"] = proposal.threshold
        scoring_path.write_text(yaml.safe_dump(scoring, sort_keys=True), encoding="utf-8")
```

```yaml
# config/tuning_state.yaml
auto_apply: false
source_weights: {}
last_applied_run: null
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_tuner.py -v`
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add pipeline/tuning/tuner.py config/tuning_state.yaml tests/test_tuner.py
git commit -m "feat: advisory tuner with clamps, exploration floor and a single write path"
```

---

### Task 15: Gate A, pre-render checks

**Files:**
- Create: `pipeline/gates/__init__.py`, `pipeline/gates/gate_a.py`
- Test: `tests/test_gate_a.py`

**Interfaces:**
- Consumes: `ApplicationDocument` (Task 5), `DerivedFacts`, `CuratedFacts` (Task 7)
- Produces: `GateFailure(field, check, detail)`; `GateResult(ok, failures)`; `run_gate_a(doc, facts, curated, jd_text) -> GateResult`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_gate_a.py
from pipeline.facts import CuratedFacts, DerivedFacts
from pipeline.gates.gate_a import run_gate_a
from pipeline.models import (
    ApplicationDocument, CoverLetterBody, EducationRow, ExperienceRow,
    ProjectRow, ResumeBody, SkillRow,
)

FACTS = DerivedFacts(
    companies=["Corominas Consulting"], titles=["Manager, AI & Automation"],
    periods=["Jun 2026 - Sep 2026"], education=[],
    allowed_numbers={"85", "18", "10M+"},
)
CURATED = CuratedFacts(
    claude_md_sha256="x" * 64,
    forbidden_strings=["fixed-term", "176K"],
    domain_tokens=["SEO", "WordPress"],
    number_aliases={},
)


def doc(bullet: str, company="Corominas Consulting",
        title="Manager, AI & Automation", period="Jun 2026 - Sep 2026"):
    return ApplicationDocument(
        company_name="Target",
        resume=ResumeBody(
            summary="Automation engineer.",
            skills=[SkillRow(label="AI", value="Claude API")],
            experience=[ExperienceRow(title=title, company=company,
                                      period=period, bullets=[bullet])],
            projects=[ProjectRow(name="SceneAgent", period="Apr 2026", bullets=["b"])],
            education=[EducationRow(degree="MS", school="Stevens", year="2025")],
        ),
        cover_letter=CoverLetterBody(date="1 September 2026", company_address="Berlin",
                                     salutation="Dear team,", paragraphs=["Hello."]),
    )


def test_clean_document_passes():
    assert run_gate_a(doc("Built a pipeline across 85 client sites"),
                      FACTS, CURATED, jd_text="automation").ok

def test_en_dash_fails_and_names_the_field():
    result = run_gate_a(doc("Built a pipeline \u2013 unattended"), FACTS, CURATED, "x")
    assert not result.ok
    failure = next(f for f in result.failures if f.check == "dash")
    assert failure.field == "resume.experience[0].bullets[0]"

def test_invented_company_is_a_hard_failure():
    result = run_gate_a(doc("Built a pipeline", company="Acme Robotics"), FACTS, CURATED, "x")
    assert any(f.check == "facts" and "Acme Robotics" in f.detail for f in result.failures)

def test_unlisted_number_fails_the_claims_check():
    result = run_gate_a(doc("Shipped across 4200 client sites"), FACTS, CURATED, "x")
    assert any(f.check == "claims" and "4200" in f.detail for f in result.failures)

def test_forbidden_string_fails():
    result = run_gate_a(doc("Held a fixed-term contract"), FACTS, CURATED, "x")
    assert any(f.check == "forbidden" for f in result.failures)

def test_domain_lead_fails_unless_the_jd_uses_that_word():
    lead = doc("SEO content pipelines built end to end")
    assert any(f.check == "rule9" for f in run_gate_a(lead, FACTS, CURATED, "automation").failures)
    assert not any(f.check == "rule9" for f in run_gate_a(lead, FACTS, CURATED, "we do SEO").failures)

def test_all_failures_are_reported_not_just_the_first():
    result = run_gate_a(doc("SEO work \u2014 fixed-term"), FACTS, CURATED, "automation")
    assert {f.check for f in result.failures} >= {"dash", "forbidden", "rule9"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_gate_a.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'pipeline.gates'`

- [ ] **Step 3: Write minimal implementation**

```python
# pipeline/gates/gate_a.py
import re

from pydantic import BaseModel

from pipeline.facts import CuratedFacts, DerivedFacts
from pipeline.models import ApplicationDocument

DASHES = {"\u2012", "\u2013", "\u2014", "\u2015", "\u2212"}
NUMBER = re.compile(r"\b\d[\d,.]*\s*(?:M\+|K\+|M|K|%|\+)?")
CHARS_PER_LINE = 105
MAX_LINES = 52


class GateFailure(BaseModel):
    field: str
    check: str
    detail: str


class GateResult(BaseModel):
    ok: bool
    failures: list[GateFailure]


def _walk(doc: ApplicationDocument):
    """Yield (field_path, text) for every string a reader will see."""
    r = doc.resume
    yield "resume.summary", r.summary
    for i, s in enumerate(r.skills):
        yield f"resume.skills[{i}].value", s.value
    for i, e in enumerate(r.experience):
        yield f"resume.experience[{i}].title", e.title
        yield f"resume.experience[{i}].company", e.company
        yield f"resume.experience[{i}].period", e.period
        for j, b in enumerate(e.bullets):
            yield f"resume.experience[{i}].bullets[{j}]", b
    for i, p in enumerate(r.projects):
        yield f"resume.projects[{i}].name", p.name
        for j, b in enumerate(p.bullets):
            yield f"resume.projects[{i}].bullets[{j}]", b
    for i, para in enumerate(doc.cover_letter.paragraphs):
        yield f"cover_letter.paragraphs[{i}]", para


def run_gate_a(doc: ApplicationDocument, facts: DerivedFacts,
               curated: CuratedFacts, jd_text: str) -> GateResult:
    """Pre-render, against the JSON artifact. Every check runs; the gate
    reports all failures rather than stopping at the first."""
    failures: list[GateFailure] = []
    jd_lower = jd_text.lower()
    fields = list(_walk(doc))

    for field, text in fields:
        for ch in DASHES:
            if ch in text:
                failures.append(GateFailure(
                    field=field, check="dash",
                    detail=f"contains U+{ord(ch):04X}"))
        for bad in curated.forbidden_strings:
            if bad.lower() in text.lower():
                failures.append(GateFailure(
                    field=field, check="forbidden", detail=f"contains '{bad}'"))

    for i, e in enumerate(doc.resume.experience):
        if e.company not in facts.companies:
            failures.append(GateFailure(
                field=f"resume.experience[{i}].company", check="facts",
                detail=f"'{e.company}' is not in the canonical record"))
        if e.title not in facts.titles:
            failures.append(GateFailure(
                field=f"resume.experience[{i}].title", check="facts",
                detail=f"'{e.title}' is not in the canonical record"))
        if e.period not in facts.periods:
            failures.append(GateFailure(
                field=f"resume.experience[{i}].period", check="facts",
                detail=f"'{e.period}' is not in the canonical record"))

    allowed = {curated.number_aliases.get(n, n) for n in facts.allowed_numbers}
    for field, text in fields:
        if not field.startswith("resume."):
            continue
        for match in NUMBER.findall(text):
            token = curated.number_aliases.get(match.strip(), match.strip())
            if token.rstrip("%") in {"20", "2025", "2026", "2022"}:
                continue  # bare years and small ordinals are not claims
            if token not in allowed:
                failures.append(GateFailure(
                    field=field, check="claims",
                    detail=f"'{token}' is not on the allowed-claims list"))

    for i, e in enumerate(doc.resume.experience):
        for j, bullet in enumerate(e.bullets):
            opener = bullet[:40].lower()
            for token in curated.domain_tokens:
                if opener.startswith(token.lower()) and token.lower() not in jd_lower:
                    failures.append(GateFailure(
                        field=f"resume.experience[{i}].bullets[{j}]", check="rule9",
                        detail=f"bullet opens with domain token '{token}' "
                               f"absent from the JD"))

    total_lines = sum(
        max(1, -(-len(text) // CHARS_PER_LINE)) for _, text in fields
        if text.startswith("resume") or True
    )
    if total_lines > MAX_LINES:
        failures.append(GateFailure(
            field="resume", check="length",
            detail=f"estimated {total_lines} lines exceeds the {MAX_LINES}-line budget"))

    return GateResult(ok=not failures, failures=failures)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_gate_a.py -v`
Expected: 7 passed

- [ ] **Step 5: Commit**

```bash
git add pipeline/gates/ tests/test_gate_a.py
git commit -m "feat: Gate A pre-render checks reporting every failure with a field path"
```

---

### Task 16: Gate B, post-render checks against the PDF

**Files:**
- Create: `pipeline/gates/gate_b.py`
- Test: `tests/test_gate_b.py`, `tests/fixtures/one_page.pdf`, `tests/fixtures/two_page.pdf`

**Interfaces:**
- Consumes: `GateResult`, `GateFailure` (Task 15), `CuratedFacts` (Task 7)
- Produces: `run_gate_b(pdf_paths: list[Path], curated: CuratedFacts, max_pages: int = 1) -> GateResult`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_gate_b.py
from pathlib import Path

from pipeline.facts import CuratedFacts
from pipeline.gates.gate_b import run_gate_b

CURATED = CuratedFacts(claude_md_sha256="x" * 64,
                       forbidden_strings=["fixed-term"], domain_tokens=[],
                       number_aliases={})


def make_pdf(path: Path, pages: int, text: str) -> Path:
    from reportlab.pdfgen import canvas
    c = canvas.Canvas(str(path))
    for _ in range(pages):
        c.drawString(72, 720, text)
        c.showPage()
    c.save()
    return path

def test_one_page_clean_pdf_passes(tmp_path):
    pdf = make_pdf(tmp_path / "a.pdf", 1, "Automation engineer")
    assert run_gate_b([pdf], CURATED).ok

def test_two_page_resume_fails(tmp_path):
    pdf = make_pdf(tmp_path / "b.pdf", 2, "Automation engineer")
    result = run_gate_b([pdf], CURATED)
    assert not result.ok
    assert any(f.check == "page_count" for f in result.failures)

def test_dash_that_survived_into_the_pdf_is_caught(tmp_path):
    pdf = make_pdf(tmp_path / "c.pdf", 1, "Automation \u2014 engineer")
    assert any(f.check == "dash" for f in run_gate_b([pdf], CURATED).failures)

def test_forbidden_string_in_the_rendered_pdf_is_caught(tmp_path):
    pdf = make_pdf(tmp_path / "d.pdf", 1, "fixed-term contract")
    assert any(f.check == "forbidden" for f in run_gate_b([pdf], CURATED).failures)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_gate_b.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'pipeline.gates.gate_b'`

- [ ] **Step 3: Write minimal implementation**

```python
# pipeline/gates/gate_b.py
from pathlib import Path

from pypdf import PdfReader

from pipeline.facts import CuratedFacts
from pipeline.gates.gate_a import DASHES, GateFailure, GateResult


def run_gate_b(pdf_paths: list[Path], curated: CuratedFacts,
               max_pages: int = 1) -> GateResult:
    """Post-render, against the artifact. Imports nothing from the generator,
    so it survives both a model swap and a renderer change."""
    failures: list[GateFailure] = []
    for path in pdf_paths:
        reader = PdfReader(str(path))
        if len(reader.pages) > max_pages:
            failures.append(GateFailure(
                field=str(path), check="page_count",
                detail=f"rendered {len(reader.pages)} pages, budget is {max_pages}"))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        for ch in DASHES:
            if ch in text:
                failures.append(GateFailure(
                    field=str(path), check="dash",
                    detail=f"rendered PDF contains U+{ord(ch):04X}"))
        for bad in curated.forbidden_strings:
            if bad.lower() in text.lower():
                failures.append(GateFailure(
                    field=str(path), check="forbidden",
                    detail=f"rendered PDF contains '{bad}'"))
    return GateResult(ok=not failures, failures=failures)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_gate_b.py -v`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add pipeline/gates/gate_b.py tests/test_gate_b.py
git commit -m "feat: Gate B post-render checks against the PDF"
```

---

### Task 17: Stage 3 generation and Stage 4 render

**Files:**
- Create: `pipeline/stages/generate.py`, `pipeline/stages/render.py`
- Create: `config/prompts/brief_static.md`, `config/prompts/document_static.md`
- Test: `tests/test_stage_generate.py`, `tests/test_stage_render.py`

**Interfaces:**
- Consumes: Tasks 5, 6, 7, 9, 15, 16
- Produces: `run_generate(store, llm, config, run_id, rows, facts, curated, briefs_prompt, doc_prompt, models) -> list[GeneratedRow]`; `employer_folder(company, role, date, root) -> Path`; `run_render(store, config, run_id, generated, curated, builder_path) -> list[RenderResult]`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_stage_generate.py
from pipeline.stages.generate import employer_folder, run_generate


def test_folder_matches_the_existing_new_application_convention(tmp_path):
    path = employer_folder("Acme Robotics GmbH", "AI Engineer", "2026-09-01", tmp_path)
    assert path.name == "2026-09-01_acme-robotics-gmbh_ai-engineer"
    assert (path / "notes").is_dir() and (path / "out").is_dir()
    assert (path / "log.md").exists()

def test_gate_a_failure_quarantines_the_row_and_the_batch_continues(
    tmp_path, seeded_rows, fake_llm_bad_then_good, config, facts, curated
):
    out = run_generate(seeded_rows.store, fake_llm_bad_then_good, config, "r1",
                       seeded_rows.rows, facts, curated, "BRIEF", "DOC",
                       {"generate": "claude-opus-5"})
    statuses = [r.status for r in out]
    assert "gate_failed" in statuses and "ok" in statuses

def test_a_gate_failure_event_names_the_bad_field(
    tmp_path, seeded_rows, fake_llm_bad_then_good, config, facts, curated
):
    run_generate(seeded_rows.store, fake_llm_bad_then_good, config, "r1",
                 seeded_rows.rows, facts, curated, "BRIEF", "DOC",
                 {"generate": "claude-opus-5"})
    row = seeded_rows.store.conn.execute(
        "SELECT * FROM stage_events WHERE status='gate_failed'").fetchone()
    assert "resume.experience[0].bullets[0]" in row["error_detail"]

def test_regenerating_documents_does_not_redo_the_brief(
    seeded_rows, fake_llm_counting, config, facts, curated
):
    run_generate(seeded_rows.store, fake_llm_counting, config, "r1", seeded_rows.rows,
                 facts, curated, "BRIEF", "DOC", {"generate": "claude-opus-5"})
    briefs_before = fake_llm_counting.brief_calls
    run_generate(seeded_rows.store, fake_llm_counting, config, "r2", seeded_rows.rows,
                 facts, curated, "BRIEF", "DOC2", {"generate": "claude-opus-5"})
    assert fake_llm_counting.brief_calls == briefs_before
    assert fake_llm_counting.doc_calls == 2
```

```python
# tests/test_stage_render.py
import json

from pipeline.stages.render import run_render


def test_render_shells_out_to_the_frozen_builder_and_records_paths(
    tmp_path, seeded_generated, config, curated
):
    results = run_render(seeded_generated.store, config, "r1", seeded_generated.rows,
                         curated, builder_path="scripts/build_resume.py")
    assert results[0].page_count == 1
    assert results[0].gate_b_status == "ok"
    assert results[0].resume_pdf.endswith(".pdf")

def test_a_builder_crash_is_a_per_row_failure_not_a_dead_batch(
    tmp_path, seeded_generated_with_one_bad, config, curated
):
    results = run_render(seeded_generated_with_one_bad.store, config, "r1",
                         seeded_generated_with_one_bad.rows, curated,
                         builder_path="scripts/build_resume.py")
    assert len(results) == 1, "the good row still rendered"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_stage_generate.py tests/test_stage_render.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'pipeline.stages.generate'`

- [ ] **Step 3: Write minimal implementation**

```python
# pipeline/stages/generate.py
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

from pydantic import BaseModel

from pipeline.gates.gate_a import run_gate_a
from pipeline.hashing import input_hash, text_hash
from pipeline.models import ApplicationDocument, TailoringBrief

BRIEF_STAGE, DOC_STAGE, GATE_STAGE = "brief", "generate", "gate_a"


class GeneratedRow(BaseModel):
    posting_id: str
    folder: str
    status: str
    failures: list[str] = []


def employer_folder(company: str, role: str, day: str, root: Path) -> Path:
    """Delegates to the existing scaffolder so folder names stay identical to
    hand-created ones and /apply, /log, /answer and /prep keep working."""
    out = subprocess.run(
        [sys.executable, "scripts/new_application.py", company, role,
         "--date", day, "--root", str(root)],
        capture_output=True, text=True, check=True,
    )
    return Path(out.stdout.strip())


def run_generate(store, llm, config, run_id: str, rows, facts, curated,
                 brief_prompt: str, doc_prompt: str, models: dict[str, str],
                 root: Path = Path("applications")) -> list[GeneratedRow]:
    out: list[GeneratedRow] = []
    model = models["generate"]
    slice_hash = config.slice_hash(["constraints.target_titles"])

    for row in rows:
        if row.evaluation.hard_pass:
            continue
        if row.evaluation.refined_score < config.scoring.threshold \
                and not row.stub.bypass_prelim_threshold:
            continue

        jd_text = row.jd_text
        brief_ih = input_hash(BRIEF_STAGE, text_hash(brief_prompt), model,
                              slice_hash, text_hash(jd_text))
        if store.should_run(row.stub.posting_id, BRIEF_STAGE, brief_ih):
            brief, _ = llm.call(BRIEF_STAGE, row.stub.posting_id, brief_prompt,
                                _brief_input(row, jd_text), TailoringBrief, model, "high")
            store.append_event(row.stub.posting_id, BRIEF_STAGE, run_id, brief_ih,
                               "ok", artifact_ref=_save_brief(row, brief))
        else:
            brief = _load_brief(row)

        doc_ih = input_hash(DOC_STAGE, text_hash(doc_prompt), model,
                            slice_hash, text_hash(jd_text + brief.model_dump_json()))
        if not store.should_run(row.stub.posting_id, DOC_STAGE, doc_ih):
            continue

        doc, _ = llm.call(DOC_STAGE, row.stub.posting_id, doc_prompt,
                          _doc_input(row, jd_text, brief), ApplicationDocument,
                          model, "high")

        gate = run_gate_a(doc, facts, curated, jd_text)
        folder = employer_folder(row.stub.company_raw, row.stub.title_raw,
                                 date.today().isoformat(), root)
        if not gate.ok:
            detail = "; ".join(f"{f.field}: {f.check}: {f.detail}" for f in gate.failures)
            store.append_event(row.stub.posting_id, GATE_STAGE, run_id, doc_ih,
                               "gate_failed", error_class="gate_a", error_detail=detail)
            out.append(GeneratedRow(posting_id=row.stub.posting_id, folder=str(folder),
                                    status="gate_failed",
                                    failures=[f.field for f in gate.failures]))
            continue

        (folder / "application.json").write_text(
            json.dumps(doc.model_dump(mode="json"), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8")
        (folder / "evaluation.json").write_text(
            row.evaluation.model_dump_json(indent=2), encoding="utf-8")
        store.append_event(row.stub.posting_id, DOC_STAGE, run_id, doc_ih, "ok",
                           artifact_ref=str(folder / "application.json"))
        store.append_event(row.stub.posting_id, GATE_STAGE, run_id, doc_ih, "ok")
        store.mark_applied(row.stub.identity_key, str(folder))
        out.append(GeneratedRow(posting_id=row.stub.posting_id,
                                folder=str(folder), status="ok"))
    return out


def _brief_input(row, jd_text: str) -> str:
    return (f"COMPANY: {row.stub.company_raw}\nTITLE: {row.stub.title_raw}\n\n"
            f"JOB DESCRIPTION\n{jd_text}\n\nEVALUATION\n"
            f"{row.evaluation.model_dump_json(indent=2)}")


def _doc_input(row, jd_text: str, brief: TailoringBrief) -> str:
    return (f"TAILORING BRIEF\n{brief.model_dump_json(indent=2)}\n\n"
            f"COMPANY: {row.stub.company_raw}\nTITLE: {row.stub.title_raw}\n"
            f"TODAY: {date.today().strftime('%d %B %Y')}\n\n"
            f"JOB DESCRIPTION\n{jd_text}")


def _brief_path(row) -> Path:
    path = Path("artifacts") / row.stub.posting_id
    path.mkdir(parents=True, exist_ok=True)
    return path / "brief.json"


def _save_brief(row, brief: TailoringBrief) -> str:
    path = _brief_path(row)
    path.write_text(brief.model_dump_json(indent=2), encoding="utf-8")
    return str(path)


def _load_brief(row) -> TailoringBrief:
    return TailoringBrief.model_validate_json(
        _brief_path(row).read_text(encoding="utf-8"))
```

```python
# pipeline/stages/render.py
import subprocess
import sys
from pathlib import Path

from pipeline.gates.gate_b import run_gate_b
from pipeline.models import RenderResult

STAGE = "render"


def run_render(store, config, run_id: str, generated, curated,
               builder_path: str = "scripts/build_resume.py") -> list[RenderResult]:
    """Shells out to the frozen builder so its behaviour cannot change and a
    renderer exception is a per-row failure, never a dead batch."""
    results: list[RenderResult] = []
    for row in generated:
        if row.status != "ok":
            continue
        folder = Path(row.folder)
        out_dir = folder / "out"
        try:
            subprocess.run(
                [sys.executable, builder_path, str(folder / "application.json"),
                 str(out_dir)],
                capture_output=True, text=True, check=True,
            )
        except subprocess.CalledProcessError as exc:
            store.append_event(row.posting_id, STAGE, run_id, "n/a", "permanent_fail",
                               error_class="renderer", error_detail=exc.stderr[:2000])
            continue

        pdfs = sorted(out_dir.glob("*.pdf"))
        resume_pdf = next((p for p in pdfs if "CoverLetter" not in p.name), None)
        cover_pdf = next((p for p in pdfs if "CoverLetter" in p.name), None)
        gate = run_gate_b([p for p in (resume_pdf,) if p], curated)
        status = "ok" if gate.ok else "failed"
        if not gate.ok:
            detail = "; ".join(f"{f.field}: {f.check}: {f.detail}" for f in gate.failures)
            store.append_event(row.posting_id, "gate_b", run_id, "n/a", "gate_failed",
                               error_class="gate_b", error_detail=detail)
        else:
            store.append_event(row.posting_id, "gate_b", run_id, "n/a", "ok")

        from pypdf import PdfReader
        pages = len(PdfReader(str(resume_pdf)).pages) if resume_pdf else 0
        store.append_event(row.posting_id, STAGE, run_id, "n/a", "ok",
                           artifact_ref=str(resume_pdf))
        results.append(RenderResult(
            posting_id=row.posting_id, resume_pdf=str(resume_pdf),
            cover_pdf=str(cover_pdf) if cover_pdf else "", page_count=pages,
            gate_b_status=status))
    return results
```

Write `config/prompts/brief_static.md` and `config/prompts/document_static.md`. Both carry, above the cache breakpoint and with nothing per-posting: the positioning from PART 1 of `CLAUDE.md`, the capability layer from `context/tailoring-sheet.md`, the output rules from PART 4 (no dashes, one page, single column, never fabricate, lead with the pattern not the domain, tailor to the JD's own vocabulary), and the canonical employment record. The current date belongs in the varying tail, never here.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_stage_generate.py tests/test_stage_render.py -v`
Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add pipeline/stages/generate.py pipeline/stages/render.py config/prompts/ tests/
git commit -m "feat: Stage 3 generation with gate quarantine and Stage 4 render"
```

---

### Task 18: xlsx export, INBOX read-back, and the CLI

**Files:**
- Create: `pipeline/export.py`, `pipeline/cli.py`
- Test: `tests/test_export.py`, `tests/test_cli.py`

**Interfaces:**
- Consumes: everything above
- Produces: `export_run(store, run_id, path) -> Path`; `read_inbox(path) -> list[str]`; `main(argv) -> int`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_export.py
from openpyxl import Workbook, load_workbook

from pipeline.export import COLUMNS, export_run, read_inbox


def test_export_writes_one_row_per_posting_with_every_column(tmp_path, seeded_full_store):
    path = export_run(seeded_full_store, "r1", tmp_path / "run.xlsx")
    ws = load_workbook(path)["postings"]
    assert [c.value for c in ws[1]] == COLUMNS
    assert ws.max_row == 2

def test_inbox_tab_round_trips_manual_urls(tmp_path):
    wb = Workbook()
    wb.active.title = "postings"
    inbox = wb.create_sheet("INBOX")
    inbox["A1"] = "url"
    inbox["A2"] = "https://careers.example.com/jobs/7"
    inbox["A3"] = ""
    path = tmp_path / "run.xlsx"
    wb.save(path)
    assert read_inbox(path) == ["https://careers.example.com/jobs/7"]

def test_rerender_overwrites_every_column_except_decision(tmp_path, seeded_full_store):
    path = export_run(seeded_full_store, "r1", tmp_path / "run.xlsx")
    wb = load_workbook(path)
    ws = wb["postings"]
    ws.cell(row=2, column=COLUMNS.index("decision") + 1, value="apply")
    ws.cell(row=2, column=COLUMNS.index("title") + 1, value="HAND EDIT")
    wb.save(path)
    export_run(seeded_full_store, "r1", path)
    ws = load_workbook(path)["postings"]
    assert ws.cell(row=2, column=COLUMNS.index("decision") + 1).value == "apply"
    assert ws.cell(row=2, column=COLUMNS.index("title") + 1).value != "HAND EDIT"
```

```python
# tests/test_cli.py
from pipeline.cli import main


def test_facts_sync_writes_the_hash(tmp_path, project_fixture):
    assert main(["facts", "sync", "--root", str(project_fixture), "--yes"]) == 0
    text = (project_fixture / "config" / "facts_curated.yaml").read_text(encoding="utf-8")
    assert "REPLACE_BY_RUNNING" not in text

def test_a_run_halts_when_claude_md_moved(tmp_path, project_fixture):
    main(["facts", "sync", "--root", str(project_fixture), "--yes"])
    (project_fixture / "CLAUDE.md").write_text("changed", encoding="utf-8")
    assert main(["fetch", "--root", str(project_fixture), "--dry-run"]) == 3

def test_dry_run_makes_no_llm_call_and_no_write(project_fixture):
    assert main(["evaluate", "--root", str(project_fixture), "--dry-run"]) == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_export.py tests/test_cli.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'pipeline.export'`

- [ ] **Step 3: Write minimal implementation**

```python
# pipeline/export.py
from pathlib import Path

from openpyxl import Workbook, load_workbook

COLUMNS = [
    "posting_id", "url", "company", "title", "location", "source",
    "prelim", "refined", "divergence", "verdict", "status",
    "resume_pdf", "cover_pdf", "apply_url", "decision", "notes",
]
PRESERVED = {"decision"}

QUERY = """
SELECT p.posting_id, p.canonical_url, p.company_raw, p.title_raw, p.location_raw,
       p.source, p.prelim_score,
       (SELECT artifact_ref FROM stage_events e WHERE e.posting_id=p.posting_id
         AND e.stage='render' AND e.status='ok' ORDER BY event_id DESC LIMIT 1) AS resume_pdf,
       (SELECT status FROM stage_events e WHERE e.posting_id=p.posting_id
         ORDER BY event_id DESC LIMIT 1) AS status
FROM postings p WHERE p.duplicate_of IS NULL ORDER BY p.prelim_score DESC
"""


def read_inbox(path: Path) -> list[str]:
    """The manual injection channel. Column A, one URL per row, header skipped."""
    if not Path(path).exists():
        return []
    wb = load_workbook(path)
    if "INBOX" not in wb.sheetnames:
        return []
    ws = wb["INBOX"]
    return [str(r[0].value).strip() for r in ws.iter_rows(min_row=2)
            if r[0].value and str(r[0].value).strip()]


def export_run(store, run_id: str, path: Path) -> Path:
    """Re-renders the sheet from the ledger. Only the decision column and the
    INBOX tab survive; every other cell is overwritten without asking."""
    path = Path(path)
    kept: dict[str, dict[str, str]] = {}
    inbox = read_inbox(path)
    if path.exists():
        ws = load_workbook(path)["postings"]
        header = [c.value for c in ws[1]]
        for row in ws.iter_rows(min_row=2):
            values = {header[i]: c.value for i, c in enumerate(row) if i < len(header)}
            if values.get("posting_id"):
                kept[values["posting_id"]] = {
                    k: values.get(k) for k in PRESERVED}

    wb = Workbook()
    ws = wb.active
    ws.title = "postings"
    ws.append(COLUMNS)
    for r in store.conn.execute(QUERY):
        preserved = kept.get(r["posting_id"], {})
        ws.append([
            r["posting_id"], r["canonical_url"], r["company_raw"], r["title_raw"],
            r["location_raw"], r["source"], r["prelim_score"], None, None, None,
            r["status"], r["resume_pdf"], None, r["canonical_url"],
            preserved.get("decision"), None,
        ])
    inbox_ws = wb.create_sheet("INBOX")
    inbox_ws.append(["url"])
    for url in inbox:
        inbox_ws.append([url])
    wb.save(path)
    return path
```

```python
# pipeline/cli.py
import argparse
import sys
import uuid
from pathlib import Path

import yaml

from pipeline.config import load_config
from pipeline.facts import FactsDriftError, assert_facts_current, derive_facts, load_curated
from pipeline.hashing import file_hash
from pipeline.store import Store

EXIT_OK, EXIT_ERROR, EXIT_BUDGET, EXIT_FACTS = 0, 1, 2, 3


def _guard_facts(root: Path) -> None:
    curated = load_curated(root / "config" / "facts_curated.yaml")
    assert_facts_current(root / "CLAUDE.md", curated)


def cmd_facts_sync(args) -> int:
    root = Path(args.root)
    md = root / "CLAUDE.md"
    path = root / "config" / "facts_curated.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    derived = derive_facts(md.read_text(encoding="utf-8"))
    print(f"companies: {derived.companies}")
    print(f"titles: {derived.titles}")
    print(f"periods: {derived.periods}")
    print(f"allowed numbers: {sorted(derived.allowed_numbers)}")
    if not args.yes:
        print("Re-run with --yes to write the new hash.")
        return EXIT_OK
    data["claude_md_sha256"] = file_hash(md)
    path.write_text(yaml.safe_dump(data, sort_keys=True), encoding="utf-8")
    print(f"claude_md_sha256 updated to {data['claude_md_sha256'][:12]}")
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="pipeline")
    parser.add_argument("--root", default=".")
    sub = parser.add_subparsers(dest="command", required=True)

    for name in ("fetch", "evaluate", "generate", "render", "run", "report", "export"):
        p = sub.add_parser(name)
        p.add_argument("--limit", type=int, default=None)
        p.add_argument("--only", default=None)
        p.add_argument("--dry-run", action="store_true")
        p.add_argument("--force", default=None)
        p.add_argument("--root", default=".")

    facts = sub.add_parser("facts").add_subparsers(dest="facts_command", required=True)
    sync = facts.add_parser("sync")
    sync.add_argument("--root", default=".")
    sync.add_argument("--yes", action="store_true")

    tune = sub.add_parser("tune").add_subparsers(dest="tune_command", required=True)
    for name in ("show", "apply"):
        t = tune.add_parser(name)
        t.add_argument("run_id")
        t.add_argument("--root", default=".")

    args = parser.parse_args(argv)

    if args.command == "facts":
        return cmd_facts_sync(args)

    root = Path(args.root)
    try:
        _guard_facts(root)
    except FactsDriftError as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_FACTS

    config = load_config(root)
    store = Store(root / "store" / "pipeline.db")
    run_id = uuid.uuid4().hex[:12]
    # Stage dispatch is wired here; each stage function comes from Tasks 11, 12, 17.
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
```

Wire the stage dispatch in this step: `fetch` calls `run_fetch`, `evaluate` calls
`run_evaluate` then `build_report` then `propose` and writes the proposal to
`config/tuning_proposals/<run_id>.yaml`, `generate` calls `run_generate`, `render` calls
`run_render` then `export_run`, and `run` calls all four in order. Catch `BudgetExceeded`
around the whole dispatch, record `halted_reason` on the `runs` row, and return
`EXIT_BUDGET`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_export.py tests/test_cli.py -v`
Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add pipeline/export.py pipeline/cli.py tests/test_export.py tests/test_cli.py
git commit -m "feat: xlsx export with preserved decision column, INBOX read-back, CLI"
```

---

### Task 19: Regression set gating prompt changes

**Files:**
- Create: `tests/regression/postings/*.json`, `tests/regression/expected/*.json`, `tests/test_regression.py`, `scripts/run_regression.py`
- Test: `tests/test_regression.py`

**Interfaces:**
- Consumes: Tasks 12, 15, 17
- Produces: `run_regression(llm, config, facts, curated, prompts) -> RegressionReport`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_regression.py
import json
from pathlib import Path

import pytest

from scripts.run_regression import load_cases, run_regression

CASES = Path("tests/regression/postings")

def test_the_set_covers_every_required_shape():
    kinds = {json.loads(p.read_text(encoding="utf-8"))["kind"] for p in CASES.glob("*.json")}
    assert kinds == {
        "automation_fit", "agentic_fit", "data_engineering_fit",
        "german_no_c1", "hard_pass_language", "hard_pass_microsoft",
        "no_salary_metadata", "duplicate_pair",
    }

def test_assertions_are_tolerant_of_model_nondeterminism(stub_llm, config, facts, curated):
    report = run_regression(stub_llm, config, facts, curated, prompts={"eval": "S"})
    for case in report.cases:
        assert case.gate_a_ok
        assert case.verdict_class == case.expected_verdict_class
        assert abs(case.refined_score - case.expected_score) <= case.tolerance

def test_a_hard_pass_case_never_reaches_generation(stub_llm, config, facts, curated):
    report = run_regression(stub_llm, config, facts, curated, prompts={"eval": "S"})
    hard = [c for c in report.cases if c.kind.startswith("hard_pass")]
    assert hard and all(c.generated is False for c in hard)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_regression.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'scripts.run_regression'`

- [ ] **Step 3: Build the case set and the harness**

Each case file:

```json
{
  "kind": "automation_fit",
  "company": "Acme Robotics GmbH",
  "title": "Automation Engineer (m/w/d)",
  "location": "Berlin, Germany",
  "remote": true,
  "jd_text": "<frozen full JD text pasted here>",
  "expected": {
    "verdict_class": "strong_fit",
    "score": 82.0,
    "tolerance": 12.0,
    "capabilities": ["unattended pipelines", "reliability engineering"],
    "capability_overlap_min": 0.5,
    "generated": true
  }
}
```

Write eight cases, one per required kind. `duplicate_pair` holds two postings with the
same company and title on different URLs and asserts one live row.

```python
# scripts/run_regression.py
"""Runs the frozen posting set before any prompt change ships.

Assertions are on deterministic properties, never string equality: model
output is not deterministic, so an exact-match harness would fail on every
run and stop being read. A golden-set diff is written alongside for human
reading, because a change can pass every assertion and still be worse.
"""
import json
from pathlib import Path

from pydantic import BaseModel

from pipeline.gates.gate_a import run_gate_a

CASES = Path("tests/regression/postings")


class CaseResult(BaseModel):
    kind: str
    refined_score: float
    expected_score: float
    tolerance: float
    verdict_class: str
    expected_verdict_class: str
    capability_overlap: float
    gate_a_ok: bool
    generated: bool


class RegressionReport(BaseModel):
    cases: list[CaseResult]

    @property
    def passed(self) -> bool:
        return all(
            c.gate_a_ok
            and c.verdict_class == c.expected_verdict_class
            and abs(c.refined_score - c.expected_score) <= c.tolerance
            for c in self.cases
        )


def load_cases(directory: Path = CASES) -> list[dict]:
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(directory.glob("*.json"))]


def verdict_class(score: float, hard_pass: bool, threshold: float) -> str:
    if hard_pass:
        return "hard_pass"
    return "strong_fit" if score >= threshold + 15 else (
        "apply_with_reframe" if score >= threshold else "below_threshold")
```

Complete the harness: for each case, call the evaluation stage against the frozen text,
compute `verdict_class`, and when the case expects generation, run generation and Gate A
and record `gate_a_ok`. Write `artifacts/regression/<timestamp>.json` as the golden-set
diff.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_regression.py -v`
Expected: 3 passed

- [ ] **Step 5: Run the whole suite**

Run: `python -m pytest -v`
Expected: all tests pass

- [ ] **Step 6: Commit**

```bash
git add tests/regression/ scripts/run_regression.py tests/test_regression.py
git commit -m "feat: regression set gating prompt changes"
```

---

### Task 20: Scheduling, documentation, and the first live run

**Files:**
- Create: `docs/pipeline-runbook.md`, `scripts/daily_run.ps1`
- Modify: `NOW.md`

**Interfaces:**
- Consumes: Task 18 CLI
- Produces: nothing consumed by later tasks

- [ ] **Step 1: Write the runbook**

`docs/pipeline-runbook.md` covers: what each stage does, what to check after a run (row
count, cache hit ratio, budget spend, gate failures, near-miss flags), how to read a
tuning proposal and when to apply one, how to inject a URL through the INBOX tab, what
each exit code means (0 ok, 1 error, 2 budget halted, 3 facts drift), and what to do on
each halt condition.

- [ ] **Step 2: Write the scheduler script**

```powershell
# scripts/daily_run.ps1
$ErrorActionPreference = "Stop"
Set-Location "C:\Users\91910\Downloads\jobs"
python -m pipeline.cli run --root .
$code = $LASTEXITCODE
if ($code -eq 2) { Write-Host "Budget halted. Next run resumes free." }
if ($code -eq 3) { Write-Host "CLAUDE.md changed. Run: python -m pipeline.cli facts sync --yes" }
exit $code
```

Register with Task Scheduler, daily. Confirm with:
`schtasks /query /tn "job-pipeline-daily"`

- [ ] **Step 3: Sync facts and run once with a hard limit**

Run: `python -m pipeline.cli facts sync --yes`
Run: `python -m pipeline.cli fetch --limit 20`
Expected: rows in `store/pipeline.db`, an `exports/run-*.xlsx`, no LLM cost.

Run: `python -m pipeline.cli evaluate --limit 5`
Expected: 5 evaluations, a `FetchQualityReport`, a tuning proposal, spend under $0.10.

Read the report before running generation. Confirm cache hit ratio is above 0.5 on the
second call onward; a ratio near zero means a silent cache invalidator is in the static
block and must be fixed before a full run.

- [ ] **Step 4: Update NOW.md**

Add a "Pipeline" section: where the ledger lives, the daily command, the four exit codes,
the two files that must never be edited by hand (`store/pipeline.db`, any column of the
xlsx except `decision`), and the pointer to the runbook.

- [ ] **Step 5: Commit**

```bash
git add docs/pipeline-runbook.md scripts/daily_run.ps1 NOW.md
git commit -m "docs: pipeline runbook, daily scheduler, NOW.md resume state"
```

---

## Self-Review

**Spec coverage.** Section 3.1 store-not-spreadsheet: Tasks 6 and 18. Section 3.2 config
as configuration: Task 1. Section 4.1 boundary models: Task 5. Section 4.2 store schema:
Task 6. Section 5 identity, dedupe, idempotency: Tasks 2, 3, 4, 11. Section 6 fetch,
adapters, manual injection, deterministic prelim: Tasks 8, 10, 11. Section 7 evaluation,
metrics, tuner, guardrails: Tasks 12, 13, 14. Section 8 generation: Task 17. Section 9
gates: Tasks 15, 16. Section 10 facts integrity: Task 7. Section 11 three-level
observability: Task 9 (`_trace`) and Task 6 (`stage_token_totals`). Section 12 caching:
Task 9 (breakpoint placement, `cache_hit_ratio`) and Task 4 (result caching as the skip
rule). Section 13 budget and regression set: Tasks 9 and 19. Section 14 statelessness:
no store, no task, and no prompt in this plan passes another posting's content into a
call. Section 15 CLI and scheduling: Tasks 18 and 20. Section 16 error handling: Tasks
11, 17 and 18. Section 17 testing: every task.

**Known gap, deliberate.** Section 6.1 says JD page fetching happens where the adapter
payload carries no text. The plan implements `jd_loader` as an injected callable in Task
12 and the Arbeitnow adapter supplies text directly, so the HTTP page fetcher is a
one-function addition to Task 12's loader when the second adapter arrives. It is called
out here rather than left implicit.

**Type consistency.** `posting_id`, `identity_key`, `input_hash`, `run_id` are strings
everywhere. `should_run(posting_id, stage, input_hash) -> bool` is called with that
argument order in Tasks 11, 12 and 17. `run_gate_a(doc, facts, curated, jd_text)` and
`run_gate_b(pdf_paths, curated, max_pages)` keep their signatures across Tasks 15, 16 and
17. `GateFailure` and `GateResult` are defined once in `gate_a.py` and imported by
`gate_b.py`. `SUBSCORE_AXES` is the single axis list used by the scorer, the evaluation
model and the metrics.

**Two implementation notes carried inline rather than silently fixed:** Task 3 contains a
dead loop in `normalise_country` to remove, and Task 11's `seen_identity` annotation is
`dict[str, str]` not `dict[str, PostingStub]`. Both are flagged in their tasks.
