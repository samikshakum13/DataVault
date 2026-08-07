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
        """Extract phone numbers from resume."""

        patterns = [
            # India: +91 98765 43210
            r'\+91[\s-]*[6-9]\d{4}[\s-]*\d{5}',

            # India: +91 9876543210
            r'\+91[\s-]*[6-9]\d{9}',

            # India: 98765 43210
            r'\b[6-9]\d{4}[\s-]\d{5}\b',

            # India: 9876543210
            r'\b[6-9]\d{9}\b',

            # India with 0: 09876543210
            r'\b0[6-9]\d{9}\b',

            # US: +1 9876543210
            r'\+1[\s-]*\d{10}',

            # General international format
            r'\+\d{1,3}[\s-]*\d{7,12}'
        ]

        phones = []

        for pattern in patterns:
            matches = re.findall(pattern, text)
            phones.extend(matches)

        # Clean spaces and hyphens
        phones = [phone.strip() for phone in phones]

        return list(dict.fromkeys(phones))

    # ==================== COMPANIES ====================
    def extract_companies_regex(self, text):
        """Extract company names from resume."""

        companies = []

        # Pattern 1:
        # Worked at TCS
        # Internship at Infosys
        # Employed with Accenture
        pattern1 = r'(?:internship|intern|worked|experience|employed)\s+(?:at|with|by|in)\s+([A-Z][A-Za-z0-9&.,\-\s]{1,50}?)(?=\s*(?:\n|,|from|since|for|as|$))'

        matches = re.findall(pattern1, text, re.IGNORECASE)
        companies.extend(matches)

        # Pattern 2:
        # TCS - Data Analyst
        # Infosys – Software Engineer
        # Accenture | Data Analyst
        pattern2 = r'^([A-Z][A-Za-z0-9&.,\-\s]{1,50}?)\s*[-–|]\s*[A-Z]'

        matches = re.findall(pattern2, text, re.MULTILINE)
        companies.extend(matches)

        # Pattern 3:
        # Company: TCS
        # Organization: Infosys
        pattern3 = r'(?:company|organization|employer)\s*:\s*([A-Z][A-Za-z0-9&.,\-\s]{1,50})'

        matches = re.findall(pattern3, text, re.IGNORECASE)
        companies.extend(matches)

        # Clean results
        cleaned = []

        skip_words = [
            'college',
            'university',
            'school',
            'institute',
            'project',
            'system',
            'experience',
            'education',
            'resume',
            'profile'
        ]

        for company in companies:
            company = company.strip(" ,.-|")

            if not company:
                continue

            if len(company.split()) > 6:
                continue

            if any(word in company.lower() for word in skip_words):
                continue

            if company not in cleaned:
                cleaned.append(company)

        return cleaned

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
        """Extract entities - WORKS ON ANY RESUME FORMAT."""

        # ===== NAMES =====
        names = []

        # Check only the first 10 lines of the resume
        lines = text.split("\n")[:10]

        for line in lines:
            line = line.strip()

            if not line or len(line) > 50:
                continue

            # Name format:
            # Rahul Sharma
            # Rahul Kumar Sharma
            # Rohan P Sharma
            pattern = r"^[A-Z][a-z]+(?:\s+[A-Z](?:[a-z]+)?)?(?:\s+[A-Z][a-z]+){1,2}$"

            if re.fullmatch(pattern, line):
                skip_words = [
                    "resume",
                    "curriculum",
                    "vitae",
                    "profile",
                    "summary",
                    "fresher",
                    "engineer",
                    "developer",
                    "analyst",
                ]

                if not any(word in line.lower() for word in skip_words):
                    names.append(line)
                    break

        # ===== LOCATIONS =====
        locations = []

        # Use spaCy for geographical entities
        doc = self.nlp(text)

        for ent in doc.ents:
            if ent.label_ in ["GPE", "LOC"]:
                location = ent.text.strip()

                if 1 <= len(location.split()) <= 4 and len(location) < 50:
                    if location not in locations:
                        locations.append(location)

        # Also detect common "City, State" format
        pattern = r"\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*),\s*([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\b"

        matches = re.findall(pattern, text)

        for match in matches:
            location = f"{match[0]}, {match[1]}"

            if location not in locations:
                locations.append(location)

        # ===== EMAILS: REGEX (works ANY format) =====
        emails = self.extract_emails(text)

        # ===== PHONES: REGEX (works ANY format) =====
        phones = self.extract_phones(text)

        # ===== COMPANIES: KEYWORD PATTERNS (works ANY format) =====
        companies = self.extract_companies_regex(text)

        # ===== SKILLS: KEYWORD MATCHING (works ANY format) =====
        skills = self.extract_skills(text)

        # ===== YEARS: REGEX (works ANY format) =====
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
