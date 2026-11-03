# W6 边界测试记录

## 三组必做测试

| 测试条件 | 实际走的引擎 | 耗时与答案质量点评 | 是否符合预期 |
|---|---|---|---|
| ① Ollama 开，prefer="local" | 本地（qwen2.5:0.5b） | 约 8.1s（首次加载模型偏慢），自拟了一道 HSK4 阅读题，切题 | 符合 |
| ② Ollama 关，prefer="local"（自动切云端） | 本地先报 ConnectionError→自动切云端（DeepSeek） | 约 8.1s，DeepSeek 规范作答 | 符合，回退生效，本地挂程序不崩 |
| ③ prefer="api"（已配 DeepSeek 密钥） | 云端（DeepSeek） | 约 4.8s，答案质量明显更高：规范的五选一 HSK4 阅读题＋参考答案＋出题说明 | 符合，云端可用时 prefer="api" 走云端 |

### ② 切换日志原文

```
[首选引擎失败，自动切换] HTTPConnectionPool(host='localhost', port=11434): Max retries exceeded with url: /api/chat (Caused by NewConnectionError("HTTPConnection(host='localhost', port=11434): Failed to establish a new connection: [WinError 10061] 由于目标计算机积极拒绝，无法连接。"))
```

## 补充测试

| 测试条件 | 实际走的引擎 | 耗时与答案质量点评 | 是否符合预期 |
|---|---|---|---|
| ④ 未配密钥，prefer="api" | 先云端（报 Missing credentials）→自动切回本地 | 约 2.3s，本地作答 | 符合，双向回退生效，没密钥也优雅降级不崩溃 |
| ⑤ 云端不可用（无效密钥），prefer="api" | 先云端（报 401 认证失败）→自动切回本地 | 约 4.0s，本地作答 | 符合，对称回退生效，云端挂了程序不崩 |
| ⑥ max_tokens=20，prefer="local" | 本地（qwen2.5:0.5b） | 约 2.4s，输出被 max_tokens 限制成很短一句 | 符合，max_tokens 能限制输出长度 |

### ④ 切换日志原文

```
[首选引擎失败，自动切换] Missing credentials. Please pass an `api_key`, `workload_identity`, `admin_api_key`, or set the `OPENAI_API_KEY` or `OPENAI_ADMIN_KEY` environment variable.
```

### ⑤ 切换日志原文

```
[首选引擎失败，自动切换] Error code: 401 - Authentication Fails, Your api key: ****test is invalid (request_id: 7cb73288-1e4e-4f59-bce0-e7f530e6f8ae)
```

## 反思

这次三条路径跑下来，我觉得 prefer 不是随便填的。本地千问这个模型小、免费、断网也能用，出 HSK4 阅读题这种格式固定、答案对不对能自己看出来的练习，用本地就够了，不用浪费 token。还有批改学生作文这种涉及未成年人信息的，数据留在本机更安全，肯定固定走本地。云端 DeepSeek 质量确实高，像复杂教案、多步推理、改长文这种对质量要求高的，才值得用 api。反正拿不准就默认 local，本地挂了它会自动切云端，等于自带保险。

补测⑤⑥后我更确定：⑤ 把云端密钥改成无效的，prefer="api" 时它先报 401，然后自动切回本地继续出答案，没崩——说明回退是"双向"的，不只本地挂会切云端，云端挂也会切回本地，跟讲义承诺的"断网也能用"一致。⑥ 把 max_tokens 调成 20，本地输出明显被截断成很短一句，证明这个参数确实控制输出长度。所以固定走本地的就是：格式固定、能自己校验、涉及隐私的批量活；固定走云端的就是：复杂、多步、对质量要求高的任务。
