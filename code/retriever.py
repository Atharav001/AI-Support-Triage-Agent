import os
import glob
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import config

class Retriever:
    def __init__(self, data_dir=config.DATA_DIR):
        self.data_dir = data_dir
        self.model = SentenceTransformer(config.EMBEDDING_MODEL)
        self.documents = []
        self.index = None
        self._load_documents()
        self._build_index()

    def _load_documents(self):
        extensions = ['**/*.md', '**/*.txt', '**/*.html']
        for ext in extensions:
            for filepath in glob.glob(os.path.join(self.data_dir, ext), recursive=True):
                if not os.path.isfile(filepath):
                    continue
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if content.strip():
                        rel_path = os.path.relpath(filepath, self.data_dir)
                        domain = rel_path.split(os.sep)[0].lower()
                        self.documents.append({
                            "content": content,
                            "domain": domain,
                            "source": filepath
                        })
        
    def _build_index(self):
        if not self.documents:
            dim = self.model.get_sentence_embedding_dimension()
            self.index = faiss.IndexFlatIP(dim)
            return

        texts = [doc["content"] for doc in self.documents]
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        faiss.normalize_L2(embeddings)
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(embeddings)

    def search(self, query, domain=None, k=5):
        if not self.documents or self.index is None:
            return [], []

        query_emb = self.model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(query_emb)
        
        search_k = min(len(self.documents), k * 10)
        if search_k == 0:
            return [], []
            
        distances, indices = self.index.search(query_emb, search_k)

        results = []
        sims = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1: continue
            doc = self.documents[idx]
            if domain:
                if domain.lower() not in doc["domain"].lower():
                    continue
            results.append(doc)
            sims.append(dist)
            if len(results) == k:
                break
        return results, sims
