#!/usr/bin/env python3
"""Retain metadata for manually reviewed exact-stock reset windows; no execution."""
import hashlib
import json
from audit_stock_fastboot_registration import ROOT, DIGEST


def main():
    raw=(ROOT/'out/ota-loader-inspection-659664620/lk.bin').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=DIGEST:raise ValueError('Exact current stock LK required')
    data=raw[512:]
    windows=[(0x40010,0x40042),(0x28410,0x28458),(0x288e8,0x28920)]
    report=dict(lk_sha256=DIGEST,scope='Selected manually decoded exact-stock Thumb windows',
        windows=[dict(start=a,end=b,sha256=hashlib.sha256(data[a:b]).hexdigest()) for a,b in windows],
        reboot_handler_tail_target=0x28410,reboot_bootloader_tail_target=0x28410,
        reboot_bootloader_extra_call=0x288e8,common_reset_argument=1,
        reset_primitive_mmio_writes=True,reset_primitive_calls_wait_helper=True,
        wait_helper_time_units_verified=False,reset_primitive_terminal_self_loop=True,
        bootloader_extra_state_effects_fully_resolved=False,
        runtime_command_permission_verified=False,reset_completion_observed=False,
        original_state_restoration_verified=False,ram_boot_verified=False,
        firmware_executed=False,physical_test_ready=False)
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
