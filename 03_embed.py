"""Sentence-embed the parts of each blurb that talk about the man (sentences with he/him/his)."""
import re, sys
import numpy as np, pandas as pd
from sentence_transformers import SentenceTransformer

df = pd.concat(pd.read_parquet(f"data/{s}.parquet", columns=["text"]) for s in ["goodreads", "kindle", "wattpad"])
he = re.compile(r"\b(he|him|his)\b", re.I)
texts = [" ".join(s for s in re.split(r"(?<=[.!?])\s+", t[:1500]) if he.search(s)) or t[:500] for t in df.text]
model = SentenceTransformer("all-MiniLM-L6-v2", device="mps")
E = model.encode(texts, batch_size=256, show_progress_bar=False, normalize_embeddings=True)
np.save("data/emb.npy", E.astype(np.float16))
print(E.shape)
