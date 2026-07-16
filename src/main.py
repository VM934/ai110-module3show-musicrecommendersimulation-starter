"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from .recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    profiles = {
        "High-Energy Happy Pop": {
            "genre": "pop", "mood": "happy", "energy": 0.8
        },
        "Chill Acoustic Lofi": {
            "genre": "lofi", "mood": "chill", "energy": 0.35,
            "acousticness": 0.85,
        },
        "Deep Intense Rock": {
            "genre": "rock", "mood": "intense", "energy": 0.92
        },
        "Conflicted Sad Workout": {
            "genre": "edm", "mood": "sad", "energy": 0.95
        },
    }

    for profile_name, user_prefs in profiles.items():
        recommendations = recommend_songs(user_prefs, songs, k=5)
        print(f"\n{profile_name}\n{'-' * len(profile_name)}")
        for rank, (song, score, explanation) in enumerate(recommendations, 1):
            print(f"{rank}. {song['title']} by {song['artist']} - Score: {score:.2f}")
            print(f"   Because: {explanation}")


if __name__ == "__main__":
    main()
