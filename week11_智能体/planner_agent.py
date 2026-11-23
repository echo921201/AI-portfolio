import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import weekpath  # noqa: E402  让 from llm / from rag_qa 跨周导入生效

weekpath.load_env()

from llm import LLM  # noqa: E402
from rag_qa import retrieve  # noqa: E402

llm = LLM()

PLAN_PROMPT = "把《%s》的备课拆成 4 个有序步骤：定教学要点 / 写教学目标 / 出教案框架 / 配 3 道练习。只输出步骤列表。"


def planner_agent(lesson, retriever=None, auto_confirm=False, prefer="local"):
    """备课智能体。retriever 传 None 时自动用 W7 的知识库。
    prefer 透传给 LLM（W15 页面的"本地优先/云端优先"靠它生效）。
    与教师版参考实现的函数签名完全一致（参数名也叫 lesson），方便对照替换。"""
    plan = llm.ask(PLAN_PROMPT % lesson, prefer=prefer)
    steps = [s.strip(" 0123456789.、") for s in plan.splitlines() if s.strip()]
    ctx = retrieve(lesson) if retriever is None else "\n".join(
        d.page_content for d in retriever.invoke(lesson))
    outputs = []
    for step in steps:
        out = llm.ask("资料：\n%s\n\n按步骤执行：%s" % (ctx, step), prefer=prefer)
        outputs.append("【%s】\n%s" % (step, out))
        # 注入防护：执行前人工确认点
        if not auto_confirm:
            print("[待人工确认] %s\n%s\n---" % (step, out))
    return "\n\n".join(outputs)


if __name__ == "__main__":
    # 支持 --cloud / --local：本地模型过慢或没装模型时用云端
    #   python planner_agent.py            → 本地
    #   python planner_agent.py --cloud    → 云端
    prefer = "api" if "--cloud" in sys.argv else "local"
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    lesson = " ".join(args) or "愚公移山"
    print(planner_agent(lesson, auto_confirm=True, prefer=prefer))
