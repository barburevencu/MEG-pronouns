"""Generate the counterbalancing sheet for all subjects.

Per subject: 192 main trials = 12 sets x 16 cells. Each block's 32 main trials
are two consecutive sets, shuffled within the block (6 blocks), so every block
has each cell twice and each adjective once. Over the 6 blocks each adjective
takes 6 different cells, with each pronoun gender, word order and congruence 3
times. No two main trials share a first sentence (person, verb and place, in
either word order).

Fillers (fillers.csv): 48 verb + adjective items, 12 person-adjectives each
natural after 2 verbs and odd after 2 others; the pronoun always refers to the
person, and only the verb makes the adjective fit or clash. Each block gets 8,
one per judgment x person's gender x word order, at random positions among the
main trials, never two in a row (40 trials per block). Which items go in which
block, and with which gender and word order, rotates over subjects (a cycle of
24), with no verb in more than 2 of a block's fillers (FILLER_ORDER). Each
person and each place is used 3 times, with every person (and place)
once in each pair of blocks; a person never gets an adjective in EXCLUDE, and
no filler repeats the first sentence of a main trial or of another filler.

Training (block 0, before block 1): 20 trials, one more set of 16 main trials
(a random half of each adjective list) and 4 of the 48 fillers (2 natural, 2
odd, rotating over subjects), shuffled with a main trial first and never two
fillers in a row; no first sentence repeats one of the subject's other trials.

Every subject answers "congruent" / "natural" with the right button and
"incongruent" / "odd" with the left one (no counterbalancing).

Usage: python3 make_counterbalancing.py [N_SUBJECTS]
"""
import csv
import itertools
import random
import sys
from pathlib import Path

SEED = 2026
N_SETS = 12
BLOCK_SIZE = 32          # main trials per block
FILLERS_PER_BLOCK = 8
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
    "repeint": "repeinte", "luxueux": "luxueuse", "ventilé": "ventilée",
    "saccagé": "saccagée", "spacieux": "spacieuse", "restauré": "restaurée",
    "vétuste": "vétuste", "climatisé": "climatisée", "insalubre": "insalubre",
}

# English translations (adjectives keyed by masculine form).
EN = {
    "marin": "sailor", "facteur": "mail carrier", "bûcheron": "lumberjack",
    "plongeur": "diver", "bijoutier": "jeweller", "chauffeur": "chauffeur",
    "menuisier": "carpenter", "mécanicien": "mechanic", "nonne": "nun",
    "bergère": "shepherdess", "danseuse": "dancer", "serveuse": "waitress",
    "caissière": "cashier", "chanteuse": "singer", "coiffeuse": "hairdresser",
    "couturière": "seamstress",
    "attendait": "was waiting", "buvait": "was drinking", "courait": "was running",
    "criait": "was shouting", "dormait": "was sleeping", "écrivait": "was writing",
    "hésitait": "was hesitating", "lisait": "was reading", "parlait": "was talking",
    "pensait": "was thinking", "pleurait": "was crying", "rêvait": "was dreaming",
    "riait": "was laughing", "toussait": "was coughing", "tremblait": "was trembling",
    "marchait": "was walking",
    "musée": "the museum", "dortoir": "the dormitory", "tribunal": "the courtroom",
    "pressing": "the dry cleaner's", "parlement": "the parliament",
    "vestiaire": "the locker room", "chapiteau": "the circus tent",
    "réfectoire": "the dining hall", "serre": "the greenhouse",
    "piscine": "the swimming pool", "garderie": "the daycare", "clinique": "the clinic",
    "brasserie": "the brasserie", "librairie": "the bookshop",
    "boucherie": "the butcher's shop", "cathédrale": "the cathedral",
    "têtu": "stubborn", "déçu": "disappointed", "fâché": "angry", "jaloux": "jealous",
    "bavard": "talkative", "content": "happy", "fatigué": "tired", "inquiet": "worried",
    "enrhumé": "sniffly", "méfiant": "suspicious", "peureux": "fearful",
    "gourmand": "greedy", "distrait": "absent-minded", "nerveux": "nervous",
    "courageux": "brave", "paresseux": "lazy",
    "vide": "empty", "aéré": "airy", "vaste": "vast", "rénové": "renovated",
    "humide": "damp", "aménagé": "fitted out", "délabré": "dilapidated",
    "repeint": "repainted", "luxueux": "luxurious", "ventilé": "ventilated",
    "saccagé": "ransacked", "spacieux": "spacious", "restauré": "restored",
    "vétuste": "run-down", "climatisé": "air-conditioned", "insalubre": "unsanitary",
}
# Filler adjectives in English (fillers.csv gives the French forms).
FILLER_EN = {
    "assoupi": "dozing", "illettré": "illiterate", "muet": "mute", "silencieux": "silent",
    "allongé": "lying down", "assis": "sitting", "immobile": "motionless",
    "attentif": "attentive", "éveillé": "awake", "calme": "calm",
    "furieux": "furious", "joyeux": "joyful",
}
# Person + filler adjective pairs never drawn: odd from world knowledge alone.
EXCLUDE = {("chanteuse", "muet"), ("chanteuse", "silencieux"), ("facteur", "illettré"),
           ("caissière", "illettré")}
