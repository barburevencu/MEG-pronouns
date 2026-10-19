"""Generate the counterbalancing sheet for all subjects.

Per subject: 160 trials = 10 sets x 16 cells, then shuffled and cut into
blocks of 32 trials (5 blocks). Odd subjects answer "congruent" with the
left red button, even subjects with the right one.

Usage: python3 make_counterbalancing.py [N_SUBJECTS]
"""
import csv
import itertools
import random
import sys
from pathlib import Path

SEED = 2026
N_SETS = 10
BLOCK_SIZE = 32
HERE = Path(__file__).resolve().parent
N_SUBJECTS = int(sys.argv[1]) if len(sys.argv) > 1 else 30

# Feminine forms of the adjectives (stimuli.csv lists masculine forms only).
FEM = {
    # people
    "têtu": "têtue", "déçu": "déçue", "fâché": "fâchée", "jaloux": "jalouse",
    "bavard": "bavarde", "content": "contente", "fatigué": "fatiguée",
    "inquiet": "inquiète", "enrhumé": "enrhumée", "méfiant": "méfiante",
    "peureux": "peureuse", "gourmand": "gourmande", "distrait": "distraite",
    "nerveux": "nerveuse", "courageux": "courageuse", "paresseux": "paresseuse",
    # places
    "vide": "vide", "aéré": "aérée", "vaste": "vaste", "rénové": "rénovée",
    "humide": "humide", "aménagé": "aménagée", "délabré": "délabrée",
    "repeint": "repeinte", "agrandi": "agrandie", "ventilé": "ventilée",
    "saccagé": "saccagée", "spacieux": "spacieuse", "restauré": "restaurée",
    "nettoyé": "nettoyée", "climatisé": "climatisée", "insalubre": "insalubre",
}

# English translations (adjectives keyed by masculine form).
EN = {
    "banquier": "banker", "policier": "police officer", "plombier": "plumber",
    "chasseur": "hunter", "jardinier": "gardener", "chauffeur": "chauffeur",
    "mécanicien": "mechanic", "pharmacien": "pharmacist", "fermière": "farmer",
    "danseuse": "dancer", "vendeuse": "saleswoman", "serveuse": "waitress",
    "chanteuse": "singer", "caissière": "cashier", "directrice": "director",
    "boulangère": "baker",
    "attendait": "was waiting", "buvait": "was drinking", "courait": "was running",
    "criait": "was shouting", "dormait": "was sleeping", "écrivait": "was writing",
    "hésitait": "was hesitating", "lisait": "was reading", "parlait": "was talking",
    "pensait": "was thinking", "pleurait": "was crying", "rêvait": "was dreaming",
    "riait": "was laughing", "toussait": "was coughing", "tremblait": "was trembling",
    "marchait": "was walking",
    "bureau": "the office", "cinéma": "the cinema", "musée": "the museum",
    "garage": "the garage", "magasin": "the shop", "salon": "the living room",
    "gymnase": "the gym", "théâtre": "the theatre", "salle": "the hall",
    "poste": "the post office", "classe": "the classroom", "mairie": "the town hall",
    "prison": "the prison", "cuisine": "the kitchen", "piscine": "the swimming pool",
    "chambre": "the bedroom",
    "têtu": "stubborn", "déçu": "disappointed", "fâché": "angry", "jaloux": "jealous",
    "bavard": "talkative", "content": "happy", "fatigué": "tired", "inquiet": "worried",
    "enrhumé": "sniffly", "méfiant": "suspicious", "peureux": "fearful",
    "gourmand": "greedy", "distrait": "absent-minded", "nerveux": "nervous",
    "courageux": "brave", "paresseux": "lazy",
    "vide": "empty", "aéré": "airy", "vaste": "vast", "rénové": "renovated",
    "humide": "damp", "aménagé": "fitted out", "délabré": "dilapidated",
    "repeint": "repainted", "agrandi": "enlarged", "ventilé": "ventilated",
    "saccagé": "ransacked", "spacieux": "spacious", "restauré": "restored",
    "nettoyé": "cleaned", "climatisé": "air-conditioned", "insalubre": "unsanitary",
}
# English pronoun follows the French pronoun's referent (place -> "It").
EN_PRON = {"m": "He", "f": "She"}

# stimuli.csv has duplicate header names, so read by position.
with open(HERE / "stimuli.csv", encoding="utf-8") as f:
    rows = list(csv.reader(f))[1:]
people = {"m": [r[0] for r in rows if r[1] == "m"], "f": [r[0] for r in rows if r[1] == "f"]}
places = {"m": [r[5] for r in rows if r[6] == "m"], "f": [r[5] for r in rows if r[6] == "f"]}
verbs = [r[3] for r in rows]
adj_people = [r[7] for r in rows]
adj_places = [r[8] for r in rows]

