#!/usr/bin/env python3
"""Apply the experimental MT8163 overlay to a disposable pinned ACK checkout."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

BASE = Path(__file__).resolve().parents[1]
PORT = BASE / 'projects/firetabs-android/kernel/clock-port'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    source = args.source.resolve()
    lock = json.loads((PORT / 'inputs.json').read_text())
    actual = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
    if actual != lock['ack_commit']:
        raise SystemExit('Refusing a different ACK revision')
    for record in lock['inputs']:
        original = BASE / record['source']
        if hashlib.sha256(original.read_bytes()).hexdigest() != record['sha256']:
            raise SystemExit(f'Input hash mismatch: {original}')
        if (source / record['target']).exists():
            raise SystemExit(f'Refusing to overwrite {record["target"]}')
    patches = [str(PORT / name) for name in ['build-wiring.patch', 'mux-api.patch']]
    subprocess.run(['git', '-C', str(source), 'apply', '--check', *patches], check=True)
    subprocess.run(['git', '-C', str(source), 'apply', *patches], check=True)
    for record in lock['inputs']:
        target = source / record['target']
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(PORT / 'overlay' / record['target'], target)
    print('Applied experimental clock overlay; no compile/boot qualification')


if __name__ == '__main__':
    main()
