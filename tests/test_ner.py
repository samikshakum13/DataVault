"""
Test suite for NER (Named Entity Recognition) module

Tests that ResumeNER properly extracts entities from text
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
import pytest
from ner import ResumeNER

class TestResumeNER:
    """Test cases for ResumeNER."""
    
    @pytest.fixture
    def ner(self):
        """Initialize NER for each test."""
        return ResumeNER()
    
    def test_extract_emails(self, ner):
        """Test email extraction."""
        text = "Contact: john@example.com or jane.doe@company.com"
        emails = ner.extract_emails(text)
        
        assert len(emails) == 2
        assert "john@example.com" in emails
        assert "jane.doe@company.com" in emails
    
    def test_extract_phones(self, ner):
        """Test phone number extraction."""
        text = "Call +1-555-123-4567 or (555) 987-6543"
        phones = ner.extract_phones(text)
        
        assert len(phones) >= 1
        assert any("555" in p for p in phones)
    
    def test_extract_skills(self, ner):
        """Test skill extraction."""
        text = "Skills: Python, Machine Learning, FastAPI, Docker"
        skills = ner.extract_skills(text)
        
        assert "Python" in skills
        assert "Machine Learning" in skills
        assert "Docker" in skills
    
    
    def test_full_extraction(self, ner):
        """Test complete entity extraction."""
        text = """
        John Doe
        john@example.com | +1-555-123-4567
        San Francisco, CA
        
        Experience:
        ML Engineer at Google (2020-2023)
        Skills: Python, TensorFlow, FastAPI
        """
        
        entities = ner.extract_all(text)
        
        # Check all entity types extracted
        assert len(entities.get('emails', [])) > 0
        assert len(entities.get('phones', [])) > 0
        assert len(entities.get('skills', [])) > 0
        assert len(entities.get('years', [])) > 0
    
    def test_empty_text(self, ner):
        """Test handling of empty text."""
        entities = ner.extract_all("")
        
        # Should return empty lists, not crash
        assert isinstance(entities, dict)
        assert all(isinstance(v, list) for v in entities.values())


if __name__ == "__main__":
    pytest.main([__file__, "-v"])