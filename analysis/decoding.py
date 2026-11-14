"""Person-vs-place decoding: trained on the localizer, tested at the pronoun.

    python3 analysis/decoding.py 001 002        # per subject: fit, test, save, plot
    python3 analysis/decoding.py --group        # every saved subject: average, cluster stats, plot

Inputs: the cleaned epochs of the MNE-BIDS pipeline (data/preprocessing/config.py),
    <deriv-root>/sub-XXX/meg/sub-XXX_task-localizer_proc-clean_epo.fif
    <deriv-root>/sub-XXX/meg/sub-XXX_task-pronouns_proc-clean_epo.fif
Both tasks are Maxwell-filtered to the same head position (pronouns run 01), so a
decoder trained on one applies to the other.

Steps, per subject:
 1. Localizer: words and pictures of the 16 people and 16 places (animals left out),
    decimated to ~125 Hz, 0-0.8 s (the next item appears at 0.8 s). Label: person (1)
    vs place (0); the 8 m / 8 f of each category also give a gender label.
 2. Checks within the localizer: time-resolved AUC, cross-validated with whole items
    left out (StratifiedGroupKFold by item, so the decoder must generalize to unseen
    concepts); for the pooled set, words only and pictures only; across modalities
    (train words -> test pictures and back); and the gender decoder.
 3. Pronoun: main-trial pronoun epochs (fillers have their own codes and are left
    out), -0.2-1.0 s (pronoun 0, "était" 0.3, adjective 0.6). Referent = person when
    the pronoun's gender equals the agent's. Pooled over agent gender, which keeps
    pronoun gender independent of the referent.
 4. Temporal generalization: a decoder per localizer time, fitted on all localizer
    epochs (pooled, words only, pictures only), applied at every pronoun time ->
    decision values (trial x train time x test time); AUC against the referent
    (person = positive class, chance 0.5) and person - place mean decision value.
    Positive control first: the same decoders applied to the nouns of sentence 1
    (the person, label 1, and the place, label 0, of every main trial; pooled over
    word order, which balances their positions). If they cannot tell the nouns
    apart where they are read, they will not find the referent at the pronoun.
 5. Controls: per (train, test) time, decision value ~ referent + pronoun gender
    (both coded +-0.5); AUC separately for each word order; the localizer gender
    decoder on the pronoun (label: pronoun feminine); the person-vs-place decoder on
    the adjective epochs (label: person- vs place-adjective), a separate effect.
 6. Within the main task: person vs place trained on the sentence-1 nouns (-0.2-1.0 s
    around each noun), tested at the pronoun, with folds of whole trials (trials are
    told apart by the gaps between their events), so the decoder tested on a trial's
    pronoun never saw that trial's nouns; AUC against the referent, per word order,
    and the same regression as in 5. Also the nouns' own cross-validated AUC.
    Caveats: the same 32 nouns recur across trials, so the nouns' own AUC can rest
    on item identity (which the pronoun test cannot); and after +0.3 s the person is
    always followed by the verb, the place by a determiner or the end of the sentence
    (the pronoun is always followed by "était", so this adds noise, not bias, there).
Saved to analysis/decoding/sub-XXX_decoding.npz (+ the pooled decoder's per-trial
decision values and the trial table), figure sub-XXX_decoding.png.

Group: stacks the subjects' scores; one-sample cluster permutation tests of AUC - 0.5
(and betas vs 0), two-tailed, over time (curves) or train x test time (matrices).
Only with at least MIN_SUBJECTS_STATS subjects; otherwise averages only.
"""
import argparse
import re
import unicodedata
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mne
import numpy as np
import pandas as pd
from mne.decoding import GeneralizingEstimator, SlidingEstimator, cross_val_multiscore
from scipy.stats import rankdata
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