# Verb + person-adjective pairs that clash (e.g. crying but happy): never in a
# congruent main trial whose pronoun refers to the person, which would then
# look odd for the same reason as an odd filler.
CLASH = {
    ("riait", "déçu"), ("riait", "fâché"), ("pleurait", "content"),
    ("riait", "inquiet"), ("riait", "jaloux"), ("riait", "peureux"),
    ("dormait", "fâché"), ("dormait", "inquiet"), ("dormait", "nerveux"),
    ("dormait", "méfiant"), ("dormait", "jaloux"),
    ("courait", "paresseux"), ("tremblait", "courageux"),
    ("hésitait", "têtu"), ("hésitait", "courageux"),
}
# English pronoun follows the French pronoun's referent (place -> "It").
EN_PRON = {"m": "He", "f": "She"}

# stimuli.csv has two "gender" columns, each right after its noun column,
# so look columns up by header name and take gender by position.
with open(HERE / "stimuli.csv", encoding="utf-8") as f:
    header, *rows = csv.reader(f)
col = {name: i for i, name in enumerate(header)}
P, PL = col["people"], col["places"]
people = {g: [r[P] for r in rows if r[P + 1] == g] for g in "mf"}
places = {g: [r[PL] for r in rows if r[PL + 1] == g] for g in "mf"}
verbs = [r[col["verbs"]] for r in rows]
adj_people = [r[col["adjectives (masculine, for people)"]] for r in rows]
adj_places = [r[col["adjectives for places"]] for r in rows]

missing = sorted({w for w in [r[P] for r in rows] + verbs + [r[PL] for r in rows]
                  + adj_people + adj_places if w not in EN}
                 | {a for a in adj_people + adj_places if a not in FEM})
if missing:
    sys.exit(f"stimuli.csv has words missing from FEM or EN: {', '.join(missing)}")

# stimuli.csv lists bare place nouns; none starts with a vowel or h, so no l'.
ART = {"m": "le", "f": "la"}
PRON = {"m": "Il", "f": "Elle"}

# 16 cells: agent gender (place gets the other), pronoun gender, canonical order, congruence
cells = list(itertools.product(["m", "f"], ["m", "f"], [True, False], [True, False]))
# The 8 cells of a set that take a people- (or a place-) adjective, keyed by
# pronoun gender, canonical order and congruence (the agent's gender follows).
ADJ_CELLS = list(itertools.product(["m", "f"], [True, False], [True, False]))


def adjective_design(rng, adjectives):
    """The 16 adjectives of one list over the 12 sets: for each set, a dict
    ADJ_CELLS key -> adjective. Each adjective is in one set of each block
    (sets 2b-1 and 2b), in 6 different cells: all but one cell and its
    opposite (every factor flipped), so it has each pronoun gender, word order
    and congruence 3 times.

    Cell x (0-7, an index into ADJ_CELLS) has opposite 7 - x; pair q (0-3) is
    cells q and 7 - q. The adjectives form 4 groups of 4, group g never taking
    pair g. In each block every group fills one other pair, g -> g XOR s, with
    each step s in 1-3 used in 2 blocks, so a group visits each of its pairs
    twice: half its adjectives take cell q the first time and 7 - q the
    second, the other half the reverse. A cell's 2 adjectives go one to each
    set of the block."""
    adjs = rng.sample(adjectives, len(adjectives))
    groups = [adjs[4 * g:4 * g + 4] for g in range(4)]
    steps = rng.sample([1, 2, 2, 3, 3, 1], 6)
    sets = []
    visits = {}  # (group, pair) -> times visited so far
    for s in steps:
        first, second = {}, {}
        for g, members in enumerate(groups):
            q = g ^ s
            n = visits.get((g, q), 0)
            visits[(g, q)] = n + 1
            halves = (members[:2], members[2:]) if n == 0 else (members[2:], members[:2])
            for x, half in ((q, halves[0]), (7 - q, halves[1])):
                a, b = rng.sample(half, 2)
                first[ADJ_CELLS[x]], second[ADJ_CELLS[x]] = a, b
        sets += [first, second]
    return sets


