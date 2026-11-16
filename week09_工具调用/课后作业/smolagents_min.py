# W9 课后作业 4（A 路径）：smolagents 最小示例 —— 用框架重写同一个 hsk_level 工具
# 依赖：pip install smolagents（Python >= 3.10）
# 运行：python smolagents_min.py（在 week09_工具调用/课后作业 目录下）
import os
import csv
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))   # 仓库根目录（weekpath.py 在这）

import weekpath  # noqa: E402

weekpath.load_env()

from smolagents import tool, ToolCallingAgent, OpenAIModel  # noqa: E402

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


if __name__ == "__main__":
    model = OpenAIModel(
        model_id="deepseek-chat",
        api_base="https://api.deepseek.com/v1",
        api_key=os.getenv("DEEPSEEK_API_KEY"),
    )
    agent = ToolCallingAgent(tools=[hsk_level], model=model)

    for q in ["'把'字是 HSK 几级词汇？", "'无穷无尽'这个词 HSK 几级？"]:
        print("Q:", q)
        print("A:", agent.run(q))
        print("-" * 40)
