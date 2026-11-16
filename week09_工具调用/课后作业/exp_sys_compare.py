# W9 课后作业 1 的对比实验：只改 SYS 一句话，复合问句的「答一半」会不会变少？
# 运行：python exp_sys_compare.py（在 week09_工具调用/课后作业 目录下）
#
# 做法：不改 tool_agent.py 的任何逻辑，只在运行前把它的 SYS 换掉，
# 再用同一个复合问句各跑 5 次，统计「两个工具都被调用」的次数。
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))                 # 仓库根目录
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "课堂作业"))         # tool_agent.py 在这

import weekpath  # noqa: E402

weekpath.load_env()

import tool_agent as ta  # noqa: E402

QUESTION = "请依次查询两件事：1. '把'字的 HSK 等级是多少？2. 现在的时间是多少？"
EXTRA = "注意：问句里有几个子问题，就依次调用几次工具，全部查完再给出答案。"
N = 5

_called = []

# 包一层 TOOLS，记下这一轮到底执行了哪些工具
for _name, _fn in list(ta.TOOLS.items()):
    def _make(name=_name, fn=_fn):
        def wrapper(*args, **kwargs):
            _called.append(name)
            return fn(*args, **kwargs)
        return wrapper
    ta.TOOLS[_name] = _make()


def trial(sys_prompt, n=N):
    """跑 n 次，返回（两个工具都调了的次数, 明细）"""
    ta.SYS = sys_prompt
    both = 0
    detail = []
    for _ in range(n):
        _called.clear()
        try:
            ta.run(QUESTION)
        except Exception as e:
            detail.append("异常:%s" % e)
            continue
        used = sorted(set(_called))
        detail.append("+".join(used) or "（没调工具）")
        if "hsk_level" in used and "get_time" in used:
            both += 1
    return both, detail


if __name__ == "__main__":
    base_sys = ta.SYS
    b1, d1 = trial(base_sys)
    b2, d2 = trial(base_sys + EXTRA)

    print("问句：", QUESTION)
    print()
    print("[A] 原版 SYS（一次只调用一个工具）")
    print("    两个工具都调：%d/%d" % (b1, N))
    for x in d1:
        print("      -", x)
    print()
    print("[B] SYS 末尾加一句「有几个子问题就调用几次工具」")
    print("    两个工具都调：%d/%d" % (b2, N))
    for x in d2:
        print("      -", x)
