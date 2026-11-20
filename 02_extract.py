"""Extract what each blurb says the male lead *is*. Nothing is predefined: the role vocabulary and the
maleness of each role noun are all learned from the corpus itself.
Patterns: attr ("he is a duke"), appos ("Jake, a former SEAL"), title ("Sheriff Jake Ryan"), bare (any noun)."""
import json, sys, collections, multiprocessing as mp
import pandas as pd

M, F = {"he", "him", "his", "himself"}, {"she", "her", "hers", "herself"}
BE = {"be", "become", "remain"}


def anchor(t):
    w = t.lower_
    if w in M: return "M"
    if w in F: return "F"
    if t.pos_ == "PROPN": return "N:" + " ".join(c.lower_ for c in t.subtree if c.pos_ == "PROPN")
    return None


def work(texts):
    import spacy
    nlp = spacy.load("en_core_web_sm")
    out = []
    for doc in nlp.pipe(texts, batch_size=64):
        cands = []
        for t in doc:
            if t.pos_ not in ("NOUN", "PROPN") or not t.is_alpha: continue
            pat = anc = None
            head = t.head
            if t.dep_ == "conj" and head.dep_ == "attr": head = head.head
            if (t.dep_ == "attr" or head is not t.head) and head.lemma_ in BE:
                subj = [c for c in head.children if c.dep_ == "nsubj"]
                if subj: pat, anc = "attr", anchor(subj[0])
            elif t.dep_ == "appos" and t.pos_ == "NOUN" and t.head.pos_ == "PROPN": pat, anc = "appos", anchor(t.head)
            elif t.dep_ == "appos" and t.pos_ == "PROPN" and t.head.pos_ == "NOUN":
                cands.append(term(t.head) + ("appos", anchor(t)))
                continue
            elif t.dep_ == "compound" and t.head.pos_ == "PROPN": pat, anc = "title", anchor(t.head)
            if pat is None and t.pos_ == "NOUN" and not any(c.dep_ == "poss" for c in t.children): pat = "bare"
            if pat: cands.append(term(t) + (pat, anc))
        out.append(json.dumps(cands))
    return out


def term(t):
    left = [c for c in t.lefts if c.i == t.i - 1 and c.dep_ in ("compound", "amod") and c.is_alpha]
    adjs = [c.lemma_.lower() for c in t.lefts if c.dep_ == "amod"]
    lem = t.lemma_.lower()
    return (lem, left[0].lemma_.lower() + " " + lem if left else None, t.pos_ == "NOUN", adjs)


if __name__ == "__main__":
    import os, pickle
    df = pd.concat(pd.read_parquet(f"data/{s}.parquet") for s in ["goodreads", "kindle", "wattpad"]).reset_index(drop=True)
    if not os.path.exists("data/raw.pkl"):
        texts = [t[:1500] for t in df.text]
        chunks = [texts[i:i + 2000] for i in range(0, len(texts), 2000)]
        with mp.Pool(9) as pool:
            pickle.dump([json.loads(r) for part in pool.imap(work, chunks) for r in part], open("data/raw.pkl", "wb"))
    raw = pickle.load(open("data/raw.pkl", "rb"))

    # 1. first-name gender from US birth-record counts (names >=90% one sex)
    n = pd.read_csv("data/names/us-names-by-gender.csv").pivot_table(index="name", columns="sex", values="count", fill_value=0)
    n = n[(n.sum(axis=1) >= 500) & (n.max(axis=1) / n.sum(axis=1) >= .9)]
    name_g = {k.lower(): g for k, g in n.idxmax(axis=1).items()}

    def gender(a):
        if a in ("M", "F", None): return a
        return name_g.get(a[2:].split()[0]) if len(a) > 2 else None

    # 2. role vocabulary = nouns mostly said *of a person* (predicate, apposition or title); maleness from gendered uses
    uni, pred, per, mf = *(collections.Counter() for _ in range(3)), collections.defaultdict(collections.Counter)
    for cands in raw:
        for lem, big, is_noun, adjs, pat, anc in cands:
            g = gender(anc) if pat != "bare" else None
            for t in filter(None, (lem, big)):
                uni[t] += 1
                pred[t] += bool(g) and is_noun and pat in ('attr', 'appos')  # "he is a duke"
                per[t] += pat != "bare" and anc is not None
                if g: mf[t][g] += 1
    ok = lambda t: pred[t] >= 8 and pred[t] >= .012 * uni[t] and per[t] >= .1 * uni[t]  # drops "chance", places, first names
    keep_bi = {b for b in uni if " " in b and ok(b) and uni[b] >= .1 * uni[b.split()[1]]}  # "rock star", "bad boy", not "sexy billionaire"
    vocab = {t for t in uni if " " not in t and ok(t)} | keep_bi
    male = {t: (mf[t]["M"] + 1) / (mf[t]["M"] + mf[t]["F"] + 2) for t in vocab}

    # 3. per-book hero descriptors
    heroes, adj_out = [], []
    for cands in raw:
        terms, adjs = [], []
        cands = [(big if big in keep_bi else lem, a, pat, gender(anc) if pat != "bare" else None) for lem, big, _, a, pat, anc in cands]
        fem = {t for t, _, _, g in cands if g == "F"}  # "she is a vampire" -> bare "vampire" in this blurb is not him
        for t, a, pat, g in cands:
            if t not in vocab: continue
            if g == "M" or (g is None and male[t] >= .55 and t not in fem):
                terms.append([t, pat if g else "bare"])
                adjs += a
        heroes.append(json.dumps(terms)); adj_out.append(json.dumps(adjs))
    df["hero"], df["adjs"] = heroes, adj_out
    df.to_parquet("data/books.parquet")
    pd.DataFrame({"term": list(vocab), "n": [uni[t] for t in vocab], "male": [male[t] for t in vocab],
                  "m": [mf[t]["M"] for t in vocab], "f": [mf[t]["F"] for t in vocab]}).to_parquet("data/vocab.parquet")
    print(len(df), "books;", len(name_g), "names;", len(vocab), "role terms;",
          f"{(df.hero != '[]').mean():.0%} of books have a hero descriptor")
