from __future__ import annotations

from askhall.llm import complete
from askhall.rag import Hit, retrieve


class Tutor:
    name = "tutor"

    def run(self, question: str, hits: list[Hit] | None = None) -> dict:
        hits = hits if hits is not None else retrieve(question, k=4)
        if not hits:
            return {
                "role": self.name,
                "title": "教材里没找到",
                "body": "检索没有命中。我不能凭印象编一周课。请换教材里出现过的词，或先打开 docs/weeks。",
                "citations": [],
                "quotes": [],
                "mode": "extractive",
            }
        quotes = [h.as_dict() for h in hits]
        extractive = _render_quotes(hits)
        llm_text = complete(
            f"学员问题：{question}\n\n只能用下面摘录回答，并在句末标 path:line。\n"
            + "\n\n".join(f"{h.chunk.citation}\n{h.chunk.text}" for h in hits),
            system="你是问学堂讲师。没有摘录支撑的句子不要写。",
        )
        body = llm_text.strip() if llm_text else extractive
        return {
            "role": self.name,
            "title": "教材摘录",
            "body": body,
            "citations": [h.chunk.citation for h in hits],
            "quotes": quotes,
            "mode": "llm" if llm_text else "extractive",
        }


def _render_quotes(hits: list[Hit]) -> str:
    parts = ["没有云端模型时，我只给你原文。请对照引用跳回文件：", ""]
    for h in hits:
        snippet = h.chunk.text.strip().splitlines()
        preview = "\n".join(snippet[:8])
        parts.append(f"> {preview}\n\n— {h.chunk.citation}")
    return "\n\n".join(parts)
