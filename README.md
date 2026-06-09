# Harness Rush

Release cadence dashboards for AI coding agents, live at [harness-rush.vercel.app](https://harness-rush.vercel.app).

> Empirically, the headroom for improving the text layer is significant. It shows up across retrieval-augmented QA, test-time scaling, and tool-use agents: fixed-model behavior improves when we change the context or execution environment rather than the weights. Scale also appears to increase the value of text conditioning: larger models become better at using information supplied at inference time, and some context-conditioned abilities appear only at larger scale.
>
> — [Yoonho Lee](https://x.com/yoonholeee/status/2064027464926716154)

Harnesses are where that text-layer improvement ships. These dashboards track how fast it's happening.

- `/claude-code/` tracks `@anthropic-ai/claude-code` (npm publish times + official changelog)
- `/codex/` tracks `@openai/codex` stable releases (npm publish times + GitHub release notes)

## Updating

```sh
python3 refresh_data.py   # re-fetch npm/changelog/release data into data.js files
python3 build.py          # regenerate both subpages from template.html
```

Pushes to `master` auto-deploy to Vercel. An hourly cloud routine runs the refresh and pushes when data changed.

Model launch markers are hardcoded in `build.py` (`CLAUDE_MODELS` / `CODEX_MODELS`); add new model launches there as they're announced in the changelogs.
