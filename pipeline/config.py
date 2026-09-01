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
