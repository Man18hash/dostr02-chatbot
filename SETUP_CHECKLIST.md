# DOST Region II Chatbot - Setup Checklist

## ✅ Prerequisites Installation (Do These First!)

### Step 1: Install Python
- [ ] Download Python 3.11 or 3.12 from https://www.python.org/downloads/
- [ ] During installation, check "Add Python to PATH"
- [ ] Verify installation: `python --version` (should show 3.11.x or 3.12.x)

### Step 2: Install Git
- [ ] Download Git from https://git-scm.com/downloads
- [ ] Verify installation: `git --version`

### Step 3: Install Ollama (REQUIRED for LLM)
- [ ] Download Ollama from https://ollama.ai/download
- [ ] Install and start Ollama
- [ ] Verify it's running: `ollama list`
- [ ] Pull the model: `ollama pull mistral`
- [ ] Verify model: `ollama list` (should show mistral)

### Step 4: System Dependencies (Windows)
- [ ] Visual C++ Redistributable (usually pre-installed)
- [ ] For PDF processing, may need additional libraries

---

## ✅ Project Setup (After Prerequisites)

### Step 5: Clone Repository
- [ ] `git clone https://github.com/Man18hash/dostr02-chatbot.git`
- [ ] `cd dostr02-chatbot`

### Step 6: Create Virtual Environment
- [ ] `python -m venv .venv`
- [ ] Activate it:
  - Windows: `.venv\Scripts\activate`
  - Linux/Mac: `source .venv/bin/activate`

### Step 7: Install Python Dependencies
- [ ] Upgrade pip: `pip install --upgrade pip`
- [ ] Install requirements: `pip install -r requirements.txt`
- [ ] Wait for all packages to install (may take 5-10 minutes)

### Step 8: Verify Installations
- [ ] Check Gradio: `python -c "import gradio; print(gradio.__version__)"`
- [ ] Check FAISS: `python -c "import faiss; print('FAISS OK')"`
- [ ] Check LangChain: `python -c "import langchain; print('LangChain OK')"`
- [ ] Check Ollama connection: `python -c "from langchain_ollama import OllamaLLM; print('Ollama OK')"`

### Step 9: Prepare Data Files
- [ ] Add PDF/DOCX/TXT files to `data/public_docs/`
- [ ] Update `data/official/addresses.json` with real address
- [ ] Update `data/official/fees.json` with real fees
- [ ] Update `data/official/procedures.json` with real procedures
- [ ] Update `data/official/requirements.json` with real requirements
- [ ] Add logo to `img/dost_logo150.png`

### Step 10: Build FAISS Index
- [ ] Run: `python build_index.py`
- [ ] Wait for indexing to complete
- [ ] Verify: Check that `storage/faiss_index/` folder has files

### Step 11: Run the Application
- [ ] Start app: `python app.py`
- [ ] Wait for models to load (first time: 10-15 seconds)
- [ ] Access at: http://127.0.0.1:7860
- [ ] Test with a question

---

## 🔧 Troubleshooting

### If Ollama not found:
- Make sure Ollama is running: `ollama serve`
- Check if model is downloaded: `ollama list`

### If FAISS installation fails:
- Try: `pip install faiss-cpu --no-cache-dir`
- On Windows, may need Visual C++ Redistributable

### If models don't load:
- Check internet connection (first download)
- Verify Ollama is running: `ollama list`

### If port 7860 is busy:
- Change port in `app.py`: `server_port=7861`

---

## 📝 Quick Start Commands

```bash
# 1. Clone
git clone https://github.com/Man18hash/dostr02-chatbot.git
cd dostr02-chatbot

# 2. Setup environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 3. Install
pip install -r requirements.txt

# 4. Setup Ollama (in separate terminal)
ollama pull mistral

# 5. Build index
python build_index.py

# 6. Run
python app.py
```

---

## ⚠️ Important Notes

1. **Ollama must be running** before starting the app
2. **First run is slower** (models downloading/loading)
3. **Internet required** for first-time model downloads
4. **Storage space**: Models need ~4GB disk space
5. **RAM**: Recommended 8GB+ for smooth operation