PROJECT = Path(__file__).resolve().parents[1]
DERIV_ROOT = PROJECT / "data" / "meg" / "bids" / "derivatives" / "mne-bids-pipeline"
OUT = PROJECT / "analysis" / "decoding"
STIMULI = PROJECT / "counterbalancing" / "stimuli.csv"

SFREQ = 125                 # decoding sampling rate (Hz)
LOC_TMIN, LOC_TMAX = 0.0, 0.8
N_FOLDS = 5
C = 1.0                     # inverse L2 penalty of the logistic regression
SEED = 42
MIN_SUBJECTS_STATS = 6
TRIAL_GAP_S = 3.0           # event gap that separates two main-task trials (see trial_ids)
SUMMARY_TRAIN =(0.15, 0.5)  # localizer times averaged for the sentence-noun curves (picture decoding peaks here)
WORD_ONSETS = {"pronoun": 0.0, "était": 0.3, "adjective": 0.6}  # within the pronoun epoch


# ---------------------------------------------------------------------------
# Labels

def slug(text):
    """As in data/preprocessing/raw_to_bids.py: the item part of the event names."""
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def item_genders():
    """slug(person or place) -> 'm' / 'f', from stimuli.csv."""
    s = pd.read_csv(STIMULI)
    genders = dict(zip(s["people"].map(slug), s["gender"]))
    genders.update(zip(s["places"].map(slug), s["gender.1"]))
    return genders


def event_names(epochs):
    inverse = {code: name for name, code in epochs.event_id.items()}
    return [inverse[code] for code in epochs.events[:, 2]]


def localizer_trials(epochs):
    """Person and place epochs of the localizer, with their trial table."""
    names = event_names(epochs)
    keep = [i for i, n in enumerate(names)
            if n.startswith("loc/") and n.split("/")[2] in ("person", "place")]
    parts = [names[i].split("/") for i in keep]
    meta = pd.DataFrame({
        "modality": [p[1] for p in parts],
        "category": [p[2] for p in parts],
        "item": [p[3] for p in parts],
    })
    meta["person"] = (meta.category == "person").astype(int)
    meta["feminine"] = (meta.item.map(item_genders()) == "f").astype(int)
    if meta.item.map(item_genders()).isna().any():
        raise ValueError(f"items missing from stimuli.csv: {sorted(set(meta.item) - set(item_genders()))}")
    return epochs[keep], meta


def main_trials(epochs, role):
    """Main-trial epochs of one word role (e.g. 'pronoun'), with their trial table.
    Event names: word/<role>/<cong|incong>/<canon|noncanon>/<pron_m|pron_f>/<agent_m|agent_f>."""
    names = event_names(epochs)
    keep = [i for i, n in enumerate(names) if n.startswith(f"word/{role}/")]
    parts = [names[i].split("/") for i in keep]
    meta = pd.DataFrame({
        "congruent": [int(p[2] == "cong") for p in parts],
        "canonical": [int(p[3] == "canon") for p in parts],
        "pron_feminine": [int(p[4] == "pron_f") for p in parts],
        "agent_feminine": [int(p[5] == "agent_f") for p in parts],
    })
    meta["referent_person"] = (meta.pron_feminine == meta.agent_feminine).astype(int)
    # a natural trial's adjective fits the referent; an odd trial's fits the other noun
    meta["adjective_person"] = (meta.referent_person == meta.congruent).astype(int)
    meta["trial"] = epochs.metadata["trial"].to_numpy()[keep]
    return epochs[keep], meta


def trial_ids(epochs):
    """Trial index of every main-task epoch, from the event times: the words of a
    trial are at most 1.3 s apart (the break between the sentences), consecutive
    trials more than 4 s; a backwards jump in time (next run) also starts a trial."""
    samples = epochs.events[:, 0].astype(float)
    gap = np.diff(samples) / epochs.info["sfreq"]
    return np.concatenate([[0], np.cumsum((gap < 0) | (gap > TRIAL_GAP_S))])


# ---------------------------------------------------------------------------
# Data

