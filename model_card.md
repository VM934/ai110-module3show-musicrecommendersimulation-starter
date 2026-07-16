# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeCompass 1.0**

## 2. Intended Use

VibeCompass ranks a small song catalog for a listener who supplies a preferred
genre, mood, and energy level. It is a classroom simulation for learning how
features become predictions, not a production service or a substitute for a
person's listening history. It assumes that the stated preferences describe the
listener's current goal and that every catalog row is accurate.

## 3. How the Model Works

The recommender gives two points when a song's genre exactly matches, one point
when its mood matches, and up to 1.5 points when its energy is close to the
listener's target. Optional preferences for acousticness, valence, or
danceability can add up to 0.5 points each. It scores every song, sorts the list,
and returns the requested number of top results. I replaced the starter
placeholders with CSV loading, numeric conversion, shared scoring logic,
deterministic ranking, and explanations for every score.

## 4. Data

The catalog contains 17 fictional songs. I kept the original 10 and added seven
tracks spanning R&B, classical, hip hop, EDM, acoustic, Latin, and blues. Each
row has genre, mood, energy, tempo, valence, danceability, and acousticness.
Many languages, regional styles, hybrid genres, lyrics, release years, and real
listener interactions are still missing.

## 5. Strengths

The system works best when the catalog contains a direct genre and mood match.
`Sunrise City` ranks first for Happy Pop, `Library Rain` for Chill Lofi, and
`Storm Runner` for Intense Rock. The continuous energy score also avoids an
all-or-nothing comparison and gives nearby songs partial credit. The explanations
make the result auditable without reading the code.

## 6. Limitations and Bias

Exact genre and mood matching is brittle: `pop` does not match `indie pop`, and
similar moods are treated as unrelated. Fixed weights may repeatedly favor a
dominant genre, creating a filter bubble. A conflicting EDM/sad profile exposes
another weakness: there is no sad EDM track, so the system returns energetic
EDM rather than explaining that the catalog lacks a full match. Users whose
tastes depend on lyrics, culture, language, novelty, or changing context are not
well represented.

## 7. Evaluation

I ran four profiles: High-Energy Happy Pop, Chill Acoustic Lofi, Deep Intense
Rock, and a conflicting Sad EDM workout profile. I compared their top five
results and checked that different profiles produced different leaders. I also
reduced the genre weight from 2.0 to 0.5 and doubled the energy weight; this
moved `Rooftop Lights` above `Gym Hero`, showing how sensitive the ranking is to
human-selected weights. Six automated tests verify ordering, explanations,
score structure, catalog loading, distinct profiles, and top-k behavior.

## 8. Future Work

I would add fuzzy or hierarchical genre matching, a diversity penalty for
repeated artists and genres, and an explicit "no strong match" threshold. I
would learn personalized weights from likes, skips, and repeat plays instead of
using one formula for everyone. A larger, balanced catalog and a counterfactual
explanation such as "this ranked higher because energy mattered more" would
also improve usefulness.

## 9. Personal Reflection

The biggest lesson was that ranking code is simple compared with choosing and
validating the assumptions behind it. AI accelerated the first implementation
and helped surface edge cases, but I had to run the code and inspect the actual
rankings to catch a broken module import and verify the math. I was surprised
that a few transparent weights could produce plausible recommendations; that
also made the bias risk feel more concrete, because small weight changes visibly
changed what the user would hear.
