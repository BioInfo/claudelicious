# Time Estimation

Estimate at Claude Code speed, not hand-coding speed. Don't pad for "setup", "debugging", "integration" — those collapse to near-zero when Claude is writing the code.

The real wall-clock budget is the slow stuff: model downloads, GPU-hours, external API rate limits, long inference, human review checkpoints. That's what to scope around.

If compute budget has headroom, **stretch the scope**: ablations, baselines, second datasets are cheap to wire up now.

If you catch yourself saying "this would take X days", stop and re-estimate by compute cost alone.
