"""
Command line runner for the Music Recommender Simulation.

Runs the recommender against several distinct user profiles so we can
stress-test the scoring logic and compare outputs side by side.
"""

from src.recommender import load_songs, recommend_songs

# Distinct taste profiles used to stress-test the scoring logic.
PROFILES = {
    "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.9, "likes_acoustic": False},
    "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.3, "likes_acoustic": True},
    "Deep Intense Rock": {"genre": "rock", "mood": "intense", "energy": 0.85, "likes_acoustic": False},
    # Adversarial: conflicting preferences (wants sad but very high energy).
    "Conflicting (High-Energy Sad)": {"genre": "edm", "mood": "melancholy", "energy": 0.95, "likes_acoustic": False},
}


def print_recommendations(name: str, user_prefs: dict, songs: list, k: int = 5) -> None:
    """Print the top-k recommendations for a single named profile."""
    recommendations = recommend_songs(user_prefs, songs, k=k)
    print(f"=== {name} ===")
    print(
        f"prefs: genre={user_prefs['genre']}, mood={user_prefs['mood']}, "
        f"energy={user_prefs['energy']}, likes_acoustic={user_prefs['likes_acoustic']}\n"
    )
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{rank}. {song['title']} — {song['artist']}  [score: {score:.2f}]")
        print(f"   genre={song['genre']}, mood={song['mood']}, energy={song['energy']}")
        print(f"   reasons: {explanation}")
    print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}\n")
    for name, user_prefs in PROFILES.items():
        print_recommendations(name, user_prefs, songs)


if __name__ == "__main__":
    main()
