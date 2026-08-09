import asyncio
import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from mcp import Client

from servers.calculator_server import mcp as calculator_mcp
from servers.student_server import mcp as student_mcp


# ============================================================
# 1. Load Gemini API key
# ============================================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY was not found in .env")


gemini = genai.Client(api_key=api_key)


# ============================================================
# 2. Extract result from different MCP response formats
# ============================================================

def extract_tool_result(result):

    # Some MCP tools return structured content
    if result.structured_content:

        # Calculator server usually returns:
        # {"result": 117.0}
        if "result" in result.structured_content:
            return result.structured_content["result"]

        return result.structured_content

    # Other MCP tools may return text content
    if result.content:

        text = result.content[0].text

        # Student server returns JSON as text.
        # Try converting it back into a Python dictionary.
        try:
            return json.loads(text)

        except json.JSONDecodeError:
            return text

    return None


# ============================================================
# 3. Main application
# ============================================================

async def main():

    # Connect to BOTH MCP servers
    async with Client(calculator_mcp) as calculator_client:

        async with Client(student_mcp) as student_client:

            print("Connected to Calculator MCP Server")
            print("Connected to Student MCP Server")

            # =================================================
            # 4. Discover tools from both servers
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
            # 5. Build Gemini function declarations
            # =================================================

            function_declarations = []

            # This dictionary tells us which MCP client owns
            # each tool.
            tool_to_client = {}

            # -------------------------------------------------
            # Calculator tools
            # -------------------------------------------------

            for tool in calculator_tools.tools:

                declaration = {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.input_schema,
                }

                function_declarations.append(declaration)

                tool_to_client[tool.name] = calculator_client

            # -------------------------------------------------
            # Student tools
            # -------------------------------------------------

            for tool in student_tools.tools:

                declaration = {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.input_schema,
                }

                function_declarations.append(declaration)

                tool_to_client[tool.name] = student_client

            print(
                f"\nTotal tools available to Gemini: "
                f"{len(function_declarations)}"
            )

            # =================================================
            # 6. Configure Gemini
            # =================================================

            gemini_config = types.GenerateContentConfig(
                tools=[
                    types.Tool(
                        function_declarations=function_declarations
                    )
                ]
            )

            # =================================================
            # 7. Conversation memory
            # =================================================

            conversation = []

            print("\n=== Gemini Multi-Server MCP Assistant ===")
            print("Type 'exit' to quit.\n")

            # =================================================
            # 8. Conversation loop
            # =================================================

            while True:

                user_input = input("You: ")

                if user_input.lower().strip() == "exit":
                    print("Goodbye!")
                    break

                # ---------------------------------------------
                # Store user message
                # ---------------------------------------------

                conversation.append(
                    types.Content(
                        role="user",
                        parts=[
                            types.Part(
                                text=user_input
                            )
                        ],
                    )
                )

                # ---------------------------------------------
                # Ask Gemini
                # ---------------------------------------------

                response = gemini.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=conversation,
                    config=gemini_config,
                )

                # =============================================
                # 9. Agent/tool loop
                # =============================================

                while response.function_calls:

                    # Store Gemini's function-call message
                    conversation.append(
                        response.candidates[0].content
                    )

                    function_response_parts = []

                    # Gemini may request more than one function
                    for function_call in response.function_calls:

                        tool_name = function_call.name
                        arguments = dict(function_call.args)

                        print("\nGemini requested tool:")
                        print("Tool:", tool_name)
                        print("Arguments:", arguments)

                        # -------------------------------------
                        # Find which MCP server owns this tool
                        # -------------------------------------

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

                            print(
                                "Tool routing error:",
                                tool_result,
                            )

                        else:

                            # ---------------------------------
                            # Execute through correct MCP server
                            # ---------------------------------

                            try:

                                result = await mcp_client.call_tool(
                                    tool_name,
                                    arguments,
                                )

                                tool_result = extract_tool_result(
                                    result
                                )

                                print(
                                    "MCP result:",
                                    tool_result,
                                )

                            except Exception as error:

                                tool_result = {
                                    "error": str(error)
                                }

                                print(
                                    "MCP tool error:",
                                    error,
                                )

                        # -------------------------------------
                        # Convert MCP result to Gemini response
                        # -------------------------------------

                        function_response = (
                            types.Part.from_function_response(
                                name=tool_name,
                                response={
                                    "result": tool_result
                                },
                            )
                        )

                        function_response_parts.append(
                            function_response
                        )

                    # -----------------------------------------
                    # Store tool results in conversation
                    # -----------------------------------------

                    conversation.append(
                        types.Content(
                            role="user",
                            parts=function_response_parts,
                        )
                    )

                    # -----------------------------------------
                    # Continue Gemini reasoning
                    # -----------------------------------------

                    response = gemini.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=conversation,
                        config=gemini_config,
                    )

                # =============================================
                # 10. Final response
                # =============================================

                assistant_reply = response.text

                print(f"\nGemini: {assistant_reply}\n")

                # Store final Gemini response
                conversation.append(
                    response.candidates[0].content
                )


# ============================================================
# 11. Start application
# ============================================================

if __name__ == "__main__":
    asyncio.run(main())