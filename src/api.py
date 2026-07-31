"""
DataVault FastAPI REST API
Exposes resume extraction as HTTP endpoints

Purpose: Allow developers to use extraction programmatically
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import tempfile
import os
import json
from pathlib import Path

# Import our pipeline
from src.clean import TextCleaner
from src.ner import ResumeNER
import pdfplumber

class APIExtractor:
    """
    API handler for resume extraction.
    
    Why separate class?
    - Keeps API logic separate from pipeline
    - Reusable for other frameworks
    - Professional architecture
    """
    
    def __init__(self):
        """Initialize extractors."""
        self.cleaner = TextCleaner()
        self.ner = ResumeNER()
        print("✓ API Extractor initialized")
    
    def extract_from_bytes(self, file_bytes, filename):
        """
        Extract resume data from PDF bytes.
        
        Args:
            file_bytes: PDF file content (bytes)
            filename: Original filename
        
        Returns:
            Dictionary with extracted data
        """
        
        try:
            # Step 1: Save temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                tmp.write(file_bytes)
                tmp_path = tmp.name
            
            print(f"📄 Processing: {filename}")
            
            # Step 2: Extract text with pdfplumber
            text_extracted = ""
            page_count = 0
            
            with pdfplumber.open(tmp_path) as pdf:
                page_count = len(pdf.pages)
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text_extracted += extracted + "\n"
            
            if not text_extracted:
                return {
                    "success": False,
                    "error": "Could not extract text from PDF"
                }
            
            print(f"✓ Extracted {page_count} page(s)")
            
            # Step 3: Clean text
            cleaned_text = self.cleaner.clean(text_extracted)
            print("✓ Cleaned text")
            
            # Step 4: Extract entities
            entities = self.ner.extract_all(cleaned_text)
            print("✓ Extracted entities")
            
            # Step 5: Calculate quality
            quality = self.calculate_quality(entities)
            
            # Step 6: Build response
            result = {
                "success": True,
                "filename": filename,
                "pages": page_count,
                "quality_score": quality,
                "entities": entities
            }
            
            # Step 7: Cleanup
            os.unlink(tmp_path)
            
            return result
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def calculate_quality(self, entities):
        """Calculate extraction quality (0-1)."""
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


# Initialize FastAPI app
app = FastAPI(
    title="DataVault API",
    description="Resume extraction API using NLP",
    version="1.0.0"
)

# Initialize extractor
extractor = APIExtractor()


# ===== API ENDPOINTS =====

@app.get("/")
async def root():
    """
    Root endpoint - returns API info.
    
    Test with: curl http://localhost:8000/
    """
    return {
        "message": "DataVault Resume Extraction API",
        "version": "1.0.0",
        "endpoints": {
            "POST /extract": "Upload PDF and extract resume data",
            "GET /health": "Check if API is running",
            "GET /docs": "Interactive API documentation (Swagger UI)"
        }
    }


@app.get("/health")
async def health():
    """
    Health check endpoint.
    
    Test with: curl http://localhost:8000/health
    
    Returns: 200 OK if running
    """
    return {
        "status": "healthy",
        "message": "API is running"
    }


@app.post("/extract")
async def extract_resume(file: UploadFile = File(...)):
    """
    Extract resume data from PDF file.
    
    Args:
        file: PDF file (multipart form upload)
    
    Returns:
        JSON with extracted entities
    
    Test with:
        curl -X POST http://localhost:8000/extract \
          -F "file=@resume.pdf"
    
    Example Response:
        {
            "success": true,
            "filename": "resume.pdf",
            "pages": 1,
            "quality_score": 0.92,
            "entities": {
                "names": ["John Doe"],
                "emails": ["john@example.com"],
                "phones": ["+1-555-123-4567"],
                "companies": ["Google"],
                "skills": ["Python", "ML"],
                ...
            }
        }
    """
    
    # Validate file type
    if file.filename is None or not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Please upload a PDF file")
    
    print(f"\n📨 API Request: {file.filename}")
    
    # Read file bytes
    try:
        file_bytes = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")
    
    # Extract
    result = extractor.extract_from_bytes(file_bytes, file.filename)
    
    # Return response
    if result.get('success'):
        return JSONResponse(content=result, status_code=200)
    else:
        raise HTTPException(
            status_code=422,
            detail=result.get('error', 'Unknown error during extraction')
        )


@app.post("/extract-batch")
async def extract_batch(files: list = File(...)):
    """
    Extract data from multiple PDF files.
    
    Args:
        files: List of PDF files
    
    Returns:
        List of extraction results
    
    Test with:
        curl -X POST http://localhost:8000/extract-batch \
          -F "files=@resume1.pdf" \
          -F "files=@resume2.pdf"
    """
    
    results = []
    
    for file in files:
        if not file.filename.endswith('.pdf'):
            results.append({
                "filename": file.filename,
                "success": False,
                "error": "Not a PDF file"
            })
            continue
        
        file_bytes = await file.read()
        result = extractor.extract_from_bytes(file_bytes, file.filename)
        results.append(result)
    
    return JSONResponse(content=results, status_code=200)


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom error response format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    print("="*60)
    print("DataVault FastAPI Server")
    print("="*60)
    print("\n🚀 Starting API server...")
    print("📍 Local: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("📊 ReDoc: http://localhost:8000/redoc")
    print("\nPress Ctrl+C to stop\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

