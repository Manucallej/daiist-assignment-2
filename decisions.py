"""
The business decisions this pipeline runs on. These are yours to make.

The assignment's AI policy says AI may write the code, but the decisions it
grades must be your own: what each error costs, the base rate, where the
thresholds go and how much goes to a person. Every value below is therefore
left as None. train.py and app.py read them from here and nowhere else, so
each figure in REPORT.md has exactly one home in the code.

Until a value is filled in, training and evaluation still run, but the cost
sweep is skipped and the dashboard's cost views say what is missing.

Units: euros per parcel, seconds, and parcels per day.
"""

# --- Dataset (step 2) --------------------------------------------------------
# The exact Roboflow Universe version this pipeline is built on. Used as is,
# never forked.
ROBOFLOW_WORKSPACE = "eliftechpoc"
ROBOFLOW_PROJECT = "detecting-a-damaged-parcel"
ROBOFLOW_VERSION = 5

# --- What counts as "positive" (step 5) -------------------------------------
# Which detected classes make a parcel count as damaged. A parcel's score is
# the highest confidence among detections of these classes. Must be names
# from the dataset, e.g. a subset of ["hole", "screw", "wet"].
POSITIVE_CLASSES: list[str] | None = None

# --- Base rate (step 6) ------------------------------------------------------
# Share of parcels that are actually damaged at your point in the chain,
# between 0 and 1. The test split's own ratio is NOT this: the dataset was
# collected to contain damage, real parcel flow mostly does not.
BASE_RATE: float | None = None

# --- Cost of each outcome, in euros per parcel (step 6) ----------------------
COST_FALSE_NEGATIVE: float | None = None  # damaged parcel passed as fine
COST_FALSE_POSITIVE: float | None = None  # fine parcel flagged as damaged
COST_TRUE_POSITIVE: float | None = None   # damaged parcel correctly flagged
COST_TRUE_NEGATIVE: float | None = None   # fine parcel correctly passed

# --- Human review (step 7) ---------------------------------------------------
# Assumes a reviewer always gets the parcel right, so a reviewed parcel costs
# its review time plus the cost of the correct outcome. Say in REPORT.md if
# you think that is too generous.
SECONDS_PER_REVIEW: float | None = None     # time to check one flagged parcel
REVIEWER_COST_PER_HOUR: float | None = None  # loaded hourly cost of a reviewer
PARCELS_PER_DAY: int | None = None           # volume through your checkpoint
REVIEW_HOURS_PER_PERSON_PER_DAY: float | None = None  # productive review hours

# Your chosen review band: parcels scoring below the first value pass, at or
# above the second fail, and in between go to a person. Leave as None until you
# have looked at the sweep; the dashboard then starts at the cheapest band.
REVIEW_BAND: tuple[float, float] | None = None
