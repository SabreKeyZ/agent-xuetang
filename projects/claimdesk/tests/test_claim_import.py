from pathlib import Path

import pytest

from claimdesk.agents.supervisor import Supervisor
from claimdesk.config import project_root
from claimdesk.loader import claims_from_csv, claims_from_json, load_all_claims
from claimdesk.tools.payment import NEVER_PAYOUT, payout

_SAMPLES = Path(__file__).resolve().parents[1] / "samples"


def _clear_import_env(monkeypatch) -> None:
    for key in ("CLAIMDESK_IMPORT_CSV", "CLAIMDESK_IMPORT_JSON"):
        monkeypatch.delenv(key, raising=False)


def test_default_catalog_is_fixtures_without_env(monkeypatch):
    _clear_import_env(monkeypatch)
    claims = load_all_claims()
    ids = {c.id for c in claims}
    fixtures = {c.fixture_id for c in claims}
    assert len(claims) >= 8
    assert "C-2009" in ids
    assert "valid-low" in fixtures
    assert "missing-docs" in fixtures
    assert "C-IMP-01" not in ids
    assert "sample-csv" not in fixtures
    assert (project_root() / "fixtures" / "claims" / "valid-low.json").is_file()


def test_sample_csv_maps_onto_claim():
    claims = claims_from_csv(_SAMPLES / "claims.csv")
    assert len(claims) == 1
    claim = claims[0]
    assert claim.id == "C-IMP-01"
    assert claim.product == "freight"
    assert claim.insured_name == "导入被保险人"
    assert claim.claimant_name == "导入被保险人"
    assert claim.policy_no == "QT-FR-202608-901"
    assert claim.amount_yuan == 12
    assert claim.narrative.startswith("本地 CSV 导入")
    assert claim.fixture_id == "sample-csv"
    assert claim.tracking == "SF000IMP1"
    kinds = [str(a.get("kind") or a.get("name") or "") for a in claim.attachments]
    assert "运单号" in kinds
    assert "物流签收图" in kinds


def test_sample_json_maps_onto_claim():
    claims = claims_from_json(_SAMPLES / "claims.json")
    assert len(claims) == 1
    claim = claims[0]
    assert claim.id == "C-IMP-11"
    assert claim.fixture_id == "sample-json"
    assert claim.narrative.startswith("本地 JSON 导入")
    assert claim.amount_yuan == 12
    assert len(claim.attachments) == 3
    assert claim.attachments[0]["kind"] == "运单号"


def test_env_csv_replaces_fixtures(monkeypatch):
    _clear_import_env(monkeypatch)
    monkeypatch.setenv("CLAIMDESK_IMPORT_CSV", str(_SAMPLES / "claims.csv"))
    claims = load_all_claims()
    assert [c.id for c in claims] == ["C-IMP-01"]
    assert not any(c.id == "C-2009" for c in claims)


def test_env_json_replaces_fixtures(monkeypatch):
    _clear_import_env(monkeypatch)
    monkeypatch.setenv("CLAIMDESK_IMPORT_JSON", str(_SAMPLES / "claims.json"))
    claims = load_all_claims()
    assert [c.id for c in claims] == ["C-IMP-11"]


def test_missing_json_falls_back_to_fixtures(monkeypatch):
    _clear_import_env(monkeypatch)
    monkeypatch.setenv("CLAIMDESK_IMPORT_JSON", "/no/such/claimdesk-import.json")
    claims = load_all_claims()
    assert any(c.fixture_id == "valid-low" for c in claims)
    assert any(c.id == "C-2009" for c in claims)


def test_invalid_json_raises_clearly_and_loader_falls_back(tmp_path, monkeypatch):
    _clear_import_env(monkeypatch)
    missing = tmp_path / "nope.json"
    with pytest.raises(FileNotFoundError, match="不存在"):
        claims_from_json(missing)

    garbage = tmp_path / "garbage.json"
    garbage.write_text("{not json", encoding="utf-8")
    with pytest.raises(ValueError):
        claims_from_json(garbage)

    empty_list = tmp_path / "empty.json"
    empty_list.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="没有有效"):
        claims_from_json(empty_list)

    empty_csv = tmp_path / "empty.csv"
    empty_csv.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="表头"):
        claims_from_csv(empty_csv)

    monkeypatch.setenv("CLAIMDESK_IMPORT_JSON", str(garbage))
    claims = load_all_claims()
    assert any(c.fixture_id == "missing-docs" for c in claims)


def test_import_does_not_enable_payout(monkeypatch):
    _clear_import_env(monkeypatch)
    monkeypatch.setenv("CLAIMDESK_IMPORT_JSON", str(_SAMPLES / "claims.json"))
    claims = load_all_claims()
    assert claims
    assert NEVER_PAYOUT is True
    out = Supervisor().process(claims[0])
    assert out["executed"] is False
    probe = payout(claims[0].amount_yuan, "qingtu:payout:import:1200", confirm=True)
    assert probe["executed"] is False
    assert probe["status"] == "confirm_required"
    assert out["decision"]["payout"]["executed"] is False
