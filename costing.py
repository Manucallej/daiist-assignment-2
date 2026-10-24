"""
Turns per-parcel scores into outcomes, costs and review load.

Shared by train.py (which saves the sweep) and app.py (which recomputes it
live as the sliders move), so both always use the same arithmetic.

Every parcel has a true label (1 = damaged, 0 = fine) and a score (the
model's highest confidence for a positive class, 0 if it found nothing). A
review band (low, high) turns the score into one of three outcomes:

    score <  low          -> pass
    low <= score < high   -> human review
    score >= high         -> fail

With low == high the band is empty and the model decides alone.

Rates are measured separately on damaged and on fine test parcels, then
mixed at BASE_RATE. That is what lets a test split that is mostly damage say
something about a parcel flow that mostly is not.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd

import decisions

REQUIRED = [
    "BASE_RATE",
    "COST_FALSE_NEGATIVE",
    "COST_FALSE_POSITIVE",
    "COST_TRUE_POSITIVE",
    "COST_TRUE_NEGATIVE",
    "SECONDS_PER_REVIEW",
    "REVIEWER_COST_PER_HOUR",
    "PARCELS_PER_DAY",
    "REVIEW_HOURS_PER_PERSON_PER_DAY",
]

# A threshold above every possible score: nothing reaches it.
NEVER = 1.01
THRESHOLDS = np.round(np.arange(0.0, 1.0001, 0.01), 2)


def missing_decisions() -> list[str]:
    """Names in decisions.py that still need a value before costing can run."""
    return [name for name in REQUIRED if getattr(decisions, name) is None]


def parcel_level(scores: pd.DataFrame, positive: list[str]) -> tuple[np.ndarray, np.ndarray]:
    """True label and finetuned score per test parcel, for the positive classes.

    A parcel is damaged if it has a box of any positive class, and its score is
    the model's highest confidence across those classes.
    """
    y_true = scores[[f"true_{c}" for c in positive]].max(axis=1).to_numpy()
    y_score = scores[[f"score_{c}" for c in positive]].max(axis=1).to_numpy()
    return y_true, y_score


def review_cost_per_parcel() -> float:
    return decisions.SECONDS_PER_REVIEW / 3600 * decisions.REVIEWER_COST_PER_HOUR


@dataclass
class Outcome:
    """Where the test parcels land for one review band, and what it costs."""

    counts: np.ndarray       # 2x3 test counts: rows fine/damaged, cols pass/review/fail
    cost_per_1000: float     # expected euros per 1,000 parcels at BASE_RATE
    review_share: float      # expected share of parcels sent to a person
    reviews_per_day: float
    reviewers_needed: float


def outcome_counts(y_true: np.ndarray, scores: np.ndarray, low: float, high: float) -> np.ndarray:
    """Count test parcels by true label (rows) and outcome (columns)."""
    outcome = np.where(scores < low, 0, np.where(scores < high, 1, 2))
    counts = np.zeros((2, 3), dtype=int)
    for label in (0, 1):
        counts[label] = np.bincount(outcome[y_true == label], minlength=3)
    return counts


def evaluate_band(y_true: np.ndarray, scores: np.ndarray, low: float, high: float) -> Outcome:
    if low > high:
        low, high = high, low
    counts = outcome_counts(y_true, scores, low, high)
    if (counts.sum(axis=1) == 0).any():
        raise ValueError(
            "The test split needs both damaged and fine parcels to estimate both "
            "error rates. One of them has no images."
        )
    # Share of fine (row 0) and damaged (row 1) parcels in each outcome.
    rates = counts / counts.sum(axis=1, keepdims=True)
    fine_pass, fine_review, fine_fail = rates[0]
    dmg_pass, dmg_review, dmg_fail = rates[1]

    review = review_cost_per_parcel()
    cost_if_damaged = (
        dmg_pass * decisions.COST_FALSE_NEGATIVE
        + dmg_review * (review + decisions.COST_TRUE_POSITIVE)
        + dmg_fail * decisions.COST_TRUE_POSITIVE
    )
    cost_if_fine = (
        fine_pass * decisions.COST_TRUE_NEGATIVE
        + fine_review * (review + decisions.COST_TRUE_NEGATIVE)
        + fine_fail * decisions.COST_FALSE_POSITIVE
    )
    p = decisions.BASE_RATE
    cost = p * cost_if_damaged + (1 - p) * cost_if_fine
    review_share = p * dmg_review + (1 - p) * fine_review

    reviews_per_day = review_share * decisions.PARCELS_PER_DAY
    review_hours = reviews_per_day * decisions.SECONDS_PER_REVIEW / 3600
    return Outcome(
        counts=counts,
        cost_per_1000=1000 * cost,
        review_share=review_share,
        reviews_per_day=reviews_per_day,
        reviewers_needed=review_hours / decisions.REVIEW_HOURS_PER_PERSON_PER_DAY,
    )


def sweep(y_true: np.ndarray, scores: np.ndarray) -> list[dict]:
    """Cost per 1,000 parcels at every single threshold (model decides alone)."""
    rows = []
    for t in THRESHOLDS:
        result = evaluate_band(y_true, scores, t, t)
        rows.append({"threshold": float(t), "cost_per_1000": float(result.cost_per_1000)})
    return rows


def best_threshold(sweep_rows: list[dict]) -> float:
    return min(sweep_rows, key=lambda row: row["cost_per_1000"])["threshold"]


def cheapest_band(y_true: np.ndarray, scores: np.ndarray) -> tuple[float, float]:
    """The (low, high) pair on the threshold grid with the lowest expected cost."""
    best, best_cost = (0.0, 0.0), float("inf")
    for i, low in enumerate(THRESHOLDS):
        for high in THRESHOLDS[i:]:
            cost = evaluate_band(y_true, scores, low, high).cost_per_1000
            if cost < best_cost:
                best, best_cost = (float(low), float(high)), cost
    return best


def policy_comparison(y_true: np.ndarray, scores: np.ndarray, band: tuple[float, float]) -> list[dict]:
    """The four policies step 7 asks you to price against each other."""
    alone = best_threshold(sweep(y_true, scores))
    policies = {
        "Do nothing (pass every parcel)": (NEVER, NEVER),
        "A person checks every parcel": (0.0, NEVER),
        f"Model alone (threshold {alone:.2f})": (alone, alone),
        f"Model + review band ({band[0]:.2f} to {band[1]:.2f})": band,
    }
    rows = []
    for name, (low, high) in policies.items():
        result = evaluate_band(y_true, scores, low, high)
        rows.append({
            "policy": name,
            "cost_per_1000": round(float(result.cost_per_1000), 2),
            "review_share": round(float(result.review_share), 4),
            "reviews_per_day": round(float(result.reviews_per_day), 1),
            "reviewers_needed": round(float(result.reviewers_needed), 2),
        })
    return rows
