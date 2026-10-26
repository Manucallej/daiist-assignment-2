# Assignment 2 Report

*Delete this italic guidance as you fill in each section. You'll be asked to
defend any of this without your code in front of you. Write only what you
can actually explain.*

- **Name**:
- **Student ID**:
- **Email**:
- **Group**: [BBADBA 5A | BBADBA 5B | PPLEDBA 5A | BDBA 3A]

## Business problem, and the cost of being wrong

*The decision this model supports, who or what acts on it, and what happens
when it's wrong in each direction. Be concrete about the asymmetry: which
mistake is worse, roughly by how much, and why. Everything downstream (your
threshold, how much you send to a person, which metric you care about) has to trace
back to this section.*

## Dataset

*Workspace / project / version on Roboflow Universe, and the link. What one
image represents, what the classes are, and why this dataset actually serves
the problem above rather than merely resembling it.*

## What the dataset's composition implies

*Instances per class, train/val/test sizes, typical object size relative to the
image. Then the interpretation: which per-class numbers will be too thin to
trust, whether the test split resembles the images you'd really see, and what
you therefore can't conclude from your results.*

## Finetuning and baselines

*Which model and task (detection or classification) and why. A results table on
the same test split: your finetuned model, the pretrained COCO model zero-shot,
and a trivial baseline. What changed, and whether the gap is as large as you
expected.*

## Per-class evaluation and failure modes

*Per-class AP50, or per-class precision/recall and the confusion matrix.
Which class carries the headline number, which one is dragging, and what the
model actually confuses with what. Show where it breaks, not just that it
works.*

## Cost matrix and operating point

*Your euro cost for each kind of error and where each figure came from. The
base rate you assumed. The cost-against-threshold sweep, and the operating
point you chose. State the assumption that would most change your answer if it
were wrong.*

## What a person still has to check

*Your two thresholds, and what share of cases they send to a person. How many
that is per day, how long one takes to check, and how many people that needs.
Is that realistic? Then your design priced against the three alternatives:
doing nothing, having a person check everything, and letting the model decide
on its own.*

## Limitations & next steps

*Real limitations you found, and concretely how you'd address each one with
more time or data. Not generic hedging.*

## Generative AI use disclosure

*Per the syllabus AI Policy: what you used and how, or "no AI content used."*

# Assignment 2 Report

- **Name**: [your name]
- **Student ID**: [your ID]
- **Email**: [your email]
- **Group**: [BBADBA 5A | BBADBA 5B | PPLEDBA 5A | BDBA 3A]

## Business problem, and the cost of being wrong

A delivery company wants to stop riders from leaving without a helmet because this is a huge safety risk and it could be a legal liability for the company. A camera at the depot exit photographs each rider (or group of riders), and the model scores each image. Low scores pass automatically, high scores are stopped, and scores in between go to a human reviewer. The decision for each item is pass / review / fail.

The two kinds of error are asymmetric. A false negative (a rider without a helmet is let through) costs about **€5.00** per item: an expected fine of €2.00. This is because it considers a percentage of likelihood of the event actually happening since it doesn't always happen, and then the cost of it actually happening. In this case, 1% chance of a roadside inspection × €200 fine; plus an expected accident cost of €3.00 (0.02% chance of an accident on the trip × €15,000 cost to the company in sick pay, insurance and liability). A false positive (a rider with a helmet is stopped anyway) costs about **€0.65**: €0.40 of rider time (1 minute × €0.40/min) plus €0.25 of expected delivery-delay compensation (5% chance × €5).

A missed violation is around 8× worse than a false alarm. This means the threshold should lean toward catching violations (false positives are less costly than a false negative), and recall on "Without Helmet" matters more than overall accuracy.

All of these figures are just assumptions.

## Dataset

- **Source**: Roboflow Universe, workspace `a-yvlja`, project `helmet-and-non-helmet-abb47`, version 1.
- **Link**: https://universe.roboflow.com/a-yvlja/helmet-and-non-helmet-abb47
- **One image** represents one check of a rider or group of riders.
- **Classes**: "With Helmet" and "Without Helmet". An item is a violation if it contains at least one "Without Helmet" detection.
- **Why it fits the problem**: It fits because it serves well for training a model of riders without or with helmets, even when they are in groups on the same bike (although this would not regularly be the case in delivery as they would go alone). A person manually checking all the drivers implies at least a minimum wage (depending on the country this can vary), checking at all times if the drivers are going out with or without a helmet. Additionally, if there are 10 drivers going out at the same time, the person might miss or misclassify accidentally. We assume the model performs better than the human because of the speed and expected precision of the prediction. 

