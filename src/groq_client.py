import asyncio
import json
import os

from dotenv import load_dotenv
from groq import Groq
from mcp import Client

from servers.calculator_server import mcp as calculator_mcp
from servers.student_server import mcp as student_mcp


# ============================================================
# 1. Load Groq API key
# ============================================================

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY was not found in .env")

groq_client = Groq(api_key=api_key)


# ============================================================
# 2. Extract MCP tool result
# ============================================================

def extract_tool_result(result):

    # Calculator tools may return structured content
    if result.structured_content:

        if "result" in result.structured_content:
            return result.structured_content["result"]

        return result.structured_content

    # Student tools currently return JSON as text
    if result.content:

        text = result.content[0].text

        try:
            return json.loads(text)

        except json.JSONDecodeError:
            return text

    return None


# ============================================================
# 3. Convert MCP tool into Groq/OpenAI tool format
# ============================================================

def convert_mcp_tool(tool):

    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": tool.input_schema,
        },
    }


# ============================================================
# 4. Main application
# ============================================================

async def main():

    # Connect to both MCP servers
    async with Client(calculator_mcp) as calculator_client:

        async with Client(student_mcp) as student_client:

            print("Connected to Calculator MCP Server")
            print("Connected to Student MCP Server")

            # =================================================
            # 5. Discover MCP tools
            # =================================================

            calculator_tools = await calculator_client.list_tools()
            student_tools = await student_client.list_tools()

            print("\nCalculator tools:")

            for tool in calculator_tools.tools:
                print(f"- {tool.name}: {tool.description}")

            print("\nStudent tools:")

            for tool in student_tools.tools:
                print(f"- {tool.name}: {tool.description}")

            # =================================================
            # 6. Build Groq tool list + routing table
            # =================================================

            groq_tools = []

            tool_to_client = {}

            # Calculator tools
            for tool in calculator_tools.tools:

                groq_tools.append(
                    convert_mcp_tool(tool)
                )

                tool_to_client[tool.name] = calculator_client

            # Student tools
            for tool in student_tools.tools:

                groq_tools.append(
                    convert_mcp_tool(tool)
                )

                tool_to_client[tool.name] = student_client

            print(
                f"\nTotal tools available to Qwen: "
                f"{len(groq_tools)}"
            )

            # =================================================
            # 7. Conversation history
            # =================================================

            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant with access "
                        "to MCP tools. Use tools whenever they are "
                        "needed to answer the user's request. "
                        "Use conversation history to understand "
                        "references such as 'it', 'that', 'his', "
                        "'her', 'that result', and 'that average'. "
                        "Do not use a tool when the question can "
                        "be answered normally."
                    ),
                }
            ]

            print("\n=== Qwen Multi-Server MCP Assistant ===")
            print("Type 'exit' to quit.\n")

            # =================================================
            # 8. Interactive conversation
            # =================================================

            while True:

                user_input = input("You: ")

                if user_input.lower().strip() == "exit":
                    print("Goodbye!")
                    break

                messages.append(
                    {
                        "role": "user",
                        "content": user_input,
                    }
                )

                try:

                    # =========================================
                    # 9. Agent loop
                    # =========================================

                    while True:

                        response = groq_client.chat.completions.create(
                            model="qwen/qwen3.6-27b",
                            messages=messages,
                            tools=groq_tools,
                            tool_choice="auto",
                            parallel_tool_calls=True,
                        )

                        message = response.choices[0].message

                        # =====================================
                        # 10. No tool call -> final response
                        # =====================================

                        if not message.tool_calls:

                            assistant_reply = (
                                message.content
                                or "No response generated."
                            )

                            print(
                                f"\nQwen: {assistant_reply}\n"
                            )

                            messages.append(
                                {
                                    "role": "assistant",
                                    "content": assistant_reply,
                                }
                            )

                            break

                        # =====================================
                        # 11. Store assistant tool-call message
                        # =====================================

                        assistant_tool_calls = []

                        for tool_call in message.tool_calls:

                            assistant_tool_calls.append(
                                {
                                    "id": tool_call.id,
                                    "type": "function",
                                    "function": {
                                        "name": (
                                            tool_call.function.name
                                        ),
                                        "arguments": (
                                            tool_call.function.arguments
                                        ),
                                    },
                                }
                            )

                        messages.append(
                            {
                                "role": "assistant",
                                "content": message.content,
                                "tool_calls": assistant_tool_calls,
                            }
                        )

                        # =====================================
                        # 12. Execute ALL requested MCP tools
                        # =====================================

                        for tool_call in message.tool_calls:

                            tool_name = tool_call.function.name

                            try:
                                arguments = json.loads(
                                    tool_call.function.arguments
                                )

                            except json.JSONDecodeError:

                                arguments = {}

                            print("\nQwen requested tool:")
                            print("Tool:", tool_name)
                            print("Arguments:", arguments)

                            # ---------------------------------
                            # Find correct MCP server
                            # ---------------------------------

                            mcp_client = tool_to_client.get(
                                tool_name
                            )

                            if mcp_client is None:

                                tool_result = {
                                    "error": (
                                        f"Unknown MCP tool: "
                                        f"{tool_name}"
                                    )
                                }

                            else:

                                try:

                                    result = (
                                        await mcp_client.call_tool(
                                            tool_name,
                                            arguments,
                                        )
                                    )

                                    tool_result = (
                                        extract_tool_result(
                                            result
                                        )
                                    )

                                except Exception as error:

                                    tool_result = {
                                        "error": str(error)
                                    }

                            print(
                                "MCP result:",
                                tool_result,
                            )

                            # =================================
                            # 13. Send tool result into history
                            # =================================

                            messages.append(
                                {
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "name": tool_name,
                                    "content": json.dumps(
                                        tool_result
                                    ),
                                }
                            )

                        # Loop again.
                        #
                        # Qwen now receives the tool results.
                        # It can:
                        #
                        # 1. Give final answer
                        # 2. Request another tool
                        # 3. Request multiple tools
                        #
                        # This enables multi-step agent behavior.

                except Exception as error:

                    print("\nGroq/Qwen API error:")
                    print(error)
                    print(
                        "\nYou can continue asking questions.\n"
                    )


# ============================================================
# 14. Start application
# ============================================================

if __name__ == "__main__":
    asyncio.run(main())