Perfect! 🚀 FINAL FILE - docs/USAGE.md

✅ Create docs/USAGE.md - COMPLETE CODE

Create file: docs/USAGE.md

Paste ALL of this:

markdown
# Usage Guide

Complete examples and tutorials for using DataVault.

---

## Table of Contents

1. [Web UI Usage](#web-ui-usage)
2. [REST API Usage](#rest-api-usage)
3. [Python Client](#python-client)
4. [Command Line](#command-line)
5. [Advanced Examples](#advanced-examples)

---

## Web UI Usage

### Starting the Web Interface

```bash
python src/app.py
```

Then open: http://localhost:7860

---

### Basic Workflow

**Step 1: Upload Resume**

Click: "📤 Upload Resume PDF"
Select: A PDF file from your computer


**Step 2: Process**

Click: "🚀 Extract Data"
Wait for processing (usually <1 second)


**Step 3: View Results**

See extracted data:

👤 Names
✉️ Emails
📞 Phones
🏢 Companies
⚡ Skills
📍 Locations
📅 Years

**Step 4: Download**

Copy the JSON from the results box
Or download as .json file


---

### Example: Extract from Sophia Lewis Resume

**Input:** sophia_resume.pdf containing:

Name: Sophia Lewis
Email: sophia.lewis@email.com
Phone: +1 555-890-1234
Experience: Registered Nurse (2021–Present)
Skills: Patient Care, Clinical Documentation, Emergency Care
Education: B.Sc. Nursing, University of Washington, 2021


**Steps:**
1. Open http://localhost:7860
2. Upload: sophia_resume.pdf
3. Click: Extract Data
4. Results appear:

👤 Names: Sophia Lewis
✉️ Emails: sophia.lewis@email.com
📞 Phones: +1 555-890-1234
🏢 Companies: University of Washington
⚡ Skills: Patient Care, Clinical Documentation, Emergency Care, Communication, Teamwork
📅 Years: 2021


---

## REST API Usage

### Starting the API

```bash
python src/api.py
```

Then access: http://localhost:8000

---

### Interactive Documentation

Visit: http://localhost:8000/docs

You'll see a Swagger UI where you can:
- Test endpoints
- See parameters
- View response schemas
- Download API specification

---

### Example 1: Check API Health

**cURL:**
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "message": "API is running"
}
```

---

### Example 2: Extract Single Resume

**cURL:**
```bash
curl -X POST http://localhost:8000/extract \
  -F "file=@resume.pdf"
```

**Response:**
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

---

### Example 3: Extract Multiple Resumes

**cURL:**
```bash
curl -X POST http://localhost:8000/extract-batch \
  -F "files=@resume1.pdf" \
  -F "files=@resume2.pdf" \
  -F "files=@resume3.pdf"
```

**Response:**
```json
[
  {
    "success": true,
    "filename": "resume1.pdf",
    "quality_score": 0.92,
    "entities": { ... }
  },
  {
    "success": true,
    "filename": "resume2.pdf",
    "quality_score": 0.89,
    "entities": { ... }
  },
  {
    "success": true,
    "filename": "resume3.pdf",
    "quality_score": 0.87,
    "entities": { ... }
  }
]
```

---

## Python Client

### Installation

```bash
pip install requests
```

---

### Example 1: Simple Extraction

```python
import requests
import json

# Extract single resume
with open('resume.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/extract',
        files={'file': f}
    )

data = response.json()

if data['success']:
    print(f"✅ Success!")
    print(f"Quality Score: {data['quality_score']:.0%}")
    print(f"Names: {data['entities']['names']}")
    print(f"Emails: {data['entities']['emails']}")
    print(f"Skills: {data['entities']['skills']}")
else:
    print(f"❌ Error: {data['error']}")
```

**Output:**

✅ Success!
Quality Score: 92%
Names: ['John Doe']
Emails: ['john@example.com']
Skills: ['Python', 'Machine Learning', 'FastAPI']


---

### Example 2: Batch Processing

```python
import requests
import json

# Extract multiple resumes
files = [
    ('files', open('resume1.pdf', 'rb')),
    ('files', open('resume2.pdf', 'rb')),
    ('files', open('resume3.pdf', 'rb'))
]

response = requests.post(
    'http://localhost:8000/extract-batch',
    files=files
)

results = response.json()

for result in results:
    if result['success']:
        print(f"✅ {result['filename']}: {result['quality_score']:.0%}")
        print(f"   Skills: {result['entities']['skills']}")
    else:
        print(f"❌ {result['filename']}: {result['error']}")
```

**Output:**

✅ resume1.pdf: 92%
Skills: ['Python', 'Machine Learning']
✅ resume2.pdf: 89%
Skills: ['Java', 'Spring Boot']
✅ resume3.pdf: 87%
Skills: ['C++', 'Embedded Systems']


---

### Example 3: Save to Database

```python
import requests
import json
import sqlite3

# Extract and save to SQLite
conn = sqlite3.connect('resumes.db')
cursor = conn.cursor()

# Create table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY,
        filename TEXT,
        quality_score REAL,
        entities JSON
    )
''')

# Extract and save
with open('resume.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/extract',
        files={'file': f}
    )

data = response.json()

if data['success']:
    cursor.execute(
        'INSERT INTO resumes (filename, quality_score, entities) VALUES (?, ?, ?)',
        (
            data['filename'],
            data['quality_score'],
            json.dumps(data['entities'])
        )
    )
    conn.commit()
    print(f"✅ Saved to database: {data['filename']}")

conn.close()
```

---

## Command Line

### Extract with Python Script

```bash
# Run full pipeline
python src/pipeline.py

# Run metrics report
python tests/run_metrics.py
```

---

### Run Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_clean.py -v

# Specific test
pytest tests/test_clean.py::TestTextCleaner::test_remove_extra_whitespace -v
```

---

## Advanced Examples

### Example 1: Parallel Processing

```python
import requests
from concurrent.futures import ThreadPoolExecutor
import os

def extract_resume(filename):
    """Extract data from a single resume."""
    with open(filename, 'rb') as f:
        response = requests.post(
            'http://localhost:8000/extract',
            files={'file': f}
        )
    return response.json()

# Get all PDFs in folder
pdf_files = [f for f in os.listdir('data/train') if f.endswith('.pdf')]

# Process in parallel (4 threads)
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(extract_resume, pdf_files))

# Print results
for result in results:
    if result['success']:
        print(f"✅ {result['filename']}: {result['quality_score']:.0%}")
```

---

### Example 2: Filter by Quality Score

```python
import requests

# Extract multiple files
files = [('files', open(f, 'rb')) for f in ['r1.pdf', 'r2.pdf', 'r3.pdf']]
response = requests.post('http://localhost:8000/extract-batch', files=files)
results = response.json()

# Filter high quality
high_quality = [r for r in results if r['quality_score'] >= 0.85]

print(f"High quality: {len(high_quality)}/{len(results)}")
for r in high_quality:
    print(f"  ✅ {r['filename']}: {r['quality_score']:.0%}")
```

---

### Example 3: Export to CSV

```python
import requests
import csv

# Extract and export to CSV
with open('resume.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/extract',
        files={'file': f}
    )

data = response.json()

if data['success']:
    # Flatten entities for CSV
    with open('output.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Headers
        writer.writerow(['Entity Type', 'Value'])
        
        # Write data
        entities = data['entities']
        for entity_type, values in entities.items():
            for value in values:
                writer.writerow([entity_type, value])
    
    print("✅ Exported to output.csv")
```

---

### Example 4: Custom Processing

```python
import requests
from collections import Counter

# Extract resume
with open('resume.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/extract',
        files={'file': f}
    )

data = response.json()

if data['success']:
    entities = data['entities']
    
    # Count skills
    print(f"📊 Statistics:")
    print(f"  Names: {len(entities['names'])}")
    print(f"  Emails: {len(entities['emails'])}")
    print(f"  Companies: {len(entities['companies'])}")
    print(f"  Skills: {len(entities['skills'])}")
    
    # Top companies
    companies = Counter(entities['companies'])
    print(f"\n🏢 Top Companies:")
    for company, count in companies.most_common(3):
        print(f"  {company}: {count}x")
```

---

## Troubleshooting

### Issue: "Connection refused" error

**Cause:** API server not running

**Solution:**
```bash
# Start API server
python src/api.py

# In another terminal, run your script
python your_script.py
```

---

### Issue: "File not found" error

**Cause:** PDF file path incorrect

**Solution:**
```python
# Check file exists
import os
if os.path.exists('resume.pdf'):
    print("✅ File found")
else:
    print("❌ File not found - check path!")
```

---

### Issue: "Quality score is low" (< 0.5)

**Cause:** PDF is image-only or text is not extractable

**Solution:**
1. Try OCR on the PDF first
2. Or manually verify PDF contains text
3. Use a different resume

---

## Performance Tips

1. **Batch Processing:** Use `/extract-batch` instead of multiple `/extract` calls
2. **Parallel Processing:** Use ThreadPoolExecutor for concurrent requests
3. **Caching:** Cache results if processing same file multiple times
4. **Filtering:** Filter by quality score to avoid processing low-quality PDFs

---

## Next Steps

- [Installation Guide](INSTALL.md)
- [API Reference](API.md)
- [Architecture](ARCHITECTURE.md)
- [README](../README.md)