import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# --- Algorithm Recipe weights (see README "How The System Works") ---
GENRE_POINTS = 2.0
MOOD_POINTS = 1.0
ENERGY_WEIGHT = 1.5
ACOUSTIC_POINTS = 0.5
ACOUSTIC_THRESHOLD = 0.6


@dataclass
class Song:
    """Represents a song and its attributes."""
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
    """Represents a user's taste preferences."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


def _score_core(
    genre: str,
    mood: str,
    energy: float,
    acousticness: float,
    fav_genre: str,
    fav_mood: str,
    target_energy: float,
    likes_acoustic: bool,
) -> Tuple[float, List[str]]:
    """Apply the Algorithm Recipe to raw fields and return (score, reasons)."""
    score = 0.0
    reasons: List[str] = []

    if genre == fav_genre:
        score += GENRE_POINTS
        reasons.append(f"genre match (+{GENRE_POINTS})")

    if mood == fav_mood:
        score += MOOD_POINTS
        reasons.append(f"mood match (+{MOOD_POINTS})")

    # Energy closeness: reward proximity to the target, not higher values.
    closeness = 1 - abs(energy - target_energy)
    energy_points = ENERGY_WEIGHT * closeness
    score += energy_points
    reasons.append(f"energy closeness (+{energy_points:.2f})")

    if likes_acoustic and acousticness > ACOUSTIC_THRESHOLD:
        score += ACOUSTIC_POINTS
        reasons.append(f"acoustic bonus (+{ACOUSTIC_POINTS})")

    return score, reasons


class Recommender:
    """OOP recommendation engine over a list of Song objects."""

    def __init__(self, songs: List[Song]):
        """Store the catalog of songs to recommend from."""
        self.songs = songs

    def _score(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """Score a single Song against a UserProfile."""
        return _score_core(
            song.genre, song.mood, song.energy, song.acousticness,
            user.favorite_genre, user.favorite_mood,
            user.target_energy, user.likes_acoustic,
        )

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k Songs ranked highest-to-lowest by score."""
        ranked = sorted(self.songs, key=lambda s: self._score(user, s)[0], reverse=True)
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable explanation of a song's score."""
        _, reasons = self._score(user, song)
        return "; ".join(reasons) if reasons else "no strong matches"


def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file into a list of dicts with numeric fields typed."""
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["id"] = int(row["id"])
            row["tempo_bpm"] = int(row["tempo_bpm"])
            for col in ("energy", "valence", "danceability", "acousticness"):
                row[col] = float(row[col])
            songs.append(row)
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song dict against user_prefs and return (score, reasons)."""
    fav_genre = user_prefs.get("genre", user_prefs.get("favorite_genre"))
    fav_mood = user_prefs.get("mood", user_prefs.get("favorite_mood"))
    target_energy = user_prefs.get("energy", user_prefs.get("target_energy", 0.5))
    likes_acoustic = user_prefs.get("likes_acoustic", False)

    return _score_core(
        song["genre"], song["mood"], song["energy"], song["acousticness"],
        fav_genre, fav_mood, target_energy, likes_acoustic,
    )


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score, rank, and return the top-k songs as (song, score, explanation) tuples."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = "; ".join(reasons) if reasons else "no strong matches"
        scored.append((song, score, explanation))
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]
