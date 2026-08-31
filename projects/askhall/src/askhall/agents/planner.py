from __future__ import annotations

from askhall.llm import complete
from askhall.rag import Hit, retrieve


class Planner:
    name = "planner"

    def run(self, question: str, hits: list[Hit] | None = None) -> dict:
        hits = hits if hits is not None else retrieve(question, k=5)
        weeks = _unique_week_files(hits)
        steps = _extractive_steps(question, weeks, hits)
        llm_text = None
        if hits:
            packed = "\n".join(f"- {h.chunk.citation} {h.chunk.text[:180]}" for h in hits[:4])
            llm_text = complete(
                f"学员问题：{question}\n教材摘录：\n{packed}\n\n"
                "用中文列恰好三步学习计划。每一步必须点名一个 path:line。"
                "不要编造仓库里没有的文件。",
                system="你是问学堂的规划员。只依据摘录。",
            )
        body = llm_text.strip() if llm_text else "\n".join(f"{i}. {s}" for i, s in enumerate(steps, start=1))
        citations = [h.chunk.citation for h in hits[:4]]
        return {
            "role": self.name,
            "title": "三步学习计划",
            "body": body,
            "steps": steps,
            "citations": citations,
            "mode": "llm" if llm_text else "extractive",
        }


def _unique_week_files(hits: list[Hit]) -> list[Hit]:
    seen: set[str] = set()
    out: list[Hit] = []
    for hit in hits:
        if "/weeks/" not in hit.chunk.path:
            continue
        if hit.chunk.path in seen:
            continue
        seen.add(hit.chunk.path)
        out.append(hit)
    if not out:
        return hits[:3]
    return out[:3]


def _extractive_steps(question: str, weeks: list[Hit], hits: list[Hit]) -> list[str]:
    if not weeks and not hits:
        return [
            "先在 docs/weeks 目录用关键字搜你的问题（教材里暂时没有命中）。",
            "打开第 1 周，确认循环的三步还记得。",
            "把原话改写成教材里出现过的词再问一次。",
        ]
    source = weeks or hits
    labels = [
        "读标题和「目标」小节，圈出你还不认识的词",
        "对着「你将做出的东西」把命令跑一遍",
        "用「验收标准」给自己打勾，缺的留到下一轮",
    ]
    steps = []
    for i, hit in enumerate(source[:3]):
        title = next((ln.lstrip("# ").strip() for ln in hit.chunk.text.splitlines() if ln.strip()), hit.chunk.path)
        steps.append(f"看 {hit.chunk.citation}（{title}）：{labels[i]}")
    while len(steps) < 3:
        steps.append(f"回到问题「{question[:20]}」，用考试官出一道题检查自己。")
    return steps[:3]
