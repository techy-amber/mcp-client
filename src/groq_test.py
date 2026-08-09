import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY was not found in .env")


client = Groq(api_key=api_key)


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_student_marks",
            "description": "Get marks for all subjects for a student.",
            "parameters": {
                "type": "object",
                "properties": {
                    "student_id": {
                        "type": "integer"
                    }
                },
                "required": ["student_id"],
            },
        },
    }
]


response = client.chat.completions.create(
    model="qwen/qwen3.6-27b",
    messages=[
        {
            "role": "user",
            "content": (
                "What is Python? Answer briefly."
            ),
        }
    ],
    tools=tools,
    tool_choice="auto",
    parallel_tool_calls=True,
)


message = response.choices[0].message


print("\nNORMAL RESPONSE:")
print(message.content)

print("\nTOOL CALLS:")
print(message.tool_calls)


if message.tool_calls:

    print(
        "\nNumber of tool calls:",
        len(message.tool_calls),
    )

    for tool_call in message.tool_calls:

        print("\nTool call detected")
        print("Tool:", tool_call.function.name)
        print("Arguments:", tool_call.function.arguments)