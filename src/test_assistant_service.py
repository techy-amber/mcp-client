import asyncio

from assistant_service import StudentAIAssistant


async def main():

    assistant = StudentAIAssistant()

    try:
        await assistant.start()

        print("\n===== TESTING ASSISTANT SERVICE =====\n")

        response = await assistant.chat(
            "What is the average of student 100001?"
        )

        print("\n===== USER-FACING RESPONSE =====")
        print(response)

    finally:
        await assistant.stop()


if __name__ == "__main__":
    asyncio.run(main())