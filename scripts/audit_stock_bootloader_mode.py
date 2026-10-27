#!/usr/bin/env python3
"""Metadata-only selected stock mode-state review; no firmware execution."""
import hashlib
import json
from audit_stock_fastboot_registration import ROOT, DIGEST


def main():
    raw=(ROOT/'out/ota-loader-inspection-659664620/lk.bin').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=DIGEST:raise ValueError('Exact stock LK required')
    payload=raw[512:]
    windows=[(0x288e8,0x2892a),(0x26c04,0x26c20),(0x284e8,0x28512)]
    print(json.dumps(dict(lk_sha256=DIGEST,scope='Selected manually reviewed state helper and wrappers',
        windows=[dict(start=a,end=b,sha256=hashlib.sha256(payload[a:b]).hexdigest()) for a,b in windows],
        mode_helper_offset=0x288e8,register_selector=0x802c,mode_flag_mask=0x2000,
        argument_one_sets_flag=True,argument_zero_clears_flag=True,
        register_read_wrapper=0x26c04,register_write_wrapper=0x26c14,
        shared_access_backend=0x269c8,backend_physical_identity_verified=False,
        commit_helper=0x284e8,commit_write_selector=0x803c,poll_selector=0x8000,poll_mask=0x40,
        poll_has_iteration_or_elapsed_bound=False,selected_helper_checks_access_status=False,
        mode_flag_persistence_or_clear_on_boot_verified=False,
        plain_reboot_calls_mode_helper_in_selected_handler=False,
        runtime_command_acceptance=False,stock_return_verified=False,original_restore_verified=False,
        firmware_executed=False,physical_test_ready=False),indent=2))


if __name__=='__main__':main()
