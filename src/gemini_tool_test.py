import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY was not found in .env")


client = genai.Client(api_key=api_key)


# Define a tool for Gemini
add_numbers = {
    "name": "add_numbers",
    "description": "Add two numbers together.",
    "parameters": {
        "type": "object",
        "properties": {
            "a": {
                "type": "number",
                "description": "First number",
            },
            "b": {
                "type": "number",
                "description": "Second number",
            },
        },
        "required": ["a", "b"],
    },
}


response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents="Use the add_numbers tool to calculate 45 + 72.",
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(
                function_declarations=[add_numbers]
            )
        ]
    ),
)


print("TEXT:")
print(response.text)

print("\nFUNCTION CALL:")

if response.function_calls:
    for function_call in response.function_calls:
        print("Function name:", function_call.name)
        print("Arguments:", function_call.args)
else:
    print("No structured function call received.")