import asyncio
from dotenv import load_dotenv

load_dotenv()

from google.adk.runners import InMemoryRunner
from hepara.agent import hep_coordinator

async def main():
    print("Welcome to HEP-AI-Assistant!")
    runner = InMemoryRunner(hep_coordinator)
    
    print("\n--- Initializing Session ---")
    # Trigger the agent's initial instruction (e.g., reporting citations)
    # The agent is instructed to report citations first.
    initial_response = await runner.run_debug("Hi there!") # type: ignore
    # print(f"\nAssistant: {initial_response.text}")

    print("\n-----------------------------")
    print("Type 'exit' or 'quit' to stop.")
    
    while True:
        try:
            # Use run_in_executor to handle blocking input() in an async function
            user_input = await asyncio.get_event_loop().run_in_executor(None, input, "\nYou: ")
        except EOFError:
            break
            
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        
        if not user_input.strip():
            continue

        response = await runner.run_debug(user_input)
        # print(f"\nAssistant: {response.text}")

if __name__ == "__main__":
    asyncio.run(main())
