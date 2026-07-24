"""Command-line demonstration for the VibeCompass recommender."""

import argparse
from typing import Iterable, List, Tuple

from .recommender import SCORING_STRATEGIES, load_songs, recommend_songs
from .reliability import audit_recommendations


PROFILES = {
    "High-Energy Happy Pop": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "danceability": 0.85,
        "popularity": 75,
        "release_year": 2024,
        "speechiness": 0.08,
        "duration_sec": 210,
    },
    "Chill Acoustic Lofi": {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.35,
        "acousticness": 0.85,
        "instrumentalness": 0.7,
        "popularity": 45,
        "release_year": 2021,
        "speechiness": 0.04,
        "duration_sec": 185,
    },
    "Deep Intense Rock": {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.92,
        "popularity": 68,
        "release_year": 2018,
        "instrumentalness": 0.05,
        "speechiness": 0.06,
        "duration_sec": 235,
    },
    "Conflicted Sad Workout": {
        "genre": "edm",
        "mood": "sad",
        "energy": 0.95,
        "danceability": 0.9,
        "popularity": 80,
        "release_year": 2025,
        "instrumentalness": 0.15,
        "speechiness": 0.05,
        "duration_sec": 200,
    },
}


def format_table(recommendations: Iterable[Tuple[dict, float, str]]) -> str:
    """Return recommendations as an advanced ASCII transparency table."""
    rows: List[List[str]] = []
    for rank, (song, score, explanation) in enumerate(recommendations, 1):
        rows.append(
            [str(rank), song["title"], song["artist"], f"{score:.2f}", explanation]
        )
    headers = ["#", "Title", "Artist", "Score", "Why it ranked"]
    widths = [
        max(len(row[index]) for row in [headers] + rows)
        for index in range(len(headers))
    ]
    divider = "+-" + "-+-".join("-" * width for width in widths) + "-+"

    def render(row: List[str]) -> str:
        return "| " + " | ".join(
            value.ljust(widths[index]) for index, value in enumerate(row)
        ) + " |"

    return "\n".join([divider, render(headers), divider, *(render(row) for row in rows), divider])


def main(
    mode: str = "balanced",
    diversify: bool = True,
    top_k: int = 5,
    audit: bool = False,
) -> None:
    """Run four profiles with selectable strategy and reliability controls."""
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")
    print(f"Scoring mode: {mode} | Diversity reranking: {'on' if diversify else 'off'}")

    for profile_name, user_prefs in PROFILES.items():
        print(f"\n{profile_name}\n{'-' * len(profile_name)}")
        if audit:
            audit_result = audit_recommendations(
                user_prefs,
                songs,
                k=top_k,
                mode=mode,
                diversify=diversify,
            )
            for warning in audit_result.warnings:
                print(f"WARNING: {warning}")
            if audit_result.abstained:
                print(f"ABSTAINED: {audit_result.reason}")
                continue
            recommendations = audit_result.recommendations
            passed = ", ".join(
                name for name, result in audit_result.checks.items() if result
            )
            print(f"Reliability checks passed: {passed}")
        else:
            recommendations = recommend_songs(
                user_prefs,
                songs,
                k=top_k,
                mode=mode,
                diversify=diversify,
            )
        print(format_table(recommendations))


def parse_args() -> argparse.Namespace:
    """Parse CLI options for strategy, diversity, and list length."""
    parser = argparse.ArgumentParser(description="Run the VibeCompass simulator.")
    parser.add_argument(
        "--mode",
        choices=sorted(SCORING_STRATEGIES),
        default="balanced",
        help="Select the recommendation scoring strategy.",
    )
    parser.add_argument(
        "--no-diversity",
        action="store_true",
        help="Disable artist/genre diversity reranking.",
    )
    parser.add_argument("--top-k", type=int, default=5, help="Results per profile.")
    parser.add_argument(
        "--audit",
        action="store_true",
        help="Validate inputs and verify confidence, stability, and explanations.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    main(
        arguments.mode,
        not arguments.no_diversity,
        arguments.top_k,
        arguments.audit,
    )
