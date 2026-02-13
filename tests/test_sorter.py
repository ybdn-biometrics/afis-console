import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from afis_console.core.sorter import has_no_homonyme

class TestSorter(unittest.TestCase):
    @patch('fitz.open')
    def test_has_no_homonyme_true(self, mock_open):
        # Mocking the PDF doc and page
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_open.return_value = mock_doc
        mock_doc.__getitem__.return_value = mock_page
        mock_doc.__len__.return_value = 1
        
        # Mock words: (x0, y0, x1, y1, "text", ...)
        # We need "Homonymes" and "non" on same Y line
        # y=100
        mock_page.get_text.return_value = [
            (10, 100, 50, 110, "Homonymes", 0, 0, 0),
            (60, 100, 80, 110, "non", 0, 0, 1)
        ]
        
        result = has_no_homonyme("dummy.pdf")
        self.assertTrue(result)

    @patch('fitz.open')
    def test_has_no_homonyme_false(self, mock_open):
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_open.return_value = mock_doc
        mock_doc.__getitem__.return_value = mock_page
        mock_doc.__len__.return_value = 1
        
        # "Homonymes" but no "non"
        mock_page.get_text.return_value = [
            (10, 100, 50, 110, "Homonymes", 0, 0, 0),
            (60, 100, 80, 110, "detected", 0, 0, 1)
        ]
        
        result = has_no_homonyme("dummy.pdf")
        self.assertFalse(result)

    @patch('fitz.open')
    def test_homonyme_different_line(self, mock_open):
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_open.return_value = mock_doc
        mock_doc.__getitem__.return_value = mock_page
        mock_doc.__len__.return_value = 1
        
        # "Homonymes" on line 100, "non" on line 200
        mock_page.get_text.return_value = [
            (10, 100, 50, 110, "Homonymes", 0, 0, 0),
            (60, 200, 80, 210, "non", 0, 0, 1)
        ]
        
        result = has_no_homonyme("dummy.pdf")
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
