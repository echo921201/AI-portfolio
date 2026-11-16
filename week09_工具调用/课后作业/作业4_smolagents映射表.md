# 作业 4（A 路径）：smolagents 与我的手写循环 —— 5 行映射表

## 一、环境与结论

- 安装：`pip install smolagents`，实际装到 **1.26.0**（Python 3.11）
- 许可证：Apache-2.0（包内 LICENSE 已核对）
- 最小示例：`week09_工具调用/课后作业/smolagents_min.py`，**已跑通**，挂的是**两个工具**——单参数的 `hsk_level(word)` 和双参数的 `text_level(text, target)`，正好验证「框架怎么处理多参数工具」
- 运行日志（等价于运行截图）：`week09_工具调用/课后作业/smolagents_run.log`
- 路径选择：**A 路径**（本机 31 GB 内存 + RTX 5070，云端 DeepSeek 可用）

## 二、5 行映射表

| 我写的 `tool_agent.py` | smolagents 里对应什么 | 我读到的依据 |
|---|---|---|
| `TOOLS` 字典：名字 → 函数 | `@tool` 装饰器把带类型注解、`Args:` 文档的函数变成 `Tool`（`tools.py:1061` 的 `tool()`、`tools.py:106` 的 `Tool`），再交给 `ToolCallingAgent(tools=[...])` | `@tool` 要求函数有类型注解和 docstring 里的 `Args:`，否则构造时就报错 |
| `SYS` 提示词里要求「只输出一行 JSON」 | `ToolCallingAgent` 用模型原生的 tool calling（JSON-like），提示模板在 `prompts/toolcalling_agent.yaml` | 不再靠自然语言约束模型，靠 API 的 `tools` 参数 |
| `parse_calls()` 剥围栏、`re.S` 兜底抓 JSON | 框架内部解析 `ChatMessageToolCall`，不用自己写正则 | 我的 4 道解析防线在框架里变成「API 返回结构化字段」 |
| `TOOLS[name](*args)` 执行 + `try/except` 兜底 | 框架按 `Tool.inputs` 校验参数后调用，执行结果进入多步消息 | 实测框架调用时参数是**具名**的：`{'word': '无穷无尽'}`，我的是位置参数 `['无穷无尽']` |
| `run()` 手动回喂 + `max_calls` 收口 | `MultiStepAgent`（`agents.py:268`）管多步循环、步数与停止条件；`ToolCallingAgent`（`agents.py:1215`）负责每步决策 | 我的 `max_calls=2` 对应框架的 `max_steps` 默认值 |

## 三、最小示例的真实运行输出

```text
Q: '把'字是 HSK 几级词汇？
┌───────────────────────────── Step 1 ─────────────────────────────┐
│ Calling tool: 'hsk_level' with arguments: {'word': '把'}          │
└───────────────────────────────────────────────────────────────────┘
Observations: 把 是 3 级
[Step 1: Duration 0.53 seconds| Input tokens: 2,473 | Output tokens: 75]
A: “把”是 HSK 3 级词汇。

Q: '无穷无尽'这个词 HSK 几级？
│ Calling tool: 'hsk_level' with arguments: {'word': '无穷无尽'}
Observations: 无穷无尽 是 5 级
│ Calling tool: 'final_answer' with arguments: {'answer': "'无穷无尽' 是 HSK 5 级。"}
A: '无穷无尽' 是 HSK 5 级。
```

## 四、300 字反思：框架省了什么、拿走了什么

手写完那 60 行再来看框架，最直观的差别不在「能不能调用」，而在**调用是怎么被约束的**。

框架帮我省了三件事。第一是**解析**：我的 `parse_calls()` 要剥 ```json 围栏、要 `re.S` 跨行抓块、要兜住模型一口气并列输出多个 JSON 的情况——这些都是模型不老实逼出来的土办法；框架直接用 API 的 `tools` 参数，返回的是结构化字段，正则整段消失了。第二是**校验**：`@tool` 要求写类型注解和 `Args:`，写不全直接构造失败，等于把「参数该长什么样」变成了编译期错误；我是靠 `isinstance(args, list)` 在运行时挡。第三是**循环**：`MultiStepAgent` 管步数、停止条件、消息历史，我则是手写 `for _ in range(max_calls)` 加一个到顶强制收口。

框架也拿走了一些东西。最明显的是**控制权**：我的循环里，模型输出什么、怎么解析、失败怎么兜底，每一步都看得见；框架里这些藏在 `ChatMessageToolCall` 和模板后面，模型到底「看到」了什么提示词、为什么选了某个工具，我得去翻 `prompts/toolcalling_agent.yaml` 才知道。还有一个细节——框架给模型多塞了一个 `final_answer` 工具，模型用它来收口；我的循环没有这个概念，靠「没调工具就直接回答」。这多出来的一步，是控制权转移的具体形状。

所以顺序不能反：**先手写，才知道框架替你省了什么、又拿走了什么**。直接上框架，调不通时只能猜。
