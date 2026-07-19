# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

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

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
