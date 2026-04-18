\# AccessCompanion ⌨️

\### \*An Agentic AI assistant for NVDA screen reader users.\*



\*\*AccessCompanion\*\* is a multi-agent conversational assistant designed to help visually-impaired users master the \*\*NVDA screen reader\*\*. Instead of digging through a 100-page manual, users can simply ask questions in natural language and receive specific, step-by-step guidance grounded in the official documentation.



This tool bridges the gap between complex software documentation and practical user independence by providing an interactive, accessible interface for technical learning.



---



\## 🚀 Key Features

\- \*\*Intelligent RAG Pipeline\*\*: Ingests and processes the official NVDA manual while maintaining the context of shortcuts and command tables.

\- \*\*Agentic Orchestration\*\*: Uses a multi-agent workflow (Router -> Retriever -> Assistant) to handle both technical documentation and social interactions.

\- \*\*Stateful Memory\*\*: Remembers conversational context (e.g., asking "how do I use headings?" followed by "what about links?" without repeating the topic).

\- \*\*Accessibility-First Design\*\*: 

&nbsp; - \*\*Non-Visual Cues\*\*: Pygame-powered "Tik-Tik" sound to indicate the AI is processing.

&nbsp; - \*\*Screen Reader Optimized\*\*: UI integrated with \*\*ARIA-live regions\*\* and logical heading structures (H2/H3) for seamless navigation.

&nbsp; - \*\*Global Shortcuts\*\*: Alt+Shift keys for theme toggling, new conversations, and more.



---



\## 🛠️ Tech Stack

\- \*\*Frameworks\*\*: \[LangChain](https://www.langchain.com/) \& \[LangGraph](https://www.langchain.com/langgraph) (Agent Orchestration \& State Management)

\- \*\*AI Models\*\*: Google Gemini 2.5 Flash (LLM) \& Gemini-001 (Embeddings)

\- \*\*Vector Database\*\*: \[ChromaDB](https://www.trychroma.com/)

\- \*\*UI/Frontend\*\*: \[Streamlit](https://streamlit.io/)

\- \*\*Libraries\*\*: BeautifulSoup (Web Scraping), Pygame (Audio Feedback), Python Dotenv



---



\## 📁 Project Structure

```text

.

├── app.py              # Streamlit Web UI \& Accessibility Logic

├── assistant.py        # LangGraph Multi-Agent Workflow

├── ingest.py           # Manual Scraping \& Vector DB Ingestion

├── tik.wav             # Rhythmic "Tik-Tik" audio cue

├── requirements.txt    # Project Dependencies

└── README.md           # Project Documentation

