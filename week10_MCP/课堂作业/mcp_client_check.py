# 临时验证：用 MCP 客户端连一下本地 hsk_mcp_server，确认两个工具能被「发现」
# 说明：这只是给预习做验证用，不是交付物，跑完就能删。
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
            tools = await session.list_tools()
            print("发现的工具：", [t.name for t in tools.tools])
            r = await session.call_tool("hsk_level", {"word": "把"})
            print("调用 hsk_level('把') →", r.content[0].text)
            r2 = await session.call_tool("list_by_level", {"level": "5"})
            print("调用 list_by_level('5') →", r2.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
