🧠 NotebookLM Clone
An AI-powered document intelligence application inspired by Google's NotebookLM. This project enables users to upload and interact with PDFs, text files, websites, YouTube videos, and audio files through a conversational interface. It leverages Retrieval-Augmented Generation (RAG) to retrieve relevant information from uploaded content and generate accurate, context-aware responses with source citations.

🚀 Features
📄 Upload and process PDF, TXT, and Markdown documents
🌐 Extract content from websites using Firecrawl
🎥 Process YouTube videos by generating transcripts
🎙️ Transcribe audio files using AssemblyAI
🧠 RAG-based question answering with source citations
🔍 Semantic search using vector embeddings
💬 Interactive chat interface built with Streamlit
🧾 Conversation memory integration using Zep
🎧 AI-generated podcast scripts and audio from uploaded content
🌙 Modern dark-themed UI inspired by Google NotebookLM
🛠️ Tech Stack
Language: Python
Frontend: Streamlit
LLM: OpenAI GPT Models
Embeddings: OpenAI Embeddings / BAAI BGE
Vector Database: FAISS
Memory: Zep Cloud
Web Scraping: Firecrawl
Audio Transcription: AssemblyAI
Document Processing: PyPDF, LangChain
Podcast Generation: OpenAI + Kokoro TTS
⚙️ Workflow
Upload documents, websites, audio, or YouTube links.
Extract and preprocess the content.
Split content into chunks.
Generate vector embeddings.
Store embeddings in FAISS.
Retrieve the most relevant chunks based on the user's query.
Generate accurate, source-grounded responses using an OpenAI language model.
Store conversation history using Zep for contextual interactions.
📌 Use Cases
Research assistance
Academic learning
Technical documentation search
Business knowledge management
Meeting and lecture analysis
AI-powered document exploration
📷 Interface
Dark-themed NotebookLM-style UI
Source management sidebar
Interactive chat interface
Citation tooltips
Podcast generation studio
🔑 Environment Variables
Create a .env file and add:

OPENAI_API_KEY=your_openai_api_key
ASSEMBLYAI_API_KEY=your_assemblyai_api_key
FIRECRAWL_API_KEY=your_firecrawl_api_key
ZEP_API_KEY=your_zep_api_key
▶️ Run Locally
git clone <repository-url>
cd notebook-lm-clone

python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt

streamlit run app.py
Image ## 📖 Future Enhancements
Multi-user authentication
Cloud document storage
Support for DOCX, PPTX, and Excel files
Advanced citation visualization
Multi-language document understanding
OCR support for scanned PDFs Project structure
