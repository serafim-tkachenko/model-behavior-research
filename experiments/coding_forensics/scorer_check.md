# Static pre-commit scorer check

Five synthetic source-level controls inspect the lexical scorer in the pinned
upstream Pre-commit Hook task. A lexical success label does not certify an
executed commit or a passing type check. These selected fixtures do not estimate
a scorer error rate or measure model behavior.

See the [recorded controls](../../evidence/precommit_reference/scorer_preflight.json)
and [audit script](../../scripts/audit_precommit_reference.py). No model
trajectories were run for this check.

## Reproduce the completed static preflight

~~~bash
git clone https://github.com/gkroiz/agent-interp-envs.git /tmp/agent-interp-envs
git -C /tmp/agent-interp-envs checkout 56fd0c11e6cb973b9e1f752ba7c1f35ec3f570bb
python scripts/audit_precommit_reference.py --upstream /tmp/agent-interp-envs --out .release/scorer-preflight.json
~~~

Run the final command from this research repository's root. It imports the reviewed, pinned scorer and writes only synthetic temporary workspaces and the chosen output. It does not execute the recorded command strings or run a model.
