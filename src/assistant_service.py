import json
import os

from dotenv import load_dotenv
from groq import Groq
from mcp import Client

from mcp_servers.calculator_server import mcp as calculator_mcp
from mcp_servers.student_server import mcp as student_mcp 


# ============================================================
# Environment + Groq
# ============================================================

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY was not found in .env")

groq_client = Groq(api_key=api_key)


# ============================================================
# Helper: extract result returned by an MCP tool
# ============================================================

def extract_tool_result(result):

    # Some tools return structured content
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
# Helper: MCP tool -> Groq/OpenAI tool definition
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
# Student AI Assistant
# ============================================================

class StudentAIAssistant:

    def __init__(self):

        self.calculator_client = None
        self.student_client = None

        self.calculator_context = None
        self.student_context = None

        self.groq_tools = []
        self.tool_to_client = {}

        self.messages = []

        self.started = False


    # ========================================================
    # Start MCP servers and discover tools
    # ========================================================

    async def start(self):

        if self.started:
            return

        print("Starting Student AI Assistant...")

        # Enter Calculator MCP context
        self.calculator_context = Client(calculator_mcp)

        self.calculator_client = (
            await self.calculator_context.__aenter__()
        )

        # Enter Student MCP context
        self.student_context = Client(student_mcp)

        self.student_client = (
            await self.student_context.__aenter__()
        )

        print("Connected to Calculator MCP Server")
        print("Connected to Student MCP Server")

        # Discover tools
        calculator_tools = (
            await self.calculator_client.list_tools()
        )

        student_tools = (
            await self.student_client.list_tools()
        )

        # Reset tool containers in case start() is reused
        self.groq_tools = []
        self.tool_to_client = {}

        # Calculator tools
        for tool in calculator_tools.tools:

            self.groq_tools.append(
                convert_mcp_tool(tool)
            )

            self.tool_to_client[tool.name] = (
                self.calculator_client
            )

        # Student tools
        for tool in student_tools.tools:

            self.groq_tools.append(
                convert_mcp_tool(tool)
            )

            self.tool_to_client[tool.name] = (
                self.student_client
            )

        print(
            f"Total tools available to Qwen: "
            f"{len(self.groq_tools)}"
        )

        # Initial system message
        self.messages = [
            {
                "role": "system",
                "content": (
                    "You are a Student AI Analytics Assistant. "
                    "You have access to MCP tools for student "
                    "data, academic analytics, attendance, risk "
                    "analysis, and calculations. "

                    "Use the appropriate MCP tool whenever the "
                    "user asks for information that should come "
                    "from the student database. "

                    "Use conversation history to understand "
                    "references such as 'he', 'she', 'they', "
                    "'that student', 'their average', "
                    "'that result', and 'it'. "

                    "Never invent student data, marks, "
                    "attendance, academic performance, or risk "
                    "information. "

                    "Do not expose internal MCP tool names, "
                    "tool arguments, raw JSON, SQL queries, or "
                    "internal implementation details to the "
                    "user. "

                    "Convert tool results into clear, readable "
                    "natural-language responses. "

                    "Use tables or structured formatting when "
                    "comparing several students or presenting "
                    "multiple records. "

                    "Do not use a tool when the question can "
                    "be answered normally."
                ),
            }
        ]

        self.started = True

        print("Student AI Assistant ready.")


    # ========================================================
    # Process one user message
    # ========================================================

    async def chat(self, user_message: str):

        if not self.started:
            await self.start()

        if not user_message or not user_message.strip():
            return "Please enter a message."

        self.messages.append(
            {
                "role": "user",
                "content": user_message.strip(),
            }
        )

        try:

            # =================================================
            # Agent loop
            # =================================================

            while True:

                response = groq_client.chat.completions.create(
                    model="qwen/qwen3.6-27b",
                    messages=self.messages,
                    tools=self.groq_tools,
                    tool_choice="auto",
                    parallel_tool_calls=True,
                )

                message = response.choices[0].message


                # =============================================
                # No tool calls -> final response
                # =============================================

                if not message.tool_calls:

                    assistant_reply = (
                        message.content
                        or "No response generated."
                    )

                    self.messages.append(
                        {
                            "role": "assistant",
                            "content": assistant_reply,
                        }
                    )

                    return assistant_reply


                # =============================================
                # Store assistant tool-call message
                # =============================================

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

                self.messages.append(
                    {
                        "role": "assistant",
                        "content": message.content,
                        "tool_calls": assistant_tool_calls,
                    }
                )


                # =============================================
                # Execute every requested MCP tool
                # =============================================

                for tool_call in message.tool_calls:

                    tool_name = tool_call.function.name

                    try:

                        arguments = json.loads(
                            tool_call.function.arguments
                        )

                    except json.JSONDecodeError:

                        arguments = {}


                    # -----------------------------------------
                    # Developer logs
                    # -----------------------------------------

                    print("\n[TOOL CALL]")
                    print("Tool:", tool_name)
                    print("Arguments:", arguments)


                    # -----------------------------------------
                    # Route to correct MCP server
                    # -----------------------------------------

                    mcp_client = self.tool_to_client.get(
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

                            result = await mcp_client.call_tool(
                                tool_name,
                                arguments,
                            )

                            tool_result = extract_tool_result(
                                result
                            )

                        except Exception as error:

                            tool_result = {
                                "error": str(error)
                            }


                    # -----------------------------------------
                    # Developer-only result
                    # -----------------------------------------

                    print("[MCP RESULT]")
                    print(tool_result)


                    # =========================================
                    # Send result back to Qwen
                    # =========================================

                    self.messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_name,
                            "content": json.dumps(
                                tool_result
                            ),
                        }
                    )

                # Loop continues.
                #
                # Qwen receives all MCP results and can:
                #
                # - produce the final response
                # - request another tool
                # - request several additional tools


        except Exception as error:

            print("\n[ASSISTANT ERROR]")
            print(error)

            return (
                "The AI service is temporarily unavailable. "
                "Please try again."
            )


    # ========================================================
    # Reset conversation
    # ========================================================

    def reset_conversation(self):

        if not self.messages:
            return

        system_message = self.messages[0]

        self.messages = [system_message]

        print("Conversation reset.")


    # ========================================================
    # Stop MCP connections
    # ========================================================

    async def stop(self):

        if not self.started:
            return

        print("Stopping Student AI Assistant...")

        # Close in reverse order
        if self.student_context:
            await self.student_context.__aexit__(
                None,
                None,
                None,
            )

        if self.calculator_context:
            await self.calculator_context.__aexit__(
                None,
                None,
                None,
            )

        self.started = False

        print("Student AI Assistant stopped.")