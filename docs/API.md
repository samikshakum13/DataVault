# DataVault REST API Reference

Complete API documentation for programmatic access to resume extraction.

---

## Base URL

http://localhost:8000


---

## Endpoints

### 1. Health Check

Check if API is running.

**Request:**

GET /health


**Response (200 OK):**
```json
{
  "status": "healthy",
  "message": "API is running"
}
```

**Example:**
```bash
curl http://localhost:8000/health
```

---

### 2. Extract Single Resume

Extract data from a single PDF resume.

**Request:**

POST /extract
Content-Type: multipart/form-data

file: <PDF file>


**Parameters:**
- `file` (required): PDF file, max 10MB

**Response (200 OK):**
```json
{
  "success": true,
  "filename": "resume.pdf",
  "pages": 1,
  "quality_score": 0.92,
  "entities": {
    "names": ["John Doe"],
    "emails": ["john@example.com"],
    "phones": ["+1-555-123-4567"],
    "companies": ["Google", "Microsoft"],
    "skills": ["Python", "Machine Learning", "FastAPI"],
    "locations": ["San Francisco, CA"],
    "years": ["2020", "2023"]
  }
}
```

**Example:**

```bash
# Using curl
curl -X POST http://localhost:8000/extract \
  -F "file=@resume.pdf"

# Using Python
import requests
with open('resume.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/extract',
        files={'file': f}
    )
data = response.json()
print(data)
```

**Status Codes:**
- `200` - Success
- `400` - Invalid file (not PDF)
- `422` - Extraction error
- `500` - Server error

---

### 3. Extract Multiple Resumes

Extract data from multiple PDF files at once.

**Request:**

POST /extract-batch
Content-Type: multipart/form-data

files: <PDF file 1>
files: <PDF file 2>
files: <PDF file N>


**Parameters:**
- `files` (required): Multiple PDF files

**Response (200 OK):**
```json
[
  {
    "success": true,
    "filename": "resume_1.pdf",
    "pages": 1,
    "quality_score": 0.92,
    "entities": { ... }
  },
  {
    "success": true,
    "filename": "resume_2.pdf",
    "pages": 1,
    "quality_score": 0.89,
    "entities": { ... }
  }
]
```

**Example:**

```bash
curl -X POST http://localhost:8000/extract-batch \
  -F "files=@resume_1.pdf" \
  -F "files=@resume_2.pdf" \
  -F "files=@resume_3.pdf"
```

---

### 4. API Info

Get API information and available endpoints.

**Request:**

GET /


**Response (200 OK):**
```json
{
  "message": "DataVault Resume Extraction API",
  "version": "1.0.0",
  "endpoints": {
    "POST /extract": "Upload PDF and extract resume data",
    "GET /health": "Check if API is running",
    "GET /docs": "Interactive API documentation (Swagger UI)"
  }
}
```

---

## Response Schema

### Success Response

```json
{
  "success": true,
  "filename": "string",
  "pages": number,
  "quality_score": number (0-1),
  "entities": {
    "names": [string],
    "emails": [string],
    "phones": [string],
    "companies": [string],
    "skills": [string],
    "locations": [string],
    "years": [string]
  }
}
```

### Error Response

```json
{
  "success": false,
  "error": "Error message"
}
```

---

## Quality Score

Score ranges from 0 to 1:
- `0.9+` - Excellent (all entities extracted)
- `0.7-0.9` - Good (most entities extracted)
- `0.5-0.7` - Fair (some entities extracted)
- `<0.5` - Poor (few entities extracted)

**Calculation:**

Score = 0.3 × (has names) +
0.3 × (has emails) +
0.2 × (has companies) +
0.2 × (has skills)


---

## Authentication

Currently no authentication required. For production deployment, add API keys.

---

## Rate Limiting

No rate limiting currently. For production, recommend:
- 100 requests/hour per IP
- 1000 requests/day per API key

---

## Examples

### Python

```python
import requests
import json

# Single file
files = {'file': open('resume.pdf', 'rb')}
response = requests.post('http://localhost:8000/extract', files=files)
data = response.json()

print(f"Quality: {data['quality_score']:.0%}")
print(f"Names: {data['entities']['names']}")
print(f"Skills: {data['entities']['skills']}")
```

### JavaScript

```javascript
const formData = new FormData();
formData.append('file', resumeFile);

const response = await fetch('http://localhost:8000/extract', {
  method: 'POST',
  body: formData
});

const data = await response.json();
console.log(data.entities.skills);
```

### cURL

```bash
# Extract single resume
curl -X POST http://localhost:8000/extract \
  -F "file=@resume.pdf" \
  -H "Accept: application/json"

# Extract batch
curl -X POST http://localhost:8000/extract-batch \
  -F "files=@r1.pdf" \
  -F "files=@r2.pdf"

# Pretty print
curl -X POST http://localhost:8000/extract \
  -F "file=@resume.pdf" | python -m json.tool
```

---

## Interactive Documentation

Visit http://localhost:8000/docs for interactive Swagger UI where you can:
- Test all endpoints
- See parameter descriptions
- View response schemas
- Download API spec

---

## Troubleshooting

**API not responding:**
```bash
curl http://localhost:8000/health
```

**File too large:**
- Maximum file size: 10MB
- Reduce PDF or split into pages

**Extraction failed:**
- Ensure PDF contains text (not image-only)
- Check terminal for error messages

---

## Support

For issues, see main [README.md](../README.md)