def load_epochs(subject, task, deriv_root):
    path = Path(deriv_root) / f"sub-{subject}" / "meg" / f"sub-{subject}_task-{task}_proc-clean_epo.fif"
    epochs = mne.read_epochs(path, preload=True, verbose="error")
    if task == "pronouns":  # before decimating: the event samples are at the epochs' own rate
        metadata = epochs.metadata if epochs.metadata is not None else pd.DataFrame(index=range(len(epochs)))
        with mne.use_log_level("error"):
            epochs.metadata = metadata.assign(trial=trial_ids(epochs))
    factor = epochs.info["sfreq"] / SFREQ
    if factor >= 2:
        if not np.isclose(factor, round(factor)):
            raise ValueError(f"{path.name}: {epochs.info['sfreq']} Hz is not a multiple of {SFREQ} Hz")
        epochs.decimate(int(round(factor)), verbose="error")  # data are low-passed at 40 Hz
    return epochs


def common_channels(*epochs_list):
    """MEG channels good in every set, in the first set's order."""
    sets = [set(mne.pick_info(e.info, mne.pick_types(e.info, meg=True, exclude="bads")).ch_names)
            for e in epochs_list]
    first = epochs_list[0].ch_names
    return [ch for ch in first if all(ch in s for s in sets)]


def X_of(epochs, channels):
    return epochs.get_data(picks=channels, copy=True)


# ---------------------------------------------------------------------------
# Decoding

def classifier():
    return make_pipeline(StandardScaler(), LogisticRegression(C=C, solver="lbfgs", max_iter=1000))


def cv_auc(X, y, groups, n_jobs):
    """Time-resolved AUC, cross-validated with whole items left out."""
    est = SlidingEstimator(classifier(), scoring="roc_auc", n_jobs=n_jobs, verbose=False)
    cv = StratifiedGroupKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
    return cross_val_multiscore(est, X, y, groups=groups, cv=cv, verbose=False).mean(axis=0)


def transfer_auc(X_train, y_train, X_test, y_test, n_jobs):
    """Time-resolved AUC of a decoder trained on one set and tested on another (same times)."""
    est = SlidingEstimator(classifier(), scoring="roc_auc", n_jobs=n_jobs, verbose=False)
    est.fit(X_train, y_train)
    return est.score(X_test, y_test)


def fit_generalizing(X_train, y_train, n_jobs):
    """One decoder per training time; its decision_function(X_test) gives decision
    values (trial x train time x test time), positive = class 1."""
    return GeneralizingEstimator(classifier(), n_jobs=n_jobs, verbose=False).fit(X_train, y_train)


def within_task(X_noun, noun, X_pron, pron, n_jobs):
    """Person vs place trained on the sentence-1 nouns, tested at the pronoun, with
    folds of whole trials: the decoder that is tested on a trial's pronoun never saw
    that trial's nouns. Decision values of all folds are pooled (trial x train time x
    test time)."""
    trials = np.unique(np.concatenate([noun.trial, pron.trial]))
    fold = dict(zip(np.random.default_rng(SEED).permutation(trials), np.arange(len(trials)) % N_FOLDS))
    noun_fold, pron_fold = noun.trial.map(fold).to_numpy(), pron.trial.map(fold).to_numpy()
    y = noun.noun_person.to_numpy()
    dv = None
    for f in range(N_FOLDS):
        decoder = fit_generalizing(X_noun[noun_fold != f], y[noun_fold != f], n_jobs)
        test = pron_fold == f
        d = decoder.decision_function(X_pron[test])
        if dv is None:
            dv = np.zeros((len(pron),) + d.shape[1:])
        dv[test] = d
    return dv


def auc(dv, y):
    """AUC of decision values dv (trials x ...) for binary labels y, vectorized
    (Mann-Whitney U / (n1 n0)); ties get mid-ranks."""
    y = np.asarray(y).astype(bool)
    ranks = rankdata(dv, axis=0)
    n1, n0 = y.sum(), (~y).sum()
    return (ranks[y].sum(axis=0) - n1 * (n1 + 1) / 2) / (n1 * n0)


