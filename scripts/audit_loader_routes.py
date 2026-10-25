#!/usr/bin/env python3
"""Offline route eligibility audit; git object reads only, never runs device helpers."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def assess(stock, sources):
    versions = stock['loader_versions_decimal']
    limits = sources['legacy_software_maximum_versions']
    if set(versions) != {'preloader', 'lk', 'tee'} or set(limits) != set(versions):
        raise ValueError('Expected explicit preloader/LK/TEE version fields')
    if any(type(x) is not int or x < 0 for x in [*versions.values(), *limits.values()]):
        raise ValueError('Loader versions must be nonnegative integers')
    exceeded = {name: {'installed': versions[name], 'maximum': limits[name]}
                for name in versions if versions[name] > limits[name]}
    return {'scope': 'Source-backed route triage only; no device access or recovery/boot qualification',
            'legacy_software_version_gate_passes': not exceeded, 'exceeded_version_limits': exceeded,
            'routes': [
                {'route': 'stock_recovery', 'ready_for_custom_kernel': False,
                 'reason': 'Stock signed-update restoration is not proof of arbitrary-kernel acceptance or matched recovery package.'},
                {'route': 'stock_fastboot_or_handshake', 'ready_for_custom_kernel': False,
                 'reason': 'boot-fastboot.sh invokes a handshake; no verified stock RAM boot implementation or safe recovery demonstrated.'},
                {'route': 'legacy_software_unlock', 'ready_for_custom_kernel': False,
                 'version_gate_rejects': bool(exceeded), 'persistent_changes': True, 'root_required_by_source': True,
                 'reason': 'Newer-version branch intentionally clears preloader and writes LK/TEE; provided fastboot installation erases userdata.'},
                {'route': 'legacy_bootrom_chain', 'ready_for_custom_kernel': False, 'persistent_changes': True,
                 'reason': 'Host main modifies GPT/preloader/RPMB/boot/recovery and loader images; minimal mode still writes. Physical entry and recovery on this unit unqualified.'},
                {'route': 'koboreru_preloader_exploit', 'ready_for_custom_kernel': False, 'persistent_changes': True,
                 'douglas_target_exists': True, 'custom_lk_partition': 'lk2',
                 'reason': 'README requires an older vulnerable preloader/downgrade. Exact installed binary susceptibility and lk2 layout are unverified; flashing TEE/LK is a prerequisite.'},
                {'route': 'custom_tee_or_lk', 'ready_for_custom_kernel': False, 'persistent_changes': True,
                 'reason': 'Post-unlock integration option, not an established entry path from untouched stock firmware.'}],
            'next_offline_step': 'Inspect model/build-matched OTA preloader/LK/TEE artifacts with bounded local static analysis; verify patch-address/format claims without executing payloads.',
            'physical_prerequisites_still_missing': ['Matched restoration images authenticated and retained',
                'Exact-board BootROM entry and tested recovery path', 'Explicit owner authorization for any destructive unlock/wipe',
                'Verified custom kernel entry/log route'],
            'diagnostic_package_ready': False, 'physical_boot_tested': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify-sources', action='store_true', help='Read pinned git objects from cached references; no helpers execute')
    args = parser.parse_args()
    source_file = ROOT/'evidence/loader-routes/sources.json'
    stock_file = ROOT/'evidence/stock-facts/runtime-contract.json'
    sources, stock = json.loads(source_file.read_text()), json.loads(stock_file.read_text())
    if args.verify_sources:
        for item in sources['records']:
            data = subprocess.check_output(['git', '-C', str(ROOT/item['cache']), 'show', item['revision']+':'+item['path']], timeout=15)
            if len(data) != item['bytes'] or hashlib.sha256(data).hexdigest() != item['sha256']:
                raise ValueError('Pinned source mismatch')
    result = assess(stock, sources)
    result['sources_manifest_sha256'] = hashlib.sha256(source_file.read_bytes()).hexdigest()
    result['stock_facts_sha256'] = hashlib.sha256(stock_file.read_bytes()).hexdigest()
    result['auditor_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    result['cached_source_hashes_verified'] = args.verify_sources
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
