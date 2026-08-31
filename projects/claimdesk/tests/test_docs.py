from claimdesk.agents.supervisor import Supervisor
from claimdesk.loader import load_claim


def test_missing_docs_is_supplement_not_closed():
    out = Supervisor().process(load_claim("missing-docs"))
    assert out["docs"]["complete"] is False
    assert "物流签收图" in out["docs"]["missing"] or "发票或支付截图" in out["docs"]["missing"]
    assert out["decision"]["recommendation"] == "补件"
    assert out["executed"] is False
