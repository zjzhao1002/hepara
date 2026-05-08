import os
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from hepara.subagents.arxiv_tracker.agent import recommend_by_keywords, recommend_by_trends

def test_real_calls():
    # These might fail if Ollama is not running or arXiv is down
    print("Testing recommend_by_keywords('Higgs')...")
    try:
        res = recommend_by_keywords("Higgs")
        print("Result:")
        print(res)
    except Exception as e:
        print(f"Failed: {e}")

    print("\nTesting recommend_by_trends()...")
    try:
        res = recommend_by_trends()
        print("Result:")
        print(res)
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    # Ensure env vars are set (they should be from .env if run via uv run)
    test_real_calls()