## What the dataset's composition implies

| Split | Images | With Helmet (images · boxes) | Without Helmet (images · boxes) |
|---|---:|---:|---:|
| Train | 12,699 | 9,519 · 15,938 | 4,914 · 8,454 |
| Validation | 978 | 717 · 1,154 | 406 · 679 |
| Test | 711 | 563 · 799 | 248 · 359 | 
Typical object size relative to the picture ranges a lot. There are images where you can literally only see the head with the helmet and there are images where one helmet is 1/20th of the image because there are also multiple helmets. This is good in terms of how well the model will train.

Interpretation:

- **Per-class numbers too thin to trust**: [Which class has too few instances, especially in the test split?]
- **Does the test split resemble a real checkpoint?** Probably not. The dataset was collected to show both cases, whereas the real violation rate at a depot exit is assumed here to be about 3%. [Add the test split's actual ratio.]
- **What I can't conclude**: Precision measured on the test split will overstate what I'd see in production, because violations are far more common in the test data than at the real checkpoint. [Add any other limits, e.g. lighting, camera angle, helmet types.]

## Finetuning and baselines

- **Model and task**: [e.g. YOLO detection / classification, and why.]

| Model | [metric] | [metric] | Notes |
|---|---|---|---|
| Finetuned model | | | |
| Pretrained COCO model, zero-shot | | | |
| Trivial baseline (always predict "With Helmet") | | | |

[What changed between the rows, and whether the gap is as large as you expected.]

## Per-class evaluation and failure modes

[Per-class AP50, or per-class precision/recall, plus the confusion matrix.]

- **Class carrying the headline number**: [ ]
- **Class dragging it down**: [ ]
- **What the model confuses with what**: [ ]
- **Where it breaks**: [Examples of failure images: small riders, occlusion, helmet-like headwear, etc.]

## Cost matrix and operating point

| Outcome | Cost (€ per item) | Source |
|---|---|---|
| False negative | 5.00 | Fine: 1% × €200 = €2.00. Accident: 0.02% × €15,000 = €3.00. Both assumed. |
| False positive | 0.65 | Rider time: 1 min × €0.40/min = €0.40. Delay: 5% × €5 = €0.25. Assumed. |
| True positive | 3.00 | Time to fetch and put on a helmet: 5 min × €0.40/min = €2.00. Delay: 20% × €5 = €1.00. Assumed. |
| True negative | 0.00 | No intervention, no delay. |

- **Base rate assumed**: 3% of riders leave without a helmet.
- **Cost-against-threshold sweep**: [Paste the sweep plot.]
- **Operating point chosen**: [Threshold(s) and why.]
- **Assumption that would most change my answer**: The accident cost (0.02% × €15,000 = €3.00). It makes up 60% of the false-negative cost, so if it were much lower, the optimal threshold would shift toward fewer stops. [Optionally show the result at half and double this value.]

## What a person still has to check

- **Thresholds**: pass below [__], fail at or above [__], review in between.
- **Share of cases sent to a person**: [__%] of items.
- **Per day**: [share] × 1,500 items/day = [__] items.
- **Time per check**: 10 seconds.
- **People needed**: share × 1,500 × 10 / 3,600 / 6 productive hours = [__] people.
- **Is that realistic?** [Your judgement.]

Baseline alternatives, at 1,500 items/day and a 3% base rate (review costs 10 s at €20/h ≈ €0.056 per item):

| Alternative | Cost per day | Working |
|---|---|---|
| Do nothing | €225 | 1,500 × 0.03 × €5.00 (every violation is a false negative) |
| Person checks everything | ≈ €218 | 1,500 × (€0.056 + 0.03 × €3.00); about 4.2 hours of review, so under one person |
| Perfect model, no review (lower bound) | €135 | 1,500 × 0.03 × €3.00 |
| Model decides on its own | [__] | [Compute from your confusion matrix at your threshold] |
| Model + review band (my design) | [__] | [From the sweep] |

Under these assumptions, having a person check everything barely beats doing nothing, so the value of the model depends heavily on the cost assumptions. [Comment on how your design compares.]

## Limitations & next steps

[Write after seeing results. Each limitation should be a real finding paired with a concrete fix. Likely candidates:]

- **Assumed costs and base rate**: [How you would replace them with real data.]
- **Dataset mismatch with a depot exit**: [What data you would collect.]
- **Reviewer assumed always correct**: [How you would measure real reviewer accuracy.]

## Generative AI use disclosure

I used Claude to help fill in assumed cost parameters for the config and to draft sections of this report. I reviewed and revised the content and can explain each figure. [Edit to reflect what you actually did.]
