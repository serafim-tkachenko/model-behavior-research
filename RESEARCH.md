# Research brief: context, interventions and model behavior

**Status, 13 September 2026:** completed SAE observational study, completed development intervention pilot, exploratory reanalysis, and a stopped coding-repair feasibility assay. No confirmed semantic mechanism or general safety result.

## Question and motivation

When does activation-conditioned context explain what an SAE intervention does, beyond activation magnitude and generic geometry?

A fixed decoder direction can be active in different contexts. Contextual association alone is insufficient to predict selective behavioral effects. The project therefore progresses from held-out contextual comparisons to controlled interventions and incremental prediction. Its practical motivation is to make explanations useful for predicting or changing a specified behavior. That usefulness remains unestablished here.

## What was done

The main study uses pretrained Gemma 3 4B and pretrained Gemma Scope SAEs, not newly trained models. It covers 12,000 documents from two sources, layers 17 and 22, and 4,047,982 eligible token positions per layer. Every positive SAE activation was retained. Discovery-selected features were evaluated on held-out documents with separate corrected partner-composition and decoder-orthogonal displacement tests.

A development intervention pilot then examined 96 feature-prompt cases from 95 duplicate groups, with 5,376 repeated factorial comparisons. These are not 5,376 independent examples. The design held encoder, decoder-coordinate and norm constraints approximately fixed and included random directions, shuffled labels, leading-PC controls and scalar-gain comparisons. Later signed-response and incremental-PC analyses reused those data and are exploratory.

## What the evidence supports

- At the primary layer, 14/24 selected features pass the partner-composition test and 3/24 pass the separately corrected orthogonal-displacement test. Layer 22 gives 18/24 and 6/24. These are selected-feature conditional associations, not dictionary-wide prevalence.
- Feature 1645 has a positive descriptive learned-minus-random raw-interaction interval. Its beyond-gain interval crosses zero. Larger interaction magnitude does not establish selective control.
- Adding the learned context score to the PC predictor does not yield a pooled positive improvement interval for any supported feature. The result does not establish incremental predictive value.
- Predominantly odd-in-both-signs responses are compatible with local mixed curvature. They do not identify a semantic mechanism or a mediating pathway.

The [claim ledger](research/claims.md) links each statement to tables, controls and its inferential limits. The [full report](reports/research_report/report.md) and [PDF](reports/research_report/report.pdf) retain the complete methods and historical findings.

## What changed our research decision

The evidence does not yet justify treating contextual SAE structure as a validated behavioral explanation. Existing intervention data remain development material.

A separate coding pilot tested whether a specific edit-boundary reminder reduced prohibited test edits. All 48 trajectories produced compliant repairs, so the required behavioral contrast was absent. The assay was stopped. This is a feasibility decision, not evidence of general safety or reminder effectiveness.

The [next protocol](experiments/coding_forensics/next_protocol.md) starts from a documented repository task and asks whether a small local model can both perform the legitimate task and exhibit a reproducible behavioral contrast. Before inference, an independent evaluator must distinguish actual task completion from lexical shortcut flags. SAE analysis is deferred until simpler behavioral methods leave a concrete unanswered question.

## Review and reproduce

Start with the [review walkthrough](research/review.md), then the [reproduction guide](docs/reproduction.md). Frozen data and source archives have [public checksums and downloads](artifacts/README.md). The [status and decision log](research/STATUS.md) separates completed work, retrospective decisions and proposed experiments.

This project used substantial language-model assistance. Read the [contribution statement](CONTRIBUTIONS.md); maintainer review and authorship of specific scientific decisions must be recorded rather than inferred from repository ownership. Package tests and saved-output audits are distinct from independent scientific replication.
