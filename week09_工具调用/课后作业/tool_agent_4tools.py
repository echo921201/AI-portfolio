# W9 课后作业 2：给 tool_agent.py 加第 4 个工具 —— 课文难度评估 text_level
# 在课堂版 3 工具的基础上，只加了 text_level 一个函数 + TOOLS/SYS 各改一行，
# 循环（parse_calls / run）完全没动，用来验证「加工具不用改主循环」。
# 依赖：pip install openai python-dotenv
import os
import csv
import sys
import ast
import json
import re
import operator
import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import weekpath  # noqa: E402  数据路径 + 加载 .env

weekpath.load_env()

import openai  # noqa: E402

VOCAB = weekpath.data_path("生词表.csv")

MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

_client = None


def get_client():
    global _client
    if _client is None:
        key = os.getenv("DEEPSEEK_API_KEY")
        if not key:
            raise RuntimeError("未配置 DEEPSEEK_API_KEY，请先在 .env 中填写")
        base = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
        _client = openai.OpenAI(base_url=base, api_key=key)
    return _client


def get_time():
    return str(datetime.datetime.now())


# ---- 安全计算：白名单 AST，绝不使用裸 eval ----
_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
    ast.USub: operator.neg, ast.UAdd: operator.pos,
}


def _eval_node(node):
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.operand))
    raise ValueError("只允许数字与 + - * / ** % 运算")


def calc(expr):
    """教学演示用：只做四则运算。为什么不用 eval？
    因为 eval 会执行任意 Python 代码，是典型的安全反模式（本课程伦理红线之一）。"""
    try:
        return str(_eval_node(ast.parse(str(expr), mode="eval")))
    except ZeroDivisionError:
        return "错误：除数为 0"
    except Exception as e:
        return "拒绝计算：%s" % e


