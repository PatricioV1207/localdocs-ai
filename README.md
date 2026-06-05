# LocalDocs AI

LocalDocs AI is an open-source, local-first app that turns document folders into private, searchable, AI-assisted knowledge bases.

It helps users process local documents, ask questions, generate summaries, and export useful notes without requiring a cloud-first workflow.

> Status: v0.1 MVP in development.

## Why LocalDocs AI?

Many people have useful information trapped inside PDFs, notes, guides, manuals, and Markdown files.

LocalDocs AI helps turn those files into a searchable knowledge base.

The project focuses on:

- Local-first document processing
- Privacy-friendly workflows
- Answers with source references
- Markdown exports
- Simple open-source architecture
- Study and research use cases

This project is not intended to be just another "chat with PDF" app. The long-term goal is to become a private knowledge base tool for students, researchers, teachers, developers, and small teams.

## v0.1 Features

The first MVP version aims to support:

- PDF parsing
- TXT parsing
- Markdown parsing
- Text chunking
- Local TF-IDF search
- Question answering with source references
- Extractive fallback without an API key
- Optional OpenAI integration if `OPENAI_API_KEY` is configured
- Basic document summaries
- Markdown export for summaries and Q&A history
- Streamlit interface
- Basic tests

## What v0.1 is not

v0.1 is not a final product.

It does not include:

- User accounts
- Cloud sync
- Authentication
- Payment features
- OCR
- Audio transcription
- Image analysis
- Advanced vector databases
- Desktop packaging
- Mobile app
- Multi-user collaboration

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/localdocs-ai.git
cd localdocs-ai
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
streamlit run app.py
```

## Optional OpenAI configuration

LocalDocs AI must work without an OpenAI API key.

However, if you want optional LLM-generated answers, create a `.env` file:

```env
OPENAI_API_KEY=your_api_key_here
```

If no API key is configured, the app will use local extractive answers based on the most relevant document chunks.

## Usage

1. Open the Streamlit app.
2. Upload PDF, TXT, or Markdown documents.
3. Click the processing button.
4. Ask a question about your documents.
5. Review the answer and cited sources.
6. Generate summaries.
7. Export results to Markdown.

## Example workflow

Upload documents such as:

```txt
sample_docs/
├── sample_note.txt
└── sample_guide.md
```

Ask:

```txt
What is the main idea of the guide?
```

The app should return an answer with source references, for example:

```md
Sources:
- sample_guide.md, chunk 2
```

## Project structure

```txt
localdocs-ai/
├── README.md
├── LICENSE
├── requirements.txt
├── app.py
├── AGENTS.md
├── docs/
│   ├── goal.md
│   ├── architecture.md
│   └── roadmap.md
├── localdocs/
│   ├── parser.py
│   ├── chunker.py
│   ├── indexer.py
│   ├── search.py
│   ├── qa.py
│   ├── summarizer.py
│   ├── export.py
│   └── models.py
├── sample_docs/
├── exports/
└── tests/
```

## Roadmap

### v0.1

- PDF/TXT/Markdown support
- Local TF-IDF search
- Answers with sources
- Basic summaries
- Markdown export
- Streamlit UI

### v0.2

- DOCX support
- Improved UI
- Better summaries
- Configuration file
- Better error handling

### v0.3

- Obsidian export
- Anki flashcard export
- Local embeddings
- More robust indexing

### v0.4

- Research comparison mode
- Study mode
- Multi-project knowledge bases

### v1.0

- Stable API
- Plugin system
- More document formats
- Desktop packaging

## Contributing

Contributions are welcome.

Good first contributions may include:

- Improving document parsing
- Adding tests
- Improving the Streamlit interface
- Improving documentation
- Adding sample documents
- Improving Markdown export

Please keep the project simple, local-first, and beginner-friendly.

## License

This project is intended to use the MIT License.