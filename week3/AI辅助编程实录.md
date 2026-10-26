# AI 辅助编程实录（第 3 周）

> 本实录记录本周「生词表 CSV → 自动生成练习题」任务的完整过程：提示词 → AI 初版 → 我的修改 → 最终版差异。
> 用途：证明这份脚本是我「读懂后改过」的，不是直接抄的；也是 W16 结课报告中 AI 使用披露的第一手素材。

---

## 1. 任务与提示词

**要做什么**：读一份生词表（data/生词表.csv），只挑出 HSK4 的词汇，统计词性分布，再自动生成一个练习.txt（每行一道造句题），全程只用 Python 标准库，不装任何新包。

**我写的提示词（四件套）**：

```
角色：你是 Python 教学助手
任务：写一个脚本，读取生词表 CSV 并自动生成练习题
要求：
  - 输入：data/生词表.csv（表头：词汇,HSK等级,词性,释义,备注）
  - 处理：按 HSK 等级筛选出 4 级词汇 → 统计词性分布 → 生成练习.txt
  - 输出：练习.txt，每行格式——用“坚持”造一个句子。（动词）
  - 只用 Python 标准库（csv / 文件读写），不要装新包
  - 每一行都加中文注释
  - 示例输出：用“坚持”造一个句子。（动词）
边界：脚本要从任意目录运行都能找到 data/ 和练习.txt
```

（提示词可以按你真实发给 AI 的版本微调，结构保持一致即可。）

---

## 2. AI 初版代码

（下面是我让 AI 第一次给出的版本，功能能跑，但路径写死、没有统一入口，注释也少。）

```python
import csv

# 读生词表
with open("data/生词表.csv", encoding="utf-8") as f:
    words = list(csv.DictReader(f))

# 只留 HSK4
lv4 = [w for w in words if w["HSK等级"] == "4"]

# 统计词性
d = {}
for w in lv4:
    d[w["词性"]] = d.get(w["词性"], 0) + 1
print("HSK4 共", len(lv4), "个，词性分布：", d)

# 生成练习
with open("练习.txt", "w", encoding="utf-8") as f:
    for w in lv4:
        f.write('用"%s"造一个句子。（%s）\n' % (w["词汇"], w["词性"]))
print("已生成 练习.txt")
```

---

## 3. 我的修改点（≥3 条）

| # | 我改了什么 | 为什么这么改 |
|---|---|---|
| ① | 把写死的相对路径 `"data/生词表.csv"` 改成 `weekpath.data_path("生词表.csv")` | 直接写相对路径，换一个目录运行就报 FileNotFoundError（找不到文件）；weekpath 统一从代码包根目录定位 data/，保证从任何目录运行都找得到。 |
| ② | 给每个函数加中文注释，说明它做什么 | AI 初版几乎没有注释，过两天自己就看不懂了；注释帮我逐行讲清楚每个动作，结课被问到“这行为什么这么写”才答得上来。 |
| ③ | 筛选等级改成 `str(w["HSK等级"]) == str(level)` | CSV 里等级可能是字符串也可能是数字（"4" vs 4），不统一类型可能漏选；用 str() 包一层，两边都转成字符串再比，更稳。 |
| ④ | 练习.txt 的产物路径统一到 `weekpath.root_path("练习.txt")` | AI 初版把文件生成在“当前工作目录”，从哪个目录运行就落在哪，散落到处不好收拾；统一放到代码包根目录，一次跑、一个固定位置。 |

---

## 4. 最终版 vs 初版差异说明

- **AI 想多了的地方**：AI 初版没写注释、路径写死——功能对，但经不起“换目录运行”和“被老师提问”。我补上统一路径和逐行注释。
- **AI 漏了的地方**：初版没有处理“从任意目录运行”和“HSK 等级字段类型可能不一致”这两个真实问题；最终版用 `weekpath` 和 `str()` 补上。
- **我为什么这么改**：这门课要求脚本是“自动化资产”，写一次以后每周都能复用；复用的大前提就是路径不依赖当前目录、代码能看懂。所以路径统一 + 注释，比“能跑”更重要。

### 最终版完整代码（vocab_tool.py）

```python
# W3 生词表 CSV -> 自动生成练习题
# 运行：python vocab_tool.py
import os
import csv
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import weekpath  # noqa: E402  统一解析 data/ 路径，换目录也不会找不到文件

DATA = weekpath.data_path("生词表.csv")


def load_words(path=DATA):
    # ① 读：用 with 打开，用完自动关文件；encoding="utf-8" 必须写，否则 Windows 中文乱码
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))  # 每行读成一个字典，表头就是键名


def filter_by_level(words, level="4"):
    # ② 筛：列表推导式，[结果 for 变量 in 列表 if 条件]
    return [w for w in words if str(w["HSK等级"]) == str(level)]


def count_by_pos(words):
    # ③ 统：dict.get(k, 0) + 1，取不到就当 0，读到就 +1
    d = {}
    for w in words:
        d[w["词性"]] = d.get(w["词性"], 0) + 1
    return d


def gen_exercises(words, out=None):
    # ④ 写：产物统一落到代码包根目录，不依赖“从哪个目录运行”
    out = out or weekpath.root_path("练习.txt")
    with open(out, "w", encoding="utf-8") as f:
        for w in words:
            f.write("用“%s”造一个句子。（%s）\n" % (w["词汇"], w["词性"]))


if __name__ == "__main__":
    words = load_words()
    lv4 = filter_by_level(words, "4")
    print("总词汇 %d 个，其中 HSK4 词汇 %d 个，词性分布：%s"
          % (len(words), len(lv4), count_by_pos(lv4)))
    out = weekpath.root_path("练习.txt")
    gen_exercises(lv4, out)
    print("已生成：%s" % out)
```

### 运行结果（实测）

```
总词汇 13 个，其中 HSK4 词汇 4 个，词性分布：{'名词': 1, '动词': 3}
已生成：C:\Users\CHEN\Desktop\华文小助手_代码骨架\练习.txt
```

练习.txt 内容：

```
用“把字句”造一个句子。（名词）
用“商量”造一个句子。（动词）
用“感动”造一个句子。（动词）
用“坚持”造一个句子。（动词）
```

---

## 课后待办（下周四前）

- [ ] 作业1：精读 Python 官方教程「列表、字典、文件读写」三节，把学到的 1 个写法用进脚本，在本实录补记第 4 条修改点。
- [ ] 作业2：给脚本扩展 1 个功能（① 按词性分组输出；② 生成填空题把目标词挖空成 ____）。先让 AI 写，再自己读懂并改。
- [ ] 作业3：做语法卡片（列表推导式等 4 个语法点），下课前抽考。
