# Installation Guide

Step-by-step instructions to install and run DataVault.

---

## Prerequisites

- **Python 3.8+** (tested on 3.9, 3.10, 3.11, 3.13)
- **pip** (Python package manager)
- **Git** (for cloning the repository)

---

## Step 1: Clone Repository

```bash
git clone https://github.com/samikshakum13/DataVault.git
cd DataVault
```

---

## Step 2: Create Virtual Environment

**On Windows (PowerShell/CMD):**
```bash
python -m venv venv
.\venv\Scripts\activate.bat
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Verify activation:**
```bash
# You should see (venv) at the start of terminal
(venv) C:\Users\samik\DataVault>
```

---

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**What gets installed:**
- pdfplumber - PDF text extraction
- spacy - NLP/Named Entity Recognition
- fastapi - REST API framework
- uvicorn - ASGI server for FastAPI
- gradio - Web UI framework
- pandas - Data processing
- pytest - Testing framework

---

## Step 4: Download spaCy Model

```bash
python -m spacy download en_core_web_sm
```

This downloads the English NLP model (~40MB).

---

## Step 5: Verify Installation

**Test Python environment:**
```bash
python --version
```

**Test imports:**
```bash
python -c "import pdfplumber; import spacy; import fastapi; print('✅ All imports successful!')"
```

---

## Running the System

### Option 1: Gradio Web UI (Easiest)

```bash
python src/app.py
```

Then open: http://localhost:7860

**Features:**
- Upload PDF
- Extract data
- View results
- Download JSON

---

### Option 2: FastAPI REST API

**Terminal 1 - Start API:**
```bash
python src/api.py
```

**Terminal 2 - Test API:**
```bash
curl http://localhost:8000/health
```

**Open documentation:**
http://localhost:8000/docs

---

### Option 3: Run Tests

```bash
pytest tests/ -v
```

**Expected output:**

15 passed in 17.36s ✅


---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'pdfplumber'"

**Solution:**
```bash
# Make sure venv is activated
.\venv\Scripts\activate.bat

# Reinstall requirements
pip install -r requirements.txt
```

---

### Issue: "python: command not found"

**Solution:**
- Use `python3` instead of `python` (on macOS/Linux)
- Or add Python to PATH (on Windows)

```bash
python3 -m venv venv
python3 -m spacy download en_core_web_sm
python3 src/app.py
```

---

### Issue: "spaCy model not found"

**Solution:**
```bash
python -m spacy download en_core_web_sm
```

---

### Issue: "Address already in use" (port 7860 or 8000)

**Solution:**
- Close other applications using these ports
- Or change port in `src/app.py` / `src/api.py`:

```python
# In src/app.py
demo.launch(server_name="localhost", server_port=7861)

# In src/api.py
uvicorn.run(app, host="0.0.0.0", port=8001)
```

---

## File Structure After Installation

DataVault/
├── venv/ ← Virtual environment (auto-created)
├── src/
│ ├── app.py ← Gradio web UI
│ ├── api.py ← FastAPI server
│ ├── pipeline.py ← Main processing logic
│ ├── extract.py ← PDF extraction
│ ├── clean.py ← Text cleaning
│ └── ner.py ← NLP entity extraction
├── tests/ ← Test files
├── data/ ← Data files (PDFs, JSON)
├── docs/ ← Documentation
├── README.md ← Project overview
├── requirements.txt ← Dependencies
└── LICENSE ← MIT License


---

## Uninstall

To remove everything:

```bash
# Deactivate virtual environment
deactivate

# Delete venv folder
rm -r venv  # (on macOS/Linux)
rmdir /s venv  # (on Windows)
```

---

## Next Steps

1. Read [README.md](../README.md) for project overview
2. See [USAGE.md](USAGE.md) for examples
3. Check [API.md](API.md) for API reference
4. View [ARCHITECTURE.md](ARCHITECTURE.md) for system design

---

## Support

For issues:
- Check [Troubleshooting](#troubleshooting) section
- Review [README.md](../README.md)
- Check GitHub issues