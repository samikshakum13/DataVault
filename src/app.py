"""
DataVault Gradio Web Interface
User-friendly resume extraction demo

Purpose: Let anyone upload a resume PDF and see extracted data instantly
"""

import gradio as gr
import json
import tempfile
import os
from pathlib import Path

# Import our pipeline modules
from clean import TextCleaner
from ner import ResumeNER
from pipeline import DataPipeline

class ResumeExtractorApp:
    """
    Gradio app wrapper for the resume extraction pipeline.
    
    Why Gradio?
    - 10 lines of code for a full web UI
    - No HTML/CSS knowledge needed
    - Deploy to Hugging Face Spaces for free
    - Mobile-friendly
    """
    
    def __init__(self):
        """Initialize the pipeline."""
        self.cleaner = TextCleaner()
        self.ner = ResumeNER()
        print("✓ App initialized: Pipeline ready")
    
    def extract_from_pdf(self, pdf_file):
        """
        Process a single PDF file and extract resume data.
        
        Args:
            pdf_file: Uploaded PDF file (Gradio returns a file path)
        
        Returns:
            Tuple of (status, results_html, json_download)
        """
        
        try:
            # Step 1: Check if file exists
            if pdf_file is None:
                return "❌ Please upload a PDF file", "", None
            
            print(f"\n📄 Processing: {pdf_file}")
            
            # Step 2: Extract text using pdfplumber
            import pdfplumber
            
            text_extracted = ""
            page_count = 0
            
            with pdfplumber.open(pdf_file) as pdf:
                page_count = len(pdf.pages)
                for page in pdf.pages:
                    extracted_page = page.extract_text()
                    if extracted_page:
                        text_extracted += extracted_page + "\n"
            
            if not text_extracted:
                return "❌ Could not extract text from PDF", "", None
            
            print(f"✓ Extracted text from {page_count} page(s)")
            
            # Step 3: Clean text
            cleaned_text = self.cleaner.clean(text_extracted)
            print("✓ Cleaned text")
            
            # Step 4: Extract entities
            entities = self.ner.extract_all(cleaned_text)
            print("✓ Extracted entities")
            
            # Step 5: Calculate quality score
            quality_score = self.calculate_quality(entities)
            print(f"✓ Quality score: {quality_score:.1%}")
            
            # Step 6: Create results
            result = {
                "status": "success",
                "filename": Path(pdf_file).name,
                "pages": page_count,
                "quality_score": quality_score,
                "entities": entities
            }
            
            # Step 7: Format for display
            html_result = self.format_html(result)
            json_result = json.dumps(result, indent=2)
            
            return "✅ Success!", html_result, json_result
        
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            print(error_msg)
            return error_msg, "", None
    
    def calculate_quality(self, entities):
        """
        Score the quality of extraction (0-1 scale).
        
        Quality is high if we extracted:
        - Names (30%)
        - Emails (30%)
        - Companies (20%)
        - Skills (20%)
        """
        score = 0.0
        
        if entities.get('names'):
            score += 0.3
        if entities.get('emails'):
            score += 0.3
        if entities.get('companies'):
            score += 0.2
        if entities.get('skills'):
            score += 0.2
        
        return min(score, 1.0)
    
    def format_html(self, result):
        """
        Format extraction results as HTML for display.
        
        Why HTML?
        - Looks professional
        - Easy to read
        - Color-coded for different entity types
        """
        
        entities = result.get('entities', {})
        quality = result.get('quality_score', 0)
        
        # Determine quality color
        if quality >= 0.85:
            quality_color = "#10b981"  # green
        elif quality >= 0.70:
            quality_color = "#f59e0b"  # amber
        else:
            quality_color = "#ef4444"  # red
        
        html = f"""
        <div style="font-family: sans-serif; padding: 20px; background: #f9fafb; border-radius: 8px;">
            
            <h2 style="margin: 0 0 20px; color: #1f2937;">📋 Extraction Results</h2>
            
            <div style="margin-bottom: 20px; padding: 12px; background: white; border-radius: 6px;">
                <p style="margin: 8px 0;"><strong>File:</strong> {result.get('filename', 'unknown')}</p>
                <p style="margin: 8px 0;"><strong>Pages:</strong> {result.get('pages', '?')}</p>
                <p style="margin: 8px 0;">
                    <strong>Quality Score:</strong> 
                    <span style="background: {quality_color}; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">
                        {quality:.0%}
                    </span>
                </p>
            </div>
            
            <h3 style="color: #1f2937; margin-top: 20px; margin-bottom: 10px;">Extracted Entities</h3>
            
            <!-- Names -->
            <div style="margin-bottom: 16px; padding: 12px; background: white; border-left: 4px solid #3b82f6; border-radius: 4px;">
                <strong style="color: #1f2937;">👤 Names</strong><br>
                <span style="color: #6b7280; font-size: 13px;">
                    {', '.join(entities.get('names', [])) or 'No names found'}
                </span>
            </div>
            
            <!-- Emails -->
            <div style="margin-bottom: 16px; padding: 12px; background: white; border-left: 4px solid #8b5cf6; border-radius: 4px;">
                <strong style="color: #1f2937;">✉️ Emails</strong><br>
                <span style="color: #6b7280; font-size: 13px;">
                    {', '.join(entities.get('emails', [])) or 'No emails found'}
                </span>
            </div>
            
            <!-- Phones -->
            <div style="margin-bottom: 16px; padding: 12px; background: white; border-left: 4px solid #ec4899; border-radius: 4px;">
                <strong style="color: #1f2937;">📞 Phones</strong><br>
                <span style="color: #6b7280; font-size: 13px;">
                    {', '.join(entities.get('phones', [])) or 'No phones found'}
                </span>
            </div>
            
            <!-- Companies -->
            <div style="margin-bottom: 16px; padding: 12px; background: white; border-left: 4px solid #f59e0b; border-radius: 4px;">
                <strong style="color: #1f2937;">🏢 Companies</strong><br>
                <span style="color: #6b7280; font-size: 13px;">
                    {', '.join(entities.get('companies', [])) or 'No companies found'}
                </span>
            </div>
            
            <!-- Locations -->
            <div style="margin-bottom: 16px; padding: 12px; background: white; border-left: 4px solid #10b981; border-radius: 4px;">
                <strong style="color: #1f2937;">📍 Locations</strong><br>
                <span style="color: #6b7280; font-size: 13px;">
                    {', '.join(entities.get('locations', [])) or 'No locations found'}
                </span>
            </div>
            
            <!-- Skills -->
            <div style="margin-bottom: 16px; padding: 12px; background: white; border-left: 4px solid #06b6d4; border-radius: 4px;">
                <strong style="color: #1f2937;">⚡ Skills</strong><br>
                <span style="color: #6b7280; font-size: 13px;">
                    {', '.join(entities.get('skills', [])) or 'No skills found'}
                </span>
            </div>
            
            <!-- Years -->
            <div style="margin-bottom: 16px; padding: 12px; background: white; border-left: 4px solid #6366f1; border-radius: 4px;">
                <strong style="color: #1f2937;">📅 Years</strong><br>
                <span style="color: #6b7280; font-size: 13px;">
                    {', '.join(entities.get('years', [])) or 'No years found'}
                </span>
            </div>
            
        </div>
        """
        
        return html
    
    def launch(self):
        """
        Launch the Gradio web interface.
        
        This creates a beautiful, responsive web app.
        """
        
        # Create Gradio interface
        with gr.Blocks(title="DataVault - Resume Extractor") as demo:
            
            # Header
            gr.Markdown("""
            # 📄 DataVault Resume Extractor
            
            **Upload a resume PDF and extract structured data instantly**
            
            This system uses NLP to extract:
            - Names, emails, phone numbers
            - Companies and job titles
            - Skills and education
            - Locations and work dates
            """)
            
            # Main content
            with gr.Row():
                with gr.Column(scale=1):
                    # Input: File upload
                    pdf_input = gr.File(
                        label="📤 Upload Resume PDF",
                        file_types=[".pdf"],
                        file_count="single"
                    )
                    
                    # Processing button
                    extract_btn = gr.Button(
                        "🚀 Extract Data",
                        variant="primary",
                        size="lg"
                    )
                
                with gr.Column(scale=1):
                    # Output: Status
                    status_output = gr.Textbox(
                        label="Status",
                        interactive=False,
                        lines=1
                    )
            
            # Results display
            results_output = gr.HTML(
                label="📊 Results",
                value="<p style='color: #9ca3af;'>Upload a PDF and click Extract to see results...</p>"
            )
            
            # JSON download
            json_output = gr.Textbox(
                label="📋 JSON (for downloading/processing)",
                interactive=False,
                lines=10,
                visible=False
            )
            
            # Connect button to processing function
            extract_btn.click(
                fn=self.extract_from_pdf,
                inputs=[pdf_input],
                outputs=[status_output, results_output, json_output]
            )
            
            # Footer
            gr.Markdown("""
            ---
            
            **How it works:**
            1. Upload a resume PDF
            2. Click "Extract Data"
            3. View structured entities
            4. Copy JSON for further processing
            
            **Built with:** pdfplumber, spaCy, Gradio
            """)
        
        return demo


if __name__ == "__main__":
    print("="*60)
    print("DataVault - Resume Extraction Web App")
    print("="*60)
    
    # Create app
    app = ResumeExtractorApp()
    demo = app.launch()
    
    # Launch locally (http://localhost:7860)
    print("\n🚀 Launching Gradio app...")
    print("📍 Open: http://localhost:7860")
    print("Press Ctrl+C to stop\n")

# THIS RUNS ON IMPORT (for Railway)
app = ResumeExtractorApp()
demo = app.launch()