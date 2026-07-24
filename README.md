# 🎵 VibeCompass 2.0 — Music Recommender Simulation

VibeCompass is an explainable, content-based music recommender. It ranks a
17-song catalog against a listener profile, supports four interchangeable
scoring modes, reduces repetitive results with diversity reranking, and prints
the reasons behind every score in a transparent ASCII table.

## How the System Works

Real platforms such as Spotify and YouTube combine many signals. Content-based
filtering compares song features—genre, mood, tempo, energy, and other audio
attributes—with one listener's preferences. Collaborative filtering instead
uses behavior across many listeners, such as plays, likes, skips, repeats, and
playlist co-occurrence. In both cases, catalog and behavior data are inputs, a
user profile represents taste, and a ranking algorithm selects what appears
first. VibeCompass intentionally uses the smaller, auditable content-based
approach so every recommendation can be traced to a rule.

`User preferences → score every song → apply diversity reranking → top-k explained results`

### Song and Profile Features

Every song has an ID, title, artist, genre, mood, energy, tempo, valence,
danceability, and acousticness. The stretch implementation adds five more
meaningful attributes and uses each in scoring when the profile supplies a
target:

- popularity (0–100)
- release year
- instrumentalness (0.0–1.0)
- speechiness (0.0–1.0)
- duration in seconds

Profiles always include genre, mood, and target energy. They may also include
targets for any numeric song attribute. This lets a profile distinguish, for
example, a short vocal workout track from a long instrumental study track.

### Scoring and Ranking Recipe

The default `balanced` strategy awards:

- exact genre match: +2.0
- exact mood match: +1.0
- energy similarity: up to +1.5
- optional valence, danceability, and acousticness similarities: up to +0.5 each
- optional popularity, release year, instrumentalness, speechiness, and
  duration similarities: up to +0.2–0.4 each

Similarity is continuous: a song close to a numeric target earns more than a
distant song, but no mismatch subtracts points. All songs are scored, sorted by
score, and tie-broken by title for deterministic output.

The `ScoringStrategy` pattern keeps ranking policy separate from the scoring
engine. A user switches modes without changing code:

- `balanced`: balances genre, mood, and energy
- `genre_first`: makes an exact genre match most important
- `mood_first`: emphasizes emotional context
- `energy_focus`: emphasizes energy similarity

After base scoring, optional diversity reranking applies a 0.75-point penalty
for each already-selected song by the same artist and 0.25 points for each
already-selected song in the same genre. The penalty is shown in the reasons,
so the fairness intervention is visible rather than hidden.

