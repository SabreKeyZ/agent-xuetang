from pathlib import Path

import pytest

from ticketdesk.agents.supervisor import Supervisor
from ticketdesk.config import project_root
from ticketdesk.loader import (
    load_all_tickets,
    tickets_from_csv,
    tickets_from_dir,
    tickets_from_github,
    tickets_from_github_issues,
)
from ticketdesk.safety import NEVER_EXECUTE, NEVER_PAY
from ticketdesk.tools import payment as payment_mod

_SAMPLES = Path(__file__).resolve().parents[1] / "samples"


def _clear_import_env(monkeypatch) -> None:
    for key in ("TICKETDESK_IMPORT_CSV", "TICKETDESK_IMPORT_DIR", "TICKETDESK_GITHUB_REPO", "GITHUB_TOKEN"):
        monkeypatch.delenv(key, raising=False)


def test_default_catalog_is_fixtures_without_env_or_token(monkeypatch):
    _clear_import_env(monkeypatch)
    tickets = load_all_tickets()
    ids = {t.id for t in tickets}
    fixtures = {t.fixture_id for t in tickets}
    assert len(tickets) >= 8
    assert "T-1001" in ids
    assert "missing-order-id" in fixtures
    assert "happy-quality" in fixtures
    assert "T-IMP-01" not in ids
    assert "sample-csv" not in fixtures
    assert (project_root() / "fixtures" / "tickets" / "happy-quality.json").is_file()


def test_sample_csv_maps_onto_ticket():
    tickets = tickets_from_csv(_SAMPLES / "tickets.csv")
    assert [t.id for t in tickets] == ["T-IMP-01", "T-IMP-02"]
    first = tickets[0]
    assert first.title == "墨条缺角"
    assert first.body.startswith("开箱发现砚台小样缺角")
    assert first.order_id == "QX-202608-8801"
    assert first.customer_name == "导入顾客"
    assert first.amount_yuan == 72
    assert first.refund_yuan == 72
    assert first.attachments == ["unbox.jpg"]
    assert first.labels == ["质量"]
    assert first.channel == "在线客服"
    assert first.fixture_id == "sample-csv"
    assert first.shop_id == "qingxia"
    assert first.priority == "P2"


def test_sample_dir_maps_onto_ticket():
    tickets = tickets_from_dir(_SAMPLES / "dir")
    assert len(tickets) == 1
    ticket = tickets[0]
    assert ticket.id == "T-IMP-11"
    assert ticket.fixture_id == "sample-dir"
    assert ticket.title == "砚台裂纹"
    assert ticket.refund_yuan == 72
    assert "crack.jpg" in ticket.attachments


def test_env_csv_replaces_fixtures(monkeypatch):
    _clear_import_env(monkeypatch)
    monkeypatch.setenv("TICKETDESK_IMPORT_CSV", str(_SAMPLES / "tickets.csv"))
    tickets = load_all_tickets()
    assert {t.id for t in tickets} == {"T-IMP-01", "T-IMP-02"}
    assert all(t.fixture_id == "sample-csv" for t in tickets)
    assert not any(t.id == "T-1001" for t in tickets)


def test_env_dir_replaces_fixtures(monkeypatch):
    _clear_import_env(monkeypatch)
    monkeypatch.setenv("TICKETDESK_IMPORT_DIR", str(_SAMPLES / "dir"))
    tickets = load_all_tickets()
    assert [t.id for t in tickets] == ["T-IMP-11"]


def test_missing_csv_falls_back_to_fixtures(monkeypatch):
    _clear_import_env(monkeypatch)
    monkeypatch.setenv("TICKETDESK_IMPORT_CSV", "/no/such/ticketdesk-import.csv")
    tickets = load_all_tickets()
    assert any(t.fixture_id == "happy-quality" for t in tickets)
    assert any(t.id == "T-1001" for t in tickets)


def test_invalid_csv_raises_clearly_and_loader_falls_back(tmp_path, monkeypatch):
    _clear_import_env(monkeypatch)
    empty = tmp_path / "empty.csv"
    empty.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="表头"):
        tickets_from_csv(empty)

    missing = tmp_path / "nope.csv"
    with pytest.raises(FileNotFoundError, match="不存在"):
        tickets_from_csv(missing)

    garbage = tmp_path / "garbage.csv"
    garbage.write_text("not,a,ticket,header\n,,,\n", encoding="utf-8")
    with pytest.raises(ValueError, match="没有有效行"):
        tickets_from_csv(garbage)

    monkeypatch.setenv("TICKETDESK_IMPORT_CSV", str(empty))
    tickets = load_all_tickets()
    assert any(t.fixture_id == "missing-order-id" for t in tickets)


