study_name = "Pronouns"
bids_root = "../meg/bids"  # relative to this folder: run the pipeline from data/preprocessing

task = ["pronouns", "localizer"]

runs = 'all'

ch_types = ['meg']
data_type = 'meg'

find_flat_channels_meg = True
find_noisy_channels_meg = True
use_maxwell_filter = True

mf_ctc_fname = bids_root + "/system_calibration_files/ct_sparse.fif"
mf_cal_fname = bids_root + "/system_calibration_files/sss_cal_3176_20240123_2.dat"

# Realign all runs (both tasks) to one reference run of the main task.
# The subject must be given (--subject XXX): the union of bad channels is per subject.
import argparse as _argparse, sys as _sys
from pathlib import Path as _Path
import pandas as _pd

_parser = _argparse.ArgumentParser(add_help=False)
_parser.add_argument("--subject")
_subject = _parser.parse_known_args(_sys.argv[1:])[0].subject
if _subject is None:
    raise ValueError("Pass --subject XXX: the bad channels are unioned per subject.")
mf_reference_task = "pronouns"
mf_reference_run = "01"

# Union of bad channels: a channel marked bad (inspect_dataset, raw_to_bids.py --inspect) in any
# run of the subject is marked bad in all its runs, so that Maxwell filtering and ICA treat
# every run alike. The pipeline reads the bads from each run's channels.tsv, so they are
# written there (idempotent; channels are only ever added, never un-marked).
def _union_bads(subject):
    paths = sorted(_Path(bids_root, f"sub-{subject}", "meg").glob(f"sub-{subject}_task-*_channels.tsv"))
    tables = [_pd.read_csv(f, sep="\t", dtype=str, keep_default_na=False) for f in paths]
    union = set().union(*[set(t.name[t.status == "bad"]) for t in tables]) if tables else set()
    for f, t in zip(paths, tables):
        new = t.name.isin(union) & (t.status != "bad")
        if new.any():
            t.loc[new, "status"] = "bad"
            t.loc[new, "status_description"] = "bad in another run (union)"
            t.to_csv(f, sep="\t", index=False)
    return sorted(union)

_bads = _union_bads(_subject)
print(f"sub-{_subject}: {len(_bads)} bad channels (union over runs): {_bads}")

# =============== Filtering parameters ==================

# -------------------------------------------------------
l_freq = 0.5
h_freq = 40
notch_freq = 50
raw_resample_sfreq = 250

# ICA is not run for now:
# # ============== Artifact correction ====================
# # A single ICA is fitted on all runs of both tasks
# spatial_filter = "ica"
# ica_algorithm = 'fastica'
# ica_n_components = 50
# ica_max_iterations = 1000
# random_state = 10
# ica_l_freq = 1.0

# # ==== ICA rejection settings (set to none, manual ICA) ====
# ica_reject = None

# epoching params
epochs_tmin = -0.2
epochs_tmax = 1
epochs_decim = 1
baseline = None

# Conditions / events to consider when epoching, per task (hierarchical tags of the event names)
conditions = {
    "pronouns": ["word/det_subj", "word/noun_subj", "word/verb", "word/dans", "word/det_place",
                 "word/noun_place", "word/pronoun", "word/etait", "word/adjective"],
    "localizer": ["loc/word", "loc/image"],
}

# With multiple tasks, contrasts must be a per-task dict (even when empty)
contrasts = {
    "pronouns": [],
    "localizer": [],
}

reject = dict(grad=4000e-13, mag=4e-12)
# 6e-12, 4e-10
n_jobs = 8
