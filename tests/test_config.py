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

def test_real_config_loads():
    repo_root = Path(__file__).resolve().parents[1]
    cfg = load_config(repo_root)
    assert "NO" in cfg.constraints.countries
    assert all(isinstance(c, str) for c in cfg.constraints.countries)
    assert all(isinstance(lang, str) for lang in cfg.constraints.working_languages)