with open(HERE / "fillers.csv", encoding="utf-8") as f:
    filler_items = list(csv.DictReader(f))
if sorted({r["adjective_m"] for r in filler_items}) != sorted(FILLER_EN):
    sys.exit("fillers.csv and FILLER_EN list different adjectives")
# Natural items in the order adjective 1-12 (first verb), then adjective 1-12
# (second verb); odd items likewise. Items i and i + 12 (same adjective) are
# then 12 rotation steps, i.e. 3 blocks, apart. The adjective order and which
# verb comes first (found by search) keep every verb to at most 2 of a block's
# fillers, and the 4 training fillers to 4 different verbs, for every subject.
FILLER_ORDER = [  # adjective, its first natural verb, its first odd verb
    ("allongé", "pleurait", "courait"),
    ("attentif", "écrivait", "rêvait"),
    ("silencieux", "marchait", "criait"),
    ("assis", "riait", "marchait"),
    ("éveillé", "courait", "dormait"),
    ("assoupi", "rêvait", "courait"),
    ("joyeux", "criait", "pleurait"),
    ("muet", "marchait", "criait"),
    ("immobile", "dormait", "marchait"),
    ("illettré", "courait", "écrivait"),
    ("calme", "marchait", "tremblait"),
    ("furieux", "criait", "riait"),
]


def filler_list(judgment, col):
    items = {(r["adjective_m"], r["verb"]): r for r in filler_items if r["judgment"] == judgment}
    first = [items.pop((adj, row[col])) for adj, *row in FILLER_ORDER]
    second = [items.pop(next(k for k in items if k[0] == adj)) for adj, *_ in FILLER_ORDER]
    assert not items
    return first + second


NATURAL, ODD = filler_list("natural", 0), filler_list("odd", 1)
assert len(NATURAL) == len(ODD) == 24
# Rotation step k puts natural items k'..k'+3 and odd items k'-8..k'-5 (mod 24)
# in one block, for every start k'.
for j in range(24):
    block_verbs = [NATURAL[(j + t) % 24]["verb"] for t in range(4)] + \
                  [ODD[(j - 8 + t) % 24]["verb"] for t in range(4)]
    assert max(block_verbs.count(v) for v in block_verbs) <= 2, f"verb cap broken at {j}"
# Either form of a filler adjective -> its masculine form.
FILLER_ADJ = {r[k]: r["adjective_m"] for r in filler_items for k in ("adjective_m", "adjective_f")}


def make_fillers(subject_id, main_trials, rng):
    """The subject's 48 fillers, with block_number set, in block order."""
    # Rotation (see the README, "How the filler rotation works"): 24 slots of
    # (block, version) per judgment; subject n moves every item n - 1 slots
    # on, so over 24 subjects each item takes every slot once.
    k = (subject_id - 1) % 24
    slots = []  # (item, block, agent gender, canonical)
    for items, shift in ((NATURAL, 0), (ODD, 8)):  # odd items 2 blocks after natural
        for i, item in enumerate(items):
            s = (i + k + shift) % 24
            block, cell = s // 4 + 1, (s + s // 4) % 4  # each block: all 4 cells
            slots.append((item, block, "mf"[cell & 1], cell < 2))
    slots.sort(key=lambda x: x[1])
    main_s1 = {(t["subject"], t["verb"], t["place"]) for t in main_trials}

    # Nouns: three shuffles of each gender's 8 people (and places), one per
    # pair of blocks, so each block's 4 people of a gender are all different.
    for _ in range(10000):
        ppl = {g: [x for _ in range(3) for x in rng.sample(people[g], 8)] for g in "mf"}
        plc = {g: [x for _ in range(3) for x in rng.sample(places[g], 8)] for g in "mf"}
        fillers, seen = [], set()
        for item, block, agent_g, canonical in slots:
            place_g = "f" if agent_g == "m" else "m"
            subj, place = ppl[agent_g].pop(0), plc[place_g].pop(0)
            fillers.append((item, block, agent_g, place_g, canonical, subj, place))
            seen.add((subj, item["verb"], place))
        if (len(seen) == len(fillers) and not seen & main_s1
                and not any((f[5], f[0]["adjective_m"]) in EXCLUDE for f in fillers)):
            break
    else:
        sys.exit(f"subject {subject_id}: no filler nouns satisfy the constraints")

    return [filler_row(subject_id, item, block, agent_g, canonical, subj, place)
            for item, block, agent_g, place_g, canonical, subj, place in fillers]


