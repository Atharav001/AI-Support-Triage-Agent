import os

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
MODEL_NAME = "gpt-4o-mini"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
SIMILARITY_THRESHOLD = 0.3
MAX_TOKENS = 500

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
INPUT_CSV = os.path.join(BASE_DIR, "support_tickets", "support_tickets.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "support_tickets")
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "output.csv")
