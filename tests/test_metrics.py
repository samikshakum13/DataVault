"""
Calculate accuracy metrics for the extraction system

Computes: Precision, Recall, F1 Score
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
import pytest
from pipeline import DataPipeline


class TestMetrics:
    """Calculate and test extraction accuracy metrics."""
    
    @pytest.fixture
    def pipeline(self):
        """Initialize pipeline."""
        return DataPipeline()
    
    def test_calculate_metrics(self, pipeline):
        """
        Calculate precision, recall, F1 for resume extraction.
        
        Ground truth: Manually verified data
        Predictions: What system extracted
        """
        
        # Example: Manually verified resume data (ground truth)
        ground_truth = {
            'resume_1.pdf': {
                'emails': ['john@example.com'],
                'phones': ['+1-555-123-4567'],
                'names': ['John Doe'],
                'companies': ['Google', 'Microsoft'],
                'skills': ['Python', 'Machine Learning', 'TensorFlow']
            }
        }
        
        # Simulate system predictions
        predictions = {
            'resume_1.pdf': {
                'emails': ['john@example.com'],
                'phones': ['+1-555-123-4567'],
                'names': ['John Doe'],
                'companies': ['Google', 'Microsoft'],
                'skills': ['Python', 'Machine Learning', 'TensorFlow']
            }
        }
        
        # Calculate metrics
        metrics = self.calculate_metrics(ground_truth, predictions)
        
        # Perfect match should give 100% precision/recall
        assert metrics['precision'] == 1.0
        assert metrics['recall'] == 1.0
        assert metrics['f1_score'] == 1.0
    
    @staticmethod
    def calculate_metrics(ground_truth, predictions):
        """
        Calculate precision, recall, F1 score.
        
        Precision = TP / (TP + FP)  - How many we got RIGHT
        Recall = TP / (TP + FN)     - How many we FOUND
        F1 = 2 * (P * R) / (P + R)  - Balanced score
        """
        
        total_tp = 0  # True positives
        total_fp = 0  # False positives
        total_fn = 0  # False negatives
        
        for filename in ground_truth:
            truth_entities = ground_truth[filename]
            pred_entities = predictions.get(filename, {})
            
            # Check each entity type
            for entity_type in truth_entities:
                truth_set = set(truth_entities[entity_type])
                pred_set = set(pred_entities.get(entity_type, []))
                
                # Count matches
                tp = len(truth_set & pred_set)  # Intersection
                fp = len(pred_set - truth_set)  # False positives
                fn = len(truth_set - pred_set)  # False negatives
                
                total_tp += tp
                total_fp += fp
                total_fn += fn
        
        # Calculate metrics
        precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
        recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'true_positives': total_tp,
            'false_positives': total_fp,
            'false_negatives': total_fn
        }


if __name__ == "__main__":
    pytest.main([__file__, "-v"])