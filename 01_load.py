"""Normalise all sources into data/books.parquet: source, id, title, text, tags, year, pop, pub."""
import gzip, json, re, sys, glob
import pandas as pd

D = "data/"
TRAD = re.compile(r"harlequin|avon|berkley|penguin|random house|harper|simon|st\. martin|grand central|"
                  r"kensington|zebra|sourcebooks|mills|silhouette|ballantine|bantam|pocket|signet|jove|dell|"
                  r"forever|entangled|carina|macmillan|hachette|tor|ace|love inspired|montlake|william morrow|"
                  r"atria|gallery|little, brown|scholastic|headline|piatkus|mira|hqn|loveswept|leisure|dorchester", re.I)
SELF = re.compile(r"^$|createspace|smashwords|amazon digital|independently|self[- ]?pub|kindle|lulu|draft2digital|author", re.I)
clean = lambda s: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s or "")).strip()
english = lambda s: len(re.findall(r"\b(the|and|her|his|he|she|to|of)\b", s.lower())) >= 8


def goodreads():
    works = {}
    for line in gzip.open(D + "goodreads/books_romance.json.gz", "rt"):
        b = json.loads(line)
        w = works.setdefault(b["work_id"] or b["book_id"], dict(pop=0, year=9999, best=-1))
        n = int(b["ratings_count"] or 0)
        w["pop"] += n
        y = int(b["publication_year"] or 0)
        if 1950 <= y <= 2018: w["year"] = min(w["year"], y)
        text = clean(b["description"])
        if n > w["best"] and len(text) > 200 and english(text):
            shelves = {s["name"]: int(s["count"]) for s in b["popular_shelves"][:60]}
            w.update(best=n, id=b["book_id"], title=b["title_without_series"], text=text, publisher=b["publisher"],
                     tags=json.dumps(shelves))
    for w in works.values():
        if "text" not in w: continue
        sh = json.loads(w["tags"])
        top = sorted(sh, key=sh.get, reverse=True)[:8]
        if not any("romance" in s for s in top): continue  # readers must treat it as a romance
        p = w["publisher"]
        yield dict(source="goodreads", id=w["id"], title=w["title"], text=w["text"], tags=w["tags"],
                   year=w["year"] if w["year"] < 9999 else None, pop=w["pop"],
                   pub="trad" if TRAD.search(p) else "self" if SELF.search(p) else "small")


def kindle():
    seen = set()
    if True:
        for line in gzip.open(D + "kindle/meta_Kindle_Store.jsonl.gz", "rt"):
            b = json.loads(line)
            cats = " > ".join(b.get("categories") or [])
            text = clean(" ".join((b.get("features") or []) + (b.get("description") or [])))
            if "Romance" not in cats or len(text) < 200 or not english(text) or b["title"] in seen: continue
            seen.add(b["title"])
            det = b.get("details") or {}
            m = re.search(r"(19|20)\d\d", str(det.get("Publication date", "")))
            p = str(det.get("Publisher", ""))
            yield dict(source="kindle", id=b["parent_asin"], title=b["title"], text=text, tags=json.dumps(b["categories"]),
                       year=int(m.group()) if m else None, pop=b.get("rating_number") or 0,
                       pub="trad" if TRAD.search(p) else "self" if SELF.search(p.split("(")[0].strip()) else "small")


def wattpad():
    seen = set()
    for fn in glob.glob(D + "wattpad_*.jsonl"):
        for line in open(fn):
            b = json.loads(line)
            text, tags = clean(b.get("description")), b.get("tags") or []
            romance = "romance" in fn or any(t in ("romance", "love", "lovestory") for t in tags)
            if b["id"] in seen or not romance or len(text) < 200 or not english(text): continue
            seen.add(b["id"])
            yield dict(source="wattpad", id=str(b["id"]), title=b["title"], text=text, tags=json.dumps(tags),
                       year=None, pop=b.get("readCount") or 0, pub="web")


if __name__ == "__main__":
    which = sys.argv[1:] or ["goodreads", "kindle", "wattpad"]
    for name in which:
        df = pd.DataFrame(globals()[name]())
        df.to_parquet(f"{D}{name}.parquet")
        print(name, len(df), df["pub"].value_counts().to_dict(), pd.to_numeric(df["year"]).agg(["min", "median", "max"]).to_dict())
