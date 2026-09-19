# SAE context and intervention prediction

The current study is **[Can activation context predict SAE intervention effects?](reports/sae_context_study/report.md)** ([PDF](reports/sae_context_study/report.pdf)).

The motivation was to use ordinary activation context to predict the effect of editing a fixed SAE decoder direction. The observational tests found contextual differences among selected entries. The intervention pilot did not turn those differences into a useful predictor: the fit-set mean had lower pooled check MSE than every fitted model for each of the three tested features.

The constants were added retrospectively to saved inference. This is a negative development result on two diagnostic logit contrasts, with 16 check groups per feature. It does not establish that context is generally uninformative, nor does it demonstrate selective behavioral control.

The report links the methods, per-case errors and controls. See [reproduction](docs/reproduction.md) for the commands, [claim details](research/claims.md) for exact inferential limits, and [status](research/STATUS.md) for the distinction between completed studies and proposals.

The separate [coding-repair pilot](experiments/coding_forensics/RESULTS.md) was stopped because all 48 repairs complied with the editing boundary. Its proposed follow-up has not produced model results.
