"""Tests for the Project 4 reliability layer."""

from src.reliability import audit_recommendations, validate_profile
from src.recommender import load_songs


def test_invalid_numeric_profile_abstains_with_reason():
    songs = load_songs("data/songs.csv")
    result = audit_recommendations(
        {"genre": "pop", "mood": "happy", "energy": 2.0},
        songs,
    )
    assert result.abstained
    assert "energy must be between 0 and 1" in result.reason
    assert result.checks["input_valid"] is False


def test_valid_profile_passes_integrity_and_stability_checks():
    songs = load_songs("data/songs.csv")
    result = audit_recommendations(
        {"genre": "pop", "mood": "happy", "energy": 0.8},
        songs,
    )
    assert not result.abstained
    assert result.recommendations[0][0]["title"] == "Sunrise City"
    assert all(result.checks.values())


def test_missing_catalog_labels_produce_honest_warnings():
    songs = load_songs("data/songs.csv")
    result = audit_recommendations(
        {"genre": "opera", "mood": "mysterious", "energy": 0.5},
        songs,
    )
    assert len(result.warnings) == 2
    assert any("genre 'opera'" in warning for warning in result.warnings)
    assert any("mood 'mysterious'" in warning for warning in result.warnings)


def test_low_confidence_threshold_can_force_abstention():
    songs = load_songs("data/songs.csv")
    result = audit_recommendations(
        {"genre": "opera", "mood": "mysterious", "energy": 0.5},
        songs,
        minimum_score=10.0,
    )
    assert result.abstained
    assert "confidence threshold" in result.reason


def test_validation_rejects_blank_label_and_non_numeric_value():
    errors = validate_profile({"genre": " ", "energy": "loud"})
    assert "genre cannot be blank" in errors
    assert "energy must be numeric" in errors
