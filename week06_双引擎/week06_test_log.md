# W6 边界测试记录（week06_test_log.md）

> 说明：下面每组都是必做的三条测试路径。跑完用你的真实数据填表，
> **第 2 组"关掉 Ollama"那条的切换日志原文必须抄进来**，这是最关键证据，别只写"成功了"。

## 三组必做测试

| 测试条件 | 实际走的引擎 | 耗时与答案质量点评 | 是否符合预期／怎么改的 |
|---|---|---|---|
| ① Ollama 开，prefer="local" | 本地（qwen2.5:0.5b） | 约 8.1s（首次加载模型偏慢），自拟了一道 HSK4 阅读题，切题 | 符合 |
| ② Ollama 关，prefer="local"（自动切云端） | 本地先报 ConnectionError→自动切云端（DeepSeek） | 约 8.1s，DeepSeek 规范作答 | 符合，回退生效，本地挂程序不崩 |

### ② 切换日志原文（原样复制，别改写）

```
[首选引擎失败，自动切换] HTTPConnectionPool(host='localhost', port=11434): Max retries exceeded with url: /api/chat (Caused by NewConnectionError("HTTPConnection(host='localhost', port=11434): Failed to establish a new connection: [WinError 10061] 由于目标计算机积极拒绝，无法连接。"))
```
| ③ prefer="api"（已配 DeepSeek 密钥） | 云端（DeepSeek） | 约 4.8s，答案质量明显更高：规范的五选一 HSK4 阅读题＋参考答案＋出题说明 | 符合，云端可用时 prefer="api" 走云端 |

## 补充测试（对应作业 2 的补测场景：云端不可用时 prefer="api"）

| 测试条件 | 实际走的引擎 | 耗时与答案质量点评 | 是否符合预期／怎么改的 |
|---|---|---|---|
| ④ 未配密钥，prefer="api" | 先云端（报 Missing credentials）→自动切回本地 | 约 2.3s，本地作答 | 符合，双向回退生效，没密钥也优雅降级不崩溃 |

### ④ 切换日志原文（原样复制，别改写）

```
[首选引擎失败，自动切换] Missing credentials. Please pass an `api_key`, `workload_identity`, `admin_api_key`, or set the `OPENAI_API_KEY` or `OPENAI_ADMIN_KEY` environment variable.
```

## 第 4、5 组（课后自己设计）

| 测试条件 | 实际走的引擎 | 耗时与答案质量点评 | 是否符合预期／怎么改的 |
|---|---|---|---|
| ④ | | | |
| ⑤ | | | |

## 反思（作业 2 要求，约 200 字）

> 什么任务固定走本地、什么固定走云端？写下你的判断依据。

通过这次三条路径实测，我体会到 prefer 不是随便选的。本地 qwen2.5:0.5b 模型小、不花钱、断网也能用，适合高频、格式固定、能人工校验的练习生成，比如批量出 HSK4 阅读题——这类任务答案对不对一眼就能看出来，没必要花 token。而且涉及学生作文批改时，未成年人数据不出本机是隐私红线，必须固定走本地。云端 DeepSeek 质量明显更高，像复杂教案设计、多步推理、长文改写这类对质量要求高的任务，值得花 token 走 api。总之：隐私和离线任务固定走本地，质量优先的任务固定走云端；拿不准就默认 local，反正失败会自动切云端，本地优先等于自带兜底。

## 验收自查

- [ ] llm.py 有 LocalEngine / APIEngine / LLM，两个引擎都能调
- [ ] prefer 参数可切换，回退是双向的
- [ ] 边界测试记录 ≥3 组，含回退日志原文
- [ ] 密钥 / .env 没进仓库（一票否决）
