from claimdesk.agents.supervisor import Supervisor
from claimdesk.loader import load_claim
from claimdesk.rag import citation_exists


def test_incident_date_uses_v2_not_v1():
    out = Supervisor().process(load_claim("wrong-policy-version"))
    assert out["policy_version"] == "v2"
    assert out["citations"]
    assert all(citation_exists(c) for c in out["citations"])
    assert all("v1" not in c for c in out["citations"])
    assert any("v2" in c or "3.2" in c for c in out["citations"])
    assert out["decision"]["recommendation"] == "拒赔"


def test_exclusion_cites_clause():
    out = Supervisor().process(load_claim("exclusion-fragile"))
    assert out["decision"]["recommendation"] == "拒赔"
    assert out["citations"]
    assert any("3.2" in c for c in out["citations"])


def test_no_clause_red_refuse():
    out = Supervisor().process(load_claim("no-clause"))
    assert out["clause"]["refused"] is True
    assert out["citations"] == []
    assert "没有引用" in (out["banner"] or out["clause"]["title"])
    assert out["executed"] is False
