# MCP 客户端自检：连上本地 hsk_mcp_server，列出工具并逐个调用一次
#
# 运行：python mcp_client_check.py（在 week10_MCP/课堂作业 目录下）
# 它在同一目录里把 hsk_mcp_server.py 当子进程拉起，走 stdio 握手——
# 与讲义第五节 demo_client.py 的做法一致，只是把「发现 → 调用」两步摊开打印。
import asyncio
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

HERE = os.path.dirname(os.path.abspath(__file__))
SERVER = os.path.join(HERE, "hsk_mcp_server.py")


async def main():
    params = StdioServerParameters(command=sys.executable, args=[SERVER])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 第一步：发现——客户端问服务端「你有哪些工具」
            tools = await session.list_tools()
            print("发现的工具：", [t.name for t in tools.tools])

            # 第二步：调用——按名字和参数请服务端执行
            r1 = await session.call_tool("hsk_level", {"word": "把"})
            print("调用 hsk_level('把') →", r1.content[0].text)

            r2 = await session.call_tool("list_by_level", {"level": "5"})
            print("调用 list_by_level('5') →", r2.content[0].text)

            r3 = await session.call_tool("count_by_level", {"level": "3"})
            print("调用 count_by_level('3') →", r3.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
