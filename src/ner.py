"""
Resume NER - Hybrid approach (Regex + spaCy)
Better accuracy for names, emails, phones, companies
"""

import spacy
import re
from pathlib import Path

class ResumeNER:
    """Named Entity Recognition for resumes - Hybrid approach."""
    
    def __init__(self):
        """Initialize spaCy model."""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            print("Downloading spaCy model...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")
    
    # ==================== NAMES ====================
    def extract_names_regex(self, text):
        """Extract names from first 5 lines (where resumes put names)."""
        names = []
        lines = text.split('\n')[:5]
        
        for line in lines:
            line = line.strip()
            if not line or len(line) > 80:  # Skip long lines (those aren't names)
                continue
            
            # Pattern: 2-3 capitalized words (typical name format)
            # Example: "Rahul Verma" or "John Smith Jr"
            pattern = r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})$'
            match = re.match(pattern, line)
            
            if match:
                name = match.group(1)
                # Skip common resume keywords
                skip_words = ['resume', 'cv', 'profile', 'data', 'analyst', 'engineer']
                if not any(skip in name.lower() for skip in skip_words):
                    names.append(name)
                    break  # Take first match
        
        return names
    
    # ==================== EMAILS ====================
    def extract_emails(self, text):
        """Extract emails using regex (99% accurate)."""
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        return re.findall(pattern, text)
    
    # ==================== PHONES ====================
    def extract_phones(self, text):
        """Extract phone numbers using regex."""
        patterns = [
            r'\+91[6-9]\d{9}',  # India: +91 XXXXXXXXXX
            r'0[6-9]\d{9}',      # India: 0XXXXXXXXXX
            r'\+1\d{10}',        # US: +1 XXXXXXXXXX
            r'\(\d{3}\)\s*\d{3}-\d{4}',  # US: (XXX) XXX-XXXX
            r'\d{10}',           # 10 digit number
        ]
        
        phones = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            phones.extend(matches)
        
        return list(set(phones))  # Remove duplicates
    
    # ==================== COMPANIES ====================
    def extract_companies_regex(self, text):
        """Extract companies using keyword patterns."""
        companies = []
        
        # Pattern 1: "internship at Company" or "worked at Company"
        pattern1 = r'(?:intern|worked|experience|employed)\s+(?:at|with|in)\s+([A-Z][a-zA-Z\s&.,-]+?)(?:\n|,|from|since|$)'
        matches1 = re.findall(pattern1, text, re.IGNORECASE)
        companies.extend([m.strip() for m in matches1])
        
        # Pattern 2: "Company Name - Job Title"
        pattern2 = r'^([A-Z][a-zA-Z\s&.,-]+?)\s*[-–]\s*[A-Z]'
        matches2 = re.findall(pattern2, text, re.MULTILINE)
        companies.extend([m.strip() for m in matches2])
        
        # Filter and clean
        filtered = []
        for company in companies:
            company = company.strip()
            # Skip if too long or contains jargon
            if (2 <= len(company.split()) <= 4 and 
                len(company) < 50 and
                not any(skip in company.lower() for skip in 
                    ['college', 'university', 'school', 'institute', 'project', 'system'])):
                filtered.append(company)
        
        return list(set(filtered))
    
    # ==================== LOCATIONS ====================
    def extract_locations_spacy(self, text):
        """Extract locations using spaCy GPE."""
        doc = self.nlp(text)
        locations = []
        
        for ent in doc.ents:
            if ent.label_ == "GPE":  # Geo-Political Entity
                location = ent.text.strip()
                # Filter: Only cities/states/countries (short names)
                if 1 <= len(location.split()) <= 3 and len(location) < 40:
                    locations.append(location)
        
        return list(set(locations))
    
    # ==================== SKILLS ====================
    def extract_skills(self, text):
        """Extract technical skills using keyword matching."""
        # Common tech skills list
        skills_list = [
            'python', 'java', 'c++', 'javascript', 'sql', 'r programming',
            'pandas', 'numpy', 'matplotlib', 'seaborn', 'scikit-learn', 'tensorflow',
            'keras', 'pytorch', 'spark', 'hadoop', 'tableau', 'power bi', 'excel',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'git', 'linux',
            'machine learning', 'deep learning', 'nlp', 'computer vision',
            'data analysis', 'data science', 'data engineering', 'analytics',
            'postgresql', 'mongodb', 'mysql', 'sqlite', 'api', 'rest', 'graphql'
        ]
        
        skills_found = []
        text_lower = text.lower()
        
        for skill in skills_list:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                skills_found.append(skill.title())
        
        return list(set(skills_found))
    
    # ==================== YEARS/DATES ====================
    def extract_years(self, text):
        """Extract years (education, experience)."""
        # Pattern: 4-digit years (1990-2099)
        pattern = r'\b(19\d{2}|20\d{2})\b'
        years = re.findall(pattern, text)
        return sorted(list(set(years)))
    
    # ==================== EXTRACT ALL ====================
    def extract_all(self, text):
        """Extract all entities - OPTIMIZED FOR STANDARD RESUME FORMAT."""
        
        # ===== NAMES: FIRST NON-EMPTY LINE =====
        names = []
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        # First line is usually the name
        if lines:
            first_line = lines[0]
            # If it's 2-3 capitalized words (typical name)
            words = first_line.split()
            if 1 <= len(words) <= 4 and all(w[0].isupper() for w in words) and len(first_line) < 50:
                names.append(first_line)
        
        # ===== EMAILS: REGEX (99% ACCURATE) =====
        emails = self.extract_emails(text)
        
        # ===== PHONES: REGEX (95% ACCURATE) =====
        phones = self.extract_phones(text)
        
        # ===== LOCATIONS: LOOK FOR "City, State" PATTERN =====
        locations = []
        pattern = r'([A-Z][a-z]+),\s*([A-Z][a-z]+)'  # "Pune, Maharashtra"
        matches = re.findall(pattern, text[:500])  # Check first 500 chars
        for match in matches:
            location = f"{match[0]}, {match[1]}"
            if location not in locations:
                locations.append(location)
        
        # Also use spaCy
        locations.extend(self.extract_locations_spacy(text))
        locations = list(set(locations))  # Remove duplicates
        
        # ===== COMPANIES: KEYWORD PATTERNS =====
        companies = self.extract_companies_regex(text)
        
        # ===== SKILLS: KEYWORD MATCHING =====
        skills = self.extract_skills(text)
        
        # ===== YEARS: DATES =====
        years = self.extract_years(text)
        
        return {
            'names': names,
            'emails': emails,
            'phones': phones,
            'companies': companies,
            'locations': locations,
            'skills': skills,
            'years': years
        }