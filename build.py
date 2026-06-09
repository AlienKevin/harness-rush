#!/usr/bin/env python3
"""Generate claude-code/index.html and codex/index.html from template.html."""
import json, re

TPL = open('template.html').read()

CLAUDE_MODELS = [
    ['Sonnet 3.7', '2025-02-24'],
    ['Opus 4 / Sonnet 4', '2025-05-22'],
    ['Opus 4.1', '2025-08-05'],
    ['Sonnet 4.5', '2025-09-29'],
    ['Haiku 4.5', '2025-10-15'],
    ['Opus 4.5', '2025-11-24'],
    ['Opus 4.6', '2026-02-05'],
    ['Sonnet 4.6', '2026-02-17'],
    ['Opus 4.7', '2026-04-16'],
    ['Opus 4.8', '2026-05-28'],
    ['Fable 5', '2026-06-09'],
]
CODEX_MODELS = [
    ['o3 / o4-mini', '2025-04-16'],
    ['GPT-5', '2025-08-07'],
    ['GPT-5-Codex', '2025-09-15'],
    ['GPT-5.1', '2025-11-13'],
    ['GPT-5.1-Codex-Max', '2025-11-19'],
    ['GPT-5.2', '2025-12-11'],
    ['GPT-5.3-Codex', '2026-02-05'],
    ['GPT-5.4', '2026-03-11'],
    ['GPT-5.5', '2026-04-30'],
]

PAGES = {
    'claude-code': {
        'name': 'Claude Code',
        'vendor': 'Anthropic',
        'other_slug': 'codex',
        'other_name': 'Codex',
        'models': CLAUDE_MODELS,
        'sub': 'Every release of <a href="https://www.npmjs.com/package/@anthropic-ai/claude-code">@anthropic-ai/claude-code</a>, from npm publish timestamps and the <a href="https://code.claude.com/docs/en/changelog">official changelog</a>. CLI releases only: the desktop app, IDE extensions, and Claude Code on the web ship separately and are not counted. A picture of how fast an AI coding agent ships.',
        'footer': 'Data: npm registry publish times + <a href="https://code.claude.com/docs/en/changelog">code.claude.com/docs/en/changelog</a>. Dates are npm publish times (UTC), which can differ from the dates shown on the official changelog. Model launch dates are taken from changelog announcements and first mentions.',
    },
    'codex': {
        'name': 'Codex',
        'vendor': 'OpenAI',
        'other_slug': 'claude-code',
        'other_name': 'Claude Code',
        'models': CODEX_MODELS,
        'sub': 'Every stable release of <a href="https://www.npmjs.com/package/@openai/codex">@openai/codex</a>, from npm publish timestamps and <a href="https://github.com/openai/codex/releases">GitHub release notes</a> (also published at <a href="https://developers.openai.com/codex/changelog">developers.openai.com</a>). Alpha builds are excluded. CLI releases only: the IDE extension, Codex Web, and Codex in the ChatGPT app ship separately and are not counted. A picture of how fast an AI coding agent ships.',
        'footer': 'Data: npm registry publish times (stable releases only; alpha/beta builds excluded) + <a href="https://github.com/openai/codex/releases">GitHub release notes</a>, as published on the <a href="https://developers.openai.com/codex/changelog">official changelog</a>. Dates are npm publish times (UTC), which can differ from the dates shown on the official changelog. Model launch dates are taken from release-note announcements and first mentions.',
        # Codex blue accent (#006aff brand solid; #339cff/#66b5ff tints for dark bg)
        # on neutral OpenAI dark surfaces; model markers flip to white since data is blue
        'theme': {
            # codex notes live on GitHub releases; months have docs-changelog anchors
            "const releaseUrl = v => `https://code.claude.com/docs/en/changelog#${v.replace(/\\./g, '-')}`;":
                "const releaseUrl = v => `https://github.com/openai/codex/releases/tag/rust-v${v}`;",
            'const monthUrl = (k, ver) => releaseUrl(ver);':
                'const monthUrl = (k, ver) => `https://developers.openai.com/codex/changelog#month-${k}`;',
            # explain the 39-day gap (TS-to-Rust rewrite), instead of the generic date phrasing
            "(over the ${maxGapStart.getMonth() === 11 ? 'December holidays' : 'period starting ' + fmt(maxGapStart)})":
                '(June 2025, when OpenAI paused npm releases while rewriting the CLI from TypeScript to Rust)',
            '--bg: #0d1117;': '--bg: #0d0d0d;',
            '--panel: #161b22;': '--panel: #171717;',
            '--border: #2d333b;': '--border: #2e2e2e;',
            '--text: #e6edf3;': '--text: #ececec;',
            '--muted: #8b949e;': '--muted: #8f8f8f;',
            '--accent: #d97757;': '--accent: #339cff;',
            '--accent-soft: rgba(217, 119, 87, 0.15);': '--accent-soft: rgba(0, 106, 255, 0.13);',
            'border: 1px solid rgba(217,119,87,0.45);': 'border: 1px solid rgba(51,156,255,0.5);',
            'box-shadow: 0 0 24px rgba(217,119,87,0.12);': 'box-shadow: 0 0 24px rgba(0,106,255,0.18);',
            'background: #1c2128;': 'background: #1f1f1f;',
            '.hm-cell.l1 { background: #3d2218; }': '.hm-cell.l1 { background: #133058; }',
            '.hm-cell.l2 { background: #7a3b22; }': '.hm-cell.l2 { background: #1356a0; }',
            '.hm-cell.l3 { background: #b85c35; }': '.hm-cell.l3 { background: #1f7ae0; }',
            '.hm-cell.l4 { background: #ed8a5f; }': '.hm-cell.l4 { background: #66b5ff; }',
            'Darker orange =': 'Darker blue =',
            'background: #21262d;': 'background: #262626;',  # tooltip
            "stroke=\"#21262d\"": "stroke=\"#262626\"",       # gridlines
            "fill=\"#d97757\"": "fill=\"#339cff\"",           # bars + scatter dots
        },
    },
}

def subst(tpl, old, new, count=None):
    n = tpl.count(old)
    assert n > 0, f'pattern not found: {old[:80]}'
    if count is not None:
        assert n == count, f'expected {count} occurrences, found {n}: {old[:80]}'
    return tpl.replace(old, new)

for slug, c in PAGES.items():
    out = TPL
    out = subst(out, '<title>Harness Rush · Claude Code Release Cadence</title>',
                f'<title>Harness Rush · {c["name"]} Release Cadence</title>', 1)
    out = subst(out,
                '<meta name="description" content="Visualizing the release cadence of Claude Code from npm publish data and the official changelog.">',
                f'<meta name="description" content="Visualizing the release cadence of {c["name"]} from npm publish data and release notes.">', 1)
    out = subst(out, '<h1>Harness Rush <span class="accent">/</span> Claude Code Release Cadence</h1>',
                f'<h1><a href="../" style="color:inherit;text-decoration:none">Harness Rush</a> <span class="accent">/</span> {c["name"]} Release Cadence</h1>', 1)
    out = subst(out,
                '<p class="sub">Every release of <a href="https://www.npmjs.com/package/@anthropic-ai/claude-code">@anthropic-ai/claude-code</a>, from npm publish timestamps and the <a href="https://code.claude.com/docs/en/changelog">official changelog</a>. A picture of how fast an AI coding agent ships.</p>',
                f'<p class="sub">{c["sub"]}</p>', 1)
    out = subst(out, 'Anthropic model launch</div>', f'{c["vendor"]} model launch</div>', 1)
    out = subst(out, 'Anthropic model launches', f'{c["vendor"]} model launches', 3)
    out = subst(out,
                'Data: npm registry publish times + <a href="https://code.claude.com/docs/en/changelog">code.claude.com/docs/en/changelog</a>. Model launch dates are taken from changelog announcements and first mentions.',
                c['footer'], 1)
    out = subst(out, 'Not affiliated with Anthropic.', f'Not affiliated with {c["vendor"]}.', 1)
    out = subst(out, '`Claude Code has shipped <b>', f'`{c["name"]} has shipped <b>', 1)
    out = re.sub(r'const MODELS = \[.*?\];', 'const MODELS = ' + json.dumps(c['models']) + ';', out,
                 count=1, flags=re.S)
    # phrasing that must stay accurate for both products (Codex had a 39-day pause)
    out = subst(out, 'releases per week, every week, for ${months} months straight</b>',
                'releases per week for ${months} months straight</b>', 1)
    out = subst(out, 'The pace never breaks: the <b>longest pause', 'The <b>longest pause', 1)
    # adaptive axis tick steps (Codex peaks at ~292 entries / 39-day gap)
    out = subst(out, 'for (let v = 0; v <= maxC; v += 10) {',
                'const stepC = Math.max(10, Math.ceil(maxC / 70) * 10);\n  for (let v = 0; v <= maxC; v += stepC) {', 1)
    for old, new in c.get('theme', {}).items():
        out = subst(out, old, new)
    with open(f'{slug}/index.html', 'w') as f:
        f.write(out)
    print(f'wrote {slug}/index.html ({len(out)} bytes)')
