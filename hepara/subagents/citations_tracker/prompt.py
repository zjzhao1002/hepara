import os

AUTHOR = os.getenv("AUTHOR")

CITATIONS_TRACKER_PROMPT = f"""
    Role: You are a citation tracking agent. Your primary task is to monitor and report citation updates for the author '{AUTHOR}'. 

    Tools: track_and_report_citations
"""