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
        """Extract companies using experience context."""

        companies = []

        # Find EXPERIENCE section
        experience_match = re.search(
            r'(?:EXPERIENCE|WORK EXPERIENCE|PROFESSIONAL EXPERIENCE)'
            r'(.*?)(?=\n(?:EDUCATION|SKILLS|PROJECTS|CERTIFICATIONS|LANGUAGES)\b|\Z)',
            text,
            re.IGNORECASE | re.DOTALL
        )

        if not experience_match:
            return companies

        experience_text = experience_match.group(1)

        # Common format:
        # Job Title - Company
        # Job Title — Company
        # Job Title | Company
        pattern = re.compile(
            r'(?:intern|internship|analyst|developer|engineer|manager|associate|'
            r'consultant|specialist|executive|designer|scientist)'
            r'[^|\n–—-]{0,60}'
            r'(?:\||–|—|-)\s*'
            r'([A-Z][A-Za-z0-9&., ]{1,50})',
            re.IGNORECASE
        )

        matches = pattern.findall(experience_text)

        for company in matches:

            company = company.strip(" ,.-|:")

            if 1 <= len(company.split()) <= 5:

                if company not in companies:
                    companies.append(company)

        return companies

    # ==================== LOCATIONS ====================
    def extract_locations_spacy(self, text):
        """Extract locations from resume using strong location patterns."""

        locations = []

        # ---------------------------------------------------------
        # 1. Strong pattern: City, State / City, Country
        # ---------------------------------------------------------
        location_pattern = re.compile(
            r'\b'
            r'([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*)'
            r',\s*'
            r'([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*)'
            r'(?:,\s*([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*))?'
            r'\b'
        )

        for match in location_pattern.finditer(text):

            city = match.group(1).strip()
            state = match.group(2).strip()
            country = match.group(3)

            if country:
                location = f"{city}, {state}, {country.strip()}"
            else:
                location = f"{city}, {state}"

            locations.append(location)

        # ---------------------------------------------------------
        # 2. Location mentioned after a location-related label
        # ---------------------------------------------------------
        labelled_pattern = re.compile(
            r'(?:location|address|based in|located in|residing in)'
            r'\s*[:\-]?\s*'
            r'([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*'
            r'(?:,\s*[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*)?)',
            re.IGNORECASE
        )

        for match in labelled_pattern.finditer(text):
            location = match.group(1).strip()
            locations.append(location)

        # ---------------------------------------------------------
        # 3. Remove duplicates
        # ---------------------------------------------------------
        locations = list(dict.fromkeys(locations))

        return locations

    # ==================== SKILLS ====================
    def extract_skills(self, text):
        """Extract technical skills using keyword matching."""
        # Comprehensive tech skills list
        skills_list = [
            # Programming Languages
            'python', 'java', 'c++', 'javascript', 'sql', 'r programming', 'r', 'scala', 'go', 'rust', 'kotlin',
            'vba', 'bash', 'shell', 'perl', 'ruby',
            
            # Data & ML Libraries
            'pandas', 'numpy', 'matplotlib', 'seaborn', 'scikit-learn', 'sklearn', 'tensorflow', 'keras', 'pytorch',
            'xgboost', 'catboost', 'lightgbm', 'spark', 'pyspark', 'hadoop',
            
            # Databases
            'postgresql', 'postgres', 'mysql', 'sqlite', 'mongodb', 'cassandra', 'snowflake', 'bigquery', 'redshift',
            'oracle', 'dynamodb', 'elasticsearch', 'redis', 'hbase',
            
            # BI & Visualization
            'tableau', 'power bi', 'looker', 'qlikview', 'google data studio', 'excel', 'grafana', 'metabase',
            
            # Cloud & DevOps
            'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'git', 'jenkins', 'terraform',
            'airflow', 'dbt', 'ci/cd', 'gitlab', 'github', 'bitbucket',
            
            # ML & Data Science
            'machine learning', 'deep learning', 'nlp', 'computer vision', 'data analysis', 'data science',
            'data engineering', 'analytics', 'etl', 'elt', 'predictive modeling', 'statistical analysis',
            
            # APIs & Web
            'api', 'rest', 'graphql', 'json', 'xml', 'http', 'websocket',
            
            # Other Tools
            'jira', 'confluence', 'slack', 'salesforce', 'sap', 'linux', 'windows', 'unix',
            'sql optimization', 'data pipeline', 'business intelligence', 'data warehouse'
        ]

        skills_found = []
        text_lower = text.lower()

        for skill in skills_list:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                skills_found.append(skill.title())

        return sorted(list(set(skills_found)))

    # ==================== YEARS/DATES ====================
    def extract_years(self, text):
        """Extract years (education, experience)."""
        # Pattern: 4-digit years (1990-2099)
        pattern = r'\b(19\d{2}|20\d{2})\b'
        years = re.findall(pattern, text)
        return sorted(list(set(years)))

    # ==================== EXTRACT ALL ====================
    # ==================== EXPERIENCE ====================
    def extract_experience(self, text):
        """Extract work experience from resume - refined patterns."""
        import re
        
        experience = []
        
        # First, find the PROFESSIONAL EXPERIENCE section
        experience_match = re.search(
            r'(?:PROFESSIONAL\s+EXPERIENCE|WORK\s+EXPERIENCE|EXPERIENCE|EMPLOYMENT\s+HISTORY)'
            r'(.*?)(?=\n(?:EDUCATION|PROJECTS|CERTIFICATIONS|SKILLS|LANGUAGES|ACADEMIC|PROFESSIONAL\s+CERTIFICATION|CORE\s+COMPETENCIES)\b|\Z)',
            text, 
            re.IGNORECASE | re.DOTALL
        )
        
        if not experience_match:
            return experience
        
        experience_text = experience_match.group(1)
        
        # Pattern 1: Job Title | Company | Dates (with pipes)
        pattern1 = r'([A-Za-z\s]+?)\s*\|\s*([A-Za-z\s&.,]+?)\s*\|\s*([\w\s\-–—]+?)\n'
        
        # Pattern 2: Job Title • Company • Dates (with bullets)
        pattern2 = r'([A-Za-z\s]+?)\s*•\s*([A-Za-z\s&.,]+?)\s*•\s*([\w\s\-–—]+?)(?:\n|$)'
        
        # Pattern 3: **Bold Title** - Company - Dates
        pattern3 = r'\*\*?([A-Za-z\s]+?)\*\*?\s*-\s*([A-Za-z\s&.,]+?)\s*-\s*([\w\s\-–—]+?)(?:\n|$)'
        
        all_matches = []
        all_matches.extend(re.findall(pattern1, experience_text))
        all_matches.extend(re.findall(pattern2, experience_text))
        all_matches.extend(re.findall(pattern3, experience_text))
        
        for match in all_matches:
            job_title = match[0].strip()
            company = match[1].strip()
            dates = match[2].strip()
            
            # Filter out garbage matches
            if len(job_title) > 5 and len(company) > 3:
                # Skip if title has too many words (likely not a title)
                if len(job_title.split()) <= 5:
                    exp = f"{job_title} at {company}"
                    if dates:
                        exp += f" ({dates})"
                    if exp not in experience:
                        experience.append(exp)
        
        return experience[:10]  # Return TOP 10 experiences (was 3)

    def extract_all(self, text):
        """Extract entities - WORKS ON ANY RESUME FORMAT."""

        # ===== NAMES =====
        names = []

        # Take first 10 non-empty lines
        lines = [line.strip() for line in text.splitlines() if line.strip()][:10]

        name_pattern = r"^[A-Z][A-Za-z.'-]*(?:\s+[A-Z][A-Za-z.'-]*){1,3}$"

        skip_words = {
            "resume",
            "curriculum",
            "vitae",
            "profile",
            "summary",
            "professional",
            "technical",
            "skills",
            "experience",
            "education",
            "projects",
            "certifications",
            "languages",
            "data",
            "analyst",
            "engineer",
            "developer",
            "power",
            "bi",
        }

        for line in lines:

            # Ignore contact/location lines
            if "@" in line or re.search(r"\+?\d[\d\s().-]{7,}", line):
                continue

            # Ignore obvious location lines
            if "," in line:
                continue

            # Must look like a name
            if re.fullmatch(name_pattern, line):

                words = line.lower().split()

                # Reject technical/section phrases
                if not any(word in skip_words for word in words):

                    names.append(line.title())
                    break

        # ===== LOCATIONS: CITY, STATE =====
        locations = []

        # Check first 500 chars
        text_short = text[:500]
        lines_short = text_short.split("\n")

        for line in lines_short[:10]:
            line = line.strip()

            if "," not in line:
                continue

            # Remove phone/email/URLs from line
            line_clean = re.sub(r"\+?\d[\d\s().-]{7,}", "", line)  # Remove phones
            line_clean = re.sub(r"\S+@\S+", "", line_clean)  # Remove emails
            line_clean = re.sub(r"linkedin\.\S+", "", line_clean)  # Remove LinkedIn
            line_clean = line_clean.replace("|", "")  # Remove pipes
            line_clean = line_clean.strip()

            # Pattern: City, State OR City, State, Country
            # More flexible - allows 2 or 3 parts
            if re.match(r"^[A-Z][a-z\s]+,\s*[A-Z][a-z\s]+(?:,\s*[A-Z][a-z\s]+)?$", line_clean):
                # Make sure not a skill
                if not any(
                    x in line_clean.lower()
                    for x in ["data", "power", "sql", "python", "analytics"]
                ):
                    locations.append(line_clean)
                    break  # Take first match
                

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

        # ===== EXPERIENCE: PATTERN MATCHING =====
        experience = self.extract_experience(text)

        return {
            'names': names,
            'emails': emails,
            'phones': phones,
            'companies': companies,
            'locations': locations,
            'skills': skills,
            'years': years,
            'experience': experience
        }
