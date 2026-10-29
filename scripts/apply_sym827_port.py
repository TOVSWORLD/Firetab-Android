#!/usr/bin/env python3
"""Hash-locked SYM827 source port; preflight every byte before target replacement."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
ROOT = Path(__file__).resolve().parents[1]
PORT = ROOT / 'projects/firetabs-android/kernel/regulator-port'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def apply(source, revision):
    lock = json.loads((PORT / 'inputs.json').read_text())
    if revision != lock['ack_commit']:
        raise ValueError('Wrong ACK revision')
    patch = PORT / lock['patch']
    if digest(patch.read_bytes()) != lock['patch_sha256']:
        raise ValueError('Patch drift')
    for path, expected in lock['sources'].items():
        if digest((ROOT / path).read_bytes()) != expected:
            raise ValueError('Evidence source drift')
    target = source / lock['target']
    original = target.read_bytes()
    if digest(original) != lock['original_sha256']:
        raise ValueError('Target source drift')
    with tempfile.TemporaryDirectory() as tmp:
        shadow = Path(tmp)
        copy = shadow / lock['target']
        copy.parent.mkdir(parents=True)
        copy.write_bytes(original)
        subprocess.run(['git', '-C', str(shadow), 'apply', str(patch)], check=True, capture_output=True)
        output = copy.read_bytes()
        if digest(output) != lock['patched_sha256']:
            raise ValueError('Patched output drift')
    # Recheck immediately before replacement; disposable checkout only.
    if target.read_bytes() != original:
        raise ValueError('Target changed during preflight')
    with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as staged:
        staged_path = Path(staged.name)
        staged.write(output)
    try:
        staged_path.chmod(target.stat().st_mode & 0o777)
        staged_path.replace(target)
    finally:
        staged_path.unlink(missing_ok=True)
    return {'source_applied': True, 'runtime_qualified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    revision = subprocess.check_output(['git', '-C', str(args.source), 'rev-parse', 'HEAD'], text=True).strip()
    print(json.dumps(apply(args.source, revision)))


if __name__ == '__main__':
    main()