def filler_row(subject_id, item, block, agent_g, canonical, subj, place):
    place_g = "f" if agent_g == "m" else "m"
    verb, adj_m = item["verb"], item["adjective_m"]
    adj = adj_m if agent_g == "m" else item["adjective_f"]
    np_subj, np_place = f"{ART[agent_g]} {subj}", f"{ART[place_g]} {place}"
    s1 = f"{np_subj} {verb} dans {np_place}." if canonical else f"dans {np_place} {np_subj} {verb}."
    s1 = s1[0].upper() + s1[1:]
    s2 = f"{PRON[agent_g]} était {adj}."
    en1 = (f"the {EN[subj]} {EN[verb]} in {EN[place]}." if canonical
           else f"in {EN[place]} the {EN[subj]} {EN[verb]}.")
    en1 = en1[0].upper() + en1[1:]
    return {
        "subject_id": subject_id,
        "block_number": block,
        "trial_type": "filler",
        "cb_set": "NA",
        "agent_gender": agent_g,
        "place_gender": place_g,
        "pronoun_gender": agent_g,
        "pronoun_referent": "agent",
        "canonical_order": int(canonical),
        "congruent": int(item["judgment"] == "natural"),  # the adjective fits the verb
        "adjective_type": "people",
        "subject": subj,
        "verb": verb,
        "place": place,
        "adjective": adj,
        "sentence1": s1,
        "sentence2": s2,
        "stimulus": f"{s1} {s2}",
        "translation": f"{en1} {EN_PRON[agent_g]} was {FILLER_EN[adj_m]}.",
    }