missing = sorted({w for w in [r[0] for r in rows] + verbs + [r[5] for r in rows]
                  + adj_people + adj_places if w not in EN}
                 | {a for a in adj_people + adj_places if a not in FEM})
if missing:
    sys.exit(f"stimuli.csv has words missing from FEM or EN: {', '.join(missing)}")

# stimuli.csv lists bare place nouns; none starts with a vowel or h, so no l'.
ART = {"m": "le", "f": "la"}
PRON = {"m": "Il", "f": "Elle"}

# 16 cells: agent gender (place gets the other), pronoun gender, canonical order, congruence
cells = list(itertools.product(["m", "f"], ["m", "f"], [True, False], [True, False]))


def adjective_pools(rng):
    """Each set uses 8 people- and 8 place-adjectives; consecutive set pairs
    exhaust the 16 of each, so every adjective appears 5 times over 10 sets."""
    while True:
        p, q = adj_people[:], adj_places[:]
        rng.shuffle(p)
        rng.shuffle(q)
        yield p[:8], q[:8]
        yield p[8:], q[8:]


def make_subject(subject_id):
    rng = random.Random(SEED + subject_id)
    pools = adjective_pools(rng)
    trials = []
    for cb_set in range(1, N_SETS + 1):
        ppl = {g: rng.sample(people[g], len(people[g])) for g in "mf"}
        plc = {g: rng.sample(places[g], len(places[g])) for g in "mf"}
        vbs = rng.sample(verbs, len(verbs))
        a_ppl, a_plc = (list(x) for x in next(pools))

        for agent_g, pron_g, canonical, congruent in cells:
            place_g = "f" if agent_g == "m" else "m"
            subj = ppl[agent_g].pop()
            place = plc[place_g].pop()
            verb = vbs.pop()

            referent = "agent" if pron_g == agent_g else "place"
            # Congruent: adjective fits the pronoun's referent; incongruent: fits the other noun.
            adj_type = referent if congruent else ("place" if referent == "agent" else "agent")
            adj_m = a_ppl.pop() if adj_type == "agent" else a_plc.pop()
            adj = adj_m if pron_g == "m" else FEM[adj_m]

            np_subj = f"{ART[agent_g]} {subj}"
            np_place = f"{ART[place_g]} {place}"
            if canonical:
                s1 = f"{np_subj} {verb} dans {np_place}."
            else:
                s1 = f"dans {np_place} {np_subj} {verb}."
            s1 = s1[0].upper() + s1[1:]
            s2 = f"{PRON[pron_g]} était {adj}."

            en_subj = f"the {EN[subj]}"
            if canonical:
                en1 = f"{en_subj} {EN[verb]} in {EN[place]}."
            else:
                en1 = f"in {EN[place]} {en_subj} {EN[verb]}."
            en1 = en1[0].upper() + en1[1:]
            en2 = f"{EN_PRON[pron_g] if referent == 'agent' else 'It'} was {EN[adj_m]}."

            trials.append({
                "subject_id": subject_id,
                "cb_set": cb_set,
                "agent_gender": agent_g,
                "place_gender": place_g,
                "pronoun_gender": pron_g,
                "pronoun_referent": referent,
                "canonical_order": int(canonical),
                "congruent": int(congruent),
                "adjective_type": "people" if adj_type == "agent" else "place",
                "subject": subj,
                "verb": verb,
                "place": place,
                "adjective": adj,
                "sentence1": s1,
                "sentence2": s2,
                "stimulus": f"{s1} {s2}",
                "translation": f"{en1} {en2}",
            })

    # Response mapping alternates across subjects: odd -> left red = congruent.
    congruent_key = "left" if subject_id % 2 else "right"
    incongruent_key = "right" if congruent_key == "left" else "left"

    rng.shuffle(trials)
    for i, t in enumerate(trials):
        t["block_number"] = i // BLOCK_SIZE + 1
        t["trial_number"] = i % BLOCK_SIZE + 1
        t["congruent_key"] = congruent_key
        t["correct_key"] = congruent_key if t["congruent"] else incongruent_key
    return trials


trials = [t for s in range(1, N_SUBJECTS + 1) for t in make_subject(s)]

first = ["subject_id", "block_number", "trial_number"]
fields = first + [k for k in trials[0] if k not in first]
with open(HERE / "counterbalancing.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(trials)
print(f"Wrote {len(trials)} trials ({N_SUBJECTS} subjects) to counterbalancing.csv")
