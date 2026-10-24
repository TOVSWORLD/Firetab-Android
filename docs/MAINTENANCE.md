# Project direction: maintainable Android ports for legacy Fire tablets

User clarification, 24 October 2026: the objective is a repeatable pathway for
maintaining supported Android release branches across these devices. A one-off
Crestron deployment or Android 11 port alone does not satisfy that objective.

## Revised interpretation of feasibility

Android 11 is an integration diagnostic milestone, not the proposed permanent
destination. Android 15 is a candidate first maintained platform branch because
the discovered kernel family has a corresponding branch and LineageOS supports
4.9-based devices there. Android 17 remains an explicit research target. None of
these statements establishes a tested douglas firmware or an absolute OS ceiling.

The outstanding question is the amount and recurring cost of compatibility work,
not whether a Cortex-A53 CPU can execute a modern Android instruction stream.
Device performance still requires measurement, especially with 1.5 GB RAM and
full Crestron Home media/intercom functionality.

## Kernel strategy decision

Two tracks merit comparison before selecting the long-term base:

1. **Maintain the existing douglas 4.9 port with explicit feature backports.**
   Inventory actual modern Android BPF programs, map types, helpers, verifier,
   cgroup attachment and syscall requirements against this tree. Establish tests
   for their real behavior. Validate ARM64 Clang builds and relevant hardening,
   binder, memory-management and filesystem interfaces. Keep a documented list
   of changes to Android itself; a growing list is maintenance cost, not progress
   hidden behind an updated version string.
2. **Forward-port the board to a newer maintained kernel.** Inventory panel,
   touchscreen variants, PMIC/regulator, storage, USB, battery/thermal, Wi-Fi,
   Bluetooth and graphics support. Identify which drivers can be reused, adapted
   or upstreamed, and which proprietary userspace ioctl contracts must be retained
   or replaced. Higher initial cost may reduce future recurring backport cost.

No evidence gathered so far quantifies which track is cheaper. The newer douglas
4.9 tree is a concrete starting asset for the first track and a hardware reference
for the second. A newer kernel cannot be substituted without adapting the board
drivers and userspace contracts.

## Required maintenance deliverables

- A common MT8163 hardware layer with per-board configuration, not copied complete
  trees for each release. Giza, douglas and Echo device differences remain explicit.
- A feature audit citing required Android source/API and matching kernel
  implementation, resolved config, test and result. Unknown is a valid status.
- Versioned blob inventories with hashes, ABI/symbol requirements and source
  provenance. Isolate graphics/audio/camera compatibility adapters instead of
  broadly weakening libc or Android security checks.
- Locked complete platform manifests and compiler/container digests, separate
  kernel/platform patch queues, repeatable image-content/size checks and CI.
- A physical test matrix: boot, display/touch, networking and UID filtering,
  suspend/resume, audio/video, relevant cameras, Home full-function tests, Google
  service installation, enforcing SELinux and long-duration operation.
- A release policy defining supported Android branches, security-update cadence,
  kernel/blob coverage, signing keys, reproducible build records, upgrade/rollback
  procedures and the criteria for ending a branch. Define “LTS” as a concrete
  project support commitment, separately from Linux LTS or upstream patch availability.

## Next engineering milestone

Produce a **kernel feature-gap audit for Android 17 against the douglas 4.9 tree**,
then compare it with the work needed for a newer kernel. This is more decision-useful
than repeatedly building intermediate Android releases without answering the
kernel question. The audit must include executable capability tests where practical;
symbol names or defconfig entries alone are insufficient.

Current work is source inspection and initial Android 11 patch adaptation only.
No feature-gap audit, maintained kernel, complete build environment, CI pipeline,
Android 15/17 port or device validation is claimed complete.
