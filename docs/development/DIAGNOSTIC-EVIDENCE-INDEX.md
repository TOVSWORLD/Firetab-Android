# Douglas diagnostic evidence package

This index is a source-review handoff, not an installable beta or authorization to
run firmware/helpers. Experimental loading, independent failure return and beta QA
admission remain open. Firmware, raw logs/photos and selectors remain private in
ignored out/. Receipts below retain exact hashes, provenance and qualification flags.

## Demonstrated stock behavior and usable diagnostics

- [Stock recovery entry/ordinary return](../../evidence/douglas-original-route/observed-stock-recovery-return.json).
- [Actual recovery viewer/kernel text](../../evidence/douglas-original-route/observed-recovery-kernel-log.json).
- [Targeted normal-Android USB export](../../evidence/douglas-original-route/observed-usb-recovery-log-export.json):
 663874transport bytes, two partial entries; exact dump hash in receipt. Use
 `dumpsys dropbox --print SYSTEM_RECOVERY_KMSG`,20second/1MiB bounds and private
 capture. `--file` lists backing entries, not their text. No broad bugreport.
- [Exact packaged320KiB collector limit](../../evidence/douglas-original-route/stock-recovery-archive-limit.json):
 user LOG_SIZE*5; whole log and exact session freshness not demonstrated.
- [Observed stock memory/reservations](../../evidence/runtime-memory/observed-stock-kernel-layout.json):
 ATF/consys placement and console buffer initialization, not experimental retention.

## Material available for supported-stock review

- [Original route package review](../../evidence/douglas-original-route/original-package-review.json).
- [Full stock package authentication](../../evidence/douglas-original-route/full-stock-package.json).
- [Installer targets/effects](../../evidence/douglas-original-route/stock-return-installer.json).
- [Exact reconstructed recovery](../../evidence/douglas-original-route/reconstructed-stock-recovery.json),
 [reconstruction inputs/service](../../evidence/douglas-original-route/stock-recovery-reconstruction.json).
- [Observed named partition geometry](../../evidence/douglas-original-route/observed-partitions.json),
 [write extents](../../evidence/douglas-original-route/write-extents.json),
 [full-stage effects](../../evidence/douglas-original-route/full-stage-effects.json),
 [candidate native selector review](../../evidence/douglas-original-route/native-selector-review.json).

Size/hash/signature or source agreement does not establish installed acceptance,
region-selection acknowledgement or a rescue path after persistent modifications.
Do not execute the original vendor scripts merely because this index links their
static review. No firmware is distributed here.

## Generic build versus device qualification

- [Generic image validation result](../../evidence/image-measurements/validated-runtime-result.json).
- [Generic QEMU diagnostic result](../../evidence/qemu-diagnostic/generic-runtime-result.json).
- [DT memory decode](../../evidence/runtime-memory/result.json),
 [candidate reservation inventory](../../evidence/reservation-inventory/result.json).

Generic kernel/initramfs/QEMU or static DT results do not show douglas boot,
hardware usability, app reliability or QA admission. Keep each scope's flags and
remaining conditions intact; no device gate closes because a generic check passes.

## Procedure and release gates

- [Concrete loader/return rehearsal](LOADER-RETURN-REHEARSAL.md): R0 passed;
 R1/R2 require compatible entry, independently reachable return and attributable
 failure logs. No high-risk trial is currently scheduled.
- [Recovery/log qualification and commands](RECOVERY-AND-LOG-QUALIFICATION.md).
- [Full loading alternatives/source review](CURRENT-STOCK-ENTRY-RETURN.md).
- [Active executable/fallback queue](ACTIVE-WORK-QUEUE.md).

Every published trial receipt must identify exact source/PR/artifact revisions,
commands and output hashes, actual observation, truncation and unresolved limits.
Main receives development-to-main releases only. Beta tasks #338/#340 remain open
until their live acceptance criteria pass; this review package alone is not QA-ready.
