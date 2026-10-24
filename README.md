# BenchBuddy AI 🔧

**An AI-powered electronics datasheet assistant for students, makers, and engineers.**

BenchBuddy AI helps users explore electronic component datasheets, find specifications, ask questions about technical documents, compare components, and generate virtual bench-test checklists.

The goal is to make electronics documentation easier to navigate and help learners understand component specifications more efficiently.

## 💡 The Problem

Electronics datasheets contain important information about electrical characteristics, operating conditions, pin configurations, and component limitations.

Finding the right specifications can be time-consuming, especially for students who are still learning how to interpret technical documentation.

BenchBuddy AI combines PDF text extraction, keyword-based search, and AI-assisted explanations to simplify this process.

## ✨ Features

### 📄 1. Datasheet Processing

- Upload electronics component datasheets in PDF format.
- Extract selectable text from individual pages.
- View document page counts and basic statistics.
- Inspect extracted text from individual pages.

### 🔎 2. Specification Search

- Search for terms such as operating temperature, supply voltage, and input offset voltage.
- Rank matching pages using keyword matching.
- View relevant extracted text and matched search terms.

### 🤖 3. AI Datasheet Assistant

- Ask questions about an uploaded datasheet.
- Send selected document excerpts to an AI model through OpenRouter.
- Request answers with supporting page references.
- Inspect the source excerpts used to generate an answer.

### ⚖️ 4. Component Comparison

- Upload two component datasheets.
- Request an AI-generated comparison of selected specifications.
- Identify information that is missing from the supplied excerpts.
- Download a comparison as a Markdown file.

### 🧪 5. Virtual Bench-Test Planning

- Generate a structured checklist for planning component tests.
- Include equipment, pre-test checks, procedures, measurements, and safety considerations.
- Generate a generic checklist when AI is unavailable.
- Download the resulting checklist as a Markdown file.

### 📥 6. Workspace Report

- Summarize the loaded datasheets and their basic statistics.
- Include available search results and generated outputs.
- Download a Markdown report for later reference.

## 🛠️ Technology Stack

- **Python** — application logic
- **Streamlit** — interactive web interface
- **PyMuPDF** — PDF text extraction
- **OpenAI Python SDK** — API client
- **OpenRouter** — access to compatible AI models
- **python-dotenv** — environment-variable configuration

## 🚀 Getting Started

### Prerequisites

Install Python and Git before starting.

An OpenRouter API key is required for the AI-powered features. PDF extraction and keyword search can be used without an API key.

### 1. Clone the repository

```bash
git clone https://github.com/Vaishali171/benchbuddy-ai.git
cd benchbuddy-ai
```

### 2. Create a virtual environment

On Windows:

```powershell
python -m venv .venv
```

Activate the environment using PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If you use another terminal, activate the virtual environment using the appropriate command for that terminal.

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure your API key

Create a file named `.env` in the project root.

Add the following settings:

```dotenv
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=openrouter/free
```

Replace `your_openrouter_api_key` with your own OpenRouter API key.

The example above uses OpenRouter's free-model router. You can configure another compatible model through the `OPENROUTER_MODEL` environment variable.

**Never publish your API key or commit your `.env` file to GitHub.**

### 5. Run BenchBuddy AI

```powershell
python -m streamlit run app.py
```

Open the local address displayed in your terminal. It is usually:

http://localhost:8501

### 6. Use the application

1. Upload an electronics datasheet in PDF format.
2. Search for component specifications.
3. Ask questions about the document using the AI assistant.
4. Upload a second datasheet to request a component comparison.
5. Generate a virtual bench-test checklist.
6. Export the available results as Markdown files.

## 🔍 Current Limitations

- PDF processing extracts selectable text. Scanned image-only documents may not provide usable text because OCR is not currently implemented.
- Search uses keyword-based ranking rather than a dedicated semantic retrieval system.
- The AI receives selected document excerpts, so relevant information elsewhere in the PDF may be missed.
- AI-generated answers may be incomplete or inaccurate, even when page references are requested.
- Component comparisons depend on the information present in the selected excerpts.
- Generated bench-test plans are planning aids, not validated manufacturer procedures.
- AI availability and response quality depend on the configured provider, model, network connection, and rate limits.

## 🔐 Privacy and Safety

When an AI feature is used, selected PDF text and the user's question may be sent to OpenRouter for processing.

Do not upload confidential documents unless you have permission and understand the applicable data-handling terms.

BenchBuddy AI is an educational tool. Always verify component ratings, pin configurations, recommended operating conditions, and test procedures against the manufacturer's original datasheet.

Do not treat AI-generated instructions as a substitute for appropriate laboratory supervision.

## 🗺️ Future Improvements

Potential areas for development include:

- More accurate specification extraction
- Semantic document retrieval
- Structured specification tables
- Side-by-side component comparisons
- OCR support for scanned datasheets
- Improved report generation
- Automated tests
- Deployment and hosting instructions

## 🤝 Contributing

Contributions, bug reports, and suggestions are welcome.

When contributing:

- Test changes before submitting them.
- Keep API keys and other secrets out of source control.
- Document new features and known limitations.
- Include steps to reproduce reported bugs when possible.

## 📄 License

A license has not yet been selected for this repository.

Add an appropriate open-source license before presenting the project as formally licensed for reuse.

---

**BenchBuddy AI — making electronics datasheets easier to explore.**