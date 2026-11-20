# Male hero archetypes in romance: what the data shows

**Bottom line.** Eighteen hero archetypes emerge from 271k romance blurbs. Two broad ones lead: the **warrior / royal** of fantasy and sci-fi romance and the **friend / boy next door**, each around 13–15% of reader demand. The folk list of five gets three right (billionaire, vampire, werewolf), and two wrong (surgeon and pirate are minor members of bigger clusters). It misses the archetypes that carry more than half of reader demand.

Treat the shares as rough: the extraction is right about two times in three, and the cluster boundaries are only moderately stable.

## Data

| Source | Size | Popularity weight | Years |
|---|---|---|---|
| Goodreads (UCSD Book Graph, romance) | 135k works | number of ratings | to 2017 |
| Amazon Kindle Store (Amazon Reviews 2023) | 132k titles, about half self-published | number of ratings | to 2023 |
| Wattpad (top-ranked stories) | 4k stories | reads | undated |
| AO3 fan fiction, F/M works | 1.45M works | none available | 2009–2025, gap in 2019–21 |

## Method

1. **Extract.** Parse each blurb and collect the nouns it applies to a male referent: "he is a duke", "Jake, a former SEAL", "Sheriff Jake Ryan". The role vocabulary is learned from the corpus (nouns mostly used of people, at least 55% of the time of men), not from a list. This gives 390 hero terms.
2. **Cluster.** Describe each term by the books it appears in, three independent ways: sentence embeddings of the blurb, blurb word statistics, and Goodreads reader shelves. Cluster each view with two algorithms, repeat on Goodreads-only, Kindle-only and six bootstrap resamples, and keep the consensus (22 clusters, 18 of them hero archetypes).
3. **Measure.** A book counts toward an archetype only when the blurb explicitly attributes the term to a man. That covers 23% of Goodreads and 20% of Kindle books. A looser version counting any mention covers about 75% and is shown as a sensitivity check.

Cluster names are my own labels.

## Archetypes and popularity

Supply is share of titles and demand is share of ratings, each averaged over Goodreads and Kindle. Stability is how often a cluster's terms stay together across views, sources and resamples (1 = always).

| Archetype | Typical terms | Demand | Supply | Demand, loose | Stability |
|---|---|---|---|---|---|
| Warrior / ruler (fantasy, sci-fi) | warrior, king, prince, alien, assassin | 15.5% | 13.9% | 14.8% | 0.56 |
| Friend / ex / boy next door | best friend, ex, crush, single dad, firefighter | 13.4% | 15.0% | 15.2% | 0.54 |
| Billionaire / playboy tycoon | billionaire, playboy, CEO, tycoon | 8.6% | 5.9% | 4.6% | 0.69 |
| Husband material | husband, bachelor, widower, fiancé | 8.1% | 8.0% | 6.3% | 0.41 |
| Boss / workplace and celebrity | boss, actor, chef, colleague | 6.9% | 8.0% | 6.2% | 0.49 |
| Shifter / alpha wolf | shifter, alpha, wolf, werewolf, bear | 6.9% | 8.2% | 9.5% | 0.59 |
| Aristocrat and historical rogue | duke, earl, rake, laird, knight, pirate | 6.2% | 7.1% | 6.4% | 0.49 |
| Neighbor / tradesman | neighbor, owner, contractor, carpenter | 5.1% | 4.7% | 3.2% | 0.85 |
| Lawman and criminal | detective, cop, FBI agent, bodyguard, mobster | 4.8% | 6.1% | 5.0% | 0.66 |
| Vampire, demon, other supernatural | vampire, demon, dragon, god, archangel | 4.2% | 3.7% | 8.1% | 0.81 |
| Bad boy | bad boy, biker, bully, jerk, tattooed | 4.1% | 2.7% | 3.9% | 0.69 |
| Military and medic | soldier, Navy SEAL, marine, doctor, surgeon | 3.8% | 4.1% | 4.5% | 0.52 |
| Cowboy and western lawman | cowboy, rancher, sheriff, outlaw | 2.9% | 4.0% | 3.1% | 0.55 |
| Athlete | player, quarterback, hockey player, coach | 2.6% | 2.1% | 2.3% | 0.95 |
| Lawyer / politician | lawyer, attorney, judge, senator | 1.9% | 2.1% | 2.1% | 0.51 |
| Rock star / musician | rock star, lead singer, drummer | 1.8% | 2.0% | 1.7% | 0.85 |
| Professor / genius | professor, genius, engineer | 1.6% | 1.5% | 1.5% | 0.39 |
| Fighter / rival | fighter, boxer, rival, nemesis | 1.5% | 1.1% | 1.4% | 0.53 |

- **Readers over-reward** billionaires, bad boys and athletes (demand above supply). They under-reward cowboys, lawmen and shifters.
- **Billionaire demand leans on a few hits.** Without the 100 most-rated books per platform it falls from 8.6% to 6.0%; in 2009–11, the Fifty Shades years, the cluster takes 32% of Goodreads ratings against 6% of titles.
- **Self-published vs traditional.** Self-published titles skew to shifters (10.5% vs 4.0%), bad boys and rock stars. Traditional publishers skew to cowboys, lawmen, aristocrats and husbands.
- **Fan fiction differs.** Among AO3 F/M works with a matching tag (26% of works), friend/boy-next-door leads (22%), then shifter/alpha (14%), boss (12%), supernatural (11%) and bad boy (9%). Billionaires are nearly absent (0.3%).

## Example books

Hand-picked from the most-rated books in each cluster, keeping only ones I recognise as correctly assigned.

| Archetype | Examples |
|---|---|
| Warrior / ruler | The Selection; Outlander; The Crown of Gilded Bones |
| Friend / boy next door | The Cheat Sheet; To Love Jason Thorn; Thoughtless |
| Billionaire | Fifty Shades of Grey; The Marriage Bargain; This Man |
| Husband material | Landline; Mr. Maybe; Fall into Temptation |
| Boss / celebrity | Beautiful Bastard; To Hate Adam Connor; Motorcycle Man |
| Shifter / alpha | Slave to Sensation; Feral Sins; Fair Game |
| Aristocrat / rogue | The Bride (Garwood); When He Was Wicked |
| Neighbor | Wallbanger; Slammed; Dirty English |
| Lawman / criminal | Law Man; The Witness; Reaper's Property |
| Vampire / supernatural | Angels' Blood; How to Marry a Millionaire Vampire; Crave |
| Bad boy | Perfect Chemistry; Down to You; Driven |
| Military / medic | The Bronze Horseman; Persuasion |
| Cowboy | Play It Safe; Taming Him; Dance Upon the Air |
| Athlete | The Mistake; Nobody's Baby But Mine; Not My Romeo |
| Lawyer | Vicious; Under One Roof |
| Rock star | Devoured; Music of the Heart; Double Time |
| Professor | The Love Hypothesis; The Perfect Match |
| Fighter | Defying the Odds; Lover Eternal; The Will |

## Shifts over time

Share of titles by archetype:

| Archetype | Goodreads 1980–94 | Goodreads 2015–17 | Kindle 2009–11 | Kindle 2021–23 |
|---|---|---|---|---|
| Aristocrat / rogue | 17.2% | 5.0% | 12.7% | 8.3% |
| Husband material | 14.8% | 6.6% | 14.4% | 6.1% |
| Friend / boy next door | 7.0% | 16.9% | 10.4% | 16.4% |
| Warrior / ruler | 15.5% | 12.6% | 15.3% | 18.2% |
| Shifter / alpha | 3.3% | 6.3% | 7.2% | 8.9% |
| Bad boy | 0.7% | 3.8% | 1.5% | 2.4% |
| Athlete | 0.2% | 3.5% | 1.4% | 2.0% |
| Cowboy | 5.3% | 3.9% | 4.9% | 3.0% |

Single terms, as mentions per 1,000 titles (any mention):

