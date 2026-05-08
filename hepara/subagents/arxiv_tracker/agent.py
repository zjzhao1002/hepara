import os
import json
import pandas as pd
import arxiv
from collections import Counter
from google.adk.agents.llm_agent import Agent
from arxivflow import arXivFlow
from .prompt import ARXIV_TRACKER_PROMPT

# ArXiv API requires a delay between requests (default 3s in the library).
# arXivFlow creates a new Client() for every category search, which bypasses
# the instance-level rate limiting. We monkeypatch arxiv.Client to return a 
# singleton instance.
_shared_arxiv_client = arxiv.Client(delay_seconds=3, num_retries=5)

class SingletonArxivClient:
    def __new__(cls, *args, **kwargs):
        return _shared_arxiv_client

arxiv.Client = SingletonArxivClient # type: ignore

CATEGORIES = os.getenv("CATEGORIES")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")
KEYWORDS_FILE = os.path.join(os.path.dirname(__file__), "keywords_record.json")

def calculate_relevance(row_keywords: str | list[str], search_keywords: list[str]) -> int:
    """
    Calculates the relevance score for a paper based on its keywords and the search keywords.
    Match papers (up to 5) based on keywords.
    """
    if not row_keywords:
        return 0
    if isinstance(row_keywords, str):
        row_k_list = [k.strip().lower() for k in row_keywords.split(',') if k.strip()]
    elif isinstance(row_keywords, list):
        row_k_list = [str(k).strip().lower() for k in row_keywords if str(k).strip()]
    else:
        return 0
        
    search_k_lower = [k.lower() for k in search_keywords]
    matches = set(search_k_lower) & set(row_k_list)
    return len(matches)

def recommend_by_keywords(keywords: str | None = None) -> str:
    """
    Recommends latest papers based on user interest (keywords).
    If keywords are provided, they are recorded for future runs.
    If no keywords are provided, uses recorded keywords.
    """
    if not CATEGORIES or not OLLAMA_MODEL:
        return "Error: One or more required environment variables (CATEGORIES, OLLAMA_MODEL) not set in .env file."
    
    categories = [cat.strip() for cat in CATEGORIES.split(',') if cat.strip()]
    # Initialize arXivFlow and fetch data
    flow = arXivFlow(categories=categories, ollama_model=OLLAMA_MODEL, max_results=None)
    df = flow.get_arxiv_data(download_pdfs=False)

    if df is None or df.empty:
        return "No papers found for the specified categories."
    
    if 'Keywords' not in df.columns:
        return "Error: The papers database does not contain a 'Keywords' column."

    # Load recorded keywords
    recorded_keywords = []
    if os.path.exists(KEYWORDS_FILE):
        try:
            with open(KEYWORDS_FILE, 'r') as f:
                recorded_keywords = json.load(f)
        except (json.JSONDecodeError, IOError):
            recorded_keywords = []

    # Determine search keywords
    if keywords:
        # User provided keywords now: Split by comma and clean up
        search_keywords = [k.strip() for k in keywords.split(',') if k.strip()]
        # Record them for future runs
        with open(KEYWORDS_FILE, 'w') as f:
            json.dump(search_keywords, f)
        source = "provided keywords"
    elif recorded_keywords:
        # User did not provide, but we have recorded ones from a previous run
        search_keywords = recorded_keywords
        source = "recorded keywords"
    else:
        return "No keywords provided by user and no recorded keywords found. "
    
    df['relevance_score'] = df['Keywords'].apply(lambda x: calculate_relevance(x, search_keywords))
    
    # Filter for relevant papers and then pick top 5
    relevant_df = df[df['relevance_score'] > 0]
    
    if relevant_df.empty:
        return f"No papers matched the keywords: {', '.join(search_keywords)} (Source: {source})"
    
    top_papers = relevant_df.sort_values(by='relevance_score', ascending=False).head(5)

    # Format the recommendation report
    report = f"Recommended papers based on {source}: {', '.join(search_keywords)}\n\n"
    for _, row in top_papers.iterrows():
        title = row.get('Title', row.get('title', 'No Title'))
        arxiv_id = row.get('arXiv ID', row.get('arxiv_id', row.get('id', 'N/A')))
        keywords_str = row.get('Keywords', 'N/A')
        if isinstance(keywords_str, list):
            keywords_str = ', '.join(keywords_str)
        
        report += f"- **{title}**\n"
        report += f"  arXiv: {arxiv_id}\n"
        report += f"  Keywords: {keywords_str}\n\n"
        
    return report

def recommend_by_trends() -> str:
    """
    Recommends latest papers based on trending topics in the last week.
    It finds the most frequent keywords in the latest papers and recommends papers matching those keywords.
    """
    if not CATEGORIES or not OLLAMA_MODEL:
        return "Error: One or more required environment variables (CATEGORIES, OLLAMA_MODEL) not set in .env file."
    
    categories = [cat.strip() for cat in CATEGORIES.split(',') if cat.strip()]
    # Initialize arXivFlow and fetch data
    flow = arXivFlow(categories=categories, ollama_model=OLLAMA_MODEL, max_results=None)
    df = flow.get_arxiv_data(download_pdfs=False)

    if df is None or df.empty:
        return "No papers found for the specified categories."
    
    if 'Keywords' not in df.columns:
        return "Error: The papers database does not contain a 'Keywords' column."
    
    all_keywords = []
    for k_val in df['Keywords'].dropna():
        if isinstance(k_val, str):
            all_keywords.extend([k.strip() for k in k_val.split(',') if k.strip()])
        elif isinstance(k_val, list):
            all_keywords.extend([str(k).strip() for k in k_val if str(k).strip()])  

    if all_keywords:
        counts = Counter(all_keywords)
        search_keywords = [k for k, _ in counts.most_common(5)]
        source = "most frequent keywords in the data"
    else:
        return "Error: No keywords found in the database to determine trends."
    
    df['relevance_score'] = df['Keywords'].apply(lambda x: calculate_relevance(x, search_keywords))
    
    # Filter for relevant papers and then pick top 5
    relevant_df = df[df['relevance_score'] > 0]
    
    if relevant_df.empty:
        return f"No papers matched the keywords: {', '.join(search_keywords)} (Source: {source})"
    
    top_papers = relevant_df.sort_values(by='relevance_score', ascending=False).head(5)

    # Format the recommendation report
    report = f"Recommended papers based on {source}: {', '.join(search_keywords)}\n\n"
    for _, row in top_papers.iterrows():
        title = row.get('Title', row.get('title', 'No Title'))
        arxiv_id = row.get('arXiv ID', row.get('arxiv_id', row.get('id', 'N/A')))
        keywords_str = row.get('Keywords', 'N/A')
        if isinstance(keywords_str, list):
            keywords_str = ', '.join(keywords_str)
        
        report += f"- **{title}**\n"
        report += f"  arXiv: {arxiv_id}\n"
        report += f"  Keywords: {keywords_str}\n\n"
        
    return report

arxiv_tracker = Agent(
    model='gemini-2.5-flash',
    name='arxiv_tracker',
    description="An arXiv tracker that can check the relevant papers in the last week and recommend papers based on the research interest of the user.",
    instruction=ARXIV_TRACKER_PROMPT,
    tools=[recommend_by_keywords, recommend_by_trends]
)
