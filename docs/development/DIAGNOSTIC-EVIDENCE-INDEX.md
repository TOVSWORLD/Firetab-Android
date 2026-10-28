# Douglas diagnostic evidence package

The [LK handoff coverage inventory](LK-HANDOFF-COVERAGE.md) consolidates nine
pinned source receipts and five explicitly unqualified runtime evidence gates.

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

The [observed stock clock ABI](../../evidence/power-port/transition-order/observed-stock-clock-abi.json)
was read over authorized normal-Android USB with strict property/byte/time bounds:
MFG70/MM67 differ from candidate54/51. This is live declared-DT metadata, not a
clock-rate or register measurement. The [transition and ABI review](../../projects/firetabs-android/kernel/power-port/TRANSITION-AND-DTB-ABI.md)
explains why matching candidate-DTB handoff remains a loading prerequisite.

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

## Candidate provider effects before experimental loading

[Power-domain/source contract](../../evidence/power-port/domain-contract/report.json)
and [probe prerequisites](../../evidence/power-port/domain-contract/probe-contract.json)
record operations initiated by the captured DT: available domains are normally
powered on during probe; pwrap enables clocks/DCM and may reset/reinitialize its
PMIC transport. Generic QEMU does not exercise these douglas providers. Treat
these hardware register writes as part of the intended experimental failure and
return plan, not as read-only log collection. Suspend-wakeup and MFG clock
placement differ from legacy and remain unqualified. No device action was used
to obtain this source evidence; stock USB log export remains a separate scope.

The [captured power topology result](../../evidence/scpsys-binding/topology-result.json)
checks declared IDs, MFG parent and INFRACFG phandle in the locked candidate;
[contract and limits](../../projects/firetabs-android/kernel/dtb/SCPSYS-BINDING.md).
It is rerun against the freshly compiled DTB in CI. This is not a register read,
voltage test or independent failed-boot recovery result.

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

The [watchdog provider contract](WATCHDOG-BINDING.md) reuses verified legacy register offsets/keys and matches the donor probe/binding. Probe can reprogram an already-running watchdog;19 schema controls and41 remaining full-context diagnostics do not qualify reset/return behavior.

The [pinctrl syscfg resource contract](PINCTRL-SYSCFG-BINDING.md) validates candidate phandle linkage and declared range against selected source tables/formulas;12 schema controls and40 remaining full-context diagnostics are not physical pin/IRQ evidence.
