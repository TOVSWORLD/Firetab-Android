# FireTabs Android

Maintain general-purpose Fire tablets with current Android releases and a maintained,
release-appropriate Android kernel. Initial device: Fire HD 8 (2017), douglas/KFDOWI,
16 GB. Initial target: Android 17. No current-kernel build or boot has been demonstrated.

Crestron is an optional workload; this project's acceptance includes ordinary Android
apps, supported browsers, graphics, audio, video, networking, storage, power management,
updates, and enforcing SELinux. Document hardware absent from a device separately from
hardware present but not supported by the port.

## Working materials

Shared paths remain at the repository root so existing source locks and commands work:

- [Feasibility and source evidence](../../docs/FEASIBILITY.md)
- [Maintained kernel strategy](../../docs/MAINTENANCE.md)
- [Continuation and resource estimates](../../docs/CONTINUE.md)
- [Source lock](../../evidence/sources.lock.json), [reference manifests](../../manifests/)
- [Historical patches](../../patches/), [environment recipe](../../Dockerfile)
- [Offline project checks](../../scripts/ci.py): `python3 scripts/ci.py firetabs-android`
- [Validation state](validation.json)

## Development sequence

1. Select and pin a maintained kernel branch appropriate to the target Android release.
2. Inventory MT8163/douglas drivers against that tree; port device tree, boot image and
   essential storage, clocks, interrupts, serial console, and display support.
3. Build the kernel reproducibly, then Android. Preserve logs and artifact hashes.
4. Owner performs explicitly authorized boot tests; collect serial/logcat/dmesg evidence.
5. Validate hardware, SELinux, update/recovery paths and sustained general-purpose use.

The 3.18/4.9 trees and Android 11 patches are historical hardware references, not the
selected maintained platform. Standard pull-request CI does not download AOSP or build
firmware. Provisioning a large Linux build host is a separate resource decision.

## Maintained-kernel audit

[Issue #5 audit](../../docs/development/DOUGLAS-KERNEL-AUDIT.md) recommends the Android 17 /
6.18 ACK family and pins an initial integration candidate. It records an existing modern
douglas DTS, reusable MT8163 drivers, boot ABI gaps and a reproduced missing-header failure.
[Component matrix](kernel/support-matrix.json) is source evidence, not hardware validation.
Run `python3 scripts/kernel_audit.py` for offline source integrity/anchor checks.
