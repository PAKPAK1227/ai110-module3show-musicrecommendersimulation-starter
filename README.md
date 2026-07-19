# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real streaming platforms like Spotify and YouTube predict what you'll love next
by blending two ideas. **Collaborative filtering** looks at *other users'*
behavior — "people whose taste matches yours also liked this" — while
**content-based filtering** looks at the *song's own attributes* — "this sounds
like what you already enjoy." They feed on data such as likes, skips, replays,
playlist adds, and audio traits like tempo, energy, and mood. Collaborative
filtering finds surprising cross-genre gems but struggles with brand-new songs
(the *cold-start* problem); content-based filtering works instantly for any song
with known attributes but tends to keep recommending more of the same.

**My version is a pure content-based recommender.** It has song attributes but no
crowd of users to learn from, so it prioritizes matching each song's *vibe* to a
user's stated taste. It rewards songs that share the user's favorite **genre** and
**mood**, and whose **energy** is *closest* to the user's target — closeness, not
just a higher number, is what earns points, so a mellow-focus user isn't handed a
high-energy gym track. Genre is weighted highest because it's the most stable
signal of taste; mood and energy refine the match.

**How a score is computed (Scoring Rule → one song):**

```
total = 2.0 · (genre match)      +   # strongest, most stable taste signal
        1.0 · (mood match)       +
        1.5 · (1 - |energy - target_energy|)  +   # rewards closeness, 0–1 scale
        0.5 · (acoustic bonus if user likes acoustic and acousticness > 0.6)
```

**How songs are chosen (Ranking Rule → list of songs):** every song is scored,
then the list is **sorted by score (highest first)** and the **top _k_** (default 5)
are returned. Scoring judges each song alone; ranking compares and selects across
all of them — you need both.

### Features used in the simulation

**`Song`** (from `data/songs.csv`):
`id`, `title`, `artist`, `genre`, `mood`, `energy`, `tempo_bpm`, `valence`,
`danceability`, `acousticness`.
The scoring core uses **`genre`**, **`mood`**, **`energy`**, and **`acousticness`**.

**`UserProfile`** (the taste profile):
`favorite_genre`, `favorite_mood`, `target_energy`, `likes_acoustic`.

Example profile the recommender compares against:

```python
user_prefs = {
    "favorite_genre": "lofi",
    "favorite_mood": "chill",
    "target_energy": 0.35,
    "likes_acoustic": True,
}
```

### Data flow

```
INPUT (user_prefs)  →  PROCESS (score every song in songs.csv)  →  OUTPUT (rank → top-K)
```

For each of the 18 songs in the catalog: score it against `user_prefs`, collect the
scores, sort highest-first, and return the top _k_ (default 5).

### Finalized Algorithm Recipe

| Rule | Condition | Points |
|------|-----------|--------|
| Genre match | `song.genre == favorite_genre` | **+2.0** |
| Mood match | `song.mood == favorite_mood` | **+1.0** |
| Energy closeness | `1 - abs(song.energy - target_energy)` | **× 1.5** (0 → 1.5) |
| Acoustic bonus | `likes_acoustic and song.acousticness > 0.6` | **+0.5** |

A genre match is worth double a mood match because genre is the most stable signal
of taste. Energy is scored by *closeness* (proximity to the target), never by
"higher is better."

### Potential biases I expect

- **Genre over-prioritization / filter bubble.** Because genre is worth 2.0 and
  requires an *exact* string match, a great song in a *different* genre that
  perfectly matches the user's mood and energy can never earn those points. The
  system will keep recommending the same genre and hide worthy neighbors (e.g. an
  `ambient/chill` track for a `lofi/chill` fan).
- **Exact-match brittleness.** `"indie pop"` ≠ `"pop"` and casing matters, so near-
  miss genres/moods score as total mismatches.
- **Catalog & feature bias.** With only 18 hand-written songs, popular genres are
  over-represented; and the recipe ignores `valence`, `tempo_bpm`, and
  `danceability`, so mood nuance those features capture is lost.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

`python -m src.main` now runs a **stress-test suite** across four profiles. Below is the
first (**High-Energy Pop**); the full run for all four profiles — plus paired
comparisons — lives in the [Evaluation section of the model card](model_card.md).

```
Loaded songs: 18

=== High-Energy Pop ===
prefs: genre=pop, mood=happy, energy=0.9, likes_acoustic=False

1. Sunrise City — Neon Echo  [score: 4.38]
   genre=pop, mood=happy, energy=0.82
   reasons: genre match (+2.0); mood match (+1.0); energy closeness (+1.38)
2. Gym Hero — Max Pulse  [score: 3.46]
   genre=pop, mood=intense, energy=0.93
   reasons: genre match (+2.0); energy closeness (+1.46)
3. Rooftop Lights — Indigo Parade  [score: 2.29]
   genre=indie pop, mood=happy, energy=0.76
   reasons: mood match (+1.0); energy closeness (+1.29)
4. Storm Runner — Voltline  [score: 1.48]
   genre=rock, mood=intense, energy=0.91
   reasons: energy closeness (+1.48)
5. Neon Overdrive — Pulse Cartel  [score: 1.43]
   genre=edm, mood=energetic, energy=0.95
   reasons: energy closeness (+1.43)
```

The top pick (*Sunrise City*) is the only song matching genre **and** mood **and** near-target energy, so it wins clearly — exactly what we'd expect.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



