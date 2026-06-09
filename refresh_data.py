#!/usr/bin/env python3
"""Refresh release data for both dashboards from npm, the Claude Code changelog,
and Codex GitHub release notes, then regenerate the data.js files.

Usage: python3 refresh_data.py && python3 build.py
Set GITHUB_TOKEN to raise the GitHub API rate limit (optional but recommended).
"""
import json
import os
import re
import urllib.request

UA = {'User-Agent': 'harness-rush-refresh'}


def get(url, headers=None):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode()


def npm_times(package, stable_only=False):
    reg = json.loads(get(f'https://registry.npmjs.org/{package}'))
    return {
        v: t for v, t in reg['time'].items()
        if v not in ('created', 'modified') and (not stable_only or '-' not in v)
    }


def refresh_claude():
    text = get('https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md')
    notes = {}
    for s in re.split(r'^## ', text, flags=re.M)[1:]:
        lines = s.strip().split('\n')
        bullets = [l[2:].strip() for l in lines[1:] if l.startswith('- ')]
        notes[lines[0].strip()] = bullets
    releases = []
    for v, t in npm_times('@anthropic-ai/claude-code').items():
        bullets = notes.get(v, [])
        releases.append({
            'version': v, 'date': t, 'changes': len(bullets),
            'highlight': (bullets or [''])[0][:200],
        })
    releases.sort(key=lambda r: r['date'])
    return releases


def refresh_codex():
    headers = {}
    if os.environ.get('GITHUB_TOKEN'):
        headers['Authorization'] = 'Bearer ' + os.environ['GITHUB_TOKEN']
    notes = {}
    for page in range(1, 30):
        batch = json.loads(get(
            f'https://api.github.com/repos/openai/codex/releases?per_page=100&page={page}',
            headers))
        if not batch:
            break
        for rel in batch:
            m = re.match(r'(?:rust-)?v?(\d+\.\d+\.\d+)$', rel['tag_name'])
            if not m:
                continue
            body = rel.get('body') or ''
            bullets = [l for l in body.split('\n') if re.match(r'\s*[-*] ', l)]
            notes[m.group(1)] = {
                'changes': len(bullets),
                'highlight': re.sub(r'^[\s*-]+', '', bullets[0])[:200] if bullets else '',
            }
        if len(batch) < 100:
            break
    releases = []
    for v, t in npm_times('@openai/codex', stable_only=True).items():
        n = notes.get(v, {'changes': 0, 'highlight': ''})
        releases.append({'version': v, 'date': t, **n})
    releases.sort(key=lambda r: r['date'])
    return releases


def write(slug, json_path, releases):
    with open(json_path, 'w') as f:
        json.dump(releases, f)
    with open(f'{slug}/data.js', 'w') as f:
        f.write('window.RELEASES = ' + json.dumps(releases) + ';')
    print(f'{slug}: {len(releases)} releases, latest {releases[-1]["version"]} ({releases[-1]["date"][:10]})')


if __name__ == '__main__':
    write('claude-code', 'data.json', refresh_claude())
    write('codex', 'codex-data.json', refresh_codex())
