#!/usr/bin/env python3
"""Metadata-only reviewed current-stock mode-flag consumer; no firmware execution."""
import hashlib
import json
from audit_stock_fastboot_registration import ROOT, DIGEST


def main():
    raw=(ROOT/'out/ota-loader-inspection-659664620/lk.bin').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=DIGEST:raise ValueError('Exact stock LK required')
    data=raw[512:]
    windows=[(0x2892c,0x2894e),(0x2439c,0x243ba),(0x24446,0x24460),(0x269c8,0x26a80)]
    print(json.dumps(dict(lk_sha256=DIGEST,scope='Selected manually decoded flag consumer/backend prefix',
        windows=[dict(start=a,end=b,sha256=hashlib.sha256(data[a:b]).hexdigest()) for a,b in windows],
        flag_reader=0x2892c,reader_call=0x243b2,selector=0x802c,bit_index=13,
        nonzero_branch=0x24446,branch_mode_code=0x63,clear_helper_tail=0x2445c,
        clear_helper=0x288e8,clear_helper_argument=0,
        clear_path_reachable_in_selected_static_branch=True,
        reader_access_status_checked=False,clear_completion_checked=False,
        backend_prefix_uses_mmio=True,backend_full_identity_verified=False,
        actual_flag_consumed_or_cleared_observed=False,reset_persistence_verified=False,
        command_entry_verified=False,stock_return_verified=False,original_restore_verified=False,
        firmware_executed=False,physical_test_ready=False),indent=2))


if __name__=='__main__':main()
