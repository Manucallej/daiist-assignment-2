# Assignment 2 Report

- **Name**: Manuela Calle
- **Student ID**: 18754
- **Email**: mcalle.ieu2022@student.ie.edu
- **Group**: BBADBA 5A

## Business problem, and the cost of being wrong

A delivery company wants to stop riders from leaving without a helmet because this is a huge safety risk and it could be a legal liability for the company. A camera at the depot exit photographs each rider (or group of riders), and the model scores each image. Low scores pass automatically, high scores are stopped, and scores in between go to a human reviewer. The decision for each item is pass / review / fail.

The two kinds of error are asymmetric. A false negative (a rider without a helmet is let through) costs about **€5.00** per item: an expected fine of €2.00. This is because it considers a percentage of likelihood of the event actually happening since it doesn't always happen, and then the cost of it actually happening. In this case, 1% chance of a roadside inspection × €200 fine; plus an expected accident cost of €3.00 (0.02% chance of an accident on the trip × €15,000 cost to the company in sick pay, insurance and liability). A false positive (a rider with a helmet is stopped anyway) costs about **€0.65**: €0.40 of rider time (1 minute × €0.40/min) plus €0.25 of expected delivery-delay compensation (5% chance × €5).

A missed violation is around 8× worse than a false alarm. This means the threshold should lean toward catching violations (false positives are less costly than a false negative), and recall on "Without Helmet" matters more than overall accuracy.

All of these figures are just assumptions.

*Addition:* The 8x figure is the headline asymmetry, but it is not the ratio that drives the threshold. Stopping a real violation is not free: a true positive still costs €3.00. So catching a violation only saves €2.00 versus missing it (5.00 - 3.00), and the ratio that matters is 2.00 / 0.65, about 3 to 1. An item is worth flagging once the chance it is a violation passes 0.65 / (0.65 + 2.00), about 25%.

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

From `dataset_stats.json`, the median head box in the test split is about 1.1% of the image area for both classes, roughly a tenth of the image width, so most targets are small. The 90th percentile is 8.3% for With Helmet and 2.8% for Without Helmet. Train has a bigger tail for With Helmet (90th percentile 24.2%), meaning close-ups that the test split barely contains.

Interpretation:

- **Per-class numbers too thin to trust**: "Without Helmet" is the smaller class in every split, and the test split has only 248 images and 359 boxes for it. Each image is worth about 0.4 points of recall, so a few images moving changes recall visibly. Anything finer than class level (small riders only, night only) would rest on a few dozen images.
- **Does the test split resemble a real checkpoint?** Probably not. The dataset was collected to show both cases, whereas the real violation rate at a depot exit is assumed here to be about 3%. In the test split, 248 of 711 images (34.9%) contain a violation. Also, 563 + 248 = 811 class-image counts on 711 images, so about 100 test images contain both classes. These count as violations at item level.
- **What I can't conclude**: Precision measured on the test split will overstate what I'd see in production, because violations are far more common in the test data than at the real checkpoint. I also cannot say anything about lighting, camera angle, helmet types or helmet-like headwear, because I did not measure performance on those slices.

## Finetuning and baselines

- **Model and task**: YOLO11n object detection, finetuned from the COCO checkpoint. Detection rather than whole-image classification because the labels are boxes, images can hold several riders, and a box shows the reviewer which rider triggered the flag. Nano size because it is fast and enough to show the pipeline.
- **Settings**: 15 epochs, early stopping patience 15, image size 640, batch 16, seed 0, deterministic. Trained on a GPU (`device 0`, Linux x86_64), per `run.json`. With 15 epochs and patience 15, early stopping could never trigger.
- **Item score**: the highest confidence the model gives any "Without Helmet" box in the image (0 if none).

| Model | Precision | Recall | Notes |
|---|---|---|---|
| Finetuned model | 0.907 | 0.948 | Item level, conf 0.25, same 711 test images. Accuracy 0.948, ROC AUC 0.977 |
| Pretrained COCO model, zero-shot | 0.369 | 0.875 | No helmet class in COCO, so it can only say "a person is here". Accuracy 0.435, ROC AUC 0.568 |
| Trivial baseline (always predict "With Helmet") | n/a | 0.00 | Accuracy 0.651 (463 of 711 items are compliant) while catching nothing |

The finetuned model catches 235 of 248 violation images and raises 24 false alarms on 463 compliant images. Zero-shot COCO has a recall of 87.5%, but only because it flags almost everything: 371 of the 463 compliant images get flagged, so its precision (36.9%) is essentially the 34.9% base rate, which is what flagging at random would give. Its accuracy (43.5%) is below the trivial "pass everything" baseline (65.1%), and its AUC (0.568) is barely above chance. The trivial baseline's 65.1% accuracy is also why accuracy is the wrong headline metric here: it looks decent while catching zero violations. Finetuning is what turns "a person is present" into "this person has no helmet".

