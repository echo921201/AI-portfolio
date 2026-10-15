# W4 作业2：多轮对话版问答机器人
# 运行：python week4_multiturn.py
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import weekpath  # noqa: E402

weekpath.load_env()

import openai  # noqa: E402

BASE_URL = "https://api.deepseek.com/v1"
MODEL = "deepseek-chat"

_client = None


def get_client():
    global _client
    if _client is None:
        key = os.getenv("DEEPSEEK_API_KEY")
        if not key:
            raise RuntimeError("未配置 DEEPSEEK_API_KEY")
        _client = openai.OpenAI(base_url=BASE_URL, api_key=key)
    return _client


if __name__ == "__main__":
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("错误：未设置 DEEPSEEK_API_KEY。")
        print("  处理：复制 .env.example 为 .env 并填入密钥，重启终端后重试。")
        sys.exit(1)

    messages = []  # 对话历史：所有轮次的问答都存在这里

    print("=" * 50)
    print("多轮对话机器人（输入 exit 或 退出 结束）")
    print("=" * 50)

    while True:
        user_input = input("\n你: ").strip()
        if user_input.lower() in ["exit", "quit", "退出"]:
            print("对话结束。")
            break
        if not user_input:
            continue

        # 把用户这一轮的问题加进历史
        messages.append({"role": "user", "content": user_input})

        try:
            r = get_client().chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=800,
            )
        except openai.APITimeoutError:
            print("请求超时了，检查一下网络再试。")
            continue

        answer = r.choices[0].message.content
        print("AI:", answer)

        # 把AI这一轮的回答也加进历史，下一轮它才能记得
        messages.append({"role": "assistant", "content": answer})

    # 把整段对话写进日志
    with open(weekpath.root_path("chat_log.txt"), "a", encoding="utf-8") as f:
        f.write("=== 多轮对话 ===\n")
        for m in messages:
            role = "Q" if m["role"] == "user" else "A"
            f.write("%s: %s\n" % (role, m["content"]))
        f.write("\n")
