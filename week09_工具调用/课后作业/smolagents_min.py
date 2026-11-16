# W9 课后作业 4（A 路径）：smolagents 最小示例
#   —— 用框架重写两个工具：hsk_level（单参数）与 text_level（多参数）
# 依赖：pip install smolagents（Python >= 3.10）
# 运行：python smolagents_min.py（在 week09_工具调用/课后作业 目录下）
import os
import csv
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))   # 仓库根目录（weekpath.py 在这）
sys.path.insert(0, HERE)                                      # 课后作业目录（复用第 4 个工具的实现）

import weekpath  # noqa: E402

weekpath.load_env()

from smolagents import tool, ToolCallingAgent, OpenAIModel  # noqa: E402
from tool_agent_4tools import text_level as _text_level_impl  # noqa: E402

VOCAB = weekpath.data_path("生词表.csv")


@tool
def hsk_level(word: str) -> str:
    """查课程生词表里词语的 HSK 等级。

    Args:
        word: 要查询的汉字或词语
    """
    with open(VOCAB, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["词汇"].strip() == str(word).strip():
                return "%s 是 %s 级" % (word, row["HSK等级"])
    return "未找到 %s" % word


@tool
def text_level(text: str, target: str) -> str:
    """评估一篇课文对某个 HSK 等级的难度：返回字数、词表覆盖率、超纲词与词表外片段。

    Args:
        text: 课文文件名（放在仓库 data/ 目录下），例如 愚公移山.txt
        target: 目标 HSK 等级，例如 4
    """
    return _text_level_impl(text, target)


if __name__ == "__main__":
    model = OpenAIModel(
        model_id="deepseek-chat",
        api_base="https://api.deepseek.com/v1",
        api_key=os.getenv("DEEPSEEK_API_KEY"),
    )
    # 两个工具一起挂上去：单参数的 hsk_level + 双参数的 text_level
    agent = ToolCallingAgent(tools=[hsk_level, text_level], model=model)

    QUESTIONS = [
        "'把'字是 HSK 几级词汇？",
        "我在给 HSK4 的学生备《愚公移山》，这篇课文对他们难吗？",
    ]

    for q in QUESTIONS:
        print("Q:", q)
        print("A:", agent.run(q))
        print("-" * 40)
