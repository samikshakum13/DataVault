"""
Resume Processing Pipeline
Combines cleaning + NER
"""

from clean import TextCleaner
from ner import ResumeNER
import json

class ResumeProcessor:
    def __init__(self):
        self.cleaner = TextCleaner()
        self.ner = ResumeNER()
    
    def process(self, raw_text):
        print("="*60)
        print("Resume Processing Pipeline")
        print("="*60)
        
        cleaned_text = self.cleaner.clean(raw_text)
        entities = self.ner.extract_all(cleaned_text)
        
        result = {
            "raw_text": raw_text[:200] + "...",
            "cleaned_text": cleaned_text[:200] + "...",
            "entities": entities
        }
        
        return result


if __name__ == "__main__":
    test_resume = """
    JOHN DOE
    john@example.com | +1-555-123-4567
    San Francisco, CA
    
    EXPERIENCE
    ML Engineer at Google (2020-2023)
    - Built ML systems in Python
    - Used TensorFlow and PyTorch
    
    Senior Developer at Microsoft (2018-2020)
    - Developed cloud solutions on Azure
    
    SKILLS
    Python, Machine Learning, FastAPI, Docker, AWS
    
    EDUCATION
    B.Tech Computer Science, 2018
    IIT Bombay, India
    """
    
    processor = ResumeProcessor()
    result = processor.process(test_resume)
    
    print("\n" + "="*60)
    print("RESULT")
    print("="*60)
    print(json.dumps(result["entities"], indent=2))
    