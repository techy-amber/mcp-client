from ollama import chat


def add_numbers(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b


response = chat(
    model="phi4-mini",
    messages=[
        {
            "role": "user",
            "content": "What is 45 + 72?",
        }
    ],
    tools=[add_numbers],
)


print("Normal response:")
print(response.message.content)

print("\nTool calls:")
print(response.message.tool_calls)