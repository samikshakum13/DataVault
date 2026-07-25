markdown
# DataVault 📄

**Resume Extraction System using NLP**

Extract structured data from resume PDFs instantly. Built with Python, spaCy, FastAPI, and Gradio.

---

## 🌟 Features

- ✅ **PDF Text Extraction** - Extract text from resume PDFs with pdfplumber
- ✅ **NLP Entity Recognition** - Extract names, emails, companies, skills using spaCy
- ✅ **Text Cleaning** - Normalize and clean raw resume text with regex
- ✅ **Fuzzy Matching** - Deduplicate entities (e.g., "Google" vs "google")
- ✅ **Quality Scoring** - Rate extraction quality (0-100%)
- ✅ **Web UI** - User-friendly Gradio interface
- ✅ **REST API** - FastAPI endpoints for developers
- ✅ **Professional Tests** - 15 unit & integration tests passing

---

## 📊 Metrics

| Metric | Score |
|--------|-------|
| **Precision** | 94% |
| **Recall** | 87% |
| **F1 Score** | 0.90 |
| **Processing Time** | ~450ms/resume |

*Tested on 2 resumes with manual verification*

---

## 🚀 Quick Start

### 1. Install & Setup

```bash
# Clone repo
git clone https://github.com/samikshakum13/DataVault.git
cd DataVault

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Web UI (Easiest)

```bash
python src/app.py
```

Open: http://localhost:7860

Upload a resume PDF → See results instantly! 📤

### 3. Run REST API (For Developers)

```bash
python src/api.py
```

Open: http://localhost:8000/docs

Test endpoints with interactive Swagger UI! 🔧

---

## 📖 Usage Examples

### Web Interface (Gradio)
Open http://localhost:7860
Click "Choose File"
Select a resume PDF
Click "Extract Data"
View results: names, emails, companies, skills
Download JSON

### REST API

**Extract single resume:**

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

### Python Client

```python
import requests

# Upload and extract
with open('resume.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/extract',
        files={'file': f}
    )

data = response.json()
print(f"Name: {data['entities']['names']}")
print(f"Skills: {data['entities']['skills']}")
print(f"Quality: {data['quality_score']:.0%}")
```

---

## 🏗️ Architecture

User Upload (PDF)
↓
pdfplumber (Day 3)
↓ extracts text
TextCleaner (Day 4a)
↓ cleans & normalizes
ResumeNER (Day 4b)
↓ extracts entities with spaCy
DataPipeline (Day 5)
↓ deduplicates & scores
Quality JSON Output
↓
Gradio UI OR FastAPI REST


**[See ARCHITECTURE.md for detailed diagrams](docs/ARCHITECTURE.md)**

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Results: 15 passing tests ✅
```

**Tests cover:**
- Text cleaning (whitespace, special chars, normalization)
- NER extraction (emails, phones, skills, entities)
- Pipeline integration (quality scoring, deduplication)
- Metrics calculation (precision, recall, F1)

---

## 📁 Project Structure

DataVault/
├── src/
│ ├── data_organizer.py # Day 2: 80/20 train/test split
│ ├── extract.py # Day 3: PDF text extraction
│ ├── clean.py # Day 4: Text cleaning
│ ├── ner.py # Day 4: NLP entity extraction
│ ├── pipeline.py # Day 5: Full processing pipeline
│ ├── app.py # Day 6: Gradio web interface
│ └── api.py # Day 7: FastAPI REST API
├── tests/
│ ├── test_clean.py # Day 8: Cleaning tests
│ ├── test_ner.py # Day 8: NER tests
│ ├── test_pipeline.py # Day 8: Pipeline tests
│ ├── test_metrics.py # Day 9: Metrics calculation
│ └── run_metrics.py # Day 9: Metrics report
├── data/
│ ├── raw/ # Original PDFs
│ ├── train/ # 80% training resumes
│ ├── test/ # 20% test resumes
│ ├── extracted_text.json # Raw text from PDFs
│ ├── processed_resumes.json # Structured output
│ └── metrics_report.json # Accuracy metrics
├── docs/
│ ├── API.md # API reference
│ ├── ARCHITECTURE.md # System design
│ ├── INSTALL.md # Setup instructions
│ └── USAGE.md # Usage examples
├── README.md # This file
├── requirements.txt # Python dependencies
└── LICENSE # MIT License


---

## 🔧 Tech Stack

| Component | Technology |
|-----------|------------|
| **PDF Extraction** | pdfplumber |
| **NLP/NER** | spaCy (en_core_web_sm) |
| **Data Processing** | Pandas, NumPy, regex |
| **Database** | SQLite (optional) |
| **REST API** | FastAPI + Uvicorn |
| **Web UI** | Gradio |
| **Testing** | pytest |
| **Deployment** | Docker (ready for Hugging Face Spaces) |

---

## 📚 Documentation

- **[API Reference](docs/API.md)** - All endpoints, parameters, responses
- **[Architecture](docs/ARCHITECTURE.md)** - System design, data flow
- **[Installation](docs/INSTALL.md)** - Detailed setup guide
- **[Usage Guide](docs/USAGE.md)** - Complete examples
- **[Metrics Report](data/metrics_report.json)** - Accuracy metrics

---

## 🚀 What's Next

**Days 13-14: Deployment**
- Docker containerization
- Deploy to Hugging Face Spaces (free, public hosting)
- Share link with anyone in the world!

---

## 📈 Project Timeline

Days 1-2: ✅ Setup + Data organization
Days 3-4: ✅ Text extraction + NLP
Day 5: ✅ Full processing pipeline
Day 6: ✅ Gradio web interface
Day 7: ✅ FastAPI REST API
Days 8-9: ✅ Testing + Metrics (Precision 94%, Recall 87%, F1 0.90)
Days 10-12: ✅ Professional documentation
Days 13-14: ⏳ Deployment to Hugging Face Spaces


---

## 👤 Author

**Samiksha Kumbhalkar**
- B.Tech Electronics & Telecom Engineering (2026)
- MKSSS Cummins College of Engineering for Women, Nagpur
- [LinkedIn](https://linkedin.com/in/samiksha-kumbhalkar-a71279256)
- [GitHub](https://github.com/samikshakum13)

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file

---

## 🤝 Contributing

This is a portfolio project. Feedback welcome!

---

## ⭐ Show Your Support

If you found this useful, please star ⭐ the repository!

---
