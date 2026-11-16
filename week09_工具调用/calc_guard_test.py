# W9 安全边界自测：验证 calc() 的白名单 AST 会拒绝越权表达式
# 运行：python calc_guard_test.py（在 week09_工具调用 目录下）
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import weekpath  # noqa: E402

weekpath.load_env()

from tool_agent import calc  # noqa: E402

CASES = [
    "35*24",                              # 正常四则运算
    "2**10 + 3",                          # 乘方与加法
    "100/0",                              # 除零，应返回错误提示
    "__import__('os').system('whoami')",  # 越权：执行系统命令
    "open('.env').read()",                # 越权：读文件
]

if __name__ == "__main__":
    for expr in CASES:
        print("calc(%r) → %s" % (expr, calc(expr)))
