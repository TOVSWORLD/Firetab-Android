# Project direction: maintainable Android ports for legacy Fire tablets

User direction, 24 October 2026: make legacy Fire devices useful as general-purpose
Android tablets through a repeatable pathway for maintaining supported Android releases.
Crestron Home is one required application, alongside broader everyday tablet use.
A dedicated control panel or a one-off older Android port does not satisfy the objective.

## Agreed kernel and platform direction

Port a current, maintained Android kernel appropriate to the target Android release to
the hardware, and keep kernel support moving with future Android releases. Android 17
is the initial platform target under investigation. Select the exact Android Common
Kernel branch and support lifetime through source-based compatibility research; no
specific kernel version has yet been selected or validated for douglas.

The existing 3.18 and 4.9 douglas trees provide hardware descriptions, drivers, boot
contracts and regression references. Keeping those old kernel bases alive through an
expanding set of backports is not the selected long-term strategy. Intermediate Android
builds may be used for a specific diagnostic purpose if justified later; they are not
mandatory release milestones or the destination.

The work is to identify existing support in the current kernel, forward-port or replace
missing drivers, adapt Android hardware interfaces, and validate the resulting device.
Inventory panel, touchscreen variants, PMIC/regulators, storage, USB, battery/thermal,
Wi-Fi, Bluetooth, sensors, audio, cameras and graphics. Preserve or replace proprietary
userspace/kernel contracts deliberately. Reuse common MT8163 work and upstream changes
where practical to reduce the cost of subsequent Android/kernel upgrades.

## General-purpose functionality

Target ordinary tablet functionality: installation and updates of compatible apps,
supported browsers and WebView, networking, display/touch, audio/video playback,
storage/SD card access, USB, sensors, charging, power management and suspend/resume.
Google Play/services remain a requested capability where feasible. Include broader app
compatibility, multitasking and sustained everyday use in performance testing, alongside
full Crestron Home functionality.

Features for hardware the device does not possess may be unavailable, as on other Android
devices. Declare capabilities accurately so apps can detect them. Distinguish physically
absent hardware from present hardware whose driver has not yet been ported; record the
latter as an implementation gap. Document limitations and their effect on apps rather
than treating every missing optional feature as a platform-wide blocker. CPU, RAM and
storage constraints require measurements, not an assumed Android version ceiling.

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
  suspend/resume, audio/video, relevant cameras, general-purpose app/browser/media tests, Home full-function tests, Google
  service installation, enforcing SELinux and long-duration operation.
- A release policy defining supported Android branches, security-update cadence,
  kernel/blob coverage, signing keys, reproducible build records, upgrade/rollback
  procedures and the criteria for ending a branch. Define “LTS” as a concrete
  project support commitment, separately from Linux LTS or upstream patch availability.

## Next engineering milestone

Produce a **current-kernel hardware-support and Android 17 integration audit** for
douglas. Choose a candidate maintained kernel branch, map existing and missing board
support, identify reusable driver implementations and proprietary interface constraints,
and define staged bring-up tests. Use the older kernels as references. Include
executable capability tests where practical; symbols or defconfig entries alone do not
establish functionality.

The user will provide the next instructions. This document update does not begin a
kernel port, large download, build, or physical device operation.

Current work is source inspection and initial Android 11 patch adaptation only.
No feature-gap audit, maintained kernel, complete build environment, CI pipeline,
Android 15/17 port or device validation is claimed complete.
