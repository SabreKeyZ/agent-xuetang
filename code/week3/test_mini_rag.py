from pathlib import Path

from mini_rag import build_corpus, repo_root, retrieve


def test_repo_root_finds_weeks():
    root = repo_root()
    assert (root / "docs" / "weeks" / "04-mcp-and-skills.md").is_file()


def test_mcp_query_hits_week4():
    chunks = build_corpus()
    hits = retrieve("第几周写 MCP", chunks, k=5)
    assert hits, "应当至少有一条命中"
    paths = [c.path for _, c in hits]
    assert any(p.endswith("04-mcp-and-skills.md") for p in paths)
    _score, top = hits[0]
    assert Path(repo_root() / top.path).is_file()
    text = (repo_root() / top.path).read_text(encoding="utf-8").splitlines()
    assert 1 <= top.start_line <= len(text)


def test_roles_query_hits_jobs():
    chunks = build_corpus()
    hits = retrieve("岗位地图", chunks, k=5)
    assert any(c.path.endswith("jobs/roles.md") for _, c in hits)


def test_empty_corpus_no_hits():
    assert retrieve("MCP", [], k=3) == []


def test_citation_format():
    chunks = build_corpus()
    hits = retrieve("问学堂有哪些角色", chunks, k=3)
    assert hits
    cite = hits[0][1].citation
    assert ":" in cite
    path, line = cite.rsplit(":", 1)
    assert path.endswith(".md")
    assert line.isdigit()
