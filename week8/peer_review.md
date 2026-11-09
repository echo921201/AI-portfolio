# 第 8 周互评记录

- **评阅人**：陈彦妃（f25210206）
- **评阅对象**：聂子乔
- **对象仓库**：https://gitee.com/nie-ziqiao/ai-portfolio
- **评阅时间**：2026-11-09
- **我的环境**：Windows 11、Python 3.11.9、Ollama 0.40.15（已有 qwen2.5:0.5b 和 nomic-embed-text）

下面只记录我照着做的步骤和看到的现象，不打分、不评价人。

---

## 维度 1：能不能跑

**现象**：在 `week08_助手v1.0` 目录下执行 `python assistant_v1.py`，程序在导入阶段就退出了，三问一问都没答出来。报错原文：

```
  File "...\华文小助手_代码骨架\week08_助手v1.0\assistant_v1.py", line 12, in <module>
    from rag_qa import retrieve, build_prompt  # noqa: E402
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ImportError: cannot import name 'retrieve' from 'rag_qa' (...\华文小助手_代码骨架\week07_RAG\rag_qa.py)
```

**我看到的对应关系**：

- `week07_RAG/rag_qa.py` 第 27 行定义的函数叫 `retrieve_with_sources`，文件里没有 `retrieve`。
- `week08_助手v1.0/assistant_v1.py` 第 12 行仍在 `from rag_qa import retrieve, build_prompt`。

看起来是第 7 周把函数改名成「带出处」的版本之后，第 8 周的粘合层没有跟着改。

**可以试的两种改法**（任选一种）：

1. 在 `rag_qa.py` 里加别名，不动 assistant_v1.py：
   ```python
   retrieve = retrieve_with_sources
   ```
2. 改 `assistant_v1.py` 第 12 行：
   ```python
   from rag_qa import retrieve_with_sources as retrieve, build_prompt
   ```

---

## 维度 2：README 能复现吗

照着 `week08_助手v1.0/README.md` 的「怎么装 / 怎么用」一步步做：

| 步骤 | 结果 |
|---|---|
| `pip install -r requirements.txt` | 在**仓库根目录**能执行（根目录有 `requirements.txt`）；但 README 写的是「从 week08_助手v1.0 目录运行」，该目录下这个文件叫 `requirments.txt`（少一个 e），在该目录里照抄这条命令会提示找不到文件 |
| `ollama pull qwen2.5:0.5b` / `nomic-embed-text` | 我本机已有这两个模型，跳过 |
| `python assistant_v1.py`（从 week08_助手v1.0 目录） | **卡住**，就是维度 1 的 ImportError |

**结论**：前面的安装步骤能走通，卡在最后一步运行。把维度 1 的 import 改掉之后，应该就能跑。

---

## 维度 3：Release 发了吗

**发了。** 远端有标签 `v1.0`（指向提交 e4f999a），Release 页面标题「学科智能问答助手 v1.0」，正文包含：

- `## 功能`
- `## 怎么装`（pip 安装、ollama pull、复制 .env.example）
- `## 怎么用`（从 week08_助手v1.0 目录运行 python assistant_v1.py）

功能 / 安装 / 用法三段齐全，内容与 README 一致。Release 正文里没有写“已知问题”，不过 README 里有。

---

## 维度 4：有没有已知限制

**有。** `week08_助手v1.0/README.md` 的「已知问题」写了两条：

1. 未启动 Ollama 时本地模式会报错，可设 `prefer="api"` 走云端。
2. 本地 0.5b 小模型归纳能力弱，复杂任务可能答非所问，建议切云端。

另外还有一份 `README说明.md`，写了约 200 字解释为什么「已知问题」要诚实写。

`answer_log.md` 里三条记录都带模式、引擎、输出摘要和点评，还记了响应耗时（8.16 秒 / 4.49 秒 / 9.91 秒），三个问题都如实写了答得不好的地方。

---

## 另外注意到的几点（不属于上面四维度，仅供参考）

1. 仓库根目录的 `README.md` 还是骨架自带的课程说明，四段式的项目 README 在 `week08_助手v1.0/README.md` 里。别人点进仓库首页，第一眼看到的是骨架说明。
2. 仓库里带着「教师版参考」目录，里面有参考答案和参考代码。按课程红线（禁止整包搬运），这部分不建议放在自己的作品集仓库里。
3. `week07_RAG` 下有个文件名是 `data 等级标准节选.txt`（名字中间带空格），看起来是某次复制时路径没拆开，容易让人误以为是一个 data 目录。

---

## 附：我照着做的完整命令

```bash
git clone https://gitee.com/nie-ziqiao/ai-portfolio.git
cd ai-portfolio/华文小助手_代码骨架/week08_助手v1.0
python assistant_v1.py
```
