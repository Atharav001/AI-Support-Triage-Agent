# AI Support Triage Agent

A robust, terminal-based Retrieval-Augmented Generation (RAG) agent built for the HackerRank Orchestrate hackathon. It intelligently triages, routes, and answers real support tickets across three distinct product ecosystems: **HackerRank**, **Claude**, and **Visa**, using exclusively a local support corpus.

---

## 🚀 How This Works

The agent processes support tickets via an automated, intelligent pipeline:
1. **Ingestion**: Reads the incoming support tickets from `support_tickets/support_tickets.csv`.
2. **Classification & Escalation**: Uses a hybrid keyword and LLM-assisted classifier to identify the request type (`product_issue`, `feature_request`, `bug`, `invalid`) and the product area. High-risk, sensitive, or unsupported cases (e.g., fraud, legal, security) are strictly and automatically **escalated**.
3. **Retrieval**: For safe queries, it queries a local vector database to fetch the most relevant support documentation from the `data/` corpus. 
4. **Generation**: The retrieved context is passed to the LLM to generate a grounded, user-facing response along with a concise justification. Hallucination is actively suppressed.
5. **Output**: Predictions are deterministically written to `support_tickets/output.csv`.

---

## 🏗️ What This Is Made Of

The agent is built using **Python** and leverages the following core components:
* **FAISS**: For lightning-fast, local vector similarity search.
* **sentence-transformers (`all-MiniLM-L6-v2`)**: To generate dense, locally-computed text embeddings of the support corpus.
* **OpenAI API**: To perform LLM-based reasoning, classification, and grounded response synthesis.
* **Thread Pools**: To process multiple support tickets concurrently.

### System Architecture (`code/`)
* **`main.py`**: The entry point. Parses inputs, orchestrates concurrent ticket routing, and writes outputs.
* **`agent.py`**: The central orchestrator coordinating retrieval, classification, and prompt generation.
* **`classifier.py`**: Handles request routing and strict escalation checks for sensitive queries.
* **`retriever.py`**: The FAISS-backed document store containing embeddings extracted from the local docs.
* **`config.py`**: Central configuration manager for environment variables and deterministic seeds.

---

## 🛠️ How It Is Made

1. **Local Document Indexing**: On startup, the agent parses the static support corpus in the `data/` directory. It splits the documents into chunks and computes dense embeddings locally using `sentence-transformers`. These embeddings are indexed using `FAISS`.
2. **Strict Grounding**: The LLM prompt is engineered to *only* rely on the context provided by the local FAISS retriever. Web calls and external knowledge bases are disabled to ensure the agent cannot hallucinate policies not found in the official corpus.
3. **Deterministic Execution**: The system uses seeded randomization and conservative LLM temperature settings to ensure results are as deterministic and reliable as possible.
4. **Security & Guardrails**: The classifier runs an initial sweep on the text before retrieval to catch severe issues early, preventing the AI from confidently answering queries related to fraud or legal disputes.

---

## 📂 Repository Layout

```
.
├── AGENTS.md                       # Rules for AI coding tools + transcript logging
├── problem_statement.md            # Full task description and I/O schema
├── README.md                       # You are here
├── code/                           # Core agent logic and scripts
│   ├── main.py                     # Entry point
│   └── README.md                   # Agent setup and configuration details
├── data/                           # Local-only support corpus
│   ├── hackerrank/                 # HackerRank help center
│   ├── claude/                     # Claude Help Center export
│   └── visa/                       # Visa consumer + small-business support
└── support_tickets/
    ├── sample_support_tickets.csv  # Inputs + expected outputs
    ├── support_tickets.csv         # Inputs to evaluate
    └── output.csv                  # Agent's final predictions
```

---

## ⚡ Quickstart

1. **Clone the repository:**
   ```bash
   git clone git@github.com:interviewstreet/hackerrank-orchestrate-may26.git
   cd hackerrank-orchestrate-may26
   ```
2. **Navigate to the code directory:**
   ```bash
   cd code
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Set your API Key:**
   ```bash
   export OPENAI_API_KEY="your-sk-api-key-here"
   ```
5. **Run the Agent:**
   ```bash
   python main.py  # Use 'python3 main.py' on macOS
   ```

*(See `code/README.md` for more execution details.)*

---

## 📝 Hackathon Submission Details

This repository ships with an `AGENTS.md` file that ensures any AI coding tools (like Cursor, Claude Code, etc.) append their conversation turns to a single shared log file. This file will be submitted as the **Chat Transcript**.

Submissions are made on the HackerRank Community Platform via three files:
1. **Code zip**: The zipped `code/` directory.
2. **Predictions CSV**: The populated `support_tickets/output.csv`.
3. **Chat transcript**: Your local `log.txt` generated by your AI agent.