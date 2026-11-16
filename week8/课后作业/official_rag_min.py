# W8 课后作业 4（A 路径）：用 LangChain 官方 2-Step RAG 的最小组装
#
# 对照对象：LangChain 官方 RAG 教程的 2-Step 形态
#   Load → Split → Embed → Store → Retrieve → Prompt → Generate
#   官方用 LCEL 把这几步串成一条链，这里照着写一遍。
#
# 与我的 rag_qa.py 的差别（也是这次改造的观察点）：
#   - rag_qa.py 手写 retrieve()/build_prompt()，检索与拼词分开两次调用；
#   - 这里用 LCEL 的 | 管道一次性串起来，检索结果自动填进 {context}。
#
# 依赖：pip install langchain langchain-community langchain-chroma langchain-ollama langchain-openai
# 运行：python official_rag_min.py            （默认用语料 data/等级标准节选.txt）
#       python official_rag_min.py 愚公移山.txt （换上改造后的语料）
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))   # 仓库根目录（weekpath.py 在这）

import weekpath  # noqa: E402

weekpath.load_env()

from langchain_community.document_loaders import TextLoader            # noqa: E402
from langchain_text_splitters import RecursiveCharacterTextSplitter    # noqa: E402
from langchain_ollama import OllamaEmbeddings                          # noqa: E402
from langchain_chroma import Chroma                                    # noqa: E402
from langchain_openai import ChatOpenAI                                # noqa: E402
from langchain_core.prompts import ChatPromptTemplate                  # noqa: E402
from langchain_core.output_parsers import StrOutputParser              # noqa: E402
from langchain_core.runnables import RunnablePassthrough               # noqa: E402

# 1) Load + Split：官方示例的两步
CORPUS = sys.argv[1] if len(sys.argv) > 1 else "等级标准节选.txt"
docs = TextLoader(weekpath.data_path(CORPUS), encoding="utf-8").load()
splits = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50).split_documents(docs)

# 2) Embed + Store：本地嵌入，数据不出本机（与我的 v1.0 一致）
embeddings = OllamaEmbeddings(model="nomic-embed-text")
PERSIST = weekpath.root_path("chroma_db_official_" + CORPUS.replace(".txt", ""))
vectorstore = Chroma.from_documents(splits, embeddings, persist_directory=PERSIST)

# 3) Retrieve
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})


def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)


# 4) Prompt + Generate：DeepSeek（OpenAI 兼容），官方示例这一步换 LLM 只改这一行
llm = ChatOpenAI(
    model="deepseek-chat",
    base_url="https://api.deepseek.com/v1",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0,
)

prompt = ChatPromptTemplate.from_template(
    "根据以下资料回答问题，资料中没有的内容就如实说「资料中未提及」：\n\n{context}\n\n问题：{question}"
)

# LCEL：检索 → 拼词 → 调模型 → 取文本，一条管道
chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

QUESTIONS = [
    "HSK4 词汇量要求是多少",
    "《愚公移山》可以设计什么课堂活动",
]

if __name__ == "__main__":
    print("语料：", CORPUS)
    print("切块数：", len(splits))
    for q in QUESTIONS:
        print("Q:", q)
        try:
            print("A:", chain.invoke(q))
        except Exception as e:
            print("A: [运行失败] %s" % e)
        print("-" * 60)
