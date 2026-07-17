"""Explainable, strategy-based recommendation logic for VibeCompass."""

import csv
from dataclasses import asdict, dataclass
from typing import Dict, List, Tuple


@dataclass
class Song:
    """Represent one catalog song and its recommendation features."""

    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    popularity: int = 50
    release_year: int = 2020
    instrumentalness: float = 0.0
    speechiness: float = 0.0
    duration_sec: int = 180


@dataclass
class UserProfile:
    """Represent the core preferences used by the classroom interface."""

    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


@dataclass(frozen=True)
class ScoringStrategy:
    """Store weights for one interchangeable recommendation strategy."""

    name: str
    genre_weight: float
    mood_weight: float
    energy_weight: float
    description: str


SCORING_STRATEGIES = {
    "balanced": ScoringStrategy(
        "balanced", 2.0, 1.0, 1.5,
        "Balances explicit genre and mood choices with energy similarity.",
    ),
    "genre_first": ScoringStrategy(
        "genre_first", 3.0, 0.75, 1.0,
        "Prioritizes the listener's requested genre.",
    ),
    "mood_first": ScoringStrategy(
        "mood_first", 1.0, 2.5, 1.0,
        "Prioritizes the emotional context of the listening session.",
    ),
    "energy_focus": ScoringStrategy(
        "energy_focus", 0.75, 0.75, 3.0,
        "Prioritizes energy similarity for workouts and activity playlists.",
    ),
}


OPTIONAL_FEATURES = {
    "valence": (0.5, 1.0),
    "danceability": (0.5, 1.0),
    "acousticness": (0.5, 1.0),
    "popularity": (0.3, 100.0),
    "release_year": (0.3, 60.0),
    "instrumentalness": (0.4, 1.0),
    "speechiness": (0.3, 1.0),
    "duration_sec": (0.2, 300.0),
}


class Recommender:
    """Provide an object-oriented wrapper around the shared scoring logic."""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(
        self, user: UserProfile, k: int = 5, mode: str = "balanced"
    ) -> List[Song]:
        """Return the top ``k`` songs ranked for the supplied user."""
        ranked = sorted(
            self.songs,
            key=lambda song: (
                -score_song(self._preferences(user), asdict(song), mode)[0],
                song.title.lower(),
            ),
        )
        return ranked[: max(0, k)]

    def explain_recommendation(
        self, user: UserProfile, song: Song, mode: str = "balanced"
    ) -> str:
        """Explain a score using the same strategy used for ranking."""
        _, reasons = score_song(self._preferences(user), asdict(song), mode)
        return "; ".join(reasons)

    @staticmethod
    def _preferences(user: UserProfile) -> Dict:
        """Translate the classroom profile object into scoring preferences."""
        return {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "acousticness": 0.8 if user.likes_acoustic else 0.2,
        }


def get_strategy(mode: str) -> ScoringStrategy:
    """Return a named strategy or raise a clear error for an invalid mode."""
    try:
        return SCORING_STRATEGIES[mode]
    except KeyError as error:
        available = ", ".join(sorted(SCORING_STRATEGIES))
        raise ValueError(
            f"Unknown scoring mode {mode!r}. Choose one of: {available}."
        ) from error


def load_songs(csv_path: str) -> List[Dict]:
    """Load catalog rows from CSV and convert all numeric fields."""
    numeric_fields = {
        "id": int,
        "energy": float,
        "tempo_bpm": float,
        "valence": float,
        "danceability": float,
        "acousticness": float,
        "popularity": int,
        "release_year": int,
        "instrumentalness": float,
        "speechiness": float,
        "duration_sec": int,
    }
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as csv_file:
        for row in csv.DictReader(csv_file):
            for field, converter in numeric_fields.items():
                row[field] = converter(row[field])
            songs.append(row)
    return songs


def _similarity(value: float, target: float, scale: float = 1.0) -> float:
    """Return a bounded 0-to-1 similarity for two numeric values."""
    return max(0.0, 1.0 - abs(value - target) / scale)


def score_song(
    user_prefs: Dict, song: Dict, mode: str = "balanced"
) -> Tuple[float, List[str]]:
    """Score one song with a named strategy and return auditable reasons."""
    strategy = get_strategy(mode)
    score = 0.0
    reasons = []

    preferred_genre = str(
        user_prefs.get("genre", user_prefs.get("favorite_genre", ""))
    ).strip().lower()
    preferred_mood = str(
        user_prefs.get("mood", user_prefs.get("favorite_mood", ""))
    ).strip().lower()

    if preferred_genre and song["genre"].strip().lower() == preferred_genre:
        score += strategy.genre_weight
        reasons.append(f"genre match (+{strategy.genre_weight:.2f})")

    if preferred_mood and song["mood"].strip().lower() == preferred_mood:
        score += strategy.mood_weight
        reasons.append(f"mood match (+{strategy.mood_weight:.2f})")

    target_energy = float(
        user_prefs.get("energy", user_prefs.get("target_energy", 0.5))
    )
    energy_points = strategy.energy_weight * _similarity(
        float(song["energy"]), target_energy
    )
    score += energy_points
    reasons.append(f"energy similarity (+{energy_points:.2f})")

    for feature, (weight, scale) in OPTIONAL_FEATURES.items():
        if feature not in user_prefs or feature not in song:
            continue
        points = weight * _similarity(
            float(song[feature]), float(user_prefs[feature]), scale
        )
        score += points
        reasons.append(f"{feature} similarity (+{points:.2f})")

    return round(score, 4), reasons


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    mode: str = "balanced",
    diversify: bool = False,
) -> List[Tuple[Dict, float, str]]:
    """Rank songs and optionally reduce repeated-artist and genre filter bubbles."""
    if k <= 0:
        return []

    candidates = []
    for song in songs:
        score, reasons = score_song(user_prefs, song, mode)
        candidates.append((song, score, reasons))
    candidates.sort(key=lambda item: (-item[1], item[0]["title"].lower()))

    if not diversify:
        return [
            (song, score, "; ".join(reasons))
            for song, score, reasons in candidates[:k]
        ]

    selected = []
    artist_counts: Dict[str, int] = {}
    genre_counts: Dict[str, int] = {}
    remaining = candidates[:]
    while remaining and len(selected) < k:
        adjusted = []
        for song, base_score, reasons in remaining:
            artist = song["artist"].strip().lower()
            genre = song["genre"].strip().lower()
            artist_penalty = 0.75 * artist_counts.get(artist, 0)
            genre_penalty = 0.25 * genre_counts.get(genre, 0)
            adjusted_score = base_score - artist_penalty - genre_penalty
            adjusted.append(
                (
                    adjusted_score,
                    song["title"].lower(),
                    song,
                    base_score,
                    reasons,
                    artist_penalty + genre_penalty,
                )
            )
        adjusted.sort(key=lambda item: (-item[0], item[1]))
        adjusted_score, _, song, _, reasons, penalty = adjusted[0]
        display_reasons = list(reasons)
        if penalty:
            display_reasons.append(f"diversity penalty (-{penalty:.2f})")
        selected.append((song, round(adjusted_score, 4), "; ".join(display_reasons)))
        artist = song["artist"].strip().lower()
        genre = song["genre"].strip().lower()
        artist_counts[artist] = artist_counts.get(artist, 0) + 1
        genre_counts[genre] = genre_counts.get(genre, 0) + 1
        remaining = [item for item in remaining if item[0] is not song]

    return selected
