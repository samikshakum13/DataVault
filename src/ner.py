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

    def extract_names_regex(self, text):
        """Extract names using regex patterns (names typically capitalized)."""
        import re

        # Pattern: Capitalized words at start of lines or after newlines
        # Typical resume format: Name at top
        names = []

        # Look for 2-3 capitalized words (typical name format)
        pattern = r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})(?:\n|$)'
        matches = re.findall(pattern, text, re.MULTILINE)
        names.extend(matches)

        # Also look for "Name:" or "Name :" patterns
        pattern2 = r'(?:name|candidate|applicant)\s*[:=]\s*([A-Z][a-zA-Z\s]+?)(?:\n|,|$)'
        matches2 = re.findall(pattern2, text, re.IGNORECASE)
        names.extend([m.strip() for m in matches2])

        return list(set(names))  # Remove duplicates

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

    def extract_locations_regex(self, text):
        """Extract locations using spaCy + filtering."""
        import re

        locations = []

        # Get spaCy GPE entities
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ == "GPE":
                locations.append(ent.text)

        # Also look for common location patterns
        pattern = r'(?:based|located|from|in)\s+([A-Z][a-zA-Z\s]+?)(?:,|$)'
        matches = re.findall(pattern, text)
        locations.extend(matches)

        # Filter: Only keep short ones (1-3 words)
        filtered = [
            l.strip() for l in locations 
            if 1 <= len(l.split()) <= 3 and len(l) < 30
        ]

        return list(set(filtered))

    def extract_companies_regex(self, text):
        """Extract company names using keyword patterns."""
        import re

        companies = []

        # Patterns for internship/work experience
        patterns = [
            r'(?:intern|worked|experience)\s+(?:at|with|in)\s+([A-Z][a-zA-Z\s&.,-]+?)(?:\n|,|$)',
            r'(?:company|organization|employer)\s*[:=]\s*([A-Z][a-zA-Z\s&.,-]+?)(?:\n|,|$)',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            companies.extend([m.strip() for m in matches])

        # Filter: Only keep if 2-4 words and < 40 chars
        filtered = [
            c for c in companies 
            if 1 <= len(c.split()) <= 4 and len(c) < 40
        ]

        return list(set(filtered))

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
        """Extract all entities from resume using spaCy."""
        doc = self.nlp(text)

        exclude_words = {
            "matplotlib",
            "power bi",
            "numpy",
            "pandas",
            "python",
            "sql",
            "excel",
            "java",
            "c++",
            "javascript",
            "react",
            "node",
            "fresher",
            "motivated",
            "quick learner",
            "team player",
            "analytical",
            "thinking",
            "knowledge",
            "professional",
            "summary",
            "skills",
            "experience",
            "education",
        }

        # Extract entities by type
        names = []
        locations = []
        companies = []

        for ent in doc.ents:
            if ent.label_ == "PERSON":
                if ent.text.lower() not in exclude_words and len(ent.text.split()) <= 3:
                    names.append(ent.text)
            elif ent.label_ == "GPE":  # Geo-Political Entity (places)
                locations.append(ent.text)
            elif ent.label_ == "ORG":  # Organizations
                companies.append(ent.text)

        # Get other entities
        emails = self.extract_emails(text)
        phones = self.extract_phones(text)
        skills = self.extract_skills(text)
        years = self.extract_years(text)

        return {
            'names': list(set(names)),  # Remove duplicates
            'emails': list(set(emails)),
            'phones': list(set(phones)),
            'companies': list(set(companies)),
            'locations': list(set(locations)),
            'skills': list(set(skills)),
            'years': list(set(years))
        }


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
