# AI Interactions Log

This log records the agentic stretch work completed with Codex and the manual
checks used to keep the final submission accurate.

## Exact User Prompt

> “Complete both courses projects to perfection, Use feedback from past
> projects and the grading rubrics if needed, and submit them”

I interpreted “to perfection” against the published Project 3 rubric instead of
adding unrelated features. The prior grader feedback also asked for exact
prompts and stronger boundary tests, so this file quotes the prompt verbatim
and the test suite includes explicit edge cases.

## Additional Song Attributes via Agentic AI

### Rubric-aware task specification used by the agent

> Audit the current Music Recommender against every Project 3 criterion. Add at
> least five meaningful song attributes that were not in the baseline catalog,
> update CSV loading and optional scoring consistently, preserve the starter
> interfaces, document the agentic workflow, and prove the changes with tests
> and a runnable CLI.

### Generated changes

- `data/songs.csv`: added popularity, release year, instrumentalness,
  speechiness, and duration to all 17 rows.
- `src/recommender.py`: added typed conversion and bounded similarity scoring
  for all five attributes.
- `src/main.py`: added profile targets that exercise the new fields.
- `tests/test_recommender.py`: verifies the new columns load with correct types.

### Manual verification and corrections

I ran `python -m pytest -q` and `python -m src.main --mode balanced --top-k 3`.
I checked that every CSV row has all new values, numeric conversions succeed,
the four profile leaders remain sensible, and reasons name the new attributes.
I kept new attributes optional so a minimal starter-style song dictionary still
works without a `KeyError`.

## Multiple Ranking Modes — Strategy Pattern

### Design prompt used

> Design a small Python Strategy pattern for balanced, genre-first, mood-first,
> and energy-focused ranking. Keep one shared scoring implementation, make the
> mode selectable from `python -m src.main`, reject unknown modes with an
> actionable error, and keep results deterministic.

### Pattern and implementation

`ScoringStrategy` is an immutable dataclass, and `SCORING_STRATEGIES` is the
strategy registry. `score_song(..., mode=...)` retrieves one strategy while
sharing all feature-similarity logic. `argparse` exposes the four modes through
`--mode`, so users switch behavior without editing the scoring engine.

### Verification

`test_ranking_modes_change_the_weighted_score` proves that strategy weights
change output, and `test_unknown_ranking_mode_has_actionable_error` checks the
failure boundary. The CLI was also run with each supported mode.

## Diversity, Novelty, and Fairness

### Design prompt used

> Add deterministic diversity reranking that discourages repeated artists and
> genres without hiding its effect. Preserve base-score explanations, append an
> explicit penalty reason, and document what the feature can and cannot fix.

### Implementation and rejected suggestion

`recommend_songs(..., diversify=True)` greedily selects the best adjusted
candidate. It subtracts 0.75 per already-selected matching artist and 0.25 per
already-selected matching genre. An early shuffle-based idea was rejected
because it would be nondeterministic, hard to test, and impossible to explain.
The deterministic penalty is included in the displayed reason.

### Verification

The diversity test uses repeated-artist candidates and asserts both ordering
and the visible penalty. README and the Model Card explain that this reduces
repetition inside one list but cannot repair missing or imbalanced catalog data.

## Visual Summary Table

### Formatting prompt used

> Create a dependency-free ASCII results table with rank, title, artist, score,
> and the complete scoring reasons. Keep it readable in a normal terminal and
> usable for every profile.

### Implementation and verification

`format_table` calculates column widths from the current results and prints a
bordered table. `test_ascii_table_contains_scores_and_explanations` verifies
that titles, numeric scores, and reasons all appear. The full CLI run confirmed
that all four profiles render as tables.

## Edge-Case Testing Prompt and Rationale

> Add adversarial tests for numeric targets at 0.0 and 1.0, out-of-range targets,
> zero and negative top-k values, unknown strategy names, repeated artists, and
> optional-feature compatibility. Ask after each test: what is the next input
> that could break the helper function?

- 0.0/1.0 and -0.5/1.5 targets test numeric boundaries and defensive clamping.
- zero/negative `k` verifies an empty result instead of surprising slicing.
- an unknown mode tests the configuration failure path.
- repeated artists test the fairness mechanism's actual trigger.
- minimal song dictionaries verify backward compatibility with starter tests.

Final verified result: **15 tests passed**.
