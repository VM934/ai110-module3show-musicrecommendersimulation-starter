"""Reliability guardrails and audits for VibeCompass recommendations."""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from .recommender import load_songs, recommend_songs


Recommendation = Tuple[Dict, float, str]


@dataclass
class AuditResult:
    """Store recommendations plus the evidence produced by reliability checks."""

    recommendations: List[Recommendation] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    checks: Dict[str, bool] = field(default_factory=dict)
    abstained: bool = False
    reason: str = ""


BOUNDED_FEATURES = {
    "energy": (0.0, 1.0),
    "valence": (0.0, 1.0),
    "danceability": (0.0, 1.0),
    "acousticness": (0.0, 1.0),
    "instrumentalness": (0.0, 1.0),
    "speechiness": (0.0, 1.0),
    "popularity": (0.0, 100.0),
    "release_year": (1900.0, 2100.0),
    "duration_sec": (30.0, 1200.0),
}


def validate_profile(profile: Dict) -> List[str]:
    """Return actionable errors for malformed or out-of-range preferences."""
    errors = []
    for feature, (minimum, maximum) in BOUNDED_FEATURES.items():
        if feature not in profile:
            continue
        try:
            value = float(profile[feature])
        except (TypeError, ValueError):
            errors.append(f"{feature} must be numeric")
            continue
        if not minimum <= value <= maximum:
            errors.append(
                f"{feature} must be between {minimum:g} and {maximum:g}"
            )

    for feature in ("genre", "mood"):
        if feature in profile and not str(profile[feature]).strip():
            errors.append(f"{feature} cannot be blank")
    return errors


def _coverage_warnings(profile: Dict, songs: List[Dict]) -> List[str]:
    """Warn when requested labels do not occur anywhere in the catalog."""
    warnings = []
    for feature in ("genre", "mood"):
        requested = str(profile.get(feature, "")).strip().lower()
        available = {
            str(song.get(feature, "")).strip().lower()
            for song in songs
        }
        if requested and requested not in available:
            warnings.append(
                f"No catalog song has the requested {feature} '{requested}'."
            )
    return warnings


def audit_recommendations(
    profile: Dict,
    songs: List[Dict],
    k: int = 5,
    mode: str = "balanced",
    diversify: bool = True,
    minimum_score: float = 1.0,
) -> AuditResult:
    """Run recommendation, validation, confidence, and integrity checks."""
    errors = validate_profile(profile)
    if errors:
        return AuditResult(
            abstained=True,
            reason="Invalid profile: " + "; ".join(errors),
            checks={"input_valid": False},
        )

    first = recommend_songs(profile, songs, k, mode, diversify)
    second = recommend_songs(profile, songs, k, mode, diversify)
    warnings = _coverage_warnings(profile, songs)
    checks = {
        "input_valid": True,
        "results_present": bool(first),
        "ranking_stable": [item[0]["id"] for item in first]
        == [item[0]["id"] for item in second],
        "explanations_present": all(bool(item[2].strip()) for item in first),
        "scores_non_negative": all(item[1] >= 0 for item in first),
    }

    if not first:
        return AuditResult(
            warnings=warnings,
            checks=checks,
            abstained=True,
            reason="No recommendations were produced.",
        )
    if first[0][1] < minimum_score:
        return AuditResult(
            warnings=warnings,
            checks=checks,
            abstained=True,
            reason=(
                f"Top score {first[0][1]:.2f} is below the "
                f"{minimum_score:.2f} confidence threshold."
            ),
        )
    if not all(checks.values()):
        failed = ", ".join(name for name, passed in checks.items() if not passed)
        return AuditResult(
            warnings=warnings,
            checks=checks,
            abstained=True,
            reason=f"Reliability checks failed: {failed}.",
        )

    return AuditResult(
        recommendations=first,
        warnings=warnings,
        checks=checks,
    )


def load_default_catalog() -> List[Dict]:
    """Load the repository's standard song catalog for evaluation scripts."""
    return load_songs("data/songs.csv")
