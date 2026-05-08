import sys
import os
import unittest
from unittest.mock import MagicMock, patch
import pandas as pd

# Add the project root to sys.path to import hepara
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from hepara.subagents.arxiv_tracker.agent import recommend_by_keywords, recommend_by_trends

class TestArxivTrackerTools(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        os.environ["CATEGORIES"] = "hep-ph"
        os.environ["OLLAMA_MODEL"] = "llama3.2"
    
    @patch('hepara.subagents.arxiv_tracker.agent.arXivFlow')
    def test_recommend_by_keywords_provided(self, mock_arxivflow):
        # Setup mock DataFrame
        mock_df = pd.DataFrame({
            'Title': ['Paper 1', 'Paper 2'],
            'arXiv ID': ['2401.00001', '2401.00002'],
            'Keywords': [['Higgs', 'LHC'], ['Dark Matter', 'WIMP']]
        })
        mock_instance = mock_arxivflow.return_value
        mock_instance.get_arxiv_data.return_value = mock_df
        
        # Test with provided keywords
        result = recommend_by_keywords(keywords="Higgs")
        self.assertIn("Recommended papers based on provided keywords: Higgs", result)
        self.assertIn("Paper 1", result)
        self.assertNotIn("Paper 2", result)

    @patch('hepara.subagents.arxiv_tracker.agent.arXivFlow')
    def test_recommend_by_trends(self, mock_arxivflow):
        # Setup mock DataFrame
        mock_df = pd.DataFrame({
            'Title': ['Paper A', 'Paper B', 'Paper C'],
            'arXiv ID': ['2401.0000A', '2401.0000B', '2401.0000C'],
            'Keywords': [['Higgs'], ['Higgs', 'LHC'], ['Dark Matter']]
        })
        mock_instance = mock_arxivflow.return_value
        mock_instance.get_arxiv_data.return_value = mock_df
        
        # Test trends
        result = recommend_by_trends()
        # Higgs appears twice, so it should be a trend
        self.assertIn("Recommended papers based on most frequent keywords", result)
        self.assertIn("Higgs", result)
        self.assertIn("Paper A", result)
        self.assertIn("Paper B", result)

if __name__ == '__main__':
    unittest.main()
