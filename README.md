# Romance hero archetypes

Which male hero archetypes dominate romance fiction, found empirically by clustering what 271k blurbs say about the hero. Full write-up, tables and limits: [REPORT.md](REPORT.md).

## Summary

Eighteen archetypes emerge. Shares are rough: extraction is right about two times in three and cluster boundaries are only moderately stable.

| Archetype | Share of ratings | Share of titles |
|---|---|---|
| Warrior / ruler (king, prince, alien) | 15.5% | 13.9% |
| Friend / ex / boy next door | 13.4% | 15.0% |
| Billionaire / playboy tycoon | 8.6% | 5.9% |
| Husband material (bachelor, widower) | 8.1% | 8.0% |
| Boss / workplace and celebrity | 6.9% | 8.0% |
| Shifter / alpha wolf | 6.9% | 8.2% |
| Aristocrat and historical rogue | 6.2% | 7.1% |
| 11 others (neighbor, lawman, vampire, bad boy, military, cowboy, athlete, ...) | 1.5–5.1% each | |

**The folk theory of five (vampire, werewolf, billionaire, surgeon, pirate):**

- Billionaire and vampire hold; each anchors a stable cluster.
- Werewolf is the right idea with the wrong word: "shifter" and "alpha" are each about twice as common.
- Surgeon and pirate do not hold; they rank about 84th and 128th among hero terms.
- The five words describe the hero in about 5% of books and miss the archetypes carrying more than half of reader demand.

**Over time:** aristocrats and husband-material heroes fell by more than half since the 1980s, the boy next door more than doubled, shifters replaced vampires after 2011, and billionaires peaked around 2015–17.

## Data

Not included in the repo (3.9 GB). Sources:

- Goodreads romance, 135k works: [UCSD Book Graph](https://mcauleylab.ucsd.edu/public_datasets/gdrive/goodreads/byGenre/goodreads_books_romance.json.gz) to `data/goodreads/books_romance.json.gz`
- Kindle Store, 132k romance titles: [Amazon Reviews 2023](https://mcauleylab.ucsd.edu/public_datasets/data/amazon_2023/raw/meta_categories/meta_Kindle_Store.jsonl.gz) to `data/kindle/`
- Wattpad, 4k stories: [sleeping-ai/Wattpad-metadata-new](https://huggingface.co/datasets/sleeping-ai/Wattpad-metadata-new) to `data/wattpad_<genre>.jsonl`
- AO3, 1.45M F/M works: [trentmkelly/archiveofourown-meta](https://huggingface.co/datasets/trentmkelly/archiveofourown-meta), filtered to F/M English, as `data/ao3.parquet`
- First-name genders: [organisciak/names](https://github.com/organisciak/names) `us-names-by-gender.csv` to `data/names/`

## Run

```bash
uv pip install pandas numpy scikit-learn sentence-transformers spacy pyarrow scipy
python 01_load.py && python 02_extract.py && python 03_embed.py && python 04_cluster.py 22 && python 05_analyze.py
```

Outputs kept in the repo: `data/clusters.json` (every term per cluster), `data/results.json` (all numbers), `data/analysis.log` (full tables).
