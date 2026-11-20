"""Cluster hero role-terms into archetypes, three independent ways, and build a consensus.
A term is characterised by the books whose hero it describes, seen through three views:
  emb    - sentence embeddings of the blurb sentences about him
  words  - TF-IDF of blurb words (the role terms themselves removed)
  shelf  - Goodreads reader shelves (readers' own tags; no blurb text involved)
Usage: 04_cluster.py K"""
import json, sys, itertools
import numpy as np, pandas as pd, scipy.sparse as sp
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import adjusted_rand_score as ari
from sklearn.preprocessing import normalize

K = int(sys.argv[1]) if len(sys.argv) > 1 else 0
# generic person words and parser debris: they say nothing about what kind of man he is
STOP = {w.replace("_", " ") for w in """man guy boy male person kind sort author today t s f no off long co material head
subject organization ticket serial member opposite only_person only_hope fantasy hero catch craving awakening shell ink
walker stick unit duo tool cut third ray pick nickname definition epitome complete_opposite replacement factor fix
copyright walking bent multi centre holden damnation user constant calm shield donor native ward mark rock youth breed
fellow safe_haven bad_news legend publisher host guide patient customer client fish ace maker breaker stray anchor peer
official senior junior""".split()}

df = pd.read_parquet("data/books.parquet")
vocab = pd.read_parquet("data/vocab.parquet").set_index("term")
hero = [sorted({t for t, _ in json.loads(h)} - STOP) for h in df.hero]
cnt = pd.Series([t for h in hero for t in h]).value_counts()
terms = [t for t in cnt.index if cnt[t] >= 150 and vocab.male[t] >= .55]
tid = {t: i for i, t in enumerate(terms)}
r, c = zip(*[(i, tid[t]) for i, h in enumerate(hero) for t in h if t in tid])
B = sp.csr_matrix((np.ones(len(r), np.float32), (r, c)), shape=(len(df), len(terms)))
print(len(terms), "terms;", (B.sum(1) > 0).mean().round(3), "of books covered")

# --- three views of each book
E = np.load("data/emb.npy").astype(np.float32)
tv = TfidfVectorizer(min_df=50, max_features=20000, stop_words="english", sublinear_tf=True)
W = tv.fit_transform(df.text.str[:1500])
own = {w for t in terms for w in t.split()} | {w + "s" for t in terms for w in t.split()}
W = W @ sp.diags([0. if w in own else 1. for w in tv.get_feature_names_out()])
gr = np.where(df.source == "goodreads")[0]
shelves = [json.loads(s) for s in df.tags[gr]]
top = pd.Series([k for s in shelves for k in s]).value_counts()
top = top[(top >= 300) & (top <= .3 * len(gr))].index  # drop near-universal shelves (to-read, romance, kindle...)
sid = {s: i for i, s in enumerate(top)}
r, c, v = zip(*[(i, sid[k], n / sum(s.values())) for i, s in enumerate(shelves) for k, n in s.items() if k in sid])
S = sp.csr_matrix((np.sqrt(v), (r, c)), shape=(len(gr), len(top)), dtype=np.float32)
own_s = [0. if any(w in s for t in terms for w in t.split() if len(w) > 3) else 1. for s in top]
S_blind = S @ sp.diags(own_s)  # also hide shelves that literally name a role ("vampires", "cowboys")


def cent(X, rows):
    """centroid of each term's books, relative to the average book"""
    Bs, Xs = B[rows], X[rows] if X.shape[0] == len(df) else X
    n = np.asarray(Bs.sum(0)).ravel()
    P = Bs.T @ Xs
    C = np.asarray(P.todense() if sp.issparse(P) else P) / np.maximum(n, 1)[:, None] - np.asarray(Xs.mean(0))
    return normalize(C), n >= 30


def cluster(C, k, algo):
    if algo == "ward": return AgglomerativeClustering(k).fit_predict(C)
    return KMeans(k, n_init=10, random_state=0).fit_predict(C)


allrows = np.arange(len(df))
views = {"emb": cent(E, allrows)[0], "words": cent(W, allrows)[0], "shelf": cent(S_blind, gr)[0]}
rng = np.random.default_rng(0)
if not K:  # scan k: agreement between views, sources and bootstraps
    for k in (8, 10, 12, 15, 18, 22, 26, 30, 36):
        lab = {v: cluster(C, k, "ward") for v, C in views.items()}
        cross = np.mean([ari(lab[a], lab[b]) for a, b in itertools.combinations(lab, 2)])
        boot = np.mean([ari(lab["emb"], cluster(cent(E, rng.integers(0, len(df), len(df)))[0], k, "ward")) for _ in range(5)])
        (Cg, okg), (Ck, okk) = cent(E, gr), cent(E, np.where(df.source == "kindle")[0])
        ok = okg & okk
        src = ari(cluster(Cg[ok], k, "ward"), cluster(Ck[ok], k, "ward"))
        print(f"k={k:2d}  cross-view ARI {cross:.2f}  bootstrap ARI {boot:.2f}  goodreads-vs-kindle ARI {src:.2f}")
    sys.exit()

# --- consensus: how often do two terms land together across views x algorithms x sources x bootstraps?
runs = [(cluster(C, K, a), np.ones(len(terms), bool)) for C in views.values() for a in ("ward", "kmeans")]
for rows in [gr, np.where(df.source == "kindle")[0]] + [rng.integers(0, len(df), len(df)) for _ in range(6)]:
    C, ok = cent(E, rows)
    lab = np.full(len(terms), -1); lab[ok] = cluster(C[ok], K, "ward")
    runs.append((lab, ok))
co, seen = np.zeros((len(terms),) * 2), np.zeros((len(terms),) * 2)
for lab, ok in runs:
    m = np.outer(ok, ok)
    co += m & (lab[:, None] == lab[None, :]); seen += m
co /= np.maximum(seen, 1)
final = AgglomerativeClustering(K, metric="precomputed", linkage="average").fit_predict(1 - co)
out = []
for k in pd.Series(final).value_counts().index:
    idx = np.where(final == k)[0]
    stab = co[np.ix_(idx, idx)][np.triu_indices(len(idx), 1)].mean() if len(idx) > 1 else 1.
    ts = sorted((terms[i] for i in idx), key=lambda t: -cnt[t])
    out.append(dict(id=int(k), stability=round(float(stab), 2), terms=ts))
    print(f"\n#{k} stability={stab:.2f} n={len(ts)}: " + ", ".join(f"{t}({cnt[t]})" for t in ts))
json.dump(out, open("data/clusters.json", "w"), indent=1)
print("\nconsensus vs single views (ARI):", {v: round(ari(final, cluster(C, K, 'ward')), 2) for v, C in views.items()})
