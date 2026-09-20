# State updates: development preflight

## Question and decision

Can a diagnosis of a language model's state-tracking error help choose a correction that generalizes better than the best fixed correction? This is the candidate research question. The current pilot only checks whether a simple behavioral assay is worth developing. It does not implement a diagnostic selector or establish a mechanism.

Start here rather than another SAE predictor: the outcome is an exact action choice, the simulator provides independently checkable labels, and simple controls can reject an unsuitable task before activation analysis. Keep EGNN paused until a faithful baseline reproduction is independently worth pursuing. World-model planning remains an alternative, not a second concurrent project.

## What runs now

Initial model: Gemma 3 1B **pretrained**, pinned to revision `fcf18a2a879aab110ca39f8bffbccd5d49d8eb29`; local cached weights; CPU float32; no training. Four named objects can occupy any of three boxes, including shared boxes. A move changes only the named object's box. The target always changes location. There are 0, 4 or 12 subsequent unrelated moves, six cases per regime, with two answers per box in each regime. The seed is 20260920. Three fixed worked examples use different object names.

For each history, score four inputs:

1. `initial_snapshot`: initial assignments only, with the initial target location as the answer. Tests basic retrieval without updates.
2. `history`: initial assignments plus all events, asking which box to open for the target.
3. `history_reminder`: the same history plus a generic instruction to use the most recent location. No gold state is supplied. This adds tokens and is not a compute-matched repair comparison.
4. `final_snapshot_oracle`: the simulator's final assignments, without history. Tests retrieval when state inference is removed. **Privileged diagnostic control, not an implementable repair.** A difference also changes prompt length and serialization, so it cannot identify a memory mechanism by itself.

Score the likelihood of the exact single-token A/B/C continuations and choose the largest. The script checks contextual tokenization. This is constrained-choice accuracy, not free-generation task success. Record full-vocabulary candidate probability mass and unrestricted top token to expose answer-format problems. Save all prompts, labels, probabilities and model/version metadata. Cases are development data; no untouched evaluation set has yet been made. After the 1B snapshot controls failed, one follow-up was selected: the same prompts and cases on cached Gemma 3 4B PT, revision `cc012e0a6d0787b4adcc0fa2c4da74402494554d`, also CPU float32. The larger model is a sequential development choice, not a preregistered independent confirmation.

The exact replay baseline should score 100%, an ignore-updates baseline 0% on these deliberately changed targets, and an always-A baseline 1/3. These are assay checks, not competitive agent baselines. The artificial 100% update rate is not an estimate of real-world prevalence. The three lag groups use different sampled histories, so their accuracy differences do not estimate a paired causal effect of delay. Initial target locations follow a fixed cyclic offset from final labels; that shortcut must be removed before fitting any data-driven predictor. Direct moves can be solved exactly by a last-relevant-event parser: this toy is an assay for model behavior, not a practical replacement for symbolic state storage.

## Decision rules for the development screen

These are working triage rules, not preregistered scientific hypotheses or significance tests. With only 18 histories, report counts and do not infer population effects.

- If either snapshot condition is below 90% accuracy, do not interpret history errors as isolated state-update failures. Inspect format competence and model suitability first.
- If snapshots pass and history is 20–90%, inspect the paired failures and candidate probability mass. This is a potentially useful assay, not proof of novelty.
- If history is almost perfect, do not keep adding arbitrary difficulty until an impressive failure appears. Decide whether a task with competing updates is independently motivated.
- A reminder that removes the failures weakens the case for a complex diagnostic method. Mixed reminder effects justify identifying a specific ambiguity, not immediately training a selector.

## Next experiment, conditional on this screen

One additional development model or prompt calibration may test whether the assay's behavior is robust. Then freeze a single task family. Add unchanged targets, independently balanced old/new box transitions, target-position counterbalancing, paired lag variants of the same base history, two prompt renderings, and a matched-length control that preserves relevant content. Separate failure modes using controlled counterfactuals before proposing internals.

Any eventual selector must be trained on development histories and compared against the strongest fixed correction selected on validation data, with equalized model calls/tokens. Include always-repeat, model-generated state extraction and a simple confidence rule. Group paired comparisons by original history; variants are not independent samples. Test new names, templates and histories only after choices are frozen. An oracle may label outcomes but must never supply hidden state to the selector. A probe alone does not prove use of a representation.

Stop the research claim if a fixed prompt explains the benefit, diagnosis does not predict held-out repair gains, or the apparent advantage depends on privileged state or extra computation. Do not add SAE analysis just to reuse the toolkit.

## Closest work and novelty limit

- [Oh & Demberg, dynamic entity tracking, v2 11 Sep 2026](https://arxiv.org/html/2606.08644v2): swap-based binding tasks and causal interventions in instruction-tuned Gemma/Llama models. Studying a box task or locating a rebinding circuit is already covered. This pilot uses direct moves and a smaller pretrained model; that difference is not a novelty claim.
- [HalluWorld](https://arxiv.org/html/2605.19341v1): controlled reference worlds, state-related errors and memory tasks. A simulator and exact state labels are not a contribution by themselves. Its serialization analyses also motivate caution about snapshot/history comparisons.
- [LeWorldModel](https://arxiv.org/abs/2603.19312): alternative path toward action-conditioned world models and planning. It would require reproducing the upstream planner before evaluating a new adaptive rule.

The potential contribution is whether a specific diagnosis predicts which repair will work on new histories at matched cost. This still needs a fuller nearest-work review before committing to a paper claim.

## Run

From the repository root:

```bash
uv run pytest -q experiments/state_updates/test_pilot.py
uv run python experiments/state_updates/pilot.py --output /tmp/state-symbolic
uv run python experiments/state_updates/pilot.py --model --output /tmp/state-model
uv run python experiments/state_updates/pilot.py --model --model-size 4b --output /tmp/state-model-4b
uv run python experiments/state_updates/analyze.py /tmp/state-model
```

Each output directory must be new. The 4B run needs roughly 18 GB of process RAM in this environment. The model command uses only cached files; download/access setup is separate. No API calls, model training or automatic GPU allocation occurs.

## Learning alongside the experiment

Work through one history by hand, implement the state transition, and explain why snapshot improvement is not causal localization. Then learn conditional likelihood, paired comparisons, and the difference between latent state, observation and action. These are the immediate fundamentals; RL training and JEPA losses are not prerequisites for this first screen. Plan the next two weeks around one reproducible result and its explanation, not a full-time research commitment.
