"""Timing checks from the behavioral logs (software timestamps, not photodiode).

    python3 -I analysis/timing.py [subjects...]

Main task: 300 ms words, SOA 300 ms (1300 ms between the two sentences), onset
vs. the trial's intended schedule. Localizer: 600 ms stimuli, SOA 800 ms.
One frame = 1000/119.93 = 8.34 ms; "dropped frames" = extra frames on screen.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd
from behavior import load

FR = 1000 / 119.93


def check(d):
    w = d[(d.task == "main") & (d.event == "word") & (d.block_number > 0)].sort_values("time_ms").copy()
    w["dev"] = w.trial_time_ms - w.intended_trial_time_ms
    k = ["block_number", "trial_number"]
    w["soa"] = w.groupby(k).time_ms.diff()
    w["extra"] = ((w.duration_ms - 300.2) / FR).round()
    wi = w[w.sentence == w.groupby(k).sentence.shift()]
    print(f"  main words: {len(w)}; duration median {w.duration_ms.median():.1f} ms, "
          f"{(w.extra > 0).sum()} with extra frames ({w.extra.value_counts().sort_index().drop(0.0, errors='ignore').to_dict()}), max {w.duration_ms.max():.1f}")
    print(f"  within-sentence SOA: median {wi.soa.median():.1f}, sd {wi.soa.std():.1f}, max {wi.soa.max():.1f}")
    print(f"  onset - intended: median {w.dev.median():.1f} ms, 95th pct {w.dev.quantile(.95):.1f}, max {w.dev.max():.1f}; "
          f"{(w.dev.abs() > 2 * FR).sum()} words ({100*(w.dev.abs() > 2 * FR).mean():.1f}%) off by > 2 frames, in "
          f"{w[w.dev.abs() > 2 * FR].groupby(k).ngroups}/{w.groupby(k).ngroups} trials")
    fx = d[(d.task == "main") & (d.event == "fixation") & (d.block_number > 0)]
    print(f"  fixation: {fx.duration_ms.min():.1f}-{fx.duration_ms.max():.1f} ms")
    l = d[(d.task == "localizer") & (d.event == "loc_stimulus") & (d.block_number > 0)].sort_values("time_ms").copy()
    l["soa"] = l.groupby(["block_number", "miniblock"]).time_ms.diff()
    le = ((l.duration_ms - 600.3) / FR).round()
    print(f"  localizer stimuli: {len(l)}; duration median {l.duration_ms.median():.1f} ms, "
          f"{(le > 0).sum()} with extra frames, max {l.duration_ms.max():.1f}; SOA median {l.soa.median():.1f}, "
          f"{((l.soa - 800.5).abs() > 2 * FR).sum()} off by > 2 frames")


if __name__ == "__main__":
    for sub, d in load([int(a) for a in sys.argv[1:]] or None).items():
        print(f"SUBJECT {sub}")
        check(d)
