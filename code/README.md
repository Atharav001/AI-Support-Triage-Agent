# HackerRank Orchestrate RAG Agent

This directory contains the codebase for a complete, deterministic, Retrieval-Augmented Generation (RAG) triage agent capable of parsing support tickets and grounding answers exclusively within the local support corpus.

## Architecture

* `main.py`: Entry point. Parses `support_tickets.csv`, orchestrates ticket routing utilizing thread pools, and writes results back to `output.csv`.
* `agent.py`: Houses the central orchestrator logic to coordinate retreival, classification, prompt building, and interaction with OpenAI.
* `classifier.py`: Initial keyword-based and LLM-assisted request routing along with strict escalation checks for sensitive queries (e.g., fraud, legal, security breach).
* `retriever.py`: FAISS-backed document store containing embeddings (generated locally via `sentence-transformers/all-MiniLM-L6-v2`) extracted from the `data/` directory.
* `config.py`: Central configuration manager handling environment variables, deterministic seeds, and hyperparameters.

## Installation

You need Python 3.9+ to run this agent.

1. Navigate to the `code/` directory:
   ```bash
   cd code
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

The agent requires access to the OpenAI API for LLM reasoning. Ensure that you have exported the key to your environment before execution:

```bash
export OPENAI_API_KEY="your-sk-api-key-here"
```

## Running the Agent

To execute the agent against the provided `support_tickets.csv` inputs:

```bash
python main.py
```

The agent will load the local documentation, build the vector index, evaluate the tickets without accessing the live web for ground-truth information, and then output the final predictions adhering strictly to the schema in `../support_tickets/output.csv`.
