# 🎧 Model Card: VibeCompass 2.0

## 1. Model Name

**VibeCompass 2.0**

## 2. Goal / Task and Intended Use

VibeCompass ranks a small classroom song catalog for a listener who supplies a
preferred genre, mood, energy level, and optional numeric targets. It is an
explainable simulation for learning how inputs, preferences, scoring, and
ranking work. It is not a production recommender and should not be used to
infer identity, mental state, culture, or sensitive personal traits.

## 3. Data Used

The catalog contains 17 fictional songs. Each row includes title, artist,
genre, mood, energy, tempo, valence, danceability, and acousticness. Five
agentic stretch attributes—popularity, release year, instrumentalness,
speechiness, and duration—add more ways to distinguish listening contexts. The
catalog has no real behavior logs, lyrics, language labels, user demographics,
or geographic coverage, and its size makes every imbalance influential.

## 4. Algorithm Summary

The default mode gives two points for an exact genre match, one point for an
exact mood match, and up to 1.5 points for energy similarity. Optional numeric
preferences add smaller similarity contributions. The scoring engine judges
every song, sorts scores from high to low, and returns the requested top `k`.
The Strategy pattern exposes `balanced`, `genre_first`, `mood_first`, and
`energy_focus` modes. Optional diversity reranking uses a deterministic greedy
step that subtracts 0.75 for each repeated artist and 0.25 for each repeated
genre already selected; any penalty appears in the result explanation.

## 5. Observed Behavior

Balanced-mode leaders were `Sunrise City` for Happy Pop, `Library Rain` for
Chill Lofi, `Storm Runner` for Intense Rock, and `Neon Pulse` for the conflicting
Sad EDM workout profile. The first three leaders each match the profile's core
features. The last profile has no complete mood/genre match, so the system
chooses an energetic EDM track and makes the missing mood contribution visible.
Changing strategy weights changes scores as expected, and diversity reranking
can promote a different artist or genre when the unadjusted list is repetitive.

## 6. Limitations, Bias, and Fairness

Exact text matching is brittle: `pop` does not match `indie pop`. A small
catalog can overrepresent whichever genres happen to have more rows. Including
popularity may favor already popular music, and a fixed formula cannot represent
changing or mixed tastes. The diversity penalty helps prevent a top list from
repeating the same artist or genre, reducing one kind of filter bubble, but it
cannot repair missing languages, cultures, genres, or artists. Historical or
real-user deployment would require consent, privacy controls, larger balanced
data, and ongoing fairness evaluation.

## 7. Evaluation Process

I ran four distinct profiles and reviewed their top five results. Happy Pop and
Chill Lofi differ because text matches and acoustic/instrumental targets pull
them toward different catalog regions; Intense Rock shifts to `Storm Runner`
because of its rock, intense, and 0.91-energy features; Sad EDM selects
`Neon Pulse` on EDM and energy but gets no sad-mood points. I compared all four
strategies, ran with diversity on and off, and tested an adversarial profile
whose requested combination is absent. Fifteen automated tests cover score
structure, top-k behavior, typed data, distinct leaders, strategy switching,
diversity penalties, output formatting, invalid modes, and boundary inputs.

## 8. Intended and Non-Intended Use

Intended: classroom demonstrations, transparent ranking experiments, and
discussion of feature weighting and filter bubbles. Non-intended: production
personalization, psychological inference, identity classification, hiring,
education, credit, health, or any other consequential decision.

## 9. Ideas for Improvement

1. Add fuzzy and hierarchical genre/mood similarity instead of exact strings.
2. Learn personalized weights from consented likes, skips, and repeat plays.
3. Expand and audit the catalog for language, region, genre, era, and artist
   balance, then evaluate fairness with metrics rather than one penalty.
4. Add a calibrated “no strong match” threshold and counterfactual explanations.

## 10. Personal Reflection

The biggest lesson was that an explainable formula can feel intelligent even
though every behavior comes from human-selected data and weights. AI helped me
organize strategies, propose edge cases, and accelerate the repetitive dataset
update. I still had to inspect every CSV conversion, reject a nondeterministic
shuffle-based diversity idea, run the CLI, and verify the exact top results.
The surprising part was how visibly a small weight change alters the user's
experience. If I extended the project, I would focus first on broader data and
evaluation rather than adding more opaque scoring complexity.
