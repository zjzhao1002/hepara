import os
import httpx
import json
from typing import Literal

DEFAULT_PAGE_SIZE = 150
AUTHOR = os.getenv("AUTHOR")
RECORD_FILE = os.path.join(os.path.dirname(__file__), "citations_record.json")

async def _fetch_literature(params: dict) -> dict:
    async with httpx.AsyncClient(timeout=15.0) as client:
        # Using the base URL directly as the tool sometimes has issues with nested URLs
        response = await client.get("https://inspirehep.net/api/literature", params=params)
        response.raise_for_status()
        return response.json()
    
async def _search_papers(query: str, sort: str="mostrecent", page_size: int=DEFAULT_PAGE_SIZE, page: int=1) -> dict:
    """
    Searches for papers on INSPIRE-HEP.

    Args:
        query (str): The search query.
        sort (str): Sort order, either 'mostrecent' or 'mostcited'. Defaults to 'mostrecent'.
        page_size (int): Number of results per page. Defaults to DEFAULT_PAGE_SIZE.
        page (int): Page number. Defaults to 1.

    Returns:
        dict: A dictionary containing the list of papers found.
    """
    if sort not in {"mostrecent", "mostcited"}:
        sort = "mostrecent"
    size = max(1, page_size)
    
    params = {'q': query, 'sort': sort, 'size': size, 'page': page}
    try:
        data = await _fetch_literature(params=params)
    except Exception as e:
        return {'Error': f"Error in fetching data from INSPIRE-HEP: {e}"}
    
    hits = data.get('hits', {}).get('hits', [])

    entries = []
    for hit in hits:
        metadata = hit.get('metadata', {})
        entry = {
            'Inspire ID': hit.get('id'),
            'Title': metadata.get('titles', [{}])[0].get('title', 'N/A'),
            'arXiv ID': metadata.get('arxiv_eprints', [{}])[0].get('value', 'N/A'),
        }
        entries.append(entry)

    results = {'Papers': entries}
    
    return results

async def get_paper_citations(query: str, direction: Literal["citing", "cited_by"] = "citing", page_size: int = DEFAULT_PAGE_SIZE) -> dict:
    """
    Retrieves the citation graph (references or citations) for a specific paper.

    Args:
        query (str): The search query to find the paper (e.g., arXiv ID or INSPIREHEP ID).
        direction (str): The direction of the citation graph. 
                         'citing' for papers this paper cites (its references).
                         'cited_by' for papers that cite this paper (citations).
                         Defaults to 'citing'.
        page_size (int): The number of results to return. Defaults to DEFAULT_PAGE_SIZE.

    Returns:
        dict: A dictionary containing the paper details and the citation graph.
    """
    valid_directions = {"citing", "cited_by"}
    if direction not in valid_directions:
        return {'Error': f"Invalid direction {direction}. The direction must be one of: {','.join(valid_directions)}"}
    
    data = await _search_papers(query=query)

    if 'Papers' not in data or not isinstance(data['Papers'], list) or not data['Papers']:
        return {'Error': f"Could not find any paper by query: {query}"}
        
    papers = data['Papers']
    if len(papers) > 1:
        results = {
            'Warning': f"{len(papers)} papers are found. Please specify the INSPIREHEP ID or arXiv ID of the paper you are looking for.",
            'Papers': papers
        }
        return results
    
    inspire_id = papers[0]['Inspire ID']
    fields = "titles,arxiv_eprints"
    try:
        if direction == 'citing':
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Papers that this paper cites (its references)
                params = {'q': f'citedby:recid:{inspire_id}', 'sort': 'mostrecent', 'size': page_size, 'fields': fields}
                response = await client.get("https://inspirehep.net/api/literature", params=params)
                response_json = response.json()
        else:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Papers that cite this paper
                params = {'q': f'refersto:recid:{inspire_id}', 'sort': 'mostrecent', 'size': page_size, 'fields': fields}
                response = await client.get("https://inspirehep.net/api/literature", params=params)
                response_json = response.json()
    except Exception as e:
        return  {'Error': f"Error in tracking citations: {e}"}
    
    hits = response_json.get('hits', {}).get('hits', [])

    entries = []
    for hit in hits:
        metadata = hit.get('metadata', {})
        entry = {
            'Inspire ID': hit.get('id'),
            'Title': metadata.get('titles', [{}])[0].get('title', 'N/A'),
            'arXiv ID': metadata.get('arxiv_eprints', [{}])[0].get('value', 'N/A'),
        }
        entries.append(entry)

    results = {'Inspire ID': inspire_id, 'Direction': direction, 'Total Papers': len(entries), 'Papers': entries}
    
    return results