def make_set(rng, subject_id, cb_set, ppl, plc, a_ppl, a_plc, avoid=frozenset()):
    """16 main trials, one per cell, from shuffled people and places (by
    gender) and the people- and place-adjective of each cell (dicts keyed as
    ADJ_CELLS). Verbs are drawn so that no congruent person-referent trial
    clashes (CLASH) and no first sentence is in avoid."""
    out = []
    draws = []
    for agent_g, pron_g, canonical, congruent in cells:
        place_g = "f" if agent_g == "m" else "m"
        referent = "agent" if pron_g == agent_g else "place"
        # Congruent: adjective fits the pronoun's referent; incongruent: fits the other noun.
        adj_type = referent if congruent else ("place" if referent == "agent" else "agent")
        adj_m = (a_ppl if adj_type == "agent" else a_plc)[(pron_g, canonical, congruent)]
        draws.append((agent_g, pron_g, canonical, congruent, place_g, referent, adj_type, adj_m,
                      ppl[agent_g].pop(), plc[place_g].pop()))
    # Verbs: reshuffled until no congruent person-referent trial clashes.
    while True:
        vbs = rng.sample(verbs, len(verbs))
        if not any(c and r == "agent" and (v, a) in CLASH or (sj, v, pl) in avoid
                   for (_, _, _, c, _, r, _, a, sj, pl), v in zip(draws, vbs)):
            break

    for (agent_g, pron_g, canonical, congruent, place_g, referent, adj_type, adj_m, subj, place), verb \
            in zip(draws, vbs):
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

        out.append({
            "subject_id": subject_id,
            "trial_type": "main",
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
    return out


def make_training(subject_id, avoid, rng):
    """Block 0: 16 main trials (one set, with a random half of each adjective
    list) and 4 of the 48 fillers, shuffled, a main trial first and never two
    fillers in a row. No first sentence repeats one in avoid (the subject's
    other trials)."""
    p, q = adj_people[:], adj_places[:]
    rng.shuffle(p)
    rng.shuffle(q)
    ppl = {g: rng.sample(people[g], len(people[g])) for g in "mf"}
    plc = {g: rng.sample(places[g], len(places[g])) for g in "mf"}
    main = make_set(rng, subject_id, "training", ppl, plc,
                    dict(zip(ADJ_CELLS, p[:8])), dict(zip(ADJ_CELLS, q[:8])), avoid)
    avoid = avoid | {(t["subject"], t["verb"], t["place"]) for t in main}

    # Fillers: 2 natural, 2 odd, of 4 different adjectives, with gender and
    # word order crossed; over 24 subjects each item is used twice.
    k = (subject_id - 1) % 24
    swap = {"m": "f", "f": "m"} if k % 2 else {"m": "m", "f": "f"}
    specs = [(NATURAL[k], swap["m"], True), (NATURAL[(k + 6) % 24], swap["f"], False),
             (ODD[(k + 3) % 24], swap["m"], False), (ODD[(k + 9) % 24], swap["f"], True)]
    for _ in range(10000):
        ppl = {g: rng.sample(people[g], 2) for g in "mf"}
        plc = {g: rng.sample(places[g], 2) for g in "mf"}
        fillers = []
        for item, agent_g, canonical in specs:
            subj, place = ppl[agent_g].pop(), plc["f" if agent_g == "m" else "m"].pop()
            fillers.append(filler_row(subject_id, item, 0, agent_g, canonical, subj, place))
        if not any((t["subject"], t["verb"], t["place"]) in avoid
                   or (t["subject"], FILLER_ADJ[t["adjective"]]) in EXCLUDE for t in fillers):
            break
    else:
        sys.exit(f"subject {subject_id}: no training filler nouns satisfy the constraints")

    rng.shuffle(main)
    rng.shuffle(fillers)
    gaps = set(rng.sample(range(1, len(main) + 1), len(fillers)))  # not before the first trial
    out = []
    for g in range(len(main) + 1):
        if g in gaps:
            out.append(fillers.pop())
        if g < len(main):
            out.append(main[g])
    for i, t in enumerate(out, 1):
        t["block_number"], t["trial_number"] = 0, i
    return out


def make_subject(subject_id):
    rng = random.Random(SEED + subject_id)
    design_ppl, design_plc = adjective_design(rng, adj_people), adjective_design(rng, adj_places)
    trials = []
    for cb_set in range(1, N_SETS + 1):
        ppl = {g: rng.sample(people[g], len(people[g])) for g in "mf"}
        plc = {g: rng.sample(places[g], len(places[g])) for g in "mf"}
        used = {(t["subject"], t["verb"], t["place"]) for t in trials}
        trials += make_set(rng, subject_id, cb_set, ppl, plc,
                           design_ppl[cb_set - 1], design_plc[cb_set - 1], used)

    # Same response mapping for everyone: right = congruent / natural.
    congruent_key, incongruent_key = "right", "left"

    # Trials are in set order: block b is sets 2b-1 and 2b, shuffled.
    blocks = [trials[i:i + BLOCK_SIZE] for i in range(0, len(trials), BLOCK_SIZE)]
    for block in blocks:
        rng.shuffle(block)

    # Fillers, from their own generator so the main trials stay as they were.
    frng = random.Random(SEED * 1000 + subject_id)
    fillers = make_fillers(subject_id, trials, frng)
    # Training (block 0), from its own generator too.
    avoid = {(t["subject"], t["verb"], t["place"]) for t in trials + fillers}
    out = make_training(subject_id, avoid, random.Random(SEED * 2000 + subject_id))
    for b, block in enumerate(blocks, 1):
        fb = [t for t in fillers if t["block_number"] == b]
        assert len(fb) == FILLERS_PER_BLOCK
        frng.shuffle(fb)
        # One filler at most in each of the 33 gaps around the main trials,
        # so no two fillers are adjacent.
        gaps = set(frng.sample(range(len(block) + 1), len(fb)))
        merged = []
        for g in range(len(block) + 1):
            if g in gaps:
                merged.append(fb.pop())
            if g < len(block):
                merged.append(block[g])
        for i, t in enumerate(merged, 1):
            t["block_number"], t["trial_number"] = b, i
        out += merged
    for t in out:
        t["congruent_key"] = congruent_key
        t["correct_key"] = congruent_key if t["congruent"] else incongruent_key
    return out


trials = [t for s in range(1, N_SUBJECTS + 1) for t in make_subject(s)]

first = ["subject_id", "block_number", "trial_number"]
fields = first + [k for k in trials[0] if k not in first]
with open(HERE / "counterbalancing.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(trials)
print(f"Wrote {len(trials)} trials ({N_SUBJECTS} subjects) to counterbalancing.csv")
