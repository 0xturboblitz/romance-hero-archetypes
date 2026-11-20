"""Popularity, trends, examples, cross-source checks and the folk-theory comparison. Writes data/results.json."""
import json, re, collections
import numpy as np, pandas as pd
from scipy.stats import spearmanr
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_mutual_info_score

# Labels are my reading of each cluster, keyed by one member term.
NAMES = {"warrior": "Warrior / ruler (fantasy, sci-fi)", "boss": "Boss / workplace & celebrity crush",
         "duke": "Aristocrat & historical rogue", "detective": "Lawman & criminal (cop, agent, mobster)",
         "shifter": "Shifter / alpha wolf", "husband": "Husband material (bachelor, widower, fiance)",
         "vampire": "Vampire, demon & other supernatural", "friend": "Friend / ex / boy next door",
         "cowboy": "Cowboy & western lawman", "soldier": "Military & medic (SEAL, soldier, doctor)",
         "billionaire": "Billionaire / playboy tycoon", "bad boy": "Bad boy (biker, bully, jerk)",
         "rock star": "Rock star / musician", "player": "Athlete", "lawyer": "Lawyer / politician",
         "owner": "Neighbor / tradesman / owner", "professor": "Professor / genius", "fighter": "Fighter / rival",
         "brother": "(relatives: brother, father, son - mostly not the hero)", "lover": "(epithets: lover, devil, bastard)",
         "outsider": "(misc: recluse, outsider)", "master": "(misc: master, patron)"}
FOLK = ["vampire", "werewolf", "billionaire", "surgeon", "pirate"]

clusters = json.load(open("data/clusters.json"))
t2c = {}
for c in clusters:
    c["name"] = next(NAMES[t] for t in c["terms"] if t in NAMES)
    t2c.update({t: c["name"] for t in c["terms"]})
real = [c["name"] for c in clusters if not c["name"].startswith("(")]

df = pd.read_parquet("data/books.parquet")
df["year"] = pd.to_numeric(df.year)
R = {"n_books": df.source.value_counts().to_dict(), "coverage": {}}


def assign(strict):
    """strict: only explicit statements about a male referent ("he is a duke", "Jake, a SEAL", "Sheriff Jake");
    loose: also bare mentions of male-leaning role nouns anywhere in the blurb (more coverage, more noise)"""
    d = df.copy()
    d["terms"] = [sorted({t for t, p in json.loads(h) if t in t2c and (p != "bare" or not strict)}) for h in d.hero]
    d["arch"] = [sorted({t2c[t] for t in ts} & set(real)) for ts in d.terms]
    has = d[d.arch.str.len() > 0]
    x = has.explode("arch")
    x["w"] = 1 / x.groupby(level=0).arch.transform("size")  # a book with two archetypes counts half for each
    x["wp"] = x.w * x["pop"]
    R["coverage"]["strict" if strict else "loose"] = (d.arch.str.len() > 0).groupby(d.source).mean().round(3).to_dict()
    return d, has, x


def shares(d):
    return pd.DataFrame({"titles": d.groupby("arch").w.sum() / d.w.sum(), "ratings": d.groupby("arch").wp.sum() / d.wp.sum()})


def table(x):
    tab = pd.concat({s: shares(x[x.source == s]) for s in ["goodreads", "kindle", "wattpad"]}, axis=1).fillna(0)
    # headline = mean of Goodreads and Kindle (equal weight per platform), by titles (supply) and by ratings (demand)
    tab[("all", "supply")] = tab[[("goodreads", "titles"), ("kindle", "titles")]].mean(axis=1)
    tab[("all", "demand")] = tab[[("goodreads", "ratings"), ("kindle", "ratings")]].mean(axis=1)
    return tab.sort_values(("all", "demand"), ascending=False)


loose = table(assign(False)[2])
df, has, x = assign(True)
tab = table(x)
tab[("loose", "supply")], tab[("loose", "demand")] = loose[("all", "supply")], loose[("all", "demand")]
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 60)
print(R["coverage"]); print((tab * 100).round(1).to_string())
R["shares"] = {a: {f"{s}_{m}": round(float(v), 4) for (s, m), v in row.items()} for a, row in tab.iterrows()}
R["stability"] = {c["name"]: c["stability"] for c in clusters}
R["terms"] = {c["name"]: c["terms"][:10] for c in clusters}

# robustness of the *ranking* across platforms
g, k, w = (tab[(s, "titles")] for s in ["goodreads", "kindle", "wattpad"])
R["rank_corr"] = {"goodreads~kindle titles": spearmanr(g, k)[0], "goodreads~wattpad titles": spearmanr(g, w)[0],
                  "goodreads~kindle ratings": spearmanr(tab[("goodreads", "ratings")], tab[("kindle", "ratings")])[0],
                  "titles~ratings (goodreads)": spearmanr(g, tab[("goodreads", "ratings")])[0],
                  "strict~loose demand": spearmanr(tab[("all", "demand")], tab[("loose", "demand")])[0]}
# without the 100 biggest books per platform: is demand driven by a few mega-hits?
nohit = x[~x.index.isin(df.groupby("source")["pop"].nlargest(100).index.get_level_values(1))]
R["demand_no_megahits"] = (pd.concat([shares(nohit[nohit.source == s]).ratings for s in ["goodreads", "kindle"]], axis=1).mean(axis=1)).round(4).to_dict()
# publisher type (Goodreads+Kindle)
R["by_pub"] = {p: shares(x[(x["pub"] == p)]).titles.round(4).to_dict() for p in ["trad", "self", "small"]}
print("demand without top-100 books/platform", {k: round(v * 100, 1) for k, v in sorted(R["demand_no_megahits"].items(), key=lambda kv: -kv[1])})
print("\nrank correlations", {k: round(v, 2) for k, v in R["rank_corr"].items()})

