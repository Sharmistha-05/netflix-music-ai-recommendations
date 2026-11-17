"""Analysis for the Netflix Music course-end project.

Everything numeric in the report comes from this module:
  * Sheet 1 (Music Data): engagement statistics, correlations, the baseline
    AI Recommendation Score and listener segments.
  * Sheet 2 (Sprint Tasks): status x priority view, workload and WSJF backlog ranking.
  * GenAI model selection: the researched benchmark table, the weighted decision
    matrix with a sensitivity check, and the monthly cost model.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "CEP_Dataset.xlsx"


# --------------------------------------------------------------------------- Sheet 1
def load_music(path=DATA):
    m = pd.read_excel(path, sheet_name=0)
    m.columns = ["user_id", "song_id", "genre", "play_count", "skip_rate",
                 "user_rating", "listening_minutes"]
    return m


def _minmax(s):
    return (s - s.min()) / (s.max() - s.min())


# Weights of the baseline (v1.0) score. Rationale: repeat plays are the strongest
# revealed preference, minutes and explicit rating confirm it, skips are negative.
SCORE_WEIGHTS = {"play_count": 0.30, "listening_minutes": 0.25, "user_rating": 0.25, "skip_rate": 0.20}


def score_music(m):
    m = m.copy()
    w = SCORE_WEIGHTS
    m["ai_recommendation_score"] = (
        w["play_count"] * _minmax(m.play_count)
        + w["listening_minutes"] * _minmax(m.listening_minutes)
        + w["user_rating"] * _minmax(m.user_rating)
        + w["skip_rate"] * (1 - _minmax(m.skip_rate))
    ).round(3)
    m["rank"] = m.ai_recommendation_score.rank(ascending=False, method="first").astype(int)
    m["minutes_per_play"] = (m.listening_minutes / m.play_count).round(2)
    m["segment"] = pd.cut(m.play_count, [0, 19, 29, 10_000], labels=["Casual", "Regular", "Power"]).astype(str)
    return m.sort_values("rank").reset_index(drop=True)


def music_correlations(m):
    return m[["play_count", "skip_rate", "user_rating", "listening_minutes"]].corr().round(2)


def music_summary(m):
    return {
        "rows": len(m),
        "users": m.user_id.nunique(),
        "genres": m.genre.nunique(),
        "plays_total": int(m.play_count.sum()),
        "plays_mean": round(m.play_count.mean(), 1),
        "minutes_total": int(m.listening_minutes.sum()),
        "minutes_mean": round(m.listening_minutes.mean(), 1),
        "skip_mean": round(m.skip_rate.mean(), 3),
        "rating_mean": round(m.user_rating.mean(), 2),
    }


# --------------------------------------------------------------------------- Sheet 2
def load_tasks(path=DATA):
    t = pd.read_excel(path, sheet_name=1)
    t.columns = ["task_id", "task_name", "status", "owner", "priority"]
    return t


# Cards the problem statement asks for, added to the Sheet 2 tasks.
# Interpretation: v1.0 (baseline recommender) is deployed and evaluated, v2 is in
# training and testing, and the GenAI layer (model selection, data, segments) is next.
NEW_CARDS = [
    ("N01", "GenAI model selection (OpenAI vs Gemini)", "Backlog", "Product Manager", "High"),
    ("N02", "Dataset preparation", "Backlog", "Hannah Wilson", "High"),
    ("N03", "User segmentation", "Backlog", "Ian Thomas", "Medium"),
    ("N04", "AI model training (v2)", "In Progress", "Alice Johnson", "High"),
    ("N05", "Recommendation accuracy testing", "In Progress", "Bob Smith", "High"),
    ("N06", "Deployment (baseline model v1.0)", "Completed", "George Miller", "High"),
    ("N07", "Performance evaluation (v1.0)", "Completed", "Bob Smith", "High"),
]

# WSJF inputs for backlog cards (relative Fibonacci estimates, team planning assumption).
# WSJF = (Business Value + Time Criticality + Risk Reduction) / Job Size
WSJF_INPUTS = {
    "N01": (8, 8, 8, 3, "Unblocks every GenAI feature; cheap to decide"),
    "T005": (8, 13, 13, 5, "Watch history is personal data: must clear before launch"),
    "N02": (8, 8, 5, 5, "Clean training data feeds v2 and segmentation"),
    "N03": (5, 5, 3, 3, "Targets playlists and GenAI tone per segment"),
    "T009": (13, 5, 3, 8, "High value but depends on N02 and N03"),
    "T008": (5, 2, 3, 5, "Improves cold start; not launch-critical"),
    "T004": (3, 2, 1, 3, "Polish; schedule after core is stable"),
}
DEPENDENCIES = {"N03": ["N02"], "T009": ["N02", "N03"]}


def board(t):
    extra = pd.DataFrame(NEW_CARDS, columns=t.columns)
    b = pd.concat([t.assign(source="Sheet 2"), extra.assign(source="Problem statement")], ignore_index=True)
    return b


def wsjf_table():
    rows = []
    for k, (bv, tc, rr, size, why) in WSJF_INPUTS.items():
        rows.append({"card": k, "business_value": bv, "time_criticality": tc, "risk_reduction": rr,
                     "job_size": size, "cost_of_delay": bv + tc + rr,
                     "wsjf": round((bv + tc + rr) / size, 2), "rationale": why})
    w = pd.DataFrame(rows).sort_values("wsjf", ascending=False).reset_index(drop=True)
    # Dependency-aware order: a card never ranks above a card it depends on.
    order = []
    remaining = list(w.card)
    while remaining:
        for c in remaining:
            if all(d in order for d in DEPENDENCIES.get(c, [])):
                order.append(c)
                remaining.remove(c)
                break
    w["backlog_rank"] = w.card.map({c: i + 1 for i, c in enumerate(order)})
    return w.sort_values("backlog_rank").reset_index(drop=True)


def task_summary(t):
    return {
        "status_priority": pd.crosstab(t.status, t.priority).reindex(
            index=["Backlog", "In Progress", "Completed"], columns=["High", "Medium", "Low"], fill_value=0),
        "completion_rate": round((t.status == "Completed").mean() * 100),
        "high_in_backlog": t[(t.status == "Backlog") & (t.priority == "High")].task_name.tolist(),
        "high_share_in_progress": round(((t.status == "In Progress") & (t.priority == "High")).sum()
                                        / (t.status == "In Progress").sum() * 100),
    }


# --------------------------------------------------------------------------- GenAI selection
# Researched on 17 November 2026. Prices: official OpenAI and Google pricing pages.
# Latency: Requesty production-traffic medians (published 11 Nov 2026).
# Accuracy: Artificial Analysis AA-Omniscience v1.1 (read 1 Nov 2026).
MODELS = pd.DataFrame([
    # vendor, model, tier, in $/1M, cached $/1M, out $/1M, context, max output, TTFT s, tok/s, AA accuracy %, AA hallucination %
    ("OpenAI", "GPT-6.1 Terra", "Workhorse", 1.00, 0.05, 5.00, "1.05M", "128K", 2.76, 128, 47.6, 34.5),
    ("OpenAI", "GPT-6.1 Sol", "Flagship", 2.00, 0.10, 10.00, "1.05M", "128K", 4.04, 71, 61.8, 51.9),
    ("OpenAI", "GPT-6 Luna", "Low-cost", 0.10, 0.01, 0.50, "1.05M", "128K", 1.91, 113, 39.6, 79.3),
    ("Google", "Gemini 3.8 Flash", "Workhorse", 0.75, 0.075, 3.75, "1.05M", "n/c", 3.58, 105, 50.5, 55.1),
    ("Google", "Gemini 3.8 Flash (from 1 Jan 2027)", "Workhorse", 1.50, 0.15, 7.50, "1.05M", "n/c", 3.58, 105, 50.5, 55.1),
    ("Google", "Gemini 4 Argon (from 1 Dec 2026)", "Flagship", 4.00, 0.20, 20.00, "1.05M", "n/c", 7.67, 84, None, 4.3),
    ("Google", "Gemini 3.5 Flash-Lite", "Low-cost", 0.30, 0.03, 2.50, "1.05M", "n/c", 0.81, 361, None, None),
], columns=["vendor", "model", "tier", "input_usd", "cached_usd", "output_usd", "context", "max_output",
            "ttft_s", "tokens_per_s", "aa_accuracy", "aa_hallucination"])

# Decision matrix: criteria from the problem statement plus ethics/privacy and integration.
CRITERIA = [
    # criterion, weight, OpenAI (GPT-6.1 Terra + Sol), Google (Gemini 3.8 Flash + 4 Argon), evidence
    ("Cost and computational efficiency", 0.25, 4.0, 3.0,
     "Terra $1/$5 is stable; Flash is $0.75/$3.75 only until 31 Dec 2026, then $1.50/$7.50"),
    ("Latency", 0.20, 4.0, 3.0, "Median time to first token 2.76 s (Terra) vs 3.58 s (Flash)"),
    ("Accuracy (low hallucination)", 0.20, 4.0, 3.0,
     "Hallucination 34.5% vs 55.1% on AA-Omniscience; Flash knows slightly more (50.5% vs 47.6%)"),
    ("Token limit", 0.10, 4.0, 5.0, "Both ~1M context; OpenAI doubles input price above 272K, Gemini Flash is flat"),
    ("Ethics and data privacy", 0.15, 4.0, 3.5,
     "OpenAI API data not used for training by default; Google marks some paid models 'used to improve products'"),
    ("Scalability and integration", 0.10, 4.5, 4.5,
     "OpenAI: realtime voice stack for an AI DJ. Gemini: native audio/video input. Both cross-cloud from AWS"),
]


def decision_matrix():
    d = pd.DataFrame(CRITERIA, columns=["criterion", "weight", "openai", "gemini", "evidence"])
    d["openai_weighted"] = (d.weight * d.openai).round(3)
    d["gemini_weighted"] = (d.weight * d.gemini).round(3)
    totals = {"openai": round(d.openai_weighted.sum(), 2), "gemini": round(d.gemini_weighted.sum(), 2)}
    # Sensitivity: judge Gemini on its 2026 promotional price (cost score 4.5 instead of 3.0).
    promo = d.copy()
    promo.loc[0, "gemini"] = 4.5
    totals["gemini_if_promo_price_kept"] = round((promo.weight * promo.gemini).sum(), 2)
    # Sensitivity: weight cost at 40% (taking 15 points evenly from latency, accuracy, privacy).
    heavy = d.copy()
    heavy.weight = [0.40, 0.15, 0.15, 0.10, 0.10, 0.10]
    totals["openai_if_cost_40pct"] = round((heavy.weight * heavy.openai).sum(), 2)
    totals["gemini_if_cost_40pct"] = round((heavy.weight * heavy.gemini).sum(), 2)
    return d, totals


# Monthly usage assumption for the GenAI layer (planning assumption, not data).
USAGE = {"mau": 5_000_000, "calls_per_user_month": 40, "input_tokens": 1_200,
         "cached_share": 0.60, "output_tokens": 250}


def monthly_cost(input_usd, cached_usd, output_usd, u=USAGE):
    calls = u["mau"] * u["calls_per_user_month"]
    in_m = calls * u["input_tokens"] / 1e6
    out_m = calls * u["output_tokens"] / 1e6
    return in_m * u["cached_share"] * cached_usd + in_m * (1 - u["cached_share"]) * input_usd + out_m * output_usd


def cost_model():
    rows = []
    for _, r in MODELS.iterrows():
        if r.model in ("GPT-6 Luna", "Gemini 3.5 Flash-Lite"):
            continue
        c = monthly_cost(r.input_usd, r.cached_usd, r.output_usd)
        rows.append({"model": r.model, "vendor": r.vendor, "monthly_usd": round(c),
                     "per_mau_usd": round(c / USAGE["mau"], 3)})
    terra = MODELS.set_index("model").loc["GPT-6.1 Terra"]
    sol = MODELS.set_index("model").loc["GPT-6.1 Sol"]
    mix = 0.85 * monthly_cost(terra.input_usd, terra.cached_usd, terra.output_usd) + \
        0.15 * monthly_cost(sol.input_usd, sol.cached_usd, sol.output_usd)
    rows.append({"model": "Recommended mix (85% Terra / 15% Sol)", "vendor": "OpenAI",
                 "monthly_usd": round(mix), "per_mau_usd": round(mix / USAGE["mau"], 3)})
    return pd.DataFrame(rows)
