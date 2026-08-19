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

        # Determine quality color - MORE OPAQUE & DARKER
        if quality >= 0.85:
            quality_color = "#059669"  # Darker green
            quality_bg = "#d1fae5"     # Light green background
        elif quality >= 0.70:
            quality_color = "#d97706"  # Darker amber
            quality_bg = "#fef3c7"     # Light amber background
        else:
            quality_color = "#dc2626"  # Darker red
            quality_bg = "#fee2e2"     # Light red background

        html = f"""
        <div style="font-family: sans-serif; padding: 20px; background: #f9fafb; border-radius: 8px;">
            
            <h2 style="margin: 0 0 20px; color: #1f2937;">📋 Extraction Results</h2>
            
            <div style="margin-bottom: 20px; padding: 16px; background: {quality_bg}; border-radius: 8px; border-left: 4px solid {quality_color};">
                <p style="margin: 8px 0;"><strong>File:</strong> {result.get('filename', 'unknown')}</p>
                <p style="margin: 8px 0;"><strong>Pages:</strong> {result.get('pages', '?')}</p>
                <p style="margin: 8px 0; display: flex; align-items: center; gap: 10px;">
                    <strong>Quality Score:</strong> 
                    <span style="background: {quality_color}; color: white; padding: 8px 16px; border-radius: 20px; font-weight: bold; font-size: 16px;">
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
        """Launch beautiful Gradio interface with modern design."""
        import gradio as gr
        
        # Custom CSS
        custom_css = """
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
        
        * { font-family: 'Poppins', sans-serif; }
        
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .gradio-container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            padding: 40px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .header h1 {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 2.5em;
            margin: 0;
            font-weight: 700;
        }
        
        .header p {
            color: #666;
            font-size: 1.1em;
            margin-top: 10px;
        }
        
        .upload-section {
            background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            border: 2px dashed #667eea;
        }
        
        .how-it-works {
            background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
            padding: 25px;
            border-radius: 15px;
            margin-top: 30px;
        }
        
        .footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 30px;
            border-top: 1px solid #eee;
            color: #999;
            font-size: 0.9em;
        }
        """
        
        with gr.Blocks(css=custom_css, title="DataVault - Resume Extractor") as demo:
            
            # Header
            gr.HTML("""
            <div class="header">
                <h1>📄 DataVault Resume Extractor</h1>
                <p>Extract structured data from resumes using advanced NLP</p>
            </div>
            """)
            
            # Upload Section
            gr.HTML('<div class="upload-section">')
            gr.Markdown("### Upload Your Resume PDF")
            pdf_input = gr.File(
                label="📤 Select Resume PDF",
                file_types=[".pdf"],
                file_count="single"
            )
            extract_btn = gr.Button("🚀 Extract Data", variant="primary", size="lg")
            gr.HTML('</div>')
            
            # Results Section - SINGLE HTML OUTPUT
            results_output = gr.HTML("""
            <div style="font-family: sans-serif; padding: 20px; background: #f9fafb; border-radius: 8px;">
                <h2 style="color: #1f2937; margin-top: 0;">📋 Extraction Results</h2>
                <p style="color: #999;">Upload a resume and click Extract to see results...</p>
            </div>
            """)
            
            # How It Works
            gr.HTML("""
            <div class="how-it-works">
                <h3>How It Works</h3>
                <ol>
                    <li>Upload a resume PDF</li>
                    <li>Click "Extract Data"</li>
                    <li>View structured entities instantly</li>
                    <li>Copy JSON for further processing</li>
                </ol>
                <p><strong>Built with:</strong> pdfplumber • spaCy NLP • Gradio</p>
            </div>
            """)
            
            # Footer
            gr.HTML("""
            <div class="footer">
                <p>DataVault © 2026 | Powered by AI & Machine Learning</p>
                <p><a href="https://github.com/samikshakum13/DataVault" target="_blank">GitHub Repository</a></p>
            </div>
            """)
            
            # Connect button - SINGLE OUTPUT
            def process_resume(pdf_file):
                status, html_result, json_result = self.extract_from_pdf(pdf_file)
                return html_result
            
            extract_btn.click(
                fn=process_resume,
                inputs=[pdf_input],
                outputs=[results_output]
            )
        
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
