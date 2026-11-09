# W8 开关对照：同一个问题，use_rag 开 / 关各答一次
# 用途：验证 answer() 的 use_rag 开关真的起作用，并把差异写进 answer_log.md
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(_HERE)))          # 仓库根目录（weekpath.py 在这）
sys.path.insert(0, os.path.join(os.path.dirname(_HERE), "课堂作业"))  # assistant_v1.py 在这
import weekpath  # noqa: E402

weekpath.load_env()

from assistant_v1 import answer  # noqa: E402

QUESTION = "把字句的教学难点有哪些"

if __name__ == "__main__":
    for use_rag in (True, False):
        tag = "use_rag=True（先查资料再答）" if use_rag else "use_rag=False（纯对话）"
        print("=" * 20, tag)
        print("Q:", QUESTION)
        try:
            print("A:", answer(QUESTION, use_rag=use_rag, prefer="local"))
        except Exception as e:
            print("A: [运行失败] %s" % e)
        print()
