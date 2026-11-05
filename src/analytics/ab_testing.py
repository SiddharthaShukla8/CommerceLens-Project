from __future__ import annotations
import numpy as np
import pandas as pd
from scipy.stats import norm

def synthetic_experiment(seed: int = 42, users_per_group: int = 2500) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    groups = np.repeat(["control", "treatment"], users_per_group)
    probability = np.where(groups == "control", 0.105, 0.122)
    return pd.DataFrame({"user_id": np.arange(len(groups)) + 1, "experiment_group": groups, "exposed": True, "converted": rng.binomial(1, probability)})

def analyse_experiment(data: pd.DataFrame, alpha: float = .05) -> dict:
    summary = data.groupby("experiment_group").converted.agg(["count", "sum", "mean"])
    c, t = summary.loc["control"], summary.loc["treatment"]
    diff = t["mean"] - c["mean"]; se = np.sqrt(c["mean"]*(1-c["mean"])/c["count"] + t["mean"]*(1-t["mean"])/t["count"])
    z = diff / se; p = 2 * norm.sf(abs(z)); ci = (diff - norm.ppf(.975)*se, diff + norm.ppf(.975)*se)
    return {"summary": summary.reset_index(), "absolute_difference": float(diff), "relative_lift": float(diff / c["mean"]), "confidence_interval": ci, "p_value": float(p), "significant": bool(p < alpha)}
