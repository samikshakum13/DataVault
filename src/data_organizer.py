"""DataVault Data Organizer - WITH DEBUGGING"""

import os
import shutil
from pathlib import Path
import pandas as pd
from datetime import datetime

class DataOrganizer:
    def __init__(self, raw_folder="data/raw", train_folder="data/train", 
                 test_folder="data/test", train_ratio=0.8):
        self.raw_folder = raw_folder
        self.train_folder = train_folder
        self.test_folder = test_folder
        self.train_ratio = train_ratio
        self.metadata = []
    
    def create_folders(self):
        """Create train and test folders"""
        Path(self.train_folder).mkdir(parents=True, exist_ok=True)
        Path(self.test_folder).mkdir(parents=True, exist_ok=True)
        print(f"✓ Folders created: {self.train_folder}, {self.test_folder}")
    
    def get_files(self):
        """Find all PDF files in raw folder"""
        print(f"\n📁 Checking folder: {self.raw_folder}")
        
        # Check if folder exists
        if not os.path.exists(self.raw_folder):
            print(f"❌ PROBLEM: Folder '{self.raw_folder}' does not exist!")
            print(f"   Please create: data/raw/ and add PDFs there")
            return []
        
        # List everything in folder
        all_items = os.listdir(self.raw_folder)
        print(f"   Found {len(all_items)} items total:")
        for item in all_items:
            print(f"     - {item}")
        
        # Filter only PDFs
        files = [f for f in all_items if f.endswith('.pdf')]
        print(f"\n📄 PDFs found: {len(files)}")
        
        if len(files) == 0:
            print("❌ PROBLEM: No PDF files found!")
            print("   Please add PDF files to: data/raw/")
            print("   Example: resume_1.pdf, resume_2.pdf, etc.")
            return []
        
        for file in files:
            size_kb = os.path.getsize(os.path.join(self.raw_folder, file)) / 1024
            print(f"   ✓ {file} ({size_kb:.1f} KB)")
        
        return sorted(files)
    
    def organize(self):
        """Split files into train/test and copy them"""
        files = self.get_files()
        
        if not files:
            print("\n⚠️  Stopping: No PDF files to organize")
            return False
        
        self.create_folders()
        
        # Calculate split
        split_point = int(len(files) * self.train_ratio)
        print(f"\n📊 Split calculation:")
        print(f"   Total files: {len(files)}")
        print(f"   Train ratio: {self.train_ratio * 100}%")
        print(f"   Split point: {split_point}")
        print(f"   Train files: {split_point}")
        print(f"   Test files: {len(files) - split_point}")
        
        print(f"\n🔄 Organizing files...")
        
        for i, file in enumerate(files):
            src = os.path.join(self.raw_folder, file)
            
            if i < split_point:
                split = "train"
                dst = os.path.join(self.train_folder, file)
            else:
                split = "test"
                dst = os.path.join(self.test_folder, file)
            
            # Copy the file
            shutil.copy(src, dst)
            print(f"   ✓ {file} → {split} folder")
            
            # Record metadata
            self.metadata.append({
                "file_name": file,
                "split": split,
                "organized_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "file_size_kb": round(os.path.getsize(src) / 1024, 2)
            })
        
        print(f"\n✅ Organized {len(files)} files successfully!")
        return True
    
    def save_metadata(self, output_file="data/metadata.csv"):
        """Save metadata to CSV"""
        if not self.metadata:
            print("❌ No metadata to save")
            return False
        
        df = pd.DataFrame(self.metadata)
        df.to_csv(output_file, index=False)
        
        print(f"\n📋 Metadata saved to: {output_file}")
        print(f"\nPreview:")
        print(df.to_string(index=False))
        return True
    
    def run(self):
        """Run the complete pipeline"""
        print("="*70)
        print("          DataVault Data Organizer - DEBUG VERSION")
        print("="*70)
        
        if self.organize():
            self.save_metadata()
            print("\n" + "="*70)
            print("✅ SUCCESS! Data organization complete!")
            print("="*70)
            return True
        else:
            print("\n" + "="*70)
            print("❌ FAILED! See messages above for why")
            print("="*70)
            return False


if __name__ == "__main__":
    print("Starting DataVault Data Organizer...\n")
    
    organizer = DataOrganizer()
    organizer.run()
    
    print("\nDone!")