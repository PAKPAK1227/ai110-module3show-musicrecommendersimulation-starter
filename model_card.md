# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeScope 1.0** — it scopes out the "vibe" of a song and matches it to your taste.

---

## 2. Intended Use  

**Goal / task.** VibeScope tries to guess which songs a person will like. You give it a
few preferences (favorite genre, favorite mood, target energy, whether you like acoustic
music). It scores every song in the catalog and hands back the top few.

**Who it's for.** This is a classroom project for learning how recommenders work. It is
**not** for real listeners or a real music app.

**What it assumes.** It assumes you can describe your taste with one genre, one mood, and
one energy level. Real taste is messier than that.

**Intended use:** learning, experimenting with scoring rules, and comparing how different
user profiles get different lists.

**Non-intended use:** do not use it to make real recommendations, to judge someone's
taste, or in any product. The catalog is tiny and the rules are simple, so its picks are
demonstrations, not real advice.

---

## 3. How the Model Works  

Think of it like a points contest. Each song starts with zero points and earns points for
matching what you asked for:

- **Same genre as your favorite:** +2 points. Genre matters most.
- **Same mood as your favorite:** +1 point.
- **Energy close to your target:** up to +1.5 points. The closer the song's energy is to
  what you want, the more points it gets. A song that is way too loud or way too quiet
  gets almost nothing here.
- **Acoustic bonus:** +0.5 points if you like acoustic music and the song is very acoustic.

Add up the points for every song, then sort them from highest to lowest. The top 5 are your
recommendations. Each pick also comes with a plain reason like "genre match (+2.0)" so you
can see why it was chosen.

**Change from the starter code:** the starter just returned the first few songs. I added the
real scoring rules, the "closeness" idea for energy, the reasons list, and ranking.

---

## 4. Data  

- **Size:** 18 songs (I expanded the starter 10 to 18).
- **Features per song:** title, artist, genre, mood, energy, tempo, valence, danceability,
  and acousticness. The scoring uses genre, mood, energy, and acousticness.
- **Genres:** pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop, edm, classical,
  metal, reggae, r&b, country, and funk.
- **Moods:** happy, chill, intense, relaxed, moody, focused, energetic, melancholy,
  aggressive, romantic, nostalgic, and dreamy.
- **What's missing:** it's still a small, made-up catalog. There are no lyrics, no language,
  no artist popularity, and no listening history. Whole styles of music are represented by
  just one song each, so the data can't capture how varied real taste is.

---

## 5. Strengths  

- It works great for **clear, non-conflicting tastes.** Ask for "chill lofi" and you get a
  tight, sensible list of quiet study music.
- **Opposite users get opposite lists.** The pop fan and the lofi fan share almost no songs,
  which is exactly right.
- Every pick comes with a **reason**, so the recommendations are easy to explain and trust.
- The **energy "closeness" rule** correctly avoids handing a calm listener a loud gym track,
  which matched my intuition in testing.

---

## 6. Limitations and Bias 

**Weakness discovered during experiments: the "energy gap" quietly overrides mood.**
Every song receives energy points on a sliding scale (`1.5 × (1 - |gap|)`), but mood
is all-or-nothing (+1.0 only on an exact match). So when a user's preferences conflict —
for example the "High-Energy Sad" profile (`energy 0.95`, `mood melancholy`) — the one
song that actually *is* melancholy (*Winter Nocturne*, energy 0.22) ranks **dead last**,
because its huge energy gap costs it ~1.1 points while loud, upbeat tracks win on energy
alone. The system effectively ignores users who want a calm mood at high intensity, or
who care about mood more than loudness. On top of that, genre and mood use **exact string
matching**, so `"indie pop"` never counts as a partial hit for a `"pop"` fan, and the
model completely ignores `valence`, `tempo_bpm`, and `danceability` — real cues for
emotional tone. Finally, the catalog is only 18 hand-written songs, so a couple of extra
pop tracks are enough to make pop look "dominant."

---

## 7. Evaluation  

I stress-tested the recommender against four profiles (defined in `src/main.py`) and
read the top-5 output for each. Three were "normal" tastes and one was **adversarial** —
deliberately conflicting preferences — to see if the scoring could be tricked.

### Profiles tested and top results

**High-Energy Pop** (`genre=pop, mood=happy, energy=0.9`)
```
1. Sunrise City — Neon Echo        [4.38]  pop / happy / 0.82   genre+mood+energy
2. Gym Hero — Max Pulse            [3.46]  pop / intense / 0.93 genre+energy
3. Rooftop Lights — Indigo Parade  [2.29]  indie pop / happy / 0.76
4. Storm Runner — Voltline         [1.48]  rock / intense / 0.91
5. Neon Overdrive — Pulse Cartel   [1.43]  edm / energetic / 0.95
```

**Chill Lofi** (`genre=lofi, mood=chill, energy=0.3, likes_acoustic=True`)
```
1. Library Rain — Paper Lanterns   [4.92]  lofi / chill / 0.35  genre+mood+energy+acoustic
2. Midnight Coding — LoRoom        [4.82]  lofi / chill / 0.42
3. Focus Flow — LoRoom             [3.85]  lofi / focused / 0.40
4. Spacewalk Thoughts — Orbit Bloom[2.97]  ambient / chill / 0.28
5. Coffee Shop Stories — Slow Stereo[1.90] jazz / relaxed / 0.37
```

**Deep Intense Rock** (`genre=rock, mood=intense, energy=0.85`)
```
1. Storm Runner — Voltline         [4.41]  rock / intense / 0.91  genre+mood+energy
2. Concrete Kingdom — Byte Marshal [2.42]  hip-hop / intense / 0.80
3. Gym Hero — Max Pulse            [2.38]  pop / intense / 0.93
4. Sunrise City — Neon Echo        [1.46]  pop / happy / 0.82
5. Rooftop Lights — Indigo Parade  [1.36]  indie pop / happy / 0.76
```

**Conflicting — High-Energy Sad** (`genre=edm, mood=melancholy, energy=0.95`)
```
1. Neon Overdrive — Pulse Cartel   [3.50]  edm / energetic / 0.95   genre+energy
2. Gym Hero — Max Pulse            [1.47]  pop / intense / 0.93
3. Iron Verdict — Blacktide Rift   [1.46]  metal / aggressive / 0.98
4. Storm Runner — Voltline         [1.44]  rock / intense / 0.91
5. Winter Nocturne — Elena Vasquez [1.41]  classical / melancholy / 0.22  (mood match, last!)
```

### What surprised me

The adversarial profile exposed the biggest surprise: when a user asks for a *sad but
high-energy* song, the only truly sad track lands in **last place**. Loud, energetic
songs win because the energy score outweighs a single mood match. In plain terms, the
system trusts "how loud/fast" far more than "how it feels."

### Profile-by-profile comparisons (plain language)

- **High-Energy Pop vs Chill Lofi** — near-perfect mirror images. Pop pulls upbeat,
  high-energy dance tracks; Lofi pulls quiet, acoustic study music (and the acoustic
  bonus only fires for Lofi). This is the system working exactly as intended: opposite
  tastes get opposite lists.
- **High-Energy Pop vs Deep Intense Rock** — both love loud, fast songs, so they *share*
  tracks like *Gym Hero* and *Storm Runner*. The genre weight is what separates them: pop
  fans get pop on top, rock fans get rock on top, but the middle of both lists overlaps
  because energy is similar.
- **Deep Intense Rock vs High-Energy Sad** — same high energy, but Rock has a clean genre
  target while the Sad profile's genre (edm) and mood (melancholy) fight each other, so
  its list is a grab-bag of "anything loud" with the actual sad song stuck at the bottom.
- **Chill Lofi vs High-Energy Sad** — the clearest proof energy drives everything: both
  *want* a specific mood, but Lofi (low energy) gets a tight, coherent calm list while
  Sad (high energy) gets scattered loud songs. Same rules, opposite energy targets, wildly
  different quality.

### Why "Gym Hero" keeps showing up (explained for a non-programmer)

*Gym Hero* is a pop song that's very loud and very fast. Our recommender gives big points
for two easy things: being the right genre, and being close to the user's energy level.
*Gym Hero* is pop **and** high-energy, so it scores well for almost anyone who likes loud
music — even someone who just wanted "happy pop," not "workout pop." The recommender never
notices that its mood ("intense") is wrong for a happy listener, because a correct genre
plus high energy already piles up more points than one missing mood match. That's why the
same loud song keeps crashing lists it doesn't emotionally belong on.

### Small data experiment

I doubled the energy weight (1.5 → 3.0) and halved the genre weight (2.0 → 1.0), then
re-ran High-Energy Pop. The **top 5 stayed in the same order**, but the scores flattened —
*Storm Runner* (rock) climbed from 1.48 to 2.97, nearly catching the pop songs. So the
change made the results *different, not more accurate*: because this dataset's pop songs
are already high-energy, weakening genre just made the model less able to tell genres
apart rather than surfacing better picks.

---

## 8. Future Work  

If I kept building VibeScope, I would:

1. **Balance mood against energy.** Right now energy can quietly overrule mood. I'd score
   mood on a sliding scale too, or let the user say what matters most to them.
2. **Use more features.** Bring in valence, tempo, and danceability so the model understands
   emotional tone, not just loudness.
3. **Add variety to the top results.** Nudge the list so the same loud song doesn't crowd out
   everything else, and allow partial genre matches (like "indie pop" counting for a pop fan).

---

## 9. Personal Reflection  

**Biggest learning moment.** My biggest "aha" was watching the adversarial profile break the
system. When I asked for a *sad but high-energy* song, the only truly sad track landed dead
last. That taught me that a recommender is really just a pile of weights, and whichever
weight is biggest quietly decides everything. The math doesn't "understand" music at all.

**How AI tools helped, and where I double-checked.** The AI helped me scaffold the CSV
loader, the scoring function, and the ranking quickly, and it explained ideas like the
`.sort()` vs `sorted()` difference and why energy should reward *closeness* instead of
higher values. I still had to double-check things myself: the CLI import was wrong for
`python -m src.main`, the user-preference dictionary keys had to actually match what the code
read, and I had to run every profile and read the real output to confirm the rankings made
sense rather than trusting they would.

**What surprised me.** I was surprised that such simple rules — add a few points, sort the
list — can *feel* like real recommendations. There's no machine learning here, just weighted
matching, yet the lists look thoughtful. It made me realize how much of a "smart" app can be
plain arithmetic, and also how easily those simple choices hide biases, like over-trusting
genre or loudness.

**What I'd try next.** I'd fix the mood-vs-energy imbalance, add the unused audio features,
and test on a much bigger catalog so one or two extra pop songs can't make pop look
dominant.
