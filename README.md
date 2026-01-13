# DOST Region II Hybrid Chatbot

A hybrid AI chatbot for DOST Region II that combines official database queries with RAG (Retrieval-Augmented Generation) from public documents.

## Features

- 🤖 Hybrid AI Assistant combining official database and document retrieval
- 📚 RAG (Retrieval-Augmented Generation) for document-based answers
- 🗄️ Official database for fees, requirements, procedures, and contact information
- 📱 Responsive design for web and mobile
- ⚡ Fast response times with model caching

## Setup Instructions

### Prerequisites

- Python 3.11 or 3.12
- Ollama installed and running

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Man18hash/dostr02-chatbot.git
   cd dostr02-chatbot
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   
   # Windows:
   .venv\Scripts\activate
   
   # Linux/Mac:
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install and setup Ollama:**
   - Download from https://ollama.ai/download
   - Pull the model: `ollama pull mistral`

5. **Add your documents:**
   - Place PDF, DOCX, or TXT files in `data/public_docs/`
   - Update JSON files in `data/official/` with real data

6. **Build the index:**
   ```bash
   python build_index.py
   ```

7. **Run the app:**
   ```bash
   python app.py
   ```

8. **Access the app:**
   - Local: http://127.0.0.1:7860
   - Network: http://YOUR_IP:7860

## Project Structure

```
dost-hybrid-chatbot/
├── app.py                 # Main Gradio application
├── build_index.py         # Script to build FAISS index
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── data/
│   ├── official/          # Official database JSON files
│   └── public_docs/       # Documents for RAG
├── img/                   # Logo and images
├── src/                   # Source code modules
└── storage/               # FAISS index storage
```

## Technologies

- **Gradio**: Web UI framework
- **LangChain**: LLM framework
- **FAISS**: Vector database for document retrieval
- **Ollama**: Local LLM inference
- **sentence-transformers**: Embeddings model

## License

MIT

