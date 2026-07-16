"""
DataVault PDF Text Extractor
Extracts text from PDFs using pdfplumber

Purpose: Convert PDF files to machine-readable text
Author: You
Date: Today
"""

import os
import json
import pdfplumber
from pathlib import Path
from datetime import datetime

class PDFExtractor:
    """
    Extracts text from PDF files.
    """
    
    def __init__(self, input_folder="data/train", output_file="data/extracted_text.json"):
        """
        Initialize paths.
        
        Args:
            input_folder: Where PDFs are located
            output_file: Where to save extracted text
        """
        self.input_folder = input_folder
        self.output_file = output_file
        self.extracted_data = []
    
    def get_pdf_files(self):
        """
        Find all PDF files in input folder.
        
        Returns:
            List of PDF file paths
            
        Why this function?
        - Separates file-finding logic
        - Easier to test and debug
        - Handles errors gracefully
        """
        if not os.path.exists(self.input_folder):
            print(f"❌ Folder '{self.input_folder}' not found!")
            return []
        
        # Find all PDF files
        pdf_files = []
        for file in os.listdir(self.input_folder):
            if file.endswith('.pdf'):
                pdf_path = os.path.join(self.input_folder, file)
                pdf_files.append(pdf_path)
        
        print(f"✓ Found {len(pdf_files)} PDF files in {self.input_folder}")
        return sorted(pdf_files)
    
    def extract_text_from_pdf(self, pdf_path):
        """
        Extract text from a single PDF file.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with filename and extracted text
            
        Why this function?
        - Handles one PDF at a time
        - Easy to debug single files
        - Can track errors per file
        """
        try:
            filename = os.path.basename(pdf_path)
            print(f"\n📄 Processing: {filename}")
            
            all_text = ""
            page_count = 0
            
            # Open PDF with pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                page_count = len(pdf.pages)
                print(f"   Pages: {page_count}")
                
                # Extract text from each page
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        all_text += f"\n--- PAGE {page_num} ---\n{text}"
                    print(f"   ✓ Extracted page {page_num}/{page_count}")
            
            # Return structured data
            return {
                "filename": filename,
                "filepath": pdf_path,
                "pages": page_count,
                "text": all_text.strip(),
                "extraction_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "text_length": len(all_text)
            }
        
        except Exception as e:
            # Handle errors gracefully
            print(f"   ❌ Error processing {filename}: {str(e)}")
            return {
                "filename": filename,
                "filepath": pdf_path,
                "error": str(e),
                "extraction_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def extract_all(self):
        """
        Extract text from all PDFs.
        
        Workflow:
        1. Get list of PDFs
        2. Process each one
        3. Store results
        4. Return success/failure
        """
        pdf_files = self.get_pdf_files()
        
        if not pdf_files:
            print("❌ No PDFs found to extract!")
            return False
        
        print(f"\n🔄 Extracting text from {len(pdf_files)} PDFs...")
        print("="*60)
        
        # Process each PDF
        for pdf_path in pdf_files:
            result = self.extract_text_from_pdf(pdf_path)
            self.extracted_data.append(result)
        
        print("\n" + "="*60)
        print(f"✅ Extracted {len(self.extracted_data)} PDFs!")
        return True
    
    def save_to_json(self):
        """
        Save extracted text to JSON file.
        
        Why JSON?
        - Easy to read and parse
        - Works with Python, JavaScript, etc.
        - Human-readable format
        - Standard for data storage
        """
        if not self.extracted_data:
            print("❌ No data to save!")
            return False
        
        # Create output directory if needed
        output_dir = os.path.dirname(self.output_file)
        if output_dir and not os.path.exists(output_dir):
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Save to JSON
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.extracted_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Saved to: {self.output_file}")
        
        # Print summary
        print(f"\n📊 Summary:")
        print(f"   Total files: {len(self.extracted_data)}")
        
        total_text = 0
        for item in self.extracted_data:
            if 'text' in item:
                total_text += item['text_length']
        
        print(f"   Total text: {total_text} characters")
        print(f"   Average per file: {total_text // len(self.extracted_data)} characters")
        
        return True
    
    def print_preview(self, max_chars=200):
        """
        Print preview of extracted text.
        
        Args:
            max_chars: Maximum characters to show per file
        """
        print(f"\n📋 Preview (first {max_chars} chars per file):")
        print("="*60)
        
        for item in self.extracted_data:
            if 'error' not in item:
                print(f"\n📄 {item['filename']}:")
                print(f"   Pages: {item['pages']}")
                print(f"   Text preview:")
                preview = item['text'][:max_chars].replace('\n', ' ')
                print(f"   {preview}...")
    
    def run(self):
        """
        Execute complete extraction pipeline.
        
        Workflow:
        1. Extract all PDFs
        2. Save to JSON
        3. Print preview
        """
        print("="*60)
        print("DataVault PDF Text Extractor")
        print("="*60)
        
        if self.extract_all():
            self.save_to_json()
            self.print_preview()
            print("\n" + "="*60)
            print("✅ SUCCESS! Text extraction complete!")
            print("="*60)
            return True
        else:
            print("\n❌ Extraction failed!")
            return False


if __name__ == "__main__":
    # Create extractor for training data
    extractor = PDFExtractor(
        input_folder="data/train",
        output_file="data/extracted_text.json"
    )
    
    # Run extraction
    extractor.run()
