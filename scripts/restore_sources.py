#!/usr/bin/env python3
"""Restore inspection checkouts at locked commits. No firmware/device operations."""
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
for entry in json.loads((root / 'evidence/sources.lock.json').read_text()):
    dest = root / entry['directory']
    if dest.exists():
        actual = subprocess.check_output(['git', '-C', str(dest), 'rev-parse', 'HEAD'], text=True).strip()
        if actual != entry['commit']:
            raise SystemExit(f'Refusing to overwrite existing checkout: {dest}')
        print('PRESERVED', entry['directory'])
        continue
    subprocess.run(['git', 'init', str(dest)], check=True)
    subprocess.run(['git', '-C', str(dest), 'remote', 'add', 'origin', entry['url']], check=True)
    subprocess.run(['git', '-C', str(dest), 'fetch', '--depth=1', 'origin', entry['commit']], check=True)
    subprocess.run(['git', '-C', str(dest), 'checkout', '--detach', 'FETCH_HEAD'], check=True)
print('Sources restored only. Apply development patches explicitly; see docs/CONTINUE.md.')
