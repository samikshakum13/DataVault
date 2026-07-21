"""
Test suite for text cleaning module

Tests that TextCleaner properly normalizes resume text
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
import pytest
from clean import TextCleaner


class TestTextCleaner:
    """Test cases for TextCleaner."""
    
    @pytest.fixture
    def cleaner(self):
        """Initialize cleaner for each test."""
        return TextCleaner()
    
    def test_remove_extra_whitespace(self, cleaner):
        """Test removal of extra whitespace."""
        raw = "JOHN    DOE\n\n\nemail@example.com"
        cleaned = cleaner.remove_extra_whitespace(raw)
        
        assert "\n" not in cleaned
        assert "  " not in cleaned
        assert cleaned == "JOHN DOE email@example.com"
    
    def test_remove_special_chars(self, cleaner):
        """Test removal of special characters."""
        raw = "JOHN***DOE|||email@example.com"
        cleaned = cleaner.remove_special_chars(raw)
        
        # Should keep alphanumeric and @
        assert "@" in cleaned
        assert "*" not in cleaned
        assert "|" not in cleaned
    
    def test_normalize_text(self, cleaner):
        """Test text normalization."""
        raw = "john DOE email@example.com"
        normalized = cleaner.normalize_text(raw)
        
        # Should be title case
        assert normalized[0].isupper()
    
    def test_full_cleaning_pipeline(self, cleaner):
        """Test complete cleaning process."""
        raw = "JOHN    DOE\n\n\njohn@example.com***"
        cleaned = cleaner.clean(raw)
        
        assert "\n" not in cleaned
        assert "  " not in cleaned
        assert "*" not in cleaned
        assert "@" in cleaned
    
    def test_empty_string(self, cleaner):
        """Test handling of empty input."""
        result = cleaner.clean("")
        assert result == ""
    

if __name__ == "__main__":
    pytest.main([__file__, "-v"])