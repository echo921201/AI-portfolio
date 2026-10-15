# W4 作业3：连续跑10次学科问题，记录token和费用
# 运行：python week4_cost_log.py
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import weekpath  # noqa: E402

weekpath.load_env()

import openai  # noqa: E402

BASE_URL = "https://api.deepseek.com/v1"
MODEL = "deepseek-chat"

# DeepSeek 定价（2026年10月参考，单位：元/百万token）
# 请去官网 https://api-docs.deepseek.com/zh-cn/quick_start/pricing 核对最新价格再改这里
INPUT_PRICE_PER_M = 1.0   # 输入：每百万token多少钱
OUTPUT_PRICE_PER_M = 2.0  # 输出：每百万token多少钱

# 10个对外汉语教学问题
QUESTIONS = [
    "把字句的教学难点有哪些？怎么突破？",
    "离合词为什么难教？有什么好的练习方法？",
    "趋向补语和结果补语怎么区分？学生容易混在哪？",
    "外国学生学声调常见的偏误有哪些？怎么纠正？",
    "动态助词'了'的用法怎么讲学生才听得懂？",
    "汉语量词为什么难？怎么设计练习让学生记牢？",
    "反问句的语用功能有哪些？适合什么阶段教？",
    "怎么设计一堂初级口语课的导入环节？给个具体例子。",
    "HSK4级对词汇和语法的具体要求是什么？",
    "给一篇中级汉语作文写三段式评语（优点/问题/建议）。",
]


def main():
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("错误：未设置 DEEPSEEK_API_KEY。")
        sys.exit(1)

    client = openai.OpenAI(
        base_url=BASE_URL,
        api_key=os.getenv("DEEPSEEK_API_KEY"),
    )

    total_input = 0
    total_output = 0
    total_cost = 0.0

    print("序号 | 输入token | 输出token | 本次费用(元)")
    print("-" * 45)

    for i, q in enumerate(QUESTIONS, 1):
        try:
            r = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": q}],
                temperature=0.7,
                max_tokens=800,
            )
        except Exception as e:
            print("%d | 请求失败: %s" % (i, e))
            continue

        p = r.usage.prompt_tokens
        c = r.usage.completion_tokens
        cost = p / 1_000_000 * INPUT_PRICE_PER_M + c / 1_000_000 * OUTPUT_PRICE_PER_M

        total_input += p
        total_output += c
        total_cost += cost

        print("%2d  |  %5d    |  %5d    |  %.6f" % (i, p, c, cost))

    print("-" * 45)
    print("合计 |  %5d    |  %5d    |  %.6f" % (total_input, total_output, total_cost))
    print()
    print("一次备课问答平均成本：%.6f 元" % (total_cost / len(QUESTIONS)))

    # 写进笔记文件
    notes_path = os.path.join(weekpath.root_path("week4_notes.md"))
    with open(notes_path, "a", encoding="utf-8") as f:
        f.write("\n## 10次调用费用记录\n\n")
        f.write("- 输入token合计：%d\n" % total_input)
        f.write("- 输出token合计：%d\n" % total_output)
        f.write("- 总花费：%.6f 元\n" % total_cost)
        f.write("- 一次备课问答平均成本：%.6f 元\n" % (total_cost / len(QUESTIONS)))


if __name__ == "__main__":
    main()