def regress(dv, predictors):
    """OLS of dv (trials x ...) on an intercept and the given 0/1 predictors coded
    +-0.5; returns one beta map per predictor."""
    design = np.column_stack([np.ones(len(dv))] + [np.asarray(p) - 0.5 for p in predictors])
    betas, *_ = np.linalg.lstsq(design, dv.reshape(len(dv), -1), rcond=None)
    return [b.reshape(dv.shape[1:]) for b in betas[1:]]


# ---------------------------------------------------------------------------
# Per subject

def run_subject(subject, deriv_root, n_jobs):
    loc_epochs, loc = localizer_trials(load_epochs(subject, "localizer", deriv_root))
    main_epochs = load_epochs(subject, "pronouns", deriv_root)
    pron_epochs, pron = main_trials(main_epochs, "pronoun")
    adj_epochs, adj = main_trials(main_epochs, "adjective")
    subj_epochs, subj = main_trials(main_epochs, "noun_subj")
    place_epochs, place = main_trials(main_epochs, "noun_place")
    loc_epochs.crop(LOC_TMIN, LOC_TMAX)

    channels = common_channels(loc_epochs, pron_epochs)
    X_loc, X_pron, X_adj = (X_of(e, channels) for e in (loc_epochs, pron_epochs, adj_epochs))
    # Nouns of sentence 1 (positive control): the person (1) and the place (0) of every
    # trial. Pooled over word order, their positions in the sentence are balanced
    # (canonical: person 2nd, place 6th; non-canonical: place 3rd, person 5th).
    X_noun = np.concatenate([X_of(subj_epochs, channels), X_of(place_epochs, channels)])
    noun = pd.concat([subj.assign(noun_person=1), place.assign(noun_person=0)], ignore_index=True)
    print(f"sub-{subject}: {len(channels)} channels; localizer {len(loc)} epochs "
          f"({(loc.modality == 'word').sum()} words, {(loc.modality == 'image').sum()} pictures); "
          f"pronoun {len(pron)} ({pron.referent_person.sum()} person referents); adjective {len(adj)}; "
          f"nouns {len(subj)} person + {len(place)} place")

    word = (loc.modality == "word").to_numpy()
    sets = {"pooled": np.ones(len(loc), bool), "word": word, "image": ~word}
    r = {"loc_times": loc_epochs.times, "pron_times": pron_epochs.times, "adj_times": adj_epochs.times,
         "noun_times": subj_epochs.times, "n_channels": len(channels), "n_loc": len(loc),
         "n_pron": len(pron), "n_adj": len(adj), "n_noun": len(noun)}

    # 2. Checks within the localizer
    for name, s in sets.items():
        r[f"loc_cv_{name}"] = cv_auc(X_loc[s], loc.person[s].to_numpy(), loc.item[s].to_numpy(), n_jobs)
    r["loc_word_to_image"] = transfer_auc(X_loc[word], loc.person[word], X_loc[~word], loc.person[~word], n_jobs)
    r["loc_image_to_word"] = transfer_auc(X_loc[~word], loc.person[~word], X_loc[word], loc.person[word], n_jobs)
    r["loc_cv_gender"] = cv_auc(X_loc, loc.feminine.to_numpy(), loc.item.to_numpy(), n_jobs)

    # Decoders fitted on the whole localizer, one per training set
    decoders = {name: fit_generalizing(X_loc[s], loc.person[s].to_numpy(), n_jobs) for name, s in sets.items()}

    # Positive control: the nouns of sentence 1
    noun_person = noun.noun_person.to_numpy()
    canon = noun.canonical.to_numpy() == 1
    for name, decoder in decoders.items():
        dv = decoder.decision_function(X_noun)
        r[f"noun_auc_{name}"] = auc(dv, noun_person)
        if name == "pooled":
            r["noun_auc_canonical"] = auc(dv[canon], noun_person[canon])
            r["noun_auc_noncanonical"] = auc(dv[~canon], noun_person[~canon])

    # 4. Temporal generalization to the pronoun
    referent = pron.referent_person.to_numpy()
    for name, decoder in decoders.items():
        dv = decoder.decision_function(X_pron)
        r[f"pron_auc_{name}"] = auc(dv, referent)
        if name == "pooled":
            dv_pooled = dv
    r["pron_diff_pooled"] = dv_pooled[referent == 1].mean(0) - dv_pooled[referent == 0].mean(0)

    # 5. Controls
    r["pron_beta_referent"], r["pron_beta_pron_gender"] = regress(
        dv_pooled, [referent, pron.pron_feminine.to_numpy()])
    canon = pron.canonical.to_numpy() == 1
    r["pron_auc_canonical"] = auc(dv_pooled[canon], referent[canon])
    r["pron_auc_noncanonical"] = auc(dv_pooled[~canon], referent[~canon])
    r["pron_gender_auc"] = auc(fit_generalizing(X_loc, loc.feminine.to_numpy(), n_jobs).decision_function(X_pron),
                               pron.pron_feminine.to_numpy())
    r["adj_auc_pooled"] = auc(decoders["pooled"].decision_function(X_adj), adj.adjective_person.to_numpy())

    # 6. Within the main task: sentence-1 nouns -> pronoun, folds of whole trials
    r["within_noun_cv"] = cv_auc(X_noun, noun_person, noun.trial.to_numpy(), n_jobs)
    dv_within = within_task(X_noun, noun, X_pron, pron, n_jobs)
    canon_p = pron.canonical.to_numpy() == 1
    r["within_pron_auc"] = auc(dv_within, referent)
    r["within_pron_auc_canonical"] = auc(dv_within[canon_p], referent[canon_p])
    r["within_pron_auc_noncanonical"] = auc(dv_within[~canon_p], referent[~canon_p])
    r["within_pron_beta_referent"], r["within_pron_beta_pron_gender"] = regress(
        dv_within, [referent, pron.pron_feminine.to_numpy()])

    OUT.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT / f"sub-{subject}_decoding.npz", **r)
    np.save(OUT / f"sub-{subject}_pronoun_dv_pooled.npy", dv_pooled.astype(np.float32))
    pron.to_csv(OUT / f"sub-{subject}_pronoun_trials.csv", index=False)
    plot(r, f"sub-{subject}", OUT / f"sub-{subject}_decoding.png")
    print(f"sub-{subject}: saved to {OUT}")


