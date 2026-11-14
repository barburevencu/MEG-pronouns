"""Mark the ICA components listed in Data/datasheet.csv as bad, all others as good.

The datasheet may have any number of component columns named ecg, ecg-N, eog or eog-N (e.g. eog-1 ... eog-4
for a subject whose eye artifacts are spread over several components); empty cells are skipped.

Rewrites each subject's derivatives/mne-bids-pipeline/sub-XX/meg/sub-XX_proc-ica_components.tsv,
which the pipeline's apply_ica step reads. Warns when the datasheet disagrees with
the automatic detection:
  1) a datasheet component is not marked bad in the .tsv;
  2) a datasheet component is marked bad in the .tsv as the other artifact type (ECG vs EOG).

Usage: python mark_ica_components.py                (all subjects in the datasheet)
       python mark_ica_components.py 03 14          (some subjects)
       python mark_ica_components.py --dry-run      (only print warnings, write nothing)
"""

import argparse
import re
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASHEET = PROJECT_ROOT / "Data" / "datasheet.csv"
DERIV_ROOT = PROJECT_ROOT / "Data" / "BIDS" / "derivatives" / "mne-bids-pipeline"

# Datasheet columns that hold components: ecg, ecg-N, eog, eog-N; the prefix is the artifact type
COMPONENT_COLUMN = re.compile(r"^(ecg|eog)(-\d+)?$")


def components_path(sub):
    return DERIV_ROOT / sub / "meg" / f"{sub}_proc-ica_components.tsv"


def marked_type(status_description):
    """'ECG' or 'EOG' if the .tsv description names one, else None."""
    for kind in ("ECG", "EOG"):
        if kind in str(status_description).upper():
            return kind
    return None


def mark(sub, row, dry_run):
    path = components_path(sub)
    if not path.exists():
        print(f"{sub}: no {path.name}, skipped")
        return
    tsv = pd.read_csv(path, sep="\t", keep_default_na=False)

    columns = [col for col in row.index if COMPONENT_COLUMN.match(col)]
    bad = {int(row[col]): col.split("-")[0].upper() for col in columns if pd.notna(row[col])}
    for comp, kind in bad.items():
        if comp not in tsv.component.values:
            print(f"WARNING {sub}: datasheet component {comp} ({kind}) is not in the .tsv")
            continue
        current = tsv.loc[tsv.component == comp].iloc[0]
        if current.status != "bad":
            print(f"WARNING {sub}: component {comp} ({kind} in datasheet) is not marked bad in the .tsv")
        elif marked_type(current.status_description) not in (kind, None):
            print(f"WARNING {sub}: component {comp} is {kind} in datasheet but "
                  f"'{current.status_description}' in the .tsv")

    was_bad = sorted(tsv.component[tsv.status == "bad"])
    is_bad = tsv.component.isin(bad)
    tsv.loc[~is_bad, ["status", "status_description"]] = ["good", "n/a"]
    tsv.loc[is_bad, "status"] = "bad"
    # Keep MNE's own label on confirmed components; label the others in the same format
    keep = is_bad & tsv.status_description.str.startswith("Auto-detected")
    tsv.loc[is_bad & ~keep, "status_description"] = [
        f"Auto-detected {bad[c]} artifact (MNE)" for c in tsv.component[is_bad & ~keep]]

    print(f"{sub}: bad {was_bad} -> {sorted(bad)}")
    if not dry_run:
        tsv.to_csv(path, sep="\t", index=False)


def main():
    parser = argparse.ArgumentParser(description="Mark ICA components from datasheet.csv.")
    parser.add_argument("subjects", nargs="*", help="e.g. 03 or 01 02 14 (default: all)")
    parser.add_argument("--dry-run", action="store_true", help="print warnings, write nothing")
    args = parser.parse_args()

    datasheet = pd.read_csv(DATASHEET).set_index("sub")
    subjects = [int(s.removeprefix("sub-")) for s in args.subjects] or list(datasheet.index)
    for s in subjects:
        mark(f"sub-{s:02d}", datasheet.loc[s], args.dry_run)


if __name__ == "__main__":
    main()