# book-level check with no term extraction at all: do blind clusters of blurb embeddings line up with archetypes?
single = has[has.arch.str.len() == 1]
E = np.load("data/emb.npy")[single.index].astype(np.float32)
km = KMeans(30, n_init=3, random_state=0).fit_predict(E)
R["blind_kmeans_ami"] = adjusted_mutual_info_score(single.arch.str[0], km)
purity = pd.crosstab(km, single.arch.str[0], normalize="index").max(axis=1)
R["blind_kmeans_dominated"] = int((purity > .4).sum())
print("blind k-means vs archetype AMI", round(R["blind_kmeans_ami"], 3), "| clusters >40% one archetype:", R["blind_kmeans_dominated"], "of 30")

# trends
bins = {"goodreads": [1980, 1995, 2000, 2005, 2009, 2012, 2015, 2018], "kindle": [2009, 2012, 2015, 2018, 2021, 2024]}
R["trend"] = {}
for s, b in bins.items():
    d = x[(x.source == s) & x.year.notna()].copy()
    d["period"] = pd.cut(d.year, b, right=False, labels=[f"{a}-{c - 1}" for a, c in zip(b, b[1:])])
    for m, col in [("titles", "w"), ("ratings", "wp")]:
        t = d.pivot_table(index="arch", columns="period", values=col, aggfunc="sum", observed=False)
        R["trend"][f"{s}_{m}"] = (t / t.sum()).round(4).T.to_dict()
        print(f"\n{s} {m} share by period (%)"); print((t / t.sum() * 100).round(1).loc[tab.index].to_string())

# examples: most-rated books whose hero terms all fall in one archetype
R["examples"] = {}
for a in tab.index:
    d = single[single.arch.str[0] == a]
    ex = pd.concat([d[d.source == s].nlargest(n, "pop") for s, n in [("goodreads", 5), ("kindle", 3), ("wattpad", 1)]])
    R["examples"][a] = [dict(title=r.title[:70], source=r.source, year=None if pd.isna(r.year) else int(r.year), pop=int(r.pop), terms=r.terms) for r in ex.itertuples()]
    print(f"\n{a}: " + " | ".join(f"{e['title']} [{e['source'][0]} {e['year']} {e['pop']} {','.join(e['terms'])}]" for e in R["examples"][a]))

# folk theory: the five named heroes as single terms
tx = df.explode("terms").dropna(subset=["terms"])
tx = tx[tx.source.isin(["goodreads", "kindle"])]
tt = pd.DataFrame({"titles": tx.groupby("terms").size() / len(has[has.source != "wattpad"]),
                   "ratings": tx.groupby("terms")["pop"].sum() / has[has.source != "wattpad"]["pop"].sum()})
tt = tt[~tt.index.map(t2c).str.startswith("(")]
tt["rank_titles"], tt["rank_ratings"] = tt.titles.rank(ascending=False), tt.ratings.rank(ascending=False)
R["folk"] = {t: dict(tt.loc[t].round(4), cluster=t2c[t]) for t in FOLK}
R["top_terms"] = tt.sort_values("ratings", ascending=False).head(25).round(4).reset_index().to_dict("records")
anyfolk = df.terms.apply(lambda ts: bool(set(ts) & set(FOLK)))
R["folk_coverage_titles"] = float(anyfolk[has.index].mean())
R["folk_coverage_ratings"] = float(has["pop"][anyfolk[has.index]].sum() / has["pop"].sum())
R["folk_clusters_demand"] = float(tab[("all", "demand")][list({t2c[t] for t in FOLK})].sum())
print("\nFOLK", json.dumps(R["folk"], indent=0, default=float), R["folk_coverage_titles"], R["folk_coverage_ratings"], R["folk_clusters_demand"])
print(tt.sort_values("ratings", ascending=False).head(25).round(4).to_string())

# fan fiction (AO3, F/M works): how often do each archetype's terms appear in author tags? (no popularity data)
ao = pd.read_parquet("data/ao3.parquet")
tags = ao.tags.str.lower()
pat = {a: re.compile(r"\b(" + "|".join(re.escape(t) for t in ts if t2c[t] == a) + r")s?\b") for a in real for ts in [list(t2c)]}
hit = pd.DataFrame({a: tags.str.contains(p) for a, p in pat.items()})
R["ao3"] = {"n": len(ao), "share_of_works": hit.mean().round(4).to_dict(), "share_among_matched": (hit.sum() / hit.sum().sum()).round(4).to_dict(),
            "folk": {t: float(tags.str.contains(rf"\b{t}s?\b").mean()) for t in FOLK}}
ao["y"] = pd.to_numeric(ao.year, errors="coerce")
R["ao3"]["trend"] = {p: (hit[m].sum() / hit[m].sum().sum()).round(4).to_dict() for p, m in
                     [("2009-2013", ao.y.between(2009, 2013)), ("2014-2018", ao.y.between(2014, 2018)), ("2022-2025", ao.y.between(2022, 2025))]}
print("\nAO3", (pd.DataFrame(R["ao3"]["trend"]).assign(all=pd.Series(R["ao3"]["share_among_matched"])) * 100).round(1).sort_values("all", ascending=False).to_string())
print("AO3 folk per 1000 works", {k: round(v * 1000, 1) for k, v in R["ao3"]["folk"].items()}, "any archetype tag:", hit.any(axis=1).mean().round(3))
json.dump(R, open("data/results.json", "w"), indent=1, default=float)
