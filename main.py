import asyncio
from google.adk.runners import InMemoryRunner
from hepara.agent import root_agent
from dotenv import load_dotenv

load_dotenv()

async def main():
    print("Hello from hep-ai-assistant!")
    runner = InMemoryRunner(root_agent)
    response = await runner.run_debug(
        "What is High Energy Physics? Search for answer by google."
    )

if __name__ == "__main__":
    asyncio.run(main())