def test_github_issues_map_onto_ticket():
    tickets = tickets_from_github_issues(
        [
            {
                "number": 7,
                "title": "墨条裂了",
                "body": "请按质量问题退款",
                "created_at": "2026-08-30T02:00:00Z",
                "updated_at": "2026-08-30T03:00:00Z",
                "user": {"login": "buyer", "id": 42},
                "labels": [{"name": "bug"}],
            },
            {"number": 8, "title": "PR", "pull_request": {"url": "https://example.invalid"}, "user": {}},
        ]
    )
    assert len(tickets) == 1
    ticket = tickets[0]
    assert ticket.id == "GH-7"
    assert ticket.title == "墨条裂了"
    assert ticket.body == "请按质量问题退款"
    assert ticket.customer_name == "buyer"
    assert ticket.customer_id == "gh_buyer"
    assert ticket.channel == "GitHub"
    assert ticket.labels == ["bug"]
    assert ticket.fixture_id == "github-7"
    assert ticket.order_id == ""
    assert ticket.amount_yuan == 0


def test_github_without_token_does_not_fetch(monkeypatch):
    _clear_import_env(monkeypatch)
    monkeypatch.setenv("TICKETDESK_GITHUB_REPO", "octo/desk")
    called: list[int] = []

    def boom(*_args, **_kwargs):
        called.append(1)
        raise AssertionError("missing token must not hit GitHub")

    monkeypatch.setattr("ticketdesk.loader.fetch_github_issues", boom)
    tickets = load_all_tickets()
    assert called == []
    assert any(t.fixture_id == "happy-quality" for t in tickets)


def test_github_token_without_repo_stays_on_fixtures(monkeypatch):
    _clear_import_env(monkeypatch)
    monkeypatch.setenv("GITHUB_TOKEN", "not-a-real-token")
    called: list[int] = []
    monkeypatch.setattr("ticketdesk.loader.fetch_github_issues", lambda *_a, **_k: called.append(1) or [])
    tickets = load_all_tickets()
    assert called == []
    assert any(t.id == "T-1001" for t in tickets)


def test_github_fetch_failure_falls_back(monkeypatch):
    _clear_import_env(monkeypatch)
    monkeypatch.setenv("GITHUB_TOKEN", "not-a-real-token")
    monkeypatch.setenv("TICKETDESK_GITHUB_REPO", "octo/desk")

    def boom(*_args, **_kwargs):
        raise OSError("network down")

    monkeypatch.setattr("ticketdesk.loader.fetch_github_issues", boom)
    tickets = load_all_tickets()
    assert any(t.fixture_id == "happy-quality" for t in tickets)


def test_github_success_uses_mapped_tickets(monkeypatch):
    _clear_import_env(monkeypatch)
    monkeypatch.setenv("GITHUB_TOKEN", "not-a-real-token")
    monkeypatch.setenv("TICKETDESK_GITHUB_REPO", "octo/desk")
    monkeypatch.setattr(
        "ticketdesk.loader.fetch_github_issues",
        lambda *_a, **_k: [
            {
                "number": 3,
                "title": "只读 Issues",
                "body": "不要打款",
                "created_at": "2026-08-30T01:00:00Z",
                "user": {"login": "reader"},
                "labels": [],
            }
        ],
    )
    tickets = load_all_tickets()
    assert [t.id for t in tickets] == ["GH-3"]
    assert tickets[0].title == "只读 Issues"


def test_github_direct_import_requires_token():
    with pytest.raises(PermissionError, match="GITHUB_TOKEN"):
        tickets_from_github("octo/desk", "")


def test_import_does_not_enable_pay_or_execute(monkeypatch):
    _clear_import_env(monkeypatch)
    monkeypatch.setenv("TICKETDESK_IMPORT_CSV", str(_SAMPLES / "tickets.csv"))
    tickets = load_all_tickets()
    assert tickets
    assert NEVER_PAY is True
    assert NEVER_EXECUTE is True
    out = Supervisor().process(tickets[0])
    assert out["executed"] is False
    assert out["gate"]["never_pay"] is True
    assert out["gate"]["never_execute"] is True
    probe = payment_mod.refund(tickets[0].refund_yuan, "qingxia:refund:import:8800", confirm=True)
    assert probe["executed"] is False
    assert probe["status"] in {"confirm_required", "demo_forbidden"}
    coupon = payment_mod.coupon(10, "qingxia:coupon:import:1000", confirm=True)
    assert coupon["executed"] is False