- **Vampire** peaked in 2009–11 (Goodreads 0.5 in 1980–94, 42 at the peak, 15 by 2015–17). **Shifter** replaced it: Goodreads 0 to 25, Kindle 15 to a peak of 71 in 2015–17.
- **Billionaire** rose from 2 to 27 on Goodreads and peaked on Kindle at 37 in 2015–17.
- **Pirate** fell from 16 to 5 on Goodreads. **Surgeon** stayed flat at 3–5.
- **Recent Kindle risers (2009–11 to 2021–23):** hockey player 0.3 to 4.3, single dad 1.3 to 7.2, bully 0.8 to 5.7, dragon 9 to 27, king 28 to 36.
- **Fan fiction:** bad-boy tags rose from 2.5% to 10.5% of matched works (2009–13 to 2022–25), shifter/alpha from 9% to 16%; supernatural fell from 16% to 11%.

## The five-archetype folk theory

| Folk hero | Verdict | Evidence |
|---|---|---|
| Billionaire | Holds | Its own stable cluster; 3rd by demand; 8th most common single term |
| Vampire | Holds, but past its peak | Core of a stable supernatural cluster; 12th most common term |
| Werewolf | Right idea, wrong word | The cluster is real, but "shifter" and "alpha" are each about twice as common as "werewolf" |
| Surgeon | Does not hold | 84th most common term; a fringe member of military/medic, where "doctor" and "soldier" dominate |
| Pirate | Does not hold | About 128th; a fringe member of the aristocrat/rogue cluster and falling since the 1980s |

- The five words together explicitly describe the hero in 5% of assigned books and about 4% of ratings.
- Read generously as the five clusters they sit in, they cover about 30% of demand.
- The theory misses warrior/royal, friend/boy next door, boss, husband, lawman, cowboy, bad boy and athlete.

## Robustness

- **Archetype ranking is consistent across platforms.** Rank correlation of title shares is 0.94 between Goodreads and Kindle and 0.75 between Goodreads and Wattpad; for ratings shares it is 0.83. Strict and loose measures correlate at 0.88.
- **Cluster boundaries are only moderately stable.** Agreement between partitions (adjusted Rand index) is about 0.3 across the three views, 0.5–0.6 across bootstraps and 0.35–0.5 between Goodreads and Kindle. No cluster count stands out, so 22 is my choice. Athlete, rock star, neighbor and supernatural are tight; professor, husband and boss are loose.
- **Hero type is not the main structure in blurbs.** Clustering blurbs blind, with no hero extraction, lines up only weakly with archetypes (adjusted mutual information 0.11; 6 of 30 blind clusters are dominated by one archetype). Plot and subgenre dominate.

## Limits

- **Extraction noise.** In my hand check of 55 sampled books, explicit matches were right about two times in three and bare mentions under half. The check is small and I was the only judge.
- **Ambiguous words.** "Captain" puts a hockey romance (Pucked) among the aristocrats; "hunter", "knight" and "savior" misfire the same way. Relational words (friend, ex, boyfriend) often point at someone other than the hero, so the friend / boy-next-door share is the least trustworthy.
- **Manual choices.** I removed about 100 generic or junk terms by hand (man, guy, author, and similar) and named the clusters.
- **Missing terms.** Highlander, sheikh and mafia were dropped by the vocabulary filters, so those heroes are undercounted.
- **Coverage.** The headline measure uses only the 20–23% of books with an explicit hero statement.
- **Popularity proxy.** Rating counts are not sales or Kindle Unlimited reads. Goodreads "romance" includes classics, young-adult and chick-lit titles (Pride and Prejudice, The Selection, Shopaholic).
- **Audience.** M/M romance is not separated out, and nothing in the data identifies reader gender.
- **Weak sources.** Wattpad is 4k top-ranked stories whose read counts are dominated by single hits, so I report only its title shares. AO3 has no popularity data and its tags mostly describe existing characters.
- **Scope.** English only; publisher type is a crude name match.

## Files

- `01_load.py`, `02_extract.py`, `03_embed.py`, `04_cluster.py 22`, `05_analyze.py`: the pipeline, run in that order.
- `data/clusters.json`: every term in every cluster.
- `data/results.json`: all numbers above.
- `data/analysis.log`: full tables by period and source.
