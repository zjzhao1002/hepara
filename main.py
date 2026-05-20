import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

AUTHOR=os.getenv('AUTHOR')

from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
from hepara.agent import hep_coordinator

async def main():
    print("Welcome to HEPARA!")
    print("Type 'exit' or 'quit' to end the conversation.\n")

    runner = InMemoryRunner(agent=hep_coordinator, app_name="HEPARA")

    session_id = "session_1"
    user_id = AUTHOR if AUTHOR else "Guest"

    await runner.session_service.create_session(app_name=runner.app_name, user_id=user_id, session_id=session_id)

    while True:
        try:
            user_input = await asyncio.to_thread(input, f"{user_id}: ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        cleaned_input = user_input.strip()
        if not cleaned_input:
            continue
        if cleaned_input.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        content = Content(role="user", parts=[Part(text=cleaned_input)])

        async for response in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
            if response.content and response.content.parts and response.author != "user":
                for part in response.content.parts:
                    if part.text:
                        print(f"{response.author}: {part.text}")
        print()

if __name__ == "__main__":
    asyncio.run(main())
