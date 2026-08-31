"""第 0 周：缺 Key 必须诚实退出。不打网。"""

from __future__ import annotations

import hello_chat


def test_missing_env_file_tells_you_to_copy(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(hello_chat, "repo_root", lambda: tmp_path)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    code = hello_chat.main()
    err = capsys.readouterr().err
    assert code == 2
    assert "缺少 .env" in err
    assert ".env.example" in err
    assert "是空的" not in err


def test_empty_key_in_existing_env(monkeypatch, capsys, tmp_path):
    (tmp_path / ".env").write_text("OPENAI_API_KEY=\n", encoding="utf-8")
    monkeypatch.setattr(hello_chat, "repo_root", lambda: tmp_path)
    monkeypatch.setenv("OPENAI_API_KEY", "")
    code = hello_chat.main()
    err = capsys.readouterr().err
    assert code == 2
    assert "是空的" in err
    assert "缺少 .env" not in err


def test_missing_key_exits_2(monkeypatch, capsys, tmp_path):
    (tmp_path / ".env").write_text("OPENAI_API_KEY=\n", encoding="utf-8")
    monkeypatch.setattr(hello_chat, "repo_root", lambda: tmp_path)
    monkeypatch.setenv("OPENAI_API_KEY", "")
    code = hello_chat.main()
    captured = capsys.readouterr()
    assert code == 2
    assert "OPENAI_API_KEY" in captured.err


def test_load_dotenv_does_not_override_existing(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("OPENAI_API_KEY=from-file\n", encoding="utf-8")
    monkeypatch.setenv("OPENAI_API_KEY", "already-set")
    hello_chat.load_dotenv(env)
    assert hello_chat.os.environ["OPENAI_API_KEY"] == "already-set"
