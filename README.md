# 学科智能问答助手 v1.0

把 week06 的双引擎 llm.py 和 week07 的知识库 rag_qa.py 接起来，做成一个能问答的助手。

## 功能

- 能问学科问题，分两种模式：查资料再答（use_rag=True）和纯聊天（use_rag=False）。
- 本地优先：默认走本机 Ollama；本地出错自动换云端 DeepSeek。
- 知识库用的是《国际中文教育中文水平等级标准》节选，答案会带资料依据。

## 怎么装

- 装依赖：pip install -r requirements.txt（Python 3.11）
- 拉模型：ollama pull qwen2.5:0.5b 和 ollama pull nomic-embed-text
- 用云端才需要：把 .env.example 复制成 .env，填 DEEPSEEK_API_KEY

## 怎么用

- 进 week8/课堂作业 目录跑：python assistant_v1.py，会依次回答三个问题。
- 想看开关效果：python compare_rag.py，同一个问题开/关 RAG 各答一次。
- 每次的问答结果记在 week8/课后作业/answer_log.md 里。

## 已知问题

- 知识库只放了一个文件（等级标准节选）。问把字句、愚公移山这种库外的东西，要么回答“资料中未提及”，要么自己编——实测把《愚公移山》说成过“孔子的名篇”，其实是《列子》里的。
- 0.5b 模型太小，对资料利用不稳定。HSK4 词汇量标准是新增 1000、累计 3245，它先后答成过“3000 个左右”和“1000 个左右”，都不看原文。
- 第一次跑要加载模型，可能超过 60 秒超时报错，重跑一遍就行。Ollama 没启动时本地模式会失败。