def hsk_level(word):
    with open(VOCAB, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["词汇"].strip() == str(word).strip():
                return "%s 是 %s 级" % (word, row["HSK等级"])
    return "未找到 %s" % word


# ================= 第 4 个工具：课文难度评估 =================
def _load_vocab():
    with open(VOCAB, encoding="utf-8") as f:
        return {r["词汇"].strip(): r["HSK等级"].strip()
                for r in csv.DictReader(f) if r["词汇"].strip()}


def _segment(text, vocab):
    """最长匹配切词：词表里有的按最长词切；切不出来的连续汉字连成一个「未收录片段」。

    中文没有空格，这里不引入分词库，用「词表最长匹配 + 未收录兜底」得到一个粗略切分，
    够回答「哪些词超纲、词表覆盖多少」这个问题。
    """
    maxlen = max(len(w) for w in vocab)
    pieces, buf, i = [], "", 0
    while i < len(text):
        ch = text[i]
        if not ("\u4e00" <= ch <= "\u9fff"):     # 标点、数字、换行都不进词块
            if buf:
                pieces.append(buf)
                buf = ""
            i += 1
            continue
        hit = ""
        for L in range(min(maxlen, len(text) - i), 0, -1):
            seg = text[i:i + L]
            if seg in vocab:
                hit = seg
                break
        if hit:
            if buf:
                pieces.append(buf)
                buf = ""
            pieces.append(hit)
            i += len(hit)
        else:
            buf += ch
            i += 1
    if buf:
        pieces.append(buf)
    return pieces


def text_level(text, target="4"):
    """课文难度评估。

    输入：
        text   —— data/ 目录下的课文文件名（如 "愚公移山.txt"），或直接给一段课文原文
        target —— 目标等级，如 "4" 或 "HSK4"
    输出（一段话）：
        词块数、词表覆盖率、目标等级以上的超纲词、较长的未收录片段
    """
    try:
        src = str(text)
        path = weekpath.data_path(src)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                body, name = f.read(), src
        else:
            body, name = src, "（直接传入的片段）"

        vocab = _load_vocab()
        pieces = _segment(body, vocab)
        if not pieces:
            return "没有可分析的中文内容"

        m = re.search(r"\d+", str(target))
        tgt = int(m.group()) if m else 4

        known = [p for p in pieces if p in vocab]
        unknown = [p for p in pieces if p not in vocab]
        over = sorted({p for p in known if vocab[p].isdigit() and int(vocab[p]) > tgt},
                      key=lambda w: (-int(vocab[w]), -len(w)))
        total_chars = sum(len(p) for p in pieces)
        covered_chars = sum(len(p) for p in known)
        cover = 100.0 * covered_chars / max(1, total_chars)
        longest = sorted({p for p in unknown if len(p) >= 2}, key=len, reverse=True)[:5]
        longest = ["%s…" % p[:12] if len(p) > 12 else p for p in longest]

        return ("课文《%s》：共 %d 个汉字，词表覆盖 %d 个（覆盖率 %.1f%%；样本词表 %d 词）；"
                "HSK%d 以上超纲词 %d 个：%s；词表外片段 %d 处，最长的如：%s"
                % (name, total_chars, covered_chars, cover, len(vocab), tgt, len(over),
                   "、".join("%s（%s级）" % (w, vocab[w]) for w in over) or "无",
                   len(unknown), "、".join(longest) or "无"))
    except Exception as e:
        return "评估失败：%s" % e


TOOLS = {"get_time": get_time, "calc": calc, "hsk_level": hsk_level, "text_level": text_level}

SYS = ("你是国际中文助教。可用工具只有这 4 个：get_time（查当前时间，无参数）、"
       "calc（四则运算，如 calc('35*24')）、hsk_level（查生词 HSK 等级，如 hsk_level('把')）、"
       "text_level（评估课文难度，两个参数：课文文件名与目标等级，如 text_level('愚公移山.txt', '4')）。"
       '如需调用，只输出一行 JSON，格式：{"tool": "工具名", "args": [参数]}；'
       "一次只调用一个工具，绝不编造不存在的工具名；无需工具时直接回答。")


def parse_calls(txt):
    """容错解析：剥掉 ```json 围栏与前后客套话，返回全部工具调用（0/1/多个）。"""
    s = (txt or "").strip()
    s = s.replace("```json", "").replace("```", "").strip()
    try:
        obj = json.loads(s)
        return [obj] if isinstance(obj, dict) else []
    except Exception:
        m = re.search(r"\{.*\}", s, re.S)
        if m:
            try:
                obj = json.loads(m.group())
                if isinstance(obj, dict):
                    return [obj]
            except Exception:
                pass
        calls = []
        for blk in re.findall(r"\{[^{}]*\}", s):
            try:
                obj = json.loads(blk)
            except Exception:
                continue
            if isinstance(obj, dict):
                calls.append(obj)
        return calls


def run(user_msg, max_calls=2):
    msgs = [{"role": "system", "content": SYS}, {"role": "user", "content": user_msg}]
    for _ in range(max_calls):
        txt = get_client().chat.completions.create(
            model=MODEL, messages=msgs).choices[0].message.content
        calls = [c for c in parse_calls(txt)
                 if isinstance(c.get("tool"), str) and c.get("tool") in TOOLS]
        if not calls:
            return txt
        results = []
        for call in calls:
            args = call.get("args") or []
            if not isinstance(args, list):
                results.append("工具参数格式错误：%r" % (args,))
                continue
            try:
                results.append("%s%r → %s" % (call["tool"], args, TOOLS[call["tool"]](*args)))
            except Exception as e:
                results.append("工具执行失败：%s" % e)
        msgs += [{"role": "assistant", "content": txt},
                 {"role": "user", "content": "工具返回：%s。请据此作答。" % "；".join(results)}]
    return get_client().chat.completions.create(
        model=MODEL, messages=msgs).choices[0].message.content


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or ("我在给 HSK4 的学生备《愚公移山》，帮我看看这篇课文难度如何，"
                                   "有哪些超纲词？")
    print("用户输入：", q)
    print("助手：", run(q))
