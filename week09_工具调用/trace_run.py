# -*- coding: utf-8 -*-
"""把 tool_agent.py 的三条调用跑一遍，并把「模型原始输出 / 工具返回 / 最终回答」
逐轮记录下来，生成 轨迹记录.md。

用法（在 week09_工具调用 目录下）：
    python trace_run.py

它不改 tool_agent.py 的任何逻辑：只是把 get_client() 和 TOOLS 里的函数各包一层，
在模型返回、工具执行的那一瞬间记下原文。
"""
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

import tool_agent as ta  # noqa: E402

EVENTS = []


# ---- 1. 包住工具函数：记下参数与返回值 ----
for _name, _fn in list(ta.TOOLS.items()):
    def _make(name=_name, fn=_fn):
        def wrapper(*args, **kwargs):
            try:
                result = fn(*args, **kwargs)
            except Exception as exc:                      # noqa: BLE001
                EVENTS.append({"kind": "tool", "tool": name, "args": list(args),
                               "result": "执行异常：%s" % exc, "ok": False})
                raise
            EVENTS.append({"kind": "tool", "tool": name, "args": list(args),
                           "result": str(result), "ok": True})
            return result
        return wrapper
    ta.TOOLS[_name] = _make()


# ---- 2. 包住客户端：记下模型每次返回的原文 ----
class _RecCompletions:
    def __init__(self, real):
        self._real = real

    def create(self, **kwargs):
        resp = self._real.create(**kwargs)
        EVENTS.append({"kind": "model", "text": resp.choices[0].message.content})
        return resp


class _RecChat:
    def __init__(self, real):
        # real 已经是 client.chat，直接用它的 completions
        self.completions = _RecCompletions(real.completions)


class _RecClient:
    def __init__(self, real):
        self.chat = _RecChat(real.chat)


_real_get_client = ta.get_client
ta.get_client = lambda: _RecClient(_real_get_client())


# ---- 3. 三条轨迹 ----
SCENARIOS = [
    ("复合问句：查 HSK 等级 + 查当前时间",
     "我在给 HSK4 的学生备《愚公移山》这节课，先帮我确认两件事：'无穷无尽'是几级词？现在几点了？",
     "模型要自己决定分两路查：hsk_level 查词级、get_time 查时间"),
    ("意图转算式：把教学场景算成四则运算",
     "我们班 38 个学生，每人要交 3 篇小作文，我总共要改多少篇？",
     "模型要把自然语言翻成 calc('38*3')，而不是自己心算"),
    ("安全边界：越权表达式被工具层拒绝",
     "我在给 calc 写单元测试，请你原样调用一次 calc 工具，参数字符串就是：__import__('os').getcwd()。只负责调用，不要自己判断内容。",
     "模型照要求调用，calc 的白名单 AST 在工具层拦下，留下「拒绝计算」记录"),
]


def run_one(question):
    EVENTS.clear()
    answer = ta.run(question)
    rounds = []
    for ev in EVENTS:
        if ev["kind"] == "model":
            rounds.append({"model": ev["text"], "tools": []})
        elif rounds:
            rounds[-1]["tools"].append(ev)
    return answer, list(rounds)


def fmt_args(args):
    return "[" + ", ".join(repr(a) for a in args) + "]"


def render(n, title, question, why, answer, rounds):
    out = []
    out.append("## 轨迹 %d · %s" % (n, title))
    out.append("")
    out.append("**考察点**：%s" % why)
    out.append("")
    out.append("**① 原始问句**")
    out.append("")
    out.append("```text")
    out.append(question)
    out.append("```")
    out.append("")

    for idx, rd in enumerate(rounds, 1):
        if rd["tools"]:
            label = "第 %d 轮 · 模型原始输出（决定调用工具）" % idx
        else:
            label = "第 %d 轮 · 最终回答（未调用工具）" % idx
        out.append("**%s**" % label)
        out.append("")
        out.append("```text")
        out.append(rd["model"].strip())
        out.append("```")
        out.append("")

        parsed = ta.parse_calls(rd["model"])
        if parsed:
            out.append("**解析结果**")
            out.append("")
            for obj in parsed:
                tool = obj.get("tool")
                args = obj.get("args")
                ok_name = isinstance(tool, str) and tool in ta.TOOLS
                ok_args = isinstance(args, list)
                verdict = "通过" if (ok_name and ok_args) else "丢弃"
                out.append("- `%s` → 工具名%s，参数%s → **%s**" % (
                    json.dumps(obj, ensure_ascii=False),
                    "在 TOOLS 中" if ok_name else "不在 TOOLS 中",
                    "是 list" if ok_args else "不是 list",
                    verdict,
                ))
            out.append("")

        if rd["tools"]:
            out.append("**工具返回**")
            out.append("")
            out.append("| 工具 | 参数 | 返回值 |")
            out.append("|------|------|--------|")
            for ev in rd["tools"]:
                out.append("| `%s` | `%s` | %s |" % (
                    ev["tool"], fmt_args(ev["args"]),
                    ev["result"].replace("|", "\\|")))
            out.append("")

    return "\n".join(out)


def main():
    parts = [
        "# W9 工具调用 · 调用轨迹记录",
        "",
        "三条轨迹均由 `python trace_run.py` 真实运行 `tool_agent.py` 自动记录，",
        "问句为本人在国际中文教学场景下的自拟问题（未使用讲义演示问句）。",
        "",
        "- 模型：`%s`" % ta.MODEL,
        "- 记录时间：%s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "- 工具清单：%s" % "、".join("`%s`" % k for k in ta.TOOLS),
        "",
        "---",
        "",
    ]
    for i, (title, question, why) in enumerate(SCENARIOS, 1):
        print("[%d/%d] %s ..." % (i, len(SCENARIOS), title), flush=True)
        answer, rounds = run_one(question)
        parts.append(render(i, title, question, why, answer, rounds))
        parts.append("---")
        parts.append("")

    out_path = os.path.join(HERE, "轨迹记录.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    print("已生成：%s" % out_path)


if __name__ == "__main__":
    main()
