# 🏦 Personal Local CPA

A completely local, privacy-first personal finance and tax management application. Built for the privacy-conscious individual who wants AI-driven financial insights without their data ever leaving their machine.

## 🌟 Key Features

- **Privacy First**: Everything runs locally. No cloud, no tracking, no data leaks.
- **Smart Knowledge Base**: Organize your IRS forms, prior returns, and receipts into **Folders (Collections)**.
- **Context-Aware AI**: The assistant automatically picks the right folder to answer your questions (e.g., searching "Bank Statements" for spending queries).
- **Guardian Inbox**: Automatically detects uncategorized transactions that need your attention.
- **Multi-Model Support**: Optimized for Ollama (Llama 3.1, Mistral) or local GGUF files via llama-cpp.

---

## 🚀 Quick Start (Installation)

The application is now unified. You only need to run the backend, and it will serve the frontend automatically.

### 1. Prerequisites
- **Ollama**: [Download and Install](https://ollama.com).
- **Python 3.11+**
- **uv**: `curl -LsSf https://astral.sh/uv/install.sh | sh`

### 2. Setup
```bash
# Clone the repository
git clone https://github.com/abhishek-jana/personalCPA.git
cd personalCPA

# Install dependencies and setup environment
uv sync

# Install system dependencies (Linux/WSL2)
# Required for vector search support
sudo apt-get update && sudo apt-get install -y libblas3 liblapack3 libomp5
```

### 3. Pull Intelligence
```bash
ollama pull llama3.1:8b-instruct-q8_0
```

### 4. Run it
```bash
export CPA_MODEL_TYPE=painless
uv run uvicorn main:app
```
Visit **http://localhost:8000** in your browser.

---

## 📁 Organizing Your Knowledge

You can ground the AI's advice in your own documents using the **Knowledge Base** section on the dashboard:

1. **Create a Folder**: Click the `+` in the Knowledge Base section (e.g., "Tax Knowledge").
2. **Upload**: Drag and drop your PDFs or text files into the folder.
3. **Chat**: Ask the Assistant questions. It will intelligently search the relevant folders to find the answer.

---

## 🛠️ Advanced Configuration

### Using Local Models (Non-Ollama)
If you prefer using GGUF files directly:
1. Run `./install_llm.sh` to compile `llama-cpp-python` for your hardware.
2. Set `CPA_LLM_BACKEND=llama-cpp` and provide your `CPA_MODEL_PATH`.

### Development
To run the frontend in development mode (with Hot Module Replacement):
```bash
cd frontend
npm install
npm run dev
```

---

## 🗺️ Roadmap
- [x] **Smart Folders**: Logical isolation for tax vs. spending data.
- [x] **Unified Serving**: Single command to run the whole app.
- [x] **Self-Healing**: Automated system health and dependency checks.
- [ ] **Multi-Year Analysis**: Comparative tax liability over time.
- [ ] **Automated Categorization**: AI-driven transaction labeling.

## 📄 License
MIT - See LICENSE for details.
