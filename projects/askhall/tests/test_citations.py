from askhall.agents.supervisor import Supervisor
from askhall.config import docs_root
from askhall.rag import citation_exists, retrieve


def test_mcp_retrieval_points_at_real_file():
    hits = retrieve("第几周写 MCP", k=5)
    assert hits
    root = docs_root()
    for hit in hits:
        assert citation_exists(hit.chunk.citation, root)
        assert (root / hit.chunk.path).is_file()


def test_tutor_citations_exist_on_disk():
    out = Supervisor().handle("什么是短记忆和长记忆")
    cites = out["turns"][0]["citations"]
    assert cites, "讲解必须带引用"
    assert all(citation_exists(c) for c in cites)


def test_planner_cites_week_files():
    out = Supervisor().handle("怎么学 MCP")
    cites = out["turns"][0]["citations"]
    assert cites
    assert all(citation_exists(c) for c in cites)


def test_unknown_jargon_does_not_invent_week_file():
    out = Supervisor().handle("什么是内部系统 FlipFlopZetaQueue")
    cites = out["turns"][0].get("citations") or []
    for c in cites:
        assert "FlipFlopZetaQueue" not in c
        assert citation_exists(c)
