from src.recommender import (
    Recommender,
    Song,
    UserProfile,
    load_songs,
    recommend_songs,
    score_song,
)

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
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
            artist="Test Artist",
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
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


def test_score_song_returns_numeric_score_and_reasons():
    score, reasons = score_song(
        {"genre": "pop", "mood": "happy", "energy": 0.8},
        {
            "genre": "pop", "mood": "happy", "energy": 0.8,
            "valence": 0.9, "danceability": 0.8, "acousticness": 0.2,
        },
    )
    assert score == 4.5
    assert "genre match (+2.00)" in reasons
    assert "mood match (+1.00)" in reasons


def test_functional_recommender_ranks_and_limits_results():
    songs = [
        {"title": "Best", "genre": "pop", "mood": "happy", "energy": 0.8},
        {"title": "Other", "genre": "rock", "mood": "sad", "energy": 0.2},
    ]
    results = recommend_songs(
        {"genre": "pop", "mood": "happy", "energy": 0.8}, songs, k=1
    )
    assert len(results) == 1
    assert results[0][0]["title"] == "Best"
    assert isinstance(results[0][2], str)


def test_catalog_loads_required_number_of_typed_songs():
    songs = load_songs("data/songs.csv")
    assert len(songs) == 17
    assert isinstance(songs[0]["id"], int)
    assert isinstance(songs[0]["energy"], float)
    assert isinstance(songs[0]["tempo_bpm"], float)


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
