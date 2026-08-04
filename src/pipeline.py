"""
DataVault Full Pipeline
Process all PDFs: Extract → Clean → NER → Fuzzy Match

Purpose: End-to-end processing of all training data
"""

import json
import os
from pathlib import Path
from clean import TextCleaner
from ner import ResumeNER
from difflib import SequenceMatcher

class DataPipeline:
    """
    Complete pipeline for processing all PDFs.
    """
    
    def __init__(self, input_file="data/extracted_text.json", 
                 output_file="data/processed_resumes.json"):
        self.input_file = input_file
        self.output_file = output_file
        self.cleaner = TextCleaner()
        self.ner = ResumeNER()
        self.processed_data = []
    
    def load_extracted_text(self):
        """
        Load extracted text from Day 3.
        
        Returns:
            List of extracted resume data
        """
        print(f"\n📂 Loading extracted text from: {self.input_file}")
        
        if not os.path.exists(self.input_file):
            print(f"❌ File not found: {self.input_file}")
            return []
        
        with open(self.input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✓ Loaded {len(data)} documents")
        return data
    
    def process_single_resume(self, resume_data, index):
        """
        Process one resume: Clean + Extract.
        
        Args:
            resume_data: Dictionary with extracted text
            index: Document index
        """
        filename = resume_data.get('filename', f'resume_{index}')
        raw_text = resume_data.get('text', '')
        
        print(f"\n📄 Processing ({index + 1}): {filename}")
        
        try:
            # Step 1: Clean text
            cleaned_text = self.cleaner.clean(raw_text)
            
            # Step 2: Extract entities
            entities = self.ner.extract_all(cleaned_text)
            
            # Step 3: Create structured output
            result = {
                "filename": filename,
                "original_text": raw_text[:200] + "..." if len(raw_text) > 200 else raw_text,
                "cleaned_text": cleaned_text[:300] + "..." if len(cleaned_text) > 300 else cleaned_text,
                "entities": entities,
                "quality_score": self.calculate_quality_score(entities)
            }
            
            print(f"   ✓ Processed successfully (quality: {result['quality_score']:.1%})")
            return result
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return {
                "filename": filename,
                "error": str(e)
            }
    
    def calculate_quality_score(self, entities):
        """
        Calculate data quality score based on extractions.
        
        Logic:
        - Good if: has name + email + companies
        - Scale 0-1
        """
        score = 0.0
        
        # Check for key entities
        if entities.get('names'):
            score += 0.3
        if entities.get('emails'):
            score += 0.3
        if entities.get('companies'):
            score += 0.2
        if entities.get('skills'):
            score += 0.2
        
        return min(score, 1.0)
    
    def fuzzy_match_dedup(self, items, threshold=0.85):
        """
        Remove near-duplicates using fuzzy matching.
        
        Example:
            ["Google", "google"] → ["Google"]
            ["AWS", "Amazon Web Services"] → ["AWS"]
        
        Args:
            items: List of strings
            threshold: Similarity threshold (0-1)
        
        Returns:
            Deduplicated list
        """
        if not items:
            return []
        
        unique = []
        for item in items:
            # Check if similar item already exists
            is_duplicate = False
            for existing in unique:
                similarity = SequenceMatcher(None, item.lower(), existing.lower()).ratio()
                if similarity >= threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique.append(item)
        
        return unique
    
    def deduplicate_entities(self, entities):
        """
        Remove duplicate entities (e.g., "Google" and "google").
        """
        deduped = {}
        
        for key, values in entities.items():
            if isinstance(values, list):
                deduped[key] = self.fuzzy_match_dedup(values)
            else:
                deduped[key] = values
        
        return deduped
    
    def process_all(self):
        """
        Process all resumes in batch.
        """
        print("="*70)
        print("DataVault Full Processing Pipeline")
        print("="*70)
        
        # Load data
        extracted_data = self.load_extracted_text()
        
        if not extracted_data:
            return False
        
        # Process each resume
        for i, resume in enumerate(extracted_data):
            result = self.process_single_resume(resume, i)
            
            # Deduplicate entities
            if 'entities' in result:
                result['entities'] = self.deduplicate_entities(result['entities'])
            
            self.processed_data.append(result)
        
        print("\n" + "="*70)
        print(f"✅ Processed {len(self.processed_data)} resumes!")
        print("="*70)
        
        return True
    
    def save_results(self):
        """
        Save processed data to JSON.
        """
        if not self.processed_data:
            print("❌ No data to save")
            return False
        
        # Create output directory if needed
        output_dir = os.path.dirname(self.output_file)
        if output_dir and not os.path.exists(output_dir):
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Save to JSON
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.processed_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Results saved to: {self.output_file}")
        
        # Print summary
        successful = len([d for d in self.processed_data if 'error' not in d])
        failed = len(self.processed_data) - successful
        
        print(f"\n📊 Summary:")
        print(f"   ✓ Successful: {successful}")
        print(f"   ❌ Failed: {failed}")
        
        return True
    
    def print_sample(self, sample_count=1):
        """
        Print sample of processed data.
        """
        print(f"\n📋 Sample Output (first {sample_count}):")
        print("="*70)
        
        for i in range(min(sample_count, len(self.processed_data))):
            item = self.processed_data[i]
            print(f"\nDocument: {item.get('filename', 'unknown')}")
            
            if 'error' not in item:
                print(f"Quality: {item.get('quality_score', 0):.1%}")
                print(f"Entities found:")
                for key, values in item.get('entities', {}).items():
                    if values:
                        print(f"  - {key}: {values}")
            else:
                print(f"Error: {item.get('error')}")
    
    def run(self):
        """
        Execute complete pipeline.
        """
        if self.process_all():
            self.save_results()
            self.print_sample(sample_count=2)
            return True
        return False


if __name__ == "__main__":
    pipeline = DataPipeline()
    pipeline.run()