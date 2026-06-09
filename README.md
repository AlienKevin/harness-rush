# Harness Rush

Release cadence dashboards for AI coding agents, live at [harness-rush.vercel.app](https://harness-rush.vercel.app).

- `/claude-code/` tracks `@anthropic-ai/claude-code` (npm publish times + official changelog)
- `/codex/` tracks `@openai/codex` stable releases (npm publish times + GitHub release notes)

## Updating

```sh
python3 refresh_data.py   # re-fetch npm/changelog/release data into data.js files
python3 build.py          # regenerate both subpages from template.html
```

Pushes to `master` auto-deploy to Vercel. An hourly cloud routine runs the refresh and pushes when data changed.

Model launch markers are hardcoded in `build.py` (`CLAUDE_MODELS` / `CODEX_MODELS`); add new model launches there as they're announced in the changelogs.
