"""
DataVault Text Cleaning Module
Cleans extracted text for NLP processing

Purpose: Normalize text (remove noise, whitespace, special chars)
"""

import re
import string

class TextCleaner:
    """
    Cleans raw text extracted from PDFs.
    
    Why?
    - PDFs have extra whitespace, newlines, special chars
    - NLP models work better with clean text
    - Improves accuracy of entity extraction
    """
    
    def __init__(self):
        pass
    
    def remove_extra_whitespace(self, text):
        """
        Remove extra spaces, tabs, newlines.
        
        Example:
            Input:  "JOHN    DOE\n\n\nemail@example.com"
            Output: "JOHN DOE email@example.com"
        """
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def remove_special_chars(self, text):
        """
        Remove unnecessary special characters.
        
        Keep: letters, numbers, @, -, (), spaces
        Remove: other symbols
        
        Example:
            Input:  "JOHN***DOE|||Email"
            Output: "JOHNDOE Email"
        """
        # Keep alphanumeric, @, -, (), spaces, periods, commas
        text = re.sub(r'[^a-zA-Z0-9@\-().,\s]', '', text)
        return text
    
    def normalize_text(self, text):
        """
        Convert to standard format.
        
        Example:
            Input:  "john DOE"
            Output: "John Doe" (title case)
        """
        # Convert to title case (proper noun format)
        text = text.title()
        return text
    
    def clean(self, text):
        """
        Main cleaning pipeline.
        
        Steps:
        1. Remove extra whitespace
        2. Remove special chars
        3. Normalize formatting
        """
        print("🧹 Cleaning text...")
        
        # Step 1: Remove extra whitespace
        text = self.remove_extra_whitespace(text)
        print("   ✓ Removed extra whitespace")
        
        # Step 2: Remove special chars
        text = self.remove_special_chars(text)
        print("   ✓ Removed special characters")
        
        # Step 3: Normalize
        text = self.normalize_text(text)
        print("   ✓ Normalized text")
        
        return text


if __name__ == "__main__":
    # Test the cleaner
    test_text = """
    JOHN    DOE
    
    
    john@example.com | +1-555-123-4567
    
    San Francisco, CA
    """
    
    cleaner = TextCleaner()
    cleaned = cleaner.clean(test_text)
    
    print("\n📊 Result:")
    print(cleaned)