"""
Test suite for full processing pipeline

Tests end-to-end resume processing
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
import json
import os
from pipeline import DataPipeline


class TestDataPipeline:
    """Test cases for DataPipeline."""
    
    @pytest.fixture
    def pipeline(self):
        """Initialize pipeline for each test."""
        return DataPipeline(
            input_file="data/extracted_text.json",
            output_file="data/test_results.json"
        )
    
    def test_load_extracted_text(self, pipeline):
        """Test loading extracted text."""
        data = pipeline.load_extracted_text()
        
        # Should load data from Day 3
        assert isinstance(data, list)
        assert len(data) > 0
        assert 'text' in data[0]
    
    def test_quality_score_calculation(self, pipeline):
        """Test quality score calculation."""
        entities = {
            'names': ['John Doe'],
            'emails': ['john@example.com'],
            'companies': ['Google'],
            'skills': ['Python']
        }
        
        score = pipeline.calculate_quality_score(entities)
        
        # Should be between 0-1
        assert 0 <= score <= 1
        # All entities = high score
        assert score == 1.0
    
    def test_fuzzy_match_dedup(self, pipeline):
        """Test fuzzy matching deduplication."""
        items = ['Google', 'google', 'GOOGLE', 'Microsoft']
        deduplicated = pipeline.fuzzy_match_dedup(items, threshold=0.85)
        
        # Should reduce duplicates
        assert len(deduplicated) < len(items)
        # Should keep at least Microsoft
        assert any('Microsoft' in d for d in deduplicated)
    
    def test_deduplicate_entities(self, pipeline):
        """Test entity deduplication."""
        entities = {
            'companies': ['Google', 'google', 'Microsoft'],
            'skills': ['Python', 'python', 'Java']
        }
        
        deduped = pipeline.deduplicate_entities(entities)
        
        # Should have fewer items
        assert len(deduped['companies']) < len(entities['companies'])
        assert len(deduped['skills']) < len(entities['skills'])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
    