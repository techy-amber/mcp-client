import asyncio
import json

from ollama import chat
from mcp import Client
from servers.calculator_server import mcp


async def main():

    async with Client(mcp) as client:

        # -----------------------------------
        # 1. Discover tools from MCP server
        # -----------------------------------

        tools_result = await client.list_tools()

        print("Connected to MCP Server")
        print("\nAvailable tools:")

        for tool in tools_result.tools:
            print(f"- {tool.name}: {tool.description}")

        # -----------------------------------
        # 2. Build tool information for Phi-3
        # -----------------------------------

        tool_descriptions = []

        for tool in tools_result.tools:
            tool_info = {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema,
            }

            tool_descriptions.append(tool_info)

        tools_json = json.dumps(tool_descriptions, indent=2)

        print("\n=== Phi-3 MCP Assistant ===")
        print("Type 'exit' to quit.\n")

        # Stores conversation history
        conversation = []

        # -----------------------------------
        # 3. Interactive loop
        # -----------------------------------

        while True:

            user_input = input("You: ")

            if user_input.lower() == "exit":
                print("Goodbye!")
                break

            # Store user's message
            conversation.append(
                {
                    "role": "user",
                    "content": user_input,
                }
            )

            # -----------------------------------
            # 4. Build conversation context
            # -----------------------------------

            conversation_text = ""

            for message in conversation:
                conversation_text += (
                    f"{message['role']}: "
                    f"{message['content']}\n"
                )

            # -----------------------------------
            # 5. Ask Phi-3 to choose a tool
            # -----------------------------------

            decision_prompt = f"""
You are a tool-routing system.

These tools are currently available:

{tools_json}

Here is the conversation so far:

{conversation_text}

Decide whether the LAST user message requires one of the available tools.

Rules:

1. Use a tool whenever the user's request matches an available tool.

2. Use previous conversation messages to understand references
   such as "it", "that", "the result", "that number", etc.

3. Do not perform the tool's task yourself if an appropriate
   tool exists.

4. If a tool is required, return:

{{
    "use_tool": true,
    "tool": "tool_name",
    "arguments": {{
        "argument_name": "argument_value"
    }}
}}

5. Arguments must follow the tool's input_schema.

6. If no available tool is appropriate, return:

{{
    "use_tool": false
}}

7. Never select a tool unless you can provide ALL required
   arguments from the user's request or conversation.

8. Never use a mathematical tool for a non-mathematical request.

9. If you are uncertain whether a tool is needed, return:

{{
    "use_tool": false
}}

Return JSON only.
"""

            decision = chat(
                model="phi3",
                messages=[
                    {
                        "role": "user",
                        "content": decision_prompt,
                    }
                ],
                format="json",
            )

            model_output = decision.message.content.strip()

            # -----------------------------------
            # 6. Parse Phi-3 decision
            # -----------------------------------

            try:
                action = json.loads(model_output)

            except json.JSONDecodeError:
                print("\nCould not understand tool decision.")
                print("Model returned:", model_output)
                print()
                continue

            # Temporary debugging output
            print("\nDEBUG decision:", action)

            # -----------------------------------
            # 7. Execute selected MCP tool
            # -----------------------------------

            if action.get("use_tool"):

                tool_name = action.get("tool")
                arguments = action.get("arguments", {})

                # -----------------------------------
                # Validate Phi-3's tool decision
                # -----------------------------------

                available_tools = {
                    tool.name: tool
                    for tool in tools_result.tools
                }

                tool_is_valid = tool_name in available_tools

                arguments_are_valid = (
                    arguments
                    and all(
                        value is not None
                        for value in arguments.values()
                    )
                )

                # If Phi-3 made a bad tool decision,
                # fall back to a normal response
                if not tool_is_valid or not arguments_are_valid:

                    print(
                        "Invalid tool request. "
                        "Answering normally instead."
                    )

                    normal_response = chat(
                        model="phi3",
                        messages=conversation,
                    )

                    assistant_reply = (
                        normal_response.message.content
                    )

                    conversation.append(
                        {
                            "role": "assistant",
                            "content": assistant_reply,
                        }
                    )

                    print(
                        f"\nPhi-3: {assistant_reply}\n"
                    )

                    continue

                # -----------------------------------
                # Tool request passed validation
                # -----------------------------------

                result = await client.call_tool(
                    tool_name,
                    arguments,
                )

                print(f"Tool used: {tool_name}")

                # Extract returned value
                if result.structured_content:

                    tool_result = (
                        result.structured_content.get(
                            "result"
                        )
                    )

                else:

                    tool_result = result.content[0].text

                print(f"Tool result: {tool_result}")

                # -----------------------------------
                # 8. Give tool result back to Phi-3
                # -----------------------------------

                final_response = chat(
                    model="phi3",
                    messages=[
                        {
                            "role": "user",
                            "content": (
                                f"The conversation so far is:\n"
                                f"{conversation_text}\n\n"
                                f"The tool '{tool_name}' returned:\n"
                                f"{tool_result}\n\n"
                                f"Answer the user's latest question "
                                f"briefly using the tool result."
                            ),
                        }
                    ],
                )

                assistant_reply = (
                    final_response.message.content
                )

                # Store assistant response
                conversation.append(
                    {
                        "role": "assistant",
                        "content": assistant_reply,
                    }
                )

                print(
                    f"\nPhi-3: {assistant_reply}\n"
                )

            # -----------------------------------
            # 9. No tool needed
            # -----------------------------------

            else:

                normal_response = chat(
                    model="phi3",
                    messages=conversation,
                )

                assistant_reply = (
                    normal_response.message.content
                )

                # Store assistant response
                conversation.append(
                    {
                        "role": "assistant",
                        "content": assistant_reply,
                    }
                )

                print(
                    f"\nPhi-3: {assistant_reply}\n"
                )


if __name__ == "__main__":
    asyncio.run(main())