"""Pattern discovery on encoded DPD journeys: shapes, n-grams, feature clusters, rule tree."""
from __future__ import annotations

from collections import Counter

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier, export_text

from .features import LETTERS, N, encode

# Run-length bands per code. R bands end at 3+ so a straight roll to 4 and to 7
# give the same shape (the current bucket is mostly a clock).
BANDS = {
    "N": [(1, "1"), (3, "2-3"), (6, "4-6"), (12, "7-12"), (24, "13-24"), (10**9, "25+")],
    "R": [(1, "1"), (2, "2"), (10**9, "3+")],
    "H": [(1, "1"), (3, "2-3"), (10**9, "4+")],
    "P": [(1, "1"), (10**9, "2+")],
}


def _band(letter: str, n: int) -> str:
    return next(lbl for hi, lbl in BANDS[letter] if n <= hi)


def shape(dpd: str, max_runs: int = 8) -> str:
    """Run-length encoded journey with banded run lengths, last `max_runs` runs."""
    _, _, c = encode(dpd)
    if len(c) == 0:
        return "(one month only)"
    runs, prev, n = [], None, 0
    for code in c:
        if code == prev:
            n += 1
        else:
            if prev is not None:
                runs.append(f"{LETTERS[prev]}{_band(LETTERS[prev], n)}")
            prev, n = code, 1
    runs.append(f"{LETTERS[prev]}{_band(LETTERS[prev], n)}")
    prefix = "… " if len(runs) > max_runs else ""
    return prefix + " ".join(runs[-max_runs:])


def shape_table(df: pd.DataFrame, label: str = "true_archetype", top: int = 30) -> pd.DataFrame:
    s = df.dpd_string.map(shape)
    g = (pd.DataFrame({"shape": s, "label": df[label]})
         .groupby("shape").label.agg(n="size",
                                     top_label=lambda x: x.value_counts().index[0],
                                     purity=lambda x: x.value_counts(normalize=True).iloc[0]))
    g = g.sort_values("n", ascending=False)
    g["share"] = g.n / len(df)
    g["cum_share"] = g.share.cumsum()
    return g.head(top).reset_index()


def ngram_table(df: pd.DataFrame, n: int = 3, min_support: float = 0.01,
                label: str | None = None, top: int = 20, seed: int = 7) -> pd.DataFrame:
    """Share of accounts containing each code n-gram (pure-normal grams skipped), and
    lift = that share / the share when each account's own codes are shuffled. Lift > 1
    means the ORDER matters (a real motif), not just that the codes are common.
    `label` (optional) adds the dominant label among accounts containing the gram —
    on real data pass the discovered clusters or states, not a planted truth."""
    rng = np.random.default_rng(seed)
    obs, shuf = [], []
    for s in df.dpd_string:
        c = encode(s)[2]
        cs = rng.permutation(c)
        for store, seq in ((obs, c), (shuf, cs)):
            grams = {tuple(seq[i:i + n]) for i in range(len(seq) - n + 1)}
            store.append({g for g in grams if any(x != N for x in g)})
    sup_obs = Counter(g for gs in obs for g in gs)
    sup_shuf = Counter(g for gs in shuf for g in gs)
    rows = []
    for g, cnt in sup_obs.items():
        sup = cnt / len(df)
        if sup < min_support:
            continue
        row = {"gram": "".join(LETTERS[x] for x in g), "support": sup,
               "lift": sup / max(sup_shuf.get(g, 0), 1) * len(df)}
        if label is not None:
            mask = np.array([g in gs for gs in obs])
            mix = df.loc[mask, label].value_counts(normalize=True)
            row.update({"top_label": mix.index[0], "purity": mix.iloc[0]})
        rows.append(row)
    return pd.DataFrame(rows).sort_values("lift", ascending=False).head(top)


# Clock-safe only: lifetime, run-up (fixed once past 4), and recent rates within the spell.
CLUSTER_FEATURES = [
    "months_before_spell", "n_blips", "n_prior_episodes", "max_prior_bucket",
    "clean_gap_before_current", "runup_len", "runup_holds", "runup_pays",
    "max_hold_run", "post4_paid_rate", "rec_paid_rate", "last6_in_band", "chg_6m",
]
LOG_FEATURES = {"months_before_spell", "clean_gap_before_current", "runup_len", "max_hold_run"}


def cluster_matrix(f: pd.DataFrame) -> np.ndarray:
    X = f[CLUSTER_FEATURES].astype(float).copy()
    for col in LOG_FEATURES:
        X[col] = np.log1p(X[col])
    return StandardScaler().fit_transform(X)


def kmeans_scan(f: pd.DataFrame, ks=range(4, 11), label: str = "true_archetype",
                seed: int = 7) -> tuple[pd.DataFrame, dict]:
    X = cluster_matrix(f)
    rng = np.random.default_rng(seed)
    sample = rng.choice(len(X), size=min(4000, len(X)), replace=False)
    rows, fits = [], {}
    for k in ks:
        km = KMeans(n_clusters=k, n_init=10, random_state=seed).fit(X)
        fits[k] = km.labels_
        rows.append({"k": k,
                     "silhouette": silhouette_score(X[sample], km.labels_[sample]),
                     "ARI_vs_truth": adjusted_rand_score(f[label], km.labels_)})
    return pd.DataFrame(rows), fits


def cluster_profile(f: pd.DataFrame, labels: np.ndarray, label: str = "true_archetype") -> pd.DataFrame:
    g = f.assign(cluster=labels).groupby("cluster")
    prof = g[CLUSTER_FEATURES].median().round(2)
    prof.insert(0, "share", (g.size() / len(f)).round(3))
    mix = g[label].agg(top_label=lambda x: x.value_counts().index[0],
                       purity=lambda x: round(x.value_counts(normalize=True).iloc[0], 2))
    return mix.join(prof).sort_values("share", ascending=False)


def rule_tree(f: pd.DataFrame, target: pd.Series, max_leaves: int = 8,
              min_leaf: float = 0.02, seed: int = 7) -> tuple[DecisionTreeClassifier, str]:
    X = f[CLUSTER_FEATURES]
    tree = DecisionTreeClassifier(max_leaf_nodes=max_leaves, min_samples_leaf=min_leaf,
                                  random_state=seed).fit(X, target)
    return tree, export_text(tree, feature_names=CLUSTER_FEATURES, decimals=2)
