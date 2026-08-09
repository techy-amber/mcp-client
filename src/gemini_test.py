import os

from dotenv import load_dotenv
from google import genai


# Load variables from .env
load_dotenv()

# Read Gemini API key
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY was not found in .env")


# Create Gemini client
client = genai.Client(api_key=api_key)


# Send our first request
response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents="What is Python? Answer in only two sentences.",
)


print("Gemini response:")
print(response.text)