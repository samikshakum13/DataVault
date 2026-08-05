"""
Resume Parser using pyresparser library
Better extraction for resumes
"""

from pyresparser import ResumeParser
import json


class ResumeParserWrapper:
    """Wrapper around pyresparser for consistent interface."""

    def __init__(self):
        """Initialize parser."""
        self.parser = ResumeParser()
        print("✓ Resume Parser initialized")

    def extract_from_pdf(self, pdf_path):
        """Extract resume data from PDF."""
        try:
            # Parse resume
            data = self.parser.get_extracted_data(pdf_path)

            # Format results
            result = {
                "names": [data.get("name", "")] if data.get("name") else [],
                "emails": [data.get("email", "")] if data.get("email") else [],
                "phones": (
                    [data.get("mobile_number", "")] if data.get("mobile_number") else []
                ),
                "companies": (
                    data.get("companies_names", [])
                    if data.get("companies_names")
                    else []
                ),
                "locations": data.get("cities", []) if data.get("cities") else [],
                "skills": data.get("skills", []) if data.get("skills") else [],
                "years": data.get("experience", []) if data.get("experience") else [],
                "education": data.get("degree", []) if data.get("degree") else [],
            }

            # Clean empty strings
            for key in result:
                result[key] = [
                    item for item in result[key] if item and str(item).strip()
                ]

            return result

        except Exception as e:
            print(f"Error parsing resume: {e}")
            return {
                "names": [],
                "emails": [],
                "phones": [],
                "companies": [],
                "locations": [],
                "skills": [],
                "years": [],
                "education": [],
            }
