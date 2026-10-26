"""
The business decisions this pipeline runs on. These are yours to make.

The assignment's AI policy says AI may write the code, but the decisions it
grades must be your own: what each error costs, the base rate, where the
thresholds go and how much goes to a person. Every value below is therefore
left as None. train.py and app.py read them from here and nowhere else, so
each figure in REPORT.md has exactly one home in the code.

Until a value is filled in, training and evaluation still run, but the cost
sweep is skipped and the dashboard's cost views say what is missing.

An "item" is one image: one piece of fruit (or one view of the line) that
gets a pass / review / fail decision.

Units: euros per item, seconds, and items per day.
"""

# --- Dataset (step 2) --------------------------------------------------------
# The exact Roboflow Universe version this pipeline is built on. Used as is,
# never forked.
ROBOFLOW_WORKSPACE = "project-irggm"
ROBOFLOW_PROJECT = "-w4yds"
ROBOFLOW_VERSION = 1

# --- What counts as "positive" (step 5) -------------------------------------
# Which detected classes make an item count as rotten. An item's score is the
# highest confidence among detections of these classes; detections of any
# other class (the fresh ones) do not raise it. Must be names from the
# dataset: fresh_apples, fresh_banana, fresh_oranges, rotten_apples,
# rotten_banana, rotten_oranges.
POSITIVE_CLASSES: list[str] | None = None

# --- Base rate (step 6) ------------------------------------------------------
# Share of items that are actually rotten at your point in the chain, between
# 0 and 1. The test split's own ratio is NOT this: the dataset was collected
# to show rot, a real sorting line mostly does not.
BASE_RATE: float | None = None

# --- Cost of each outcome, in euros per item (step 6) ------------------------
COST_FALSE_NEGATIVE: float | None = None  # rotten item passed as fresh
COST_FALSE_POSITIVE: float | None = None  # fresh item rejected as rotten
COST_TRUE_POSITIVE: float | None = None   # rotten item correctly rejected
COST_TRUE_NEGATIVE: float | None = None   # fresh item correctly passed

# --- Human review (step 7) ---------------------------------------------------
# Assumes a reviewer always gets the item right, so a reviewed item costs its
# review time plus the cost of the correct outcome. Say in REPORT.md if you
# think that is too generous.
SECONDS_PER_REVIEW: float | None = None     # time to check one flagged item
REVIEWER_COST_PER_HOUR: float | None = None  # loaded hourly cost of a reviewer
ITEMS_PER_DAY: int | None = None             # volume through your checkpoint
REVIEW_HOURS_PER_PERSON_PER_DAY: float | None = None  # productive review hours

# Your chosen review band: items scoring below the first value pass, at or
# above the second fail, and in between go to a person. Leave as None until you
# have looked at the sweep; the dashboard then starts at the cheapest band.
REVIEW_BAND: tuple[float, float] | None = None
