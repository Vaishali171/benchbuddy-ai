# BenchBuddy AI 🔧

**An AI-powered electronics datasheet assistant for students, makers, and engineers.**

BenchBuddy AI helps users explore electronic component datasheets without manually searching through every page. Upload a PDF, search for specifications, ask questions about the document, compare component datasheets, and generate a virtual bench-test checklist.

## 💡 The Problem

Electronics datasheets contain important information about electrical characteristics, operating conditions, pin configurations, and component limitations. Finding the right information can be time-consuming, especially for students who are still learning how to interpret technical documentation.

BenchBuddy AI aims to make this process more accessible through document search and AI-assisted explanations.

## ✨ Features

### 📄 Datasheet Processing

* Upload electronics datasheets in PDF format.
* Extract selectable text from individual pages.
* View page counts and basic document statistics.

### 🔎 Specification Search

* Search for terms such as operating temperature, supply voltage, and input offset voltage.
* View matching pages and their extracted text.
* Inspect keyword-match scores.

### 🤖 AI Datasheet Assistant

* Ask questions about an uploaded datasheet.
* Send relevant document excerpts to an AI model.
* Request answers with supporting page references.
* Inspect the source excerpts used for an answer.

### ⚖️ Component Comparison

* Upload two component datasheets.
* Request an AI-generated comparison of selected specifications.
* Download the comparison as a Markdown file.

### 🧪 Virtual Bench-Test Planning

* Generate a structured checklist for planning component tests.
* Include equipment, pre-test checks, measurements, and safety considerations.
* Download the resulting checklist.

### 📥 Report Export

* Download a Markdown report summarizing the loaded documents and available outputs.

## 🛠️ Technology Stack

* **Python** — application logic
* **Streamlit** — user interface
* **PyMuPDF** — PDF text extraction
* **OpenAI Python SDK** — API client for OpenRouter
* **OpenRouter** — access to compatible AI models
* **python-dotenv** — environment-variable configuration

## 🚀 Getting Started

### Prerequisites

Install Python and Git. You will also need an OpenRouter API key to use the AI features.

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd benchbuddy-ai
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with the URL of your published repository.

Alternatively, download the repository and open its folder in VS Code.

### 2. Create a virtual environment

On Windows:

```bash
python -m venv .venv
```

Activate it in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If activation is blocked by your PowerShell execution policy, you can instead run the commands using the Python executable inside `.venv`, or use the VS Code Command Prompt terminal.

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure the API key

Create a file named `.env` in the project root:

```text
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=openrouter/free
```

Replace the placeholder with your own API key.

The application defaults to `openrouter/free` when `OPENROUTER_MODEL` is not set. Model availability and rate limits depend on the provider.

**Never commit your `.env` file or publish your API key.**

### 5. Run the application

```bash
python -m streamlit run app.py
```

Open the local address shown in the terminal, usually:

```text
http://localhost:8501
```

### 6. Use BenchBuddy AI

1. Upload a component datasheet in PDF format.
2. Search for relevant specifications.
3. Ask questions about the document.
4. Upload a second datasheet to request a comparison.
5. Generate a virtual bench-test checklist.
6. Export the available results as Markdown.

## 🔍 Current Limitations

* PDF processing extracts selectable text. Image-only scanned PDFs may not provide usable text because OCR is not currently implemented.
* Search uses keyword matching and ranking rather than a dedicated semantic retrieval system.
* AI answers are based on selected document excerpts. Relevant information may be missed if it is not included in those excerpts.
* Component comparisons depend on the information extracted from both documents and may omit important differences.
* AI-generated test plans are planning aids, not validated laboratory procedures.
* Availability, latency, and output quality depend on the configured AI provider and model.

## 🔐 Privacy and Safety

PDF text excerpts and prompts may be sent to OpenRouter when an AI feature is used. Do not upload confidential documents unless you have permission and understand the provider's applicable data-handling terms.

BenchBuddy AI is an educational assistant. Always verify component ratings, pinouts, recommended operating conditions, and test procedures against the manufacturer's original datasheet. Do not use AI-generated instructions as a substitute for appropriate laboratory supervision.

## 🗺️ Future Improvements

Potential improvements include:

* More robust specification extraction
* Semantic document retrieval
* Structured specification tables
* Side-by-side component comparison
* Improved handling of scanned datasheets
* More comprehensive downloadable reports
* Automated tests and a deployment guide

## 🤝 Contributing

Contributions, bug reports, and suggestions are welcome.

Before submitting a change, test the affected functionality and avoid committing API keys, environment files, or local virtual environments.

## 📄 License

A license has not yet been selected. Add an appropriate open-source license before presenting the repository as formally licensed for reuse.

---

**BenchBuddy AI — making electronics datasheets easier to explore.**