async def get_author_citations(author: str, sort: str = "mostrecent", page_size: int = DEFAULT_PAGE_SIZE) -> dict:
    """
    Retrieves the papers and citation counts for a specific author.

    Args:
        author (str): The author name (e.g., 'John Doe').
        sort (str): Sort order, either 'mostrecent' or 'mostcited'. Defaults to 'mostrecent'.
        page_size (int): Number of results to return. Defaults to DEFAULT_PAGE_SIZE.

    Returns:
        dict: A dictionary containing the author's papers and total citation count.
    """
    if not author:
        return {'Error': "Error: author parameter is required."}
    
    if sort not in {"mostrecent", "mostcited"}:
        sort = "mostrecent"

    size = max(1, page_size)
    query = f"a {author}"
    fields = "titles,arxiv_eprints,citation_count"

    params = {'q': query, 'sort': sort, 'size': size, 'fields': fields}

    try:
        data = await _fetch_literature(params=params)
    except Exception as e:
        return {'Error': f"Error in fetching data from INSPIRE-HEP: {e}"}

    hits = data.get('hits', {}).get('hits', [])

    entries = []
    total_citations = 0
    for hit in hits:
        metadata = hit.get('metadata', {})
        entry = {
            'Inspire ID': hit.get('id'),
            'Title': metadata.get('titles', [{}])[0].get('title', 'N/A'),
            'arXiv ID': metadata.get('arxiv_eprints', [{}])[0].get('value', 'N/A'),
            'Citations': metadata.get('citation_count', 0)
        }
        entries.append(entry)
        total_citations += entry['Citations']

    results = {'Total Citations': total_citations, 'Total Papers': len(entries), 'Papers': entries}

    return results

async def track_citations_updates() -> dict:
    """
    Tracks updates to the user's citations since the last check.

    Returns:
        dict: A dictionary containing new publications and citation increases.
    """

    if not AUTHOR:
        return {'Error': "Error: AUTHOR environment variable is not set."}
    
    current_citations = await get_author_citations(AUTHOR)
    if not current_citations or 'Error' in current_citations:
        return {'Error': f"Could not find any papers or citations for author: {AUTHOR}"}
    
    current_map = {p['Inspire ID']: p['Citations'] for p in current_citations['Papers']}

    if not os.path.exists(RECORD_FILE):
        with open(RECORD_FILE, 'w') as f:
            json.dump(current_map, f)

        return {'Result': f"First run: Successfully recorded citations for author {AUTHOR}"}
    
    with open(RECORD_FILE, 'r') as f:
        previous_map = json.load(f)

    new_citations = []
    new_publications = []
    papers = current_citations['Papers']
    for paper in papers:
        pid = paper['Inspire ID']
        if pid not in previous_map:
            new_publications.append({
                'Title': paper['Title'],
                'arXiv ID': paper.get('arXiv ID', 'N/A'),
                'Citations': paper['Citations']
            })
        else:
            prev_count = previous_map[pid]
            if paper['Citations'] > prev_count:
                update = {
                    'Title': paper['Title'],
                    'Previous': prev_count,
                    'Current': paper['Citations'],
                    'Increase': paper['Citations'] - prev_count
                }
                new_citations.append(update)

    with open(RECORD_FILE, 'w') as f:
        json.dump(current_map, f)

    result_output = {}
    if new_publications:
        result_output['New Publications'] = new_publications
    if new_citations:
        result_output['Citation Updates'] = new_citations

    if result_output:
        return {'Result': result_output}
    else:
        return {'Result': f"No new publications or citations found for author '{AUTHOR}' since the last check."}