## Per-class evaluation and failure modes

Box-level results on the test split (precision and recall at the confidence that maximises F1):

| Class | Test images | Boxes | Precision | Recall | AP50 | mAP50-95 |
|---|---:|---:|---:|---:|---:|---:|
| With Helmet | 563 | 799 | 0.930 | 0.915 | 0.953 | 0.640 |
| Without Helmet | 248 | 359 | 0.846 | 0.819 | 0.874 | 0.536 |
| All classes | 711 | 1,158 | 0.888 | 0.867 | 0.913 | 0.588 |

Box-level confusion matrix at confidence 0.25 (rows are what the model predicted, columns are the truth):

| Predicted / True | With Helmet | Without Helmet | Background |
|---|---:|---:|---:|
| With Helmet | 748 | 16 | 89 |
| Without Helmet | 13 | 307 | 68 |
| Background (nothing found) | 38 | 36 | n/a |

![Confusion matrix](artifacts/confusion_matrix.png)

- **Class carrying the headline number**: With Helmet. AP50 0.953 against 0.874, and it has about twice the training boxes (15,938 vs 8,454). The overall AP50 of 0.913 sits between the two and hides the gap.
- **Class dragging it down**: Without Helmet, with recall 0.819 and AP50 0.874. It is also the class the business cares about most, so the weaker class is the one that matters.
- **What the model confuses with what**: Very little between the two classes. Only 16 true Without Helmet boxes were called With Helmet, and 13 the other way. Most errors are about finding heads at all. Of 359 Without Helmet boxes, 307 were found (85.5%), 16 were mislabelled (4.5%) and 36 were missed entirely (10.0%). The model also predicted 68 Without Helmet and 89 With Helmet boxes where nothing is labelled. The problem is detection, not judging the helmet.
- **Where it breaks**: At item level (conf 0.25) 13 violation images are missed and 24 compliant images are falsely flagged. Of the 13 misses, 9 also contain a rider with a helmet, while only about 40% of all violation images do (100 of 248), so misses seem to concentrate in group shots where one rider without a helmet stands next to helmeted riders. That is a small count, so treat it as a pattern to check, not a finding. The missed images score at most 0.20 for Without Helmet, so lowering the threshold would not rescue them. The 24 false alarms score between 0.26 and 0.79 (median 0.54), so some are confident, not borderline. **[Open a few of these failure images and name the cause you see: small riders, occlusion, helmet-like headwear. The test images are only in the Colab session (`datasets/a-yvljahelmet-and-non-helmet-abb47-v1/test/images`), and `artifacts/test_scores.csv` lists each image's name and scores.]**

## Cost matrix and operating point

| Outcome | Cost (€ per item) | Source |
|---|---|---|
| False negative | 5.00 | Fine: 1% × €200 = €2.00. Accident: 0.02% × €15,000 = €3.00. Both assumed. |
| False positive | 0.65 | Rider time: 1 min × €0.40/min = €0.40. Delay: 5% × €5 = €0.25. Assumed. |
| True positive | 3.00 | Time to fetch and put on a helmet: 5 min × €0.40/min = €2.00. Delay: 20% × €5 = €1.00. Assumed. |
| True negative | 0.00 | No intervention, no delay. |

- **Base rate assumed**: 3% of riders leave without a helmet.
- **Review cost** (added to any outcome that goes to a person): 10 seconds at €20/hour, about €0.056 per item.
- **What the costs say before any model**: send an item to a person instead of failing it when the chance of a violation is below about 91% (review €0.056 vs false alarm €0.65), and instead of passing it when above about 3% (review €0.056 vs saving €2.00 by catching). So the cost structure favours a wide review band. Model scores are not calibrated probabilities, so the sweep decides the real values.
- **Cost-against-threshold sweep**: With the model deciding alone, the cheapest single threshold is 0.66 at €112.60 per 1,000 items. Cost starts near the do-nothing level (€150) at a threshold of 0.10, bottoms out around 0.6 to 0.7, then climbs to €131.61 at 0.80 as more violations slip below the threshold.

![Cost against threshold](artifacts/cost_sweep.png)

- **Operating point chosen**: Pass below **0.27**, fail at or above **0.79**, human review in between. This is the cheapest band on the 0.01 grid: €96.54 per 1,000 items, 14% cheaper than the best single threshold. On the test split, 442 compliant items pass, 21 go to review and none are failed, while of the 248 violations 13 pass (the missed ones), 142 go to review and 93 are failed outright. Two caveats. First, cost is flat near the optimum: a band of 0.25 to 0.75 costs €100.35, within 4%. Second, 0.79 sits just above the highest false-alarm score in the test set (0.787), so that edge, and the zero false fails, are partly an effect of tuning on the test split.
- **Assumption that would most change my answer**: The accident cost (0.02% × €15,000 = €3.00). It makes up 60% of the false-negative cost, so if it were much lower, the optimal threshold would shift toward fewer stops. At half, a false negative costs €3.50 and catching saves only €0.50, so the threshold moves up. At double, catching saves €5.00 and the threshold moves down. I reran the sweep at accident costs of €1.50 and €6.00. The cheapest single threshold is 0.79 at half, 0.66 at the base case and 0.52 at double. The cheapest band stays 0.27 to 0.79 at half and becomes 0.18 to 0.79 at double. So the upper edge is stable and the lower edge moves with this assumption.

## What a person still has to check

- **Thresholds**: pass below 0.27, fail at or above 0.79, review in between.
- **Share of cases sent to a person**: 6.1% of items. About 72% of those reviews are compliant riders, because compliant riders are 97% of traffic.
- **Per day**: 6.1% × 1,500 items/day = 92 items.
- **Time per check**: 10 seconds.
- **People needed**: share × 1,500 × 10 / 3,600 / 6 productive hours = 0.04 people.
- **Is that realistic?** Yes on workload: 92 reviews at 10 seconds each is about 15 minutes a day, so it is a task for someone already at the depot, not a job. The harder parts are timing and accuracy. A rider waits at the exit while the image is reviewed, so review has to happen within seconds, and the costing assumes the reviewer is always right.

Baseline alternatives, at 1,500 items/day and a 3% base rate (review costs 10 s at €20/h ≈ €0.056 per item):

| Alternative | Cost per day | Working |
|---|---|---|
| Do nothing | €225 | 1,500 × 0.03 × €5.00 (every violation is a false negative) |
| Person checks everything | ≈ €218 | 1,500 × (€0.056 + 0.03 × €3.00); about 4.2 hours of review, so under one person |
| Perfect model, no review (lower bound) | €135 | 1,500 × 0.03 × €3.00 |
| Model decides on its own | about €169 | Threshold 0.66: €112.60 per 1,000 x 1.5 |
| Model + review band (my design) | about €145 | Band 0.27 to 0.79: €96.54 per 1,000 x 1.5, with 92 reviews a day |

Under these assumptions, having a person check everything barely beats doing nothing, so the value of the model depends heavily on the cost assumptions. *Addition:* the floor is €135 a day, so the most any model can save over doing nothing is €90 a day. My design costs about €145 a day. That is €80 below doing nothing and about €10 above the €135 floor, so it captures roughly 89% of the maximum possible saving. The model alone captures about 62% (€169). The design also beats having a person check everything (€218) by about €73 a day. These figures use the test split's error rates mixed at 3%, and the band was tuned on that same data, so treat 89% as an upper estimate.

## Limitations & next steps

- **Assumed costs and base rate**: Every euro figure and the 3% rate are my assumptions. I would replace them with the company's real fines, incident and claims history, and a count of riders without helmets from a week of depot footage, then rerun the sweep.
- **Dataset mismatch with a depot exit**: The test split is 35% violations and the images are not from a depot camera. I would collect and label a few thousand frames from the real exit camera at the real violation rate and use them as the test split.
- **Reviewer assumed always correct**: The costing treats a 10-second review as resolving the truth. I would time and score real reviewers on a labelled sample and add a reviewer error rate to `costing.py`.
- **Thresholds tuned on the test split** *(addition)*: the band was picked on the test scores and cost is reported on the same scores, so cost is slightly optimistic. I would choose thresholds on the validation split and report cost once on test. The upper edge, 0.79, sits just above the highest false-alarm score in the test set (0.787), which shows how much it depends on that one image.
- **Short training run** *(addition)*: the model trained for only 15 epochs, and with patience 15 early stopping could not stop it. I did not check whether validation mAP was still rising. I would train longer and read the validation curve before trusting the weights as final.
- **Small violation class in test** *(addition)*: with 248 violation images, recall carries wide uncertainty. I would bootstrap the test set for an interval and add more labelled violations.
- **Item score is the single highest box** *(addition)*: one spurious box can fail a group image and a missed head can pass it. I would look at group images separately and consider per-rider decisions.
- **Possible near-duplicates across splits** *(addition)*: if the same scene is in train and test, results are inflated. I would check for overlap before trusting the test numbers.

## Generative AI use disclosure

I'm yet to write this.
