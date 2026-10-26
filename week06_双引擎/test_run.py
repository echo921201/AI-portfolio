# -*- coding: utf-8 -*-
# W6 测试脚本：一键跑一条测试路径
# 用法：
#   python test_run.py local     # ① 正常本地（Ollama 开着）
#   python test_run.py local     # ② 先关掉 Ollama 再跑，看自动切云端
#   python test_run.py api       # ③ prefer="api"（云端不可用/没密钥时看回退本地）
import sys
import time
import traceback

from llm import LLM


def run(prefer):
    q = "给《愚公移山》出一道 HSK4 阅读题"
    t0 = time.time()
    print(f"[测试开始] prefer={prefer}")
    print(f"[提问] {q}")
    try:
        ans = LLM().ask(q, prefer=prefer)
        dt = time.time() - t0
        print(f"[结果] 耗时 {dt:.1f}s")
        print("----- 答案 -----")
        print(ans)
    except Exception:
        print("[失败] 以下是报错原文：")
        traceback.print_exc()


if __name__ == "__main__":
    prefer = sys.argv[1] if len(sys.argv) > 1 else "local"
    run(prefer)
