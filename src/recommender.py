import csv
from dataclasses import asdict, dataclass
from typing import Dict, List, Tuple

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
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

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top ``k`` songs ranked for the supplied user."""
        ranked = sorted(
            self.songs,
            key=lambda song: (
                -score_song(self._preferences(user), asdict(song))[0],
                song.title.lower(),
            ),
        )
        return ranked[: max(0, k)]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Explain the score using the same rules used for ranking."""
        _, reasons = score_song(self._preferences(user), asdict(song))
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

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    numeric_fields = {
        "id": int,
        "energy": float,
        "tempo_bpm": float,
        "valence": float,
        "danceability": float,
        "acousticness": float,
    }
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as csv_file:
        for row in csv.DictReader(csv_file):
            for field, converter in numeric_fields.items():
                row[field] = converter(row[field])
            songs.append(row)
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """
    score = 0.0
    reasons = []

    preferred_genre = str(
        user_prefs.get("genre", user_prefs.get("favorite_genre", ""))
    ).strip().lower()
    preferred_mood = str(
        user_prefs.get("mood", user_prefs.get("favorite_mood", ""))
    ).strip().lower()

    if preferred_genre and song["genre"].strip().lower() == preferred_genre:
        score += 2.0
        reasons.append("genre match (+2.00)")

    if preferred_mood and song["mood"].strip().lower() == preferred_mood:
        score += 1.0
        reasons.append("mood match (+1.00)")

    target_energy = float(
        user_prefs.get("energy", user_prefs.get("target_energy", 0.5))
    )
    energy_similarity = max(0.0, 1.0 - abs(float(song["energy"]) - target_energy))
    energy_points = 1.5 * energy_similarity
    score += energy_points
    reasons.append(f"energy similarity (+{energy_points:.2f})")

    # Optional numeric preferences make the design extensible without changing
    # the baseline genre/mood/energy recipe.
    for feature in ("valence", "danceability", "acousticness"):
        if feature not in user_prefs:
            continue
        similarity = max(
            0.0,
            1.0 - abs(float(song[feature]) - float(user_prefs[feature])),
        )
        points = 0.5 * similarity
        score += points
        reasons.append(f"{feature} similarity (+{points:.2f})")

    return round(score, 4), reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, "; ".join(reasons)))

    scored.sort(key=lambda item: (-item[1], item[0]["title"].lower()))
    return scored[: max(0, k)]
