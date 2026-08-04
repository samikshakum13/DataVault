"""
DataVault NER (Named Entity Recognition) Module
Extracts entities from resume text using spaCy

Purpose: Extract names, companies, dates, locations
"""

import spacy
import re
from datetime import datetime

class ResumeNER:
    """
    Extract named entities from resume text using spaCy.
    
    Why spaCy?
    - State-of-the-art NER (Named Entity Recognition)
    - Fast & accurate
    - Pre-trained models available
    - Industry standard
    """
    
    def __init__(self):
        """Load spaCy model."""
        print("🧠 Loading spaCy model...")
        try:
            self.nlp = spacy.load("en_core_web_sm")
            print("   ✓ Model loaded successfully")
        except:
            print("   ❌ Model not found. Installing...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")
    
    def extract_emails(self, text):
        """
        Extract email addresses using regex.
        
        Pattern: word@domain.extension
        
        Example:
            Input: "Contact: john@example.com"
            Output: ["john@example.com"]
        """
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(pattern, text)
        return emails
    
    def extract_phones(self, text):
        """
        Extract phone numbers using regex.
        
        Patterns:
        - +1-555-123-4567
        - (555) 123-4567
        - 555-123-4567
        - 5551234567
        """
        patterns = [
            r'\+\d{1,3}[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',  # +1-555-123-4567
            r'\(\d{3}\)\s?\d{3}[-.\s]?\d{4}',  # (555) 123-4567
            r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}'   # 555-123-4567
        ]
        
        phones = []
        for pattern in patterns:
            phones.extend(re.findall(pattern, text))
        
        return list(set(phones))  # Remove duplicates
    
    def extract_entities_spacy(self, text):
        """Extract organizations using spaCy NER with better filtering."""
        doc = self.nlp(text)
        
        # Get raw ORG entities
        raw_orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
        
        # Filter out common non-company terms
        exclude_keywords = [
            'college', 'university', 'school', 'institute',
            'tensorflow', 'scikit', 'python', 'sql', 'framework',
            'library', 'tool', 'workshop', 'course', 'program',
            'system', 'platform', 'application', 'project'
        ]
        
        # Filter companies
        filtered_orgs = [
            org for org in raw_orgs 
            if not any(keyword.lower() in org.lower() for keyword in exclude_keywords)
        ]
        
        return filtered_orgs


def extract_companies_keyword(self, text):
    """Extract companies using keyword matching (internship, worked at, etc.)"""
    import re
    
    companies = []
    
    # Pattern: "internship at Company" or "worked at Company"
    patterns = [
        r'internship\s+(?:at|with|in)\s+([A-Z][a-zA-Z\s&]+?)(?:\.|,|$)',
        r'worked\s+(?:at|with|in)\s+([A-Z][a-zA-Z\s&]+?)(?:\.|,|$)',
        r'experience\s+(?:at|with|in)\s+([A-Z][a-zA-Z\s&]+?)(?:\.|,|$)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        companies.extend(matches)
    
    return [c.strip() for c in companies if c.strip()]
    
    def extract_years(self, text):
        """
        Extract years (for experience dates).
        
        Pattern: 4-digit numbers between 1950-2050
        """
        pattern = r'\b(19|20)\d{2}\b'
        years = re.findall(pattern, text)
        return sorted(list(set(years)))
    
    def extract_skills(self, text):
        """
        Extract skills (common tech keywords).
        
        This is simplified - matches common keywords.
        """
        common_skills = [
            "Python", "Java", "JavaScript", "C++", "C#", "Go", "Rust",
            "Machine Learning", "ML", "Deep Learning", "TensorFlow", "PyTorch",
            "Data Science", "AI", "Artificial Intelligence",
            "SQL", "NoSQL", "MongoDB", "PostgreSQL", "MySQL",
            "FastAPI", "Flask", "Django", "React", "Angular", "Vue",
            "AWS", "Azure", "GCP", "Docker", "Kubernetes",
            "Git", "GitHub", "Linux", "DevOps",
            "Pandas", "NumPy", "Scikit-learn", "SpaCy"
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in common_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def extract_all(self, text):
        """Extract all entities from resume."""
        
        entities = {
            'names': self.extract_emails(text),  # existing
            'emails': self.extract_emails(text),  # existing
            'phones': self.extract_phones(text),  # existing
            'companies': self.extract_companies_keyword(text),  # NEW: Use keyword-based
            'locations': [ent.text for ent in self.nlp(text).ents if ent.label_ == "GPE"],
            'skills': self.extract_skills(text),  # existing
            'years': self.extract_years(text)  # existing
        }
        
        return entities


if __name__ == "__main__":
    # Test the NER
    test_text = """
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
    
    ner = ResumeNER()
    entities = ner.extract_all(test_text)
    
    print("\n📊 Extracted Entities:")
    for key, value in entities.items():
        print(f"  {key}: {value}")