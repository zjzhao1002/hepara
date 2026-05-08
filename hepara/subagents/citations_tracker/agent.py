import os
import json
import requests
import pandas as pd
from google.adk.agents.llm_agent import Agent
from .prompt import CITATIONS_TRACKER_PROMPT

# Load environment variables (should be loaded in the main entry point)
AUTHOR = os.getenv("AUTHOR")
RECORD_FILE = os.path.join(os.path.dirname(__file__), "citations_record.json")

def get_inspire_citations(author: str, max_papers: int = 100) -> list:
    """
    Fetches papers and their citation counts for a given author from INSPIRE-HEP.
    """
    if not author:
        return []
        
    inspire_profile = f'https://inspirehep.net/api/literature?sort=mostrecent&size={max_papers}&q=a%20{author}'

    try:
        response = requests.get(inspire_profile)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error fetching data from INSPIRE-HEP: {e}")
        return []

    hits = data.get('hits', {}).get('hits', [])
    entries = []

    for hit in hits:
        metadata = hit.get('metadata', {})
        entry = {
            'Inspire ID': hit.get('id'),
            'Title': metadata.get('titles', [{}])[0].get('title', 'N/A'),
            'arXiv ID': metadata.get('arxiv_eprints', [{}])[0].get('value', 'N/A'),
            'Citations': metadata.get('citation_count', 0)
        }
        entries.append(entry)

    return entries

def track_and_report_citations() -> str:
    """
    Tracks citations for the user specified by the AUTHOR environment variable.
    Records citations on the first run and checks for updates on subsequent runs.
    """
    if not AUTHOR:
        return "Error: AUTHOR environment variable not set in .env file."

    current_citations = get_inspire_citations(AUTHOR)
    if not current_citations:
        return f"Could not find any papers or citations for author: {AUTHOR}"

    # Create a map for persistence: {Inspire ID: Citation Count}
    current_map = {p['Inspire ID']: p['Citations'] for p in current_citations}

    if not os.path.exists(RECORD_FILE):
        # First time running: Record and report
        with open(RECORD_FILE, 'w') as f:
            json.dump(current_map, f)
        
        df = pd.DataFrame(current_citations)
        report = f"First run: Successfully recorded citations for author '{AUTHOR}'.\n"
        report += f"Total papers found: {len(current_citations)}\n\n"
        report += df[['Title', 'Citations', 'arXiv ID']].to_string(index=False)
        return report

    # Subsequent runs: Compare and report
    with open(RECORD_FILE, 'r') as f:
        previous_map = json.load(f)

    new_citations = []
    for paper in current_citations:
        pid = paper['Inspire ID']
        prev_count = previous_map.get(pid, 0)
        if paper['Citations'] > prev_count:
            new_citations.append({
                'Title': paper['Title'],
                'Previous': prev_count,
                'Current': paper['Citations'],
                'Increase': paper['Citations'] - prev_count
            })

    # Update the record file with the latest counts
    with open(RECORD_FILE, 'w') as f:
        json.dump(current_map, f)

    if new_citations:
        df_new = pd.DataFrame(new_citations)
        report = f"Updates found for author '{AUTHOR}':\n\n"
        report += df_new.to_string(index=False)
    else:
        report = f"No new citations found for author '{AUTHOR}' since the last check."

    return report

citations_tracker = Agent(
    model='gemini-2.5-flash',
    name='citations_tracker',
    description='A helpful assistant for tracking paper citations of the user.',
    instruction=CITATIONS_TRACKER_PROMPT,
    tools=[track_and_report_citations, get_inspire_citations]
)
