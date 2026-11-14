"""Convert the raw MEG recordings of one subject to BIDS (input of the MNE-BIDS pipeline).

Raw:   data/meg/raw/<SUBJECTS[sub]>/Pronouns01-06.fif  (main task, one block per file)
                                    Localizer01-02.fif (localizer, one block per file)
BIDS:  data/meg/bids/sub-XXX/meg/sub-XXX_task-<task>_run-NN_meg.fif (+ events.tsv)

Triggers: the stimulus code is in the low 8 bits of the trigger channels; bits 8-15
carry the response-pad buttons and are masked out. The codes are defined in
triggers/triggers.csv (see triggers/make_trigger_table.py). The two tasks reuse
the same numbers, so each task has its own event_id.

Usage: python raw_to_bids.py 001
       python raw_to_bids.py 001 --tasks localizer     (only one task)
       python raw_to_bids.py 001 --inspect             (open mne_bids.inspect_dataset on each run)
"""
import argparse
import re
import unicodedata
from pathlib import Path

import mne
import mne_bids
import numpy as np
import pandas as pd

PROJECT = Path(__file__).resolve().parents[2]
RAW_ROOT = PROJECT / "data" / "meg" / "raw"
BIDS_ROOT = PROJECT / "data" / "meg" / "bids"
TRIGGER_TABLE = PROJECT / "triggers" / "triggers.csv"

# BIDS subject label -> raw folder (<initials_id>/<date>) on the MEG computer
SUBJECTS = {
    "001": "ab_260306/261104",
    "002": "rv_260340/261105",
}

# BIDS task -> (raw file prefix, number of runs); raw files are <prefix><NN>.fif
TASKS = {
    "pronouns": ("Pronouns", 6),
    "localizer": ("Localizer", 2),
}

TRIGGER_MASK = 0xFF00  # bits 8-15 (response pad) are ignored

ROLES = ["det_subj", "noun_subj", "verb", "dans", "det_place", "noun_place",
         "pronoun", "etait", "adjective"]  # role r = 1..9 (code // 16)


def slug(text):
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def main_event_ids():
    """Main task: label -> trigger code."""
    ids = {}
    # critical words: 16 * role + cell; cell bits: 0 congruent, 1 canonical order,
    # 2 pronoun feminine, 3 agent feminine
    for role, name in enumerate(ROLES, start=1):
        for cell in range(16):
            label = "/".join([
                "word", name,
                "cong" if cell & 1 else "incong",
                "canon" if cell & 2 else "noncanon",
                "pron_f" if cell & 4 else "pron_m",
                "agent_f" if cell & 8 else "agent_m",
            ])
            ids[label] = 16 * role + cell
    # filler words: 214 + 4 * (role - 1) + 2 * canonical + congruent
    for r, name in enumerate(ROLES):
        for canon in (0, 1):
            for cong in (0, 1):
                label = f"filler/{name}/{'cong' if cong else 'incong'}/{'canon' if canon else 'noncanon'}"
                ids[label] = 214 + 4 * r + 2 * canon + cong
    # trial starts (code 160 + trial number)
    for n in range(1, 41):
        ids[f"trial_start/{n:02}"] = 160 + n
    ids.update({
        "feedback/correct": 211,
        "feedback/incorrect": 212,
        "feedback/timeout": 213,
    })
    return ids


def localizer_event_ids():
    """Localizer: label -> trigger code, with item names taken from triggers.csv."""
    table = pd.read_csv(TRIGGER_TABLE)
    table = table[(table.task == "localizer") & (table.code <= 96)]
    ids = {}
    for _, row in table.iterrows():
        concept = int(row.concept)
        category = "person" if concept <= 16 else "place" if concept <= 32 else "animal"
        modality = "word" if row.modality == "word" else "image"
        ids[f"loc/{modality}/{category}/{slug(row['item'])}"] = int(row.code)
    ids.update({
        "feedback/hit": 211,
    })
    return ids


EVENT_IDS = {"pronouns": main_event_ids(), "localizer": localizer_event_ids()}


def extract_events(raw, task):
    """Stimulus triggers of a run, restricted to the codes defined for the task."""
    event_id = EVENT_IDS[task]
    events = mne.find_events(raw, min_duration=0.002, mask=TRIGGER_MASK, mask_type="not_and",
                             verbose=False)
    known = np.isin(events[:, 2], list(event_id.values()))
    if not known.all():
        print(f"    dropping {(~known).sum()} events with unknown codes {np.unique(events[~known, 2])}")
    events = events[known]
    present = set(np.unique(events[:, 2]))
    return events, {k: v for k, v in event_id.items() if v in present}


def raw_to_bids(subject, tasks):
    raw_dir = RAW_ROOT / SUBJECTS[subject]
    for task in tasks:
        prefix, n_runs = TASKS[task]
        for i in range(1, n_runs + 1):
            run = f"{i:02}"
            fname = raw_dir / f"{prefix}{run}.fif"
            print(f"--- sub-{subject} task-{task} run-{run}: {fname.name} ---")
            raw = mne.io.read_raw_fif(fname, allow_maxshield=True, preload=False)
            events, event_id = extract_events(raw, task)
            bids_path = mne_bids.BIDSPath(subject=subject, task=task, run=run,
                                          datatype="meg", root=BIDS_ROOT)
            mne_bids.write_raw_bids(raw, bids_path=bids_path, events=events, event_id=event_id,
                                    allow_preload=True, format="FIF", overwrite=True)

    # MEG calibration and crosstalk files, once per subject (shared by all runs)
    bids_path = mne_bids.BIDSPath(subject=subject, datatype="meg", root=BIDS_ROOT)
    calib = BIDS_ROOT / "system_calibration_files"
    mne_bids.write_meg_calibration(calibration=calib / "sss_cal_3176_20240123_2.dat",
                                   bids_path=bids_path)
    mne_bids.write_meg_crosstalk(fname=calib / "ct_sparse.fif", bids_path=bids_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert raw MEG data of one subject to BIDS.")
    parser.add_argument("subject", choices=sorted(SUBJECTS), help="BIDS label without 'sub-', e.g. 001")
    parser.add_argument("--tasks", nargs="+", choices=sorted(TASKS), default=list(TASKS))
    parser.add_argument("--inspect", action="store_true", help="open the MNE-BIDS viewer on each run")
    args = parser.parse_args()

    raw_to_bids(args.subject, args.tasks)

    if args.inspect:
        for task in args.tasks:
            for i in range(1, TASKS[task][1] + 1):
                mne_bids.inspect_dataset(mne_bids.BIDSPath(subject=args.subject, task=task, run=f"{i:02}",
                                                           datatype="meg", root=BIDS_ROOT))
