# 🎵 Music Recommender Simulation

## Project Summary

This version, **VibeCompass 1.0**, ranks a catalog of 17 songs against a
listener profile. It combines exact genre and mood matches with a continuous
energy-similarity score, then explains every recommendation in plain language.
The project includes four evaluation profiles, deterministic ranking, and tests
for both the object-oriented and functional interfaces.

## How The System Works

Real platforms combine multiple signals. Content-based filtering compares item
features such as genre, mood, tempo, and energy with one listener's preferences.
Collaborative filtering instead learns from behavior across many people, such
as plays, likes, skips, repeats, and playlists. In both cases the raw song and
user data are inputs, the taste profile represents preferences, and a ranking
algorithm selects which candidates appear first. VibeCompass intentionally uses
the smaller, explainable content-based approach.

Each song includes an id, title, artist, genre, mood, energy, tempo, valence,
danceability, and acousticness. A basic listener profile supplies a preferred
genre, preferred mood, and target energy. The object-oriented interface also
turns `likes_acoustic` into an acousticness target.

The baseline algorithm recipe is:

- Exact genre match: **+2.0 points**
- Exact mood match: **+1.0 point**
- Energy similarity: up to **+1.5 points**, decreasing as the song moves away
  from the target energy
- Optional valence, danceability, and acousticness preferences: up to **+0.5
  points each**

Every song is scored, the full catalog is sorted from highest to lowest score,
and the top `k` items are returned. Ties are resolved by title so results are
repeatable.

`User preferences → score every song → sort by score → top-k explained results`

## Getting Started

### Setup

1. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:

   ```bash
   python -m src.main
   ```

### Running Tests

```bash
pytest
```

## Sample Recommendation Output

```text
Loaded songs: 17

High-Energy Happy Pop
1. Sunrise City by Neon Echo - Score: 4.47
   Because: genre match (+2.00); mood match (+1.00); energy similarity (+1.47)
2. Gym Hero by Max Pulse - Score: 3.31
   Because: genre match (+2.00); energy similarity (+1.30)
3. Rooftop Lights by Indigo Parade - Score: 2.44
   Because: mood match (+1.00); energy similarity (+1.44)

Chill Acoustic Lofi
1. Library Rain by Paper Lanterns - Score: 5.00
   Because: genre match (+2.00); mood match (+1.00); energy similarity (+1.50); acousticness similarity (+0.49)
2. Midnight Coding by LoRoom - Score: 4.83
   Because: genre match (+2.00); mood match (+1.00); energy similarity (+1.40); acousticness similarity (+0.43)
3. Focus Flow by LoRoom - Score: 3.89
   Because: genre match (+2.00); energy similarity (+1.42); acousticness similarity (+0.47)

Deep Intense Rock
1. Storm Runner by Voltline - Score: 4.49
   Because: genre match (+2.00); mood match (+1.00); energy similarity (+1.48)
2. Gym Hero by Max Pulse - Score: 2.48
   Because: mood match (+1.00); energy similarity (+1.48)
3. Neon Pulse by Kairo Flux - Score: 1.43
   Because: energy similarity (+1.43)
```

## Experiments You Tried

- **Profile comparison:** Happy Pop selected `Sunrise City`; Chill Lofi selected
  `Library Rain`; Intense Rock selected `Storm Runner`. These results match the
  profile features and show that one song does not dominate every list.
- **Adversarial profile:** A user asking for EDM + sad + 0.95 energy receives
  `Neon Pulse` first because the catalog has no sad EDM song. This exposes a
  coverage gap instead of inventing a perfect match.
- **Weight-shift experiment:** Reducing genre from 2.0 to 0.5 and doubling the
  energy contribution moved `Rooftop Lights` above `Gym Hero`. The change made
  close-energy songs more competitive, but also weakened the user's explicit
  genre preference.

## Limitations and Risks

- The 17-song classroom catalog is too small to represent real musical taste.
- Exact text matches treat related genres such as `pop` and `indie pop` as
  unrelated.
- Fixed weights can create a filter bubble by repeatedly rewarding the same
  genre and mood.
- The model has no listening history, skip behavior, lyrics, culture, language,
  or changing context.

## Reflection

Read the complete [Model Card](model_card.md).

This project showed me that a recommendation can feel intelligent even when it
is only a transparent weighted formula. The most important engineering step was
not sorting the songs; it was deciding what each feature should mean and making
the score explainable. Keeping the reasons beside every score made it much
easier to catch results that were mathematically valid but did not match the
profile's intent.

AI helped accelerate the implementation and test design, but I still had to
verify the import path, numeric conversions, and rankings by running the code.
The conflicting EDM/sad profile was the clearest reminder that an algorithm can
only choose from its data. A larger system would need broader data, learned or
personalized weights, diversity controls, and feedback from real listeners.
