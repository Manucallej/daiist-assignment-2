"""
The business decisions this pipeline runs on. These are yours to make.

The assignment's AI policy says AI may write the code, but the decisions it
grades must be your own: what each error costs, the base rate, where the
thresholds go and how much goes to a person. Every value below is therefore
left as None. train.py and app.py read them from here and nowhere else, so
each figure in REPORT.md has exactly one home in the code.

Until a value is filled in, training and evaluation still run, but the cost
sweep is skipped and the dashboard's cost views say what is missing.

An "item" is one image: one check of a rider (or group of riders) that gets a
pass / review / fail decision. A violation is an item with someone not
wearing a helmet.

Units: euros per item, seconds, and items per day.
"""

# --- Dataset (step 2) --------------------------------------------------------
# The exact Roboflow Universe version this pipeline is built on. Used as is,
# never forked.
ROBOFLOW_WORKSPACE = "a-yvlja"
ROBOFLOW_PROJECT = "helmet-and-non-helmet-abb47"
ROBOFLOW_VERSION = 1

# --- What counts as "positive" (step 5) -------------------------------------
# Which detected classes make an item a violation. An item's score is the
# highest confidence among detections of these classes; detections of any
# other class do not raise it. Must be names from the dataset:
# "With Helmet", "Without Helmet".
POSITIVE_CLASSES: list[str] | None = ["Without Helmet"]

# --- Base rate (step 6) ------------------------------------------------------
# Share of items that really are violations at your checkpoint, between 0 and
# 1. The test split's own ratio is NOT this: the dataset was collected to show
# both cases, a real depot exit mostly does not.
BASE_RATE: float | None = None

# --- Cost of each outcome, in euros per item (step 6) ------------------------
# Each outcome's cost is the sum of its components. Fill in every component
# of an outcome (0 is a valid answer) and its total is computed below; leave
# any one as None and that outcome stays unset. Write in REPORT.md where each
# figure comes from.


def _total(*components: float | None) -> float | None:
    return None if any(c is None for c in components) else float(sum(components))


# False negative: rider without a helmet let through.
FN_SAFETY_FINE: float | None = None         # expected fine per violation: chance an
                                            # inspection catches it x the fine
FN_EXPECTED_ACCIDENT_COST: float | None = None  # chance of an accident on this trip x
                                                # its cost to the company (sick pay,
                                                # insurance, liability)

# False positive: rider with a helmet stopped anyway.
FP_RIDER_TIME: float | None = None          # minutes lost x rider's cost per minute
FP_DELIVERY_DELAY: float | None = None      # late-delivery compensation, if any

# True positive: rider without a helmet correctly stopped.
TP_RIDER_TIME: float | None = None          # minutes to fetch and put on a helmet x cost
TP_DELIVERY_DELAY: float | None = None      # late-delivery compensation, if any

# True negative: rider with a helmet correctly let through.
TN_COST: float | None = None                # usually nothing, but say why

COST_FALSE_NEGATIVE = _total(FN_SAFETY_FINE, FN_EXPECTED_ACCIDENT_COST)
COST_FALSE_POSITIVE = _total(FP_RIDER_TIME, FP_DELIVERY_DELAY)
COST_TRUE_POSITIVE = _total(TP_RIDER_TIME, TP_DELIVERY_DELAY)
COST_TRUE_NEGATIVE = _total(TN_COST)

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
