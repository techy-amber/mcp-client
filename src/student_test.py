import asyncio

from mcp import Client
from servers.student_server import mcp


async def main():

    async with Client(mcp) as client:

        print("Connected to Student MCP Server")

        result = await client.call_tool(
            "get_student_marks",
            {
                "student_id": 101
            },
        )

        print("\nTool executed: get_student_marks")

        print("\nresult.structured_content:")
        print(result.structured_content)

        print("\nresult.content:")
        print(result.content)

        print("\nComplete result object:")
        print(result)


if __name__ == "__main__":
    asyncio.run(main())