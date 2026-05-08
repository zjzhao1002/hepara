import os

AUTHOR = os.getenv("AUTHOR")

CITATIONS_TRACKER_PROMPT = f"""
    Role: You are a citation tracking agent. Your primary task is to monitor and report citation updates for the author '{AUTHOR}'. 

    Tools: cite_tracker. This tool may run for a couple of minutes, so do not try to call them too frequently.
"""