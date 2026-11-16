# 第 8 周互评记录

- **评阅人**：陈彦妃（f25210206）
- **评阅对象**：王一嘉
- **对象仓库**：https://github.com/wangyijia2007/ai-portfolio
- **评阅时间**：2026-11-16
- **我的环境**：Windows 11、Python 3.11.9、Ollama 0.40.15（qwen2.5:0.5b + nomic-embed-text 已 pull）

下面只记录我照着做的步骤和看到的现象，不打分、不评价人。

---

## 维度 1：能不能跑

**第一次运行**（`week08_助手v1.0` 目录下 `python assistant_v1.py`），第一问就失败了：

```
Q: 把字句的教学难点有哪些
[本地失败，自动切换云端] HTTPConnectionPool(host='localhost', port=11434): Read timed out. (read timeout=60)
[回退引擎也失败] 未配置 DEEPSEEK_API_KEY：请复制 .env.example 为 .env 并填入密钥…纯本地模式请调用 ask(..., prefer='local')。
A: [运行失败] 未配置 DEEPSEEK_API_KEY：…
```

**第二次运行**（模型已经加载过），三问都有回答：

```
Q: HSK4 词汇量要求是多少
[耗时] local/qwen2.5:0.5b 10.86s | 费用 ¥0（本地不计费）
A: HSK4 的词汇量要求是 500 个左右，具体取决于考试的题型和难度。
```

**看到的现象**：

1. 冷启动时模型首次加载超过 `llm.py` 里 60 秒的读超时，第一问会走「本地失败→云端」，而没配 `DEEPSEEK_API_KEY` 时云端也失败，于是三问里第一问是失败收场。热启动后就正常。
2. 三问的回答内容**和仓库里的 `answer_log.md` 记录不一致**：日志里 HSK4 记的是「约 1200 个词语」，我这边跑出来是「500 个左右」；日志里第三问没有明显错误，我这边跑出来说《愚公移山》是「毛泽东的长篇散文」。同一份代码、同一份语料，两次输出差异很大。

**同学 README 的「已知问题」里没写「冷启动第一问会超时」这一条**，建议补一句：「首次运行前先单独跑一次 `ollama run qwen2.5:0.5b` 预热，或把 `llm.py` 的超时调大」。

---

## 维度 2：README 能复现吗

照 `week08_助手v1.0/README.md` 的「怎么装 / 怎么用」一步步做：

| 步骤 | 结果 |
|---|---|
| `pip install -r week08_助手v1.0/requirements.txt` | ✅ 文件在（9 个依赖，W6/W7 的都在里面） |
| `ollama pull qwen2.5:0.5b` / `nomic-embed-text` | ✅ 两条命令正确 |
| `cd D:\workspace\ai-portfolio\week08_助手v1.0` | ⚠️ **路径写成了同学自己电脑上的绝对路径**，别人照抄一定失败，得改成「从仓库根目录 cd 进来」 |
| `python assistant_v1.py` | ✅ 能跑（见维度 1，冷启动首问会超时） |

**建议**：把 README 里的 `cd D:\workspace\...` 换成相对路径写法，比如：

```powershell
cd week08_助手v1.0        # 从仓库根目录进入
python assistant_v1.py
```

---

## 维度 3：Release 发了吗

**发了。**

- 远端标签 `v1.0` 存在（指向 `e3270f0`）
- Release 页面标题「学科智能问答助手 v1.0」，发布时间 2026-11-09 13:25
- 正文四段齐全：`## 功能`、`## 怎么装`、`## 怎么用`、`## 已知问题`

**一个小瑕疵**：Release 正文里有多余的反斜杠转义，比如：

```
\nswer(question, use_rag=True, prefer="local")\ 支持纯对话 / 基于资料
\pip install -r week08_助手v1.0/requirements.txt
```

代码块前后的 ``` 和函数名前的 `\` 没写对，页面上会显示成一串反斜杠。不影响内容理解，重新编辑一下正文即可。

---

## 维度 4：有没有已知限制

**有，而且写得比要求的更细。** `week08_助手v1.0/README.md` 的「已知问题」三条：

1. 未启动 Ollama / 未 pull `nomic-embed-text` 时本地 RAG 会失败，可设 `prefer="api"` 或先启动 Ollama。
2. 机房代理可能劫持 localhost，脚本依赖 `rag_qa.py` 里已处理的 `NO_PROXY`。
3. `qwen2.5:0.5b` 生成质量有限，数字类问题务必开 `use_rag=True`。

另外还单独写了 `known_issues_why.md`（约 200 字，解释为什么要把已知问题写清楚）。

`answer_log.md` 三条记录都带点评，还额外做了「同一问题 `use_rag` 开/关对比」：裸答答成 6500，开 RAG 回到 1200——这个对比很有说服力。

---

## 补充观察（不属于四维度，供参考）

- 语料是自建版本：`data/等级标准节选.txt` 共 40 行，同时写了「旧版 HSK4 约 1200」和「新标准四级累计约 3245」两套数字，并有一行「课堂提示：问『HSK4 需要掌握多少词汇』时，本资料中的标准答案是 1200」。所以 `answer_log` 里 HSK4 答 1200 是这份语料决定的；换回课程骨架的原始语料，答案会变。
- `week08_助手v1.0/` 里还放了 `rag_pipeline_map.md`、`reflect_rag_c.md`、`w9_tools_preview.md`、`peer_review.md`，课后作业也一起交了。

---

## 附：我照着做的完整命令

```bash
git clone https://github.com/wangyijia2007/ai-portfolio.git
cd ai-portfolio/week08_助手v1.0
pip install -r requirements.txt
python assistant_v1.py
```
