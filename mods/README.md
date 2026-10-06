# Mods

Mods are Claude Code plugins built on function hooks. Each one is a hooks module that listens to session events and can draw a pane, show a toast, or add a line to the model's context. This folder is published as a plugin marketplace from the repo root, so you add the marketplace once and install mods by name.

```
/plugin marketplace add BioInfo/claudelicious
```

| Mod | What it does | Install |
|-----|--------------|---------|
| [command-center](command-center/) | A pane beside the session with the intent, running jobs, files changed, the last reply's open questions, one-click prompts, and the 5h/7d limit pace. | `/plugin install command-center@claudelicious` |

Run `/reload-plugins` after an install. More mods will follow.
