#!/usr/bin/env python3
"""Gate QEMU package installation on a disposable Linux GitHub runner."""
import argparse
import json
import os
from pathlib import Path
import shlex
import subprocess

LIMIT = 200*1024*1024


def package_bytes(output):
    sizes = []
    for line in output.splitlines():
        if "://" in line and ".deb" in line and not line.startswith("'"):
            raise ValueError("Unrecognized apt URI format")
        if line.startswith("'"):
            fields = shlex.split(line)
            if len(fields) < 3 or not fields[2].isdigit():
                raise ValueError('Unrecognized apt URI record')
            sizes.append(int(fields[2]))
    total = sum(sizes)
    if total > LIMIT:
        raise ValueError('QEMU package download exceeds 200 MiB gate')
    return total


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install', action='store_true')
    args = parser.parse_args()
    if not args.install or os.environ.get('GITHUB_ACTIONS') != 'true' or not Path('/etc/os-release').is_file():
        parser.error('Explicit --install on a disposable Linux GitHub runner required')
    command = ['sudo', 'apt-get', '--no-remove', '--no-install-recommends', '-y', 'install', 'qemu-system-arm']
    plan = subprocess.check_output(command[:2]+['--print-uris']+command[2:], text=True, env={**os.environ, 'LC_ALL': 'C'})
    size = package_bytes(plan)
    print(json.dumps({'scope': 'APT planned package archive bytes; metadata/TLS overhead excluded',
                      'download_bytes': size, 'download_limit': LIMIT}), flush=True)
    subprocess.run(command, check=True)
    subprocess.run(['dpkg-query', '-W', 'qemu-system-arm', 'qemu-system-common', 'qemu-system-data'], check=True)


if __name__ == '__main__':
    main()