## Setup and Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.main
```

Choose another ranking strategy or disable diversity reranking:

```bash
python -m src.main --mode genre_first
python -m src.main --mode mood_first --top-k 3
python -m src.main --mode energy_focus --no-diversity
```

## Tests

```bash
python -m pytest -q
```

Latest verified result:

```text
...............                                                          [100%]
15 passed in 0.04s
```

The suite covers the required OOP and functional interfaces, CSV type
conversion, top-k behavior, distinct profiles, every ranking mode, invalid
mode errors, diversity penalties, formatted output, zero/negative `k`, and
energy targets at and beyond the 0.0/1.0 boundaries.

## Sample Recommendation Output

The CLI prints full tables. These are the top three results from a verified
`balanced` run with diversity reranking enabled.

### High-Energy Happy Pop

```text
1  Sunrise City    Neon Echo       6.00  genre match; mood match; energy, danceability, popularity, release-year, speechiness, and duration similarities
2  Gym Hero        Max Pulse       4.62  genre match; energy and profile similarities; diversity penalty (-0.25)
3  Rooftop Lights  Indigo Parade  3.99  mood match; energy and profile similarities
```

`Sunrise City` ranks first because it directly matches both genre and mood and
nearly matches the 0.80 energy target. `Gym Hero` keeps a strong genre and
energy score but loses 0.25 because another pop song was already selected.

### Chill Acoustic Lofi

```text
1  Library Rain        Paper Lanterns  6.43  genre match; mood match; energy, acousticness, instrumentalness, and profile similarities
2  Midnight Coding     LoRoom          6.01  genre match; mood match; energy and profile similarities; diversity penalty (-0.25)
3  Spacewalk Thoughts  Orbit Bloom     4.15  mood match; energy, acousticness, instrumentalness, and profile similarities
```

This profile shifts toward low-energy, highly acoustic and instrumental tracks.
`Library Rain` wins because it satisfies the lofi/chill text features and the
numeric targets at the same time.

### Deep Intense Rock

```text
1  Storm Runner   Voltline      5.95  genre match; mood match; energy and profile similarities
2  Gym Hero       Max Pulse     3.89  mood match; energy and profile similarities
3  Salsa Skyline  Luna Mercado  2.85  energy and profile similarities
```

This profile is dominated by `Storm Runner` because it is the only direct
rock/intense match. The other results remain competitive through energy and
new numeric attributes rather than receiving a generic explanation.

### Conflicted Sad Workout (Adversarial Profile)

```text
1  Neon Pulse     Kairo Flux    5.36  genre match; energy, danceability, and profile similarities
2  Gym Hero       Max Pulse     3.38  energy, danceability, and profile similarities
3  Salsa Skyline  Luna Mercado  3.26  energy, danceability, and profile similarities
```

The catalog has no sad EDM song. `Neon Pulse` therefore wins on EDM, energy,
and danceability but receives no mood points. This exposes a coverage gap
instead of pretending the catalog contains a perfect match.

## Evaluation and Experiment

- Different profiles produced different leaders: `Sunrise City`,
  `Library Rain`, `Storm Runner`, and `Neon Pulse`.
- Switching from `balanced` to `genre_first` increases an exact genre match
  from 2.0 to 3.0 points. `energy_focus` instead raises energy's maximum from
  1.5 to 3.0, which makes close-energy cross-genre songs more competitive.
- Disabling diversity restores pure score order; enabling it can move a
  different artist or genre upward and shows the applied penalty in the output.
- The adversarial sad/EDM profile demonstrates that ranking is constrained by
  available data. Good math cannot manufacture a missing catalog segment.

## Limitations, Bias, and Fairness

The 17 fictional songs are too small to represent real taste. Exact genre and
mood matching treats related labels such as `pop` and `indie pop` as unrelated.
Popularity can reinforce a popularity bias, while fixed weights can still
create filter bubbles. Diversity reranking reduces repeated artists and genres
in one recommendation list, but it does not make the underlying catalog
balanced across cultures, languages, eras, or styles. VibeCompass should not be
used for consequential decisions or as evidence of a person's identity or
preferences.

## Reflection

The biggest learning moment was seeing that ranking code is simpler than
choosing and validating the assumptions behind it. AI accelerated the modular
implementation, edge-case tests, and documentation, but I verified every
numeric conversion and ranking by running the program and tests. A useful AI
suggestion was separating strategies from the scoring loop; a flawed early idea
was to treat diversity as a post-processing shuffle, which would have made the
results nondeterministic and unexplained. I kept a deterministic greedy penalty
instead. If I continued, I would add hierarchical genre matching, learn weights
from real feedback, expand and rebalance the catalog, and add a clear “no strong
match” threshold.

See [model_card.md](model_card.md) for the complete model card and
[ai_interactions.md](ai_interactions.md) for the agentic stretch-work log.

## Project 4: Applied AI System Extension

This repository is also the base for the Week 8 Applied AI System project. The
original system is the Project 3 VibeCompass recommender described above. The
new integrated feature is a reliability harness in `src/reliability.py`:

- validates numeric ranges and blank labels before ranking;
- warns when the requested genre or mood is missing from the catalog;
- abstains on invalid input, failed integrity checks, or low confidence;
- verifies deterministic ranking, non-negative scores, and explanations;
- runs predefined normal and adversarial cases through `evaluation.py`.

The implemented data flow is documented as Mermaid source in
[`architecture.mmd`](architecture.mmd), and the design reflection is in
[`project4_reflection.md`](project4_reflection.md).

Run the working system with the reliability layer:

```bash
python -m src.main --audit
```

Run the evaluation harness and tests:

```bash
python evaluation.py
python -m pytest -q
```