# ---------------------------------------------------------------------------
# Group

def chance_of(key):
    return 0.0 if ("beta" in key or "diff" in key) else 0.5


def run_group():
    files = sorted(OUT.glob("sub-*_decoding.npz"))
    if not files:
        raise SystemExit(f"no sub-*_decoding.npz in {OUT}: run the subjects first")
    subjects = [f.name.split("_")[0] for f in files]
    data = [dict(np.load(f)) for f in files]
    keys = [k for k in sorted(set().union(*data))
            if k.startswith(("loc_", "pron_", "adj_", "noun_", "within_")) and not k.endswith("_times")]
    missing = [s for s, d in zip(subjects, data) if set(keys) - set(d)]
    if missing:
        raise SystemExit(f"{', '.join(missing)} lack some results (an older run?): rerun them")
    for k in ("loc_times", "pron_times", "adj_times", "noun_times"):
        if not all(np.allclose(d[k], data[0][k]) for d in data):
            raise ValueError(f"{k} differ between subjects")
    mean = {k: v for k, v in data[0].items() if k.endswith("_times")}
    masks = {}
    stats = len(files) >= MIN_SUBJECTS_STATS
    print(f"{len(files)} subjects: {', '.join(subjects)}"
          + ("" if stats else f" (cluster tests need at least {MIN_SUBJECTS_STATS}: averages only)"))
    for k in keys:
        stack = np.stack([d[k] for d in data])
        mean[k] = stack.mean(0)
        if stats:
            _, clusters, p, _ = mne.stats.permutation_cluster_1samp_test(
                stack - chance_of(k), n_permutations=10000, tail=0, seed=SEED, out_type="indices", verbose=False)
            masks[k] = np.zeros(stack.shape[1:], bool)
            for c, pv in zip(clusters, p):
                if pv < 0.05:
                    masks[k][c] = True
            print(f"  {k}: {sum(pv < 0.05 for pv in p)} significant cluster(s)"
                  + (f", min p = {min(p):.4f}" if len(p) else ""))
    np.savez_compressed(OUT / "group_decoding.npz", subjects=subjects,
                        **mean, **{f"{k}_mask": m for k, m in masks.items()})
    plot(mean, f"group (n = {len(files)})", OUT / "group_decoding.png", masks)
    print(f"group: saved to {OUT}")


