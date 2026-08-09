from ollama import chat

# Stores the complete conversation
conversation = []

print("=== Local AI Chat ===")
print("Type 'exit' to quit.\n")

while True:

    # Take input from the user
    user_input = input("You: ")

    # Exit condition
    if user_input.lower() == "exit":
        print("\nGoodbye!")
        break

    # Store the user's message
    conversation.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    # Send the ENTIRE conversation to the model
    response = chat(
        model="phi3",
        messages=conversation
    )

    # Store the assistant's reply
    conversation.append(
        {
            "role": "assistant",
            "content": response.message.content
        }
    )

    # Display the response
    print(f"\nPhi-3: {response.message.content}\n")