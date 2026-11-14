"""Behavioral summary of the main task (felicity judgment) and the localizer
(animal detection), per subject.

    python3 analysis/behavior.py            # every subject in data/behavioral
    python3 analysis/behavior.py 1 2        # only these subjects

Main task: block 0 is training and is left out. Accuracy is over all trials,
RT (from the adjective's onset) over correct trials only. `congruent` is the
correct answer (1 natural, 0 odd). Localizer: a hit is a press 200-1200 ms
after an animal's onset (`correct` = 1 on the animal's loc_stimulus row); a
false alarm is a trial that is not an animal with at least one press.
"""
import glob, os, re, sys
import numpy as np
import pandas as pd
from scipy.stats import norm

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data", "behavioral")
pd.set_option("display.width", 200, "display.max_columns", 30)


def load(subjects=None):
    out = {}
    for f in sorted(glob.glob(os.path.join(DATA, "Pronouns_sub-*_date-*.csv"))):
        s = int(re.search(r"sub-(\d+)", f).group(1))
        if subjects and s not in subjects:
            continue
        out[s] = pd.read_csv(f, na_values=["NA"])
    return out


def acc_rt(g):
    c = g[g.correct == 1]
    return pd.Series({"n": len(g), "acc": g.correct.mean() * 100,
                      "rt_med": c.rt_ms.median(), "rt_mean": c.rt_ms.mean(),
                      "rt_sd": c.rt_ms.std()})


def main_task(d):
    r = d[(d.task == "main") & (d.event == "response") & (d.block_number > 0)].copy()
    r["answer"] = np.where(r.congruent == 1, "natural", "odd")
    print(f"  {len(r)} trials ({(r.trial_type=='main').sum()} main, {(r.trial_type=='filler').sum()} filler); "
          f"no-response trials: {r.response.isna().sum()}")
    print("\n  Overall")
    print(r.groupby("trial_type").apply(acc_rt).round(1).to_string())
    m = r[r.trial_type == "main"]
    print("\n  Main trials by block")
    print(m.groupby("block_number").apply(acc_rt).round(1).to_string())
    for col in ["answer", "pronoun_referent", "pronoun_gender", "canonical_order"]:
        print(f"\n  Main trials by {col}")
        print(m.groupby(col).apply(acc_rt).round(1).to_string())
    print("\n  Main trials: pronoun_referent x answer")
    print(m.groupby(["pronoun_referent", "answer"]).apply(acc_rt).round(1).to_string())
    print("\n  Fillers by answer")
    print(r[r.trial_type == "filler"].groupby("answer").apply(acc_rt).round(1).to_string())
    # response bias: share of "natural" (right) answers, and d' for natural vs odd
    m2 = m.assign(said_natural=(m.response == "right").astype(int))
    h, f = m2[m2.congruent == 1].said_natural, m2[m2.congruent == 0].said_natural
    hr, fr = (h.sum() + .5) / (len(h) + 1), (f.sum() + .5) / (len(f) + 1)
    print(f"\n  Main trials: p('natural' | natural) = {h.mean():.2f}, p('natural' | odd) = {f.mean():.2f}, "
          f"d' = {norm.ppf(hr)-norm.ppf(fr):.2f}, criterion = {-(norm.ppf(hr)+norm.ppf(fr))/2:.2f} (>0: bias towards 'odd')")
    slow = (r.rt_ms > 2000).sum(); fast = (r.rt_ms < 300).sum()
    print(f"  RT < 300 ms: {fast}; RT > 2000 ms: {slow}")


def localizer(d):
    s = d[(d.task == "localizer") & (d.event == "loc_stimulus") & (d.block_number > 0)]
    p = d[(d.task == "localizer") & (d.event == "loc_response") & (d.block_number > 0)]
    rows = []
    for mod in ["word", "image", "all"]:
        ss = s if mod == "all" else s[s.modality == mod]
        pp = p if mod == "all" else p[p.modality == mod]
        t = ss[ss.target == 1]
        nt = ss[ss.target == 0]
        keys = ["block_number", "miniblock", "trial_number"]
        fa_trials = pp[pp.target == 0][keys].drop_duplicates()
        fa = len(fa_trials.merge(nt[keys], on=keys))
        hits = int(t.correct.sum())
        hr, far = (hits + .5) / (len(t) + 1), (fa + .5) / (len(nt) + 1)
        rows.append({"modality": mod, "animals": len(t), "hits": hits, "hit%": 100 * hits / len(t),
                     "FA": fa, "FA%": 100 * fa / len(nt), "d'": norm.ppf(hr) - norm.ppf(far),
                     "hit_rt_med": t[t.correct == 1].rt_ms.median()})
    print(pd.DataFrame(rows).round(1).to_string(index=False))
    print("\n  Hit rate by block x modality")
    t = s[s.target == 1]
    print(t.groupby(["block_number", "modality"]).correct.agg(["sum", "count", "mean"]).round(2).to_string())


def figure(data, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    cols = ["#2a6fbb", "#d9822b", "#3a9d5d", "#8e5bb5"]
    fig, ax = plt.subplots(1, 4, figsize=(17, 4.2))
    n = len(data)
    w = 0.8 / n
    for i, (sub, d) in enumerate(data.items()):
        c = cols[i % len(cols)]
        r = d[(d.task == "main") & (d.event == "response") & (d.block_number > 0)]
        m = r[r.trial_type == "main"]
        # A: accuracy by block
        b = m.groupby("block_number").correct.mean() * 100
        ax[0].plot(b.index, b.values, "o-", color=c, label=f"Sub {sub}")
        # B: accuracy, referent x answer
        g = m.assign(a=np.where(m.congruent == 1, "natural", "odd")).groupby(["pronoun_referent", "a"]).correct.mean() * 100
        ax[1].bar(np.arange(len(g)) + i * w - 0.4 + w / 2, g.values, w, color=c)
        ax[1].set_xticks(range(len(g)), [f"{a}\n{b}" for a, b in g.index])
        # C: RT distribution (correct main trials)
        rt = m[m.correct == 1].rt_ms
        ax[2].hist(rt, bins=np.arange(250, 2500, 100), histtype="step", lw=2, color=c)
        ax[2].axvline(rt.median(), color=c, ls="--", lw=1)
        # D: localizer hit RT by modality
        s = d[(d.task == "localizer") & (d.event == "loc_stimulus") & (d.block_number > 0) & (d.target == 1) & (d.correct == 1)]
        for j, mod in enumerate(["word", "image"]):
            v = s[s.modality == mod].rt_ms
            ax[3].boxplot(v, positions=[j + i * 0.3 - 0.15 * (n - 1)], widths=0.25, showfliers=False,
                          boxprops=dict(color=c), medianprops=dict(color=c), whiskerprops=dict(color=c), capprops=dict(color=c))
    ax[0].set(title="Main: accuracy by block", xlabel="block", ylabel="% correct", ylim=(50, 102)); ax[0].legend(frameon=False)
    ax[1].set(title="Main: accuracy by referent × answer", ylabel="% correct", ylim=(50, 102))
    ax[2].set(title="Main: RT of correct trials (dashed: median)", xlabel="RT from adjective onset (ms)", ylabel="trials")
    ax[3].set(title="Localizer: hit RT", ylabel="ms", xticks=[0, 1], xticklabels=["word", "picture"])
    for a in ax:
        a.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(path, dpi=150)
    print("figure:", path)


if __name__ == "__main__":
    subs = [int(a) for a in sys.argv[1:]] or None
    data = load(subs)
    for sub, d in data.items():
        print("=" * 78 + f"\nSUBJECT {sub}\n" + "=" * 78)
        print("\nMAIN TASK (blocks 1-6)")
        main_task(d)
        print("\nLOCALIZER (blocks 1-2)")
        localizer(d)
        print()
    figure(data, os.path.join(HERE, "behavior.png"))