# ---------------------------------------------------------------------------
# Figure

def plot(r, title, fname, masks=None):
    masks = masks or {}
    lt, pt, at, nt = r["loc_times"], r["pron_times"], r["adj_times"], r["noun_times"]
    fig, axes = plt.subplots(5, 4, figsize=(20, 22))
    next_words = {f"+{i}": 0.3 * i for i in range(4)}

    def curves(ax, keys, labels, heading, times=lt, xlabel="localizer time (s)", onsets=None):
        for k, label in zip(keys, labels):
            line, = ax.plot(times, r[k], label=label)
            if k in masks and masks[k].any():
                ax.plot(times[masks[k]], np.full(masks[k].sum(), 0.48), "s", ms=3, color=line.get_color())
        ax.axhline(0.5, color="k", lw=0.5)
        for t in (onsets or {}).values():
            ax.axvline(t, color="k", lw=0.5, ls=":")
        ax.set(title=heading, xlabel=xlabel, ylabel="AUC")
        ax.legend(fontsize=8)

    def matrix(ax, key, heading, test_times, onsets, centre=0.5, train_times=lt,
               ylabel="localizer train time (s)"):
        m = r[key]
        lim = max(np.abs(m - centre).max(), 1e-6)
        im = ax.imshow(m, origin="lower", aspect="auto", cmap="RdBu_r", vmin=centre - lim, vmax=centre + lim,
                       extent=[test_times[0], test_times[-1], train_times[0], train_times[-1]])
        if key in masks and masks[key].any():
            ax.contour(test_times, train_times, masks[key], levels=[0.5], colors="k", linewidths=1)
        for t in onsets.values():
            ax.axvline(t, color="k", lw=0.5, ls=":")
        ax.set(title=heading, xlabel="test time (s)", ylabel=ylabel)
        fig.colorbar(im, ax=ax, fraction=0.046)

    # Row 1: the localizer itself
    curves(axes[0, 0], ["loc_cv_pooled", "loc_cv_word", "loc_cv_image"], ["pooled", "words", "pictures"],
           "localizer: person vs place (items left out)")
    curves(axes[0, 1], ["loc_word_to_image", "loc_image_to_word"], ["words → pictures", "pictures → words"],
           "localizer: across modalities")
    curves(axes[0, 2], ["loc_cv_gender"], ["m vs f"], "localizer: gender (items left out)")
    matrix(axes[0, 3], "adj_auc_pooled", "adjective: person- vs place-adjective", at, {"adjective": 0.0})

    # Row 2: positive control, localizer -> sentence-1 nouns
    matrix(axes[1, 0], "noun_auc_pooled", "sentence nouns: person vs place (words + pictures)", nt, next_words)
    matrix(axes[1, 1], "noun_auc_word", "sentence nouns (trained on words)", nt, next_words)
    matrix(axes[1, 2], "noun_auc_image", "sentence nouns (trained on pictures)", nt, next_words)
    ax = axes[1, 3]
    train = (lt >= SUMMARY_TRAIN[0]) & (lt <= SUMMARY_TRAIN[1])
    for k, label in [("noun_auc_pooled", "words + pictures"), ("noun_auc_word", "words"),
                     ("noun_auc_image", "pictures")]:
        ax.plot(nt, r[k][train].mean(axis=0), label=label)
    ax.axhline(0.5, color="k", lw=0.5)
    for t in next_words.values():
        ax.axvline(t, color="k", lw=0.5, ls=":")
    ax.set(title=f"sentence nouns, localizer decoders at {SUMMARY_TRAIN[0]}-{SUMMARY_TRAIN[1]} s (mean)",
           xlabel="test time (s)", ylabel="AUC")
    ax.legend(fontsize=8)

    # Rows 3-4: localizer -> pronoun
    matrix(axes[2, 0], "pron_auc_pooled", "pronoun referent (trained on words + pictures)", pt, WORD_ONSETS)
    matrix(axes[2, 1], "pron_auc_word", "pronoun referent (trained on words)", pt, WORD_ONSETS)
    matrix(axes[2, 2], "pron_auc_image", "pronoun referent (trained on pictures)", pt, WORD_ONSETS)
    matrix(axes[2, 3], "pron_diff_pooled", "person − place decision value", pt, WORD_ONSETS, centre=0.0)

    matrix(axes[3, 0], "pron_auc_canonical", "referent, canonical order", pt, WORD_ONSETS)
    matrix(axes[3, 1], "pron_auc_noncanonical", "referent, non-canonical order", pt, WORD_ONSETS)
    matrix(axes[3, 2], "pron_beta_referent", "β referent (with pronoun gender)", pt, WORD_ONSETS, centre=0.0)
    matrix(axes[3, 3], "pron_gender_auc", "gender decoder: pronoun m vs f", pt, WORD_ONSETS)

    # Row 5: within the main task, sentence-1 nouns -> pronoun
    curves(axes[4, 0], ["within_noun_cv"], ["person vs place nouns"],
           "main task: sentence nouns (trials left out)", times=nt, xlabel="noun time (s)", onsets=next_words)
    noun_y = "sentence-noun train time (s)"
    matrix(axes[4, 1], "within_pron_auc", "nouns → pronoun referent", pt, WORD_ONSETS,
           train_times=nt, ylabel=noun_y)
    matrix(axes[4, 2], "within_pron_auc_canonical", "nouns → referent, canonical order", pt, WORD_ONSETS,
           train_times=nt, ylabel=noun_y)
    matrix(axes[4, 3], "within_pron_auc_noncanonical", "nouns → referent, non-canonical order", pt,
           WORD_ONSETS, train_times=nt, ylabel=noun_y)

    fig.suptitle(f"{title}: person vs place decoding (dotted: word onsets; pronoun rows: pronoun, était, adjective)")
    fig.tight_layout(rect=(0, 0, 1, 0.98))
    fig.savefig(fname, dpi=100)
    plt.close(fig)


# ---------------------------------------------------------------------------

def main():
    global OUT
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("subjects", nargs="*", help="BIDS subject labels, e.g. 001 002")
    parser.add_argument("--group", action="store_true", help="group average and statistics of saved subjects")
    parser.add_argument("--deriv-root", default=DERIV_ROOT, help="MNE-BIDS pipeline derivatives folder")
    parser.add_argument("--out", default=None, help=f"output folder (default {OUT})")
    parser.add_argument("--n-jobs", type=int, default=1)
    args = parser.parse_args()
    if args.out:
        OUT = Path(args.out)
    if not args.subjects and not args.group:
        parser.error("give subjects, --group, or both")
    for subject in args.subjects:
        run_subject(subject, args.deriv_root, args.n_jobs)
    if args.group:
        run_group()


if __name__ == "__main__":
    main()
