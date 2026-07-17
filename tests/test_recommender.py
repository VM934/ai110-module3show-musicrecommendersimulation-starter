"""Required and adversarial tests for the VibeCompass recommender."""

import pytest

from src.main import format_table
from src.recommender import (
    Recommender,
    Song,
    UserProfile,
    get_strategy,
    load_songs,
    recommend_songs,
    score_song,
)


def make_small_recommender() -> Recommender:
    """Return a two-song fixture for the object-oriented interface."""
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Repeat Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Other Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile("pop", "happy", 0.8, False)
    results = make_small_recommender().recommend(user, k=2)
    assert len(results) == 2
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile("pop", "happy", 0.8, False)
    recommender = make_small_recommender()
    explanation = recommender.explain_recommendation(user, recommender.songs[0])
    assert isinstance(explanation, str)
    assert explanation.strip()


def test_score_song_returns_numeric_score_and_reasons():
    score, reasons = score_song(
        {"genre": "pop", "mood": "happy", "energy": 0.8},
        {"genre": "pop", "mood": "happy", "energy": 0.8},
    )
    assert score == 4.5
    assert "genre match (+2.00)" in reasons
    assert "mood match (+1.00)" in reasons


@pytest.mark.parametrize("target", [-0.5, 0.0, 1.0, 1.5])
def test_energy_similarity_is_bounded_at_edge_and_out_of_range_targets(target):
    """A large gap must never subtract points or produce a negative score."""
    score, reasons = score_song(
        {"genre": "none", "mood": "none", "energy": target},
        {"genre": "pop", "mood": "happy", "energy": 0.5},
    )
    assert score >= 0
    assert any(reason.startswith("energy similarity") for reason in reasons)


def test_functional_recommender_ranks_and_limits_results():
    songs = [
        {"title": "Best", "artist": "A", "genre": "pop", "mood": "happy", "energy": 0.8},
        {"title": "Other", "artist": "B", "genre": "rock", "mood": "sad", "energy": 0.2},
    ]
    results = recommend_songs(
        {"genre": "pop", "mood": "happy", "energy": 0.8}, songs, k=1
    )
    assert len(results) == 1
    assert results[0][0]["title"] == "Best"
    assert isinstance(results[0][2], str)


def test_zero_and_negative_k_return_empty_results():
    song = {"title": "Only", "artist": "A", "genre": "pop", "mood": "happy", "energy": 0.8}
    assert recommend_songs({}, [song], k=0) == []
    assert recommend_songs({}, [song], k=-1) == []


def test_catalog_loads_required_number_and_all_stretch_attributes():
    songs = load_songs("data/songs.csv")
    assert len(songs) == 17
    required_new_features = {
        "popularity",
        "release_year",
        "instrumentalness",
        "speechiness",
        "duration_sec",
    }
    assert required_new_features.issubset(songs[0])
    assert isinstance(songs[0]["popularity"], int)
    assert isinstance(songs[0]["instrumentalness"], float)


def test_distinct_profiles_produce_distinct_top_results():
    songs = load_songs("data/songs.csv")
    profiles = [
        {"genre": "pop", "mood": "happy", "energy": 0.8},
        {"genre": "lofi", "mood": "chill", "energy": 0.35},
        {"genre": "rock", "mood": "intense", "energy": 0.92},
    ]
    leaders = {
        recommend_songs(profile, songs, k=3)[0][0]["title"]
        for profile in profiles
    }
    assert leaders == {"Sunrise City", "Library Rain", "Storm Runner"}


def test_ranking_modes_change_the_weighted_score():
    song = {"genre": "pop", "mood": "sad", "energy": 0.8}
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    balanced, _ = score_song(prefs, song, "balanced")
    genre_first, _ = score_song(prefs, song, "genre_first")
    assert genre_first > balanced


def test_unknown_ranking_mode_has_actionable_error():
    with pytest.raises(ValueError, match="Unknown scoring mode"):
        get_strategy("mystery")


def test_diversity_reranking_penalizes_repeated_artist():
    songs = [
        {"title": "A1", "artist": "Same", "genre": "pop", "mood": "happy", "energy": 0.8},
        {"title": "A2", "artist": "Same", "genre": "pop", "mood": "happy", "energy": 0.79},
        {"title": "B1", "artist": "Different", "genre": "indie", "mood": "happy", "energy": 0.79},
    ]
    results = recommend_songs(
        {"genre": "pop", "mood": "happy", "energy": 0.8},
        songs,
        k=3,
        diversify=True,
    )
    assert [item[0]["title"] for item in results] == ["A1", "A2", "B1"]
    assert "diversity penalty" in results[1][2]


def test_ascii_table_contains_scores_and_explanations():
    output = format_table(
        [({"title": "Best", "artist": "A"}, 4.5, "genre match (+2.00)")]
    )
    assert "Why it ranked" in output
    assert "Best" in output
    assert "genre match" in output
