"""
DataVault Gradio Web Interface
User-friendly resume extraction demo

Purpose: Let anyone upload a resume PDF and see extracted data instantly
"""

import gradio as gr
import json
import tempfile
import os
import pdfplumber
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
        print("✓ App initialized")

    def extract_from_pdf(self, pdf_file):
        """Extract resume data."""
        try:
            if pdf_file is None:
                return "❌ Upload a PDF", "", None

            print(f"\n📄 Processing: {pdf_file}")

            # Extract text
            text_extracted = ""
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_extracted += text + "\n"

            if not text_extracted:
                return "❌ Could not extract text", "", None

            # Clean
            cleaned_text = self.cleaner.clean(text_extracted)
            # DEBUG: Print first 10 lines to see structure
            print("\n=== CLEANED TEXT - FIRST 10 LINES ===")
            debug_lines = cleaned_text.split('\n')[:10]
            for i, line in enumerate(debug_lines):
                print(f"Line {i}: '{line}'")
            print("===================================\n")
            # Extract using NEW smart NER
            entities = self.ner.extract_all(text_extracted)

            # Post-process
            for key in entities:
                if entities[key]:
                    entities[key] = list(set(entities[key]))

            # Quality score
            quality_score = self.calculate_quality(entities)

            result = {
                "status": "success",
                "filename": pdf_file.split('/')[-1] if '/' in pdf_file else pdf_file,
                "quality_score": quality_score,
                "entities": entities
            }

            html_result = self.format_html(result)
            json_result = json.dumps(result, indent=2)

            return "✅ Success!", html_result, json_result

        except Exception as e:
            return f"❌ Error: {str(e)}", "", None
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


def main():
    """Main entry point."""
    print("="*60)
    print("DataVault - Resume Extraction Web App")
    print("="*60)
    
    app = ResumeExtractorApp()
    demo = app.launch()
    
    print("\n🚀 Launching Gradio app...")
    print("📍 Open: http://localhost:7860")
    print("Press Ctrl+C to stop\n")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", 7860)),
        share=False
    )

if __name__ == "__main__":
    main()

# THIS RUNS ON IMPORT (for Railway)
if True:  # Always run this for production
    app = ResumeExtractorApp()
    demo = app.launch()
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", 7860)),
        share=False
    )
