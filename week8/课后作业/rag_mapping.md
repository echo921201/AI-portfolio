# 官方 RAG 流水线 ↔ 我的 rag_qa.py 对照表

| 官方流水线 | llm-universe 对应章节 | 我的代码 |
|---|---|---|
| Load + Split 加载与分块 | C3 数据处理：读取、清洗与切片 | TextLoader 读 data/等级标准节选.txt，RecursiveCharacterTextSplitter 切 500 / 重叠 50 |
| Embed + Store 向量化入库 | C3 词向量及向量知识库 | OllamaEmbeddings 用 nomic-embed-text，Chroma 存到本地 chroma_db/ |
| Retrieve 检索 | C4 基于 LangChain 搭建检索问答链 | retrieve() 取前 3 段，use_rag=True 时先查再答 |
| Prompt + Generate 拼词与生成 | C4 将 LLM 接入 LangChain | build_prompt() 把系统提示、资料、问题拼一起，交给 LLM().ask() |
| Deploy + Evaluate 部署与评估 | C4 Streamlit 部署；C5 系统评估与优化 | 现在用 answer_log.md 人工对比，部署留到 W15 |

几句读数：

- 官方说 loaders、splitters、embeddings、vector stores 都能单独换。我把嵌入换成本地 nomic-embed-text，语料换成等级标准节选，就是我的 v1.0。
- llm-universe 把几家大模型 API 包成一个接口。我 week06 的 LLM().ask(prefer="local"/"api") 是一个思路。
- llm-universe C5 分别评生成和检索。我的 answer_log 就是最土的办法：同样的问题，看它答得对不对。

我按配置算 A 路径（31G 内存 + RTX 5070，本地模型和嵌入都跑得动）。这张表只是读数，没改 v1.0 的代码，改造和反思放课后。
