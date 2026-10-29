#!/usr/bin/env python3
"""Verify pinned source receipts and the bounded wakeup branch comparison."""
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    path = ROOT / 'evidence/power-port/wakeup-core'
    report = json.loads((path / 'report.json').read_text())
    for name, digest in report['inputs'].items():
        assert hashlib.sha256((path / name).read_bytes()).hexdigest() == digest, name
    ack = (path / 'ack-genpd-core.c').read_text()
    legacy = (path / 'legacy-domain.c').read_text()
    header = (path / 'ack-pm_wakeup.h').read_text()
    assert ack.count('device_awake_path(dev) && genpd_is_active_wakeup(genpd) &&') == 2
    assert ack.count('!device_out_band_wakeup(dev)') == 2
    assert 'return device_wakeup_path(dev);' in header
    assert 'return dev->power.wakeup_path;' in header
    assert 'return dev->power.out_band_wakeup;' in header
    assert legacy.count('dev->power.wakeup_path && genpd_dev_active_wakeup(genpd, dev)') == 2
    assert 'return device_may_wakeup(dev) ? active_wakeup : !active_wakeup;' in legacy
    expected = []
    for wake, active, outband, off in itertools.product([False, True], repeat=4):
        old = off or (wake and active)
        new = wake and active and not outband
        expected.append(dict(wakeup_path=wake, active_policy=active,
                             out_band_wakeup=outband, legacy_suspend_power_off=off,
                             legacy_noirq_early_return=old,
                             ack_noirq_early_return=new, same_branch=old == new))
    assert report['rows'] == expected
    assert report['runtime_qualified'] is False
    assert all(r['same_branch'] for r in expected
               if not r['legacy_suspend_power_off'] and not r['out_band_wakeup'])
    print('PASS: pinned source receipts/anchors and16 bounded branch cases; no runtime equivalence')

if __name__ == '__main__':
    main()
