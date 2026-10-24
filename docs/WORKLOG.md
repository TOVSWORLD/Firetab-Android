# Work log — 24 October 2026

## Commands and results

- Inspected the empty workspace; no applicable AGENTS.md found. Initialized outer
  Git repository on `port/douglas-bringup`. No remote added and nothing pushed.
- Initial sandbox network Git failed DNS resolution; approved network execution
  succeeded. This was an environment restriction, not an unavailable repository.
- Queried official Android/AOSP and Lineage release sources. Retrieved official
  Lineage changelogs with curl after web-reader 403 responses.
- Used `git ls-remote`, shallow `git clone --depth 1`, GitHub public REST metadata
  and selected raw source files. Exact clone commits/URLs are in the source lock.
- Inspected device/common/kernel/vendor/hardware sources, release notes, original
  and newer amonet source, current amazon-oss common/giza trees and compatibility
  patches. Never executed the exploit or repository installer scripts.
- Enumerated direct forks and searched related newer MT8163 work. Found explicit
  douglas board support in amazon-oss 4.9.337, including its lineage-22.2 branch.
- Read actual Android 17/Lineage 24 `NetBpfLoad.cpp` runtime gates. Copies saved.
  Lineage 24 Connectivity head inspected: `7c04d866538e6f689823b769fb5c1e614ca0e295`.
- Fetched official Play HTML, decoded its embedded JSON and checked the scraper
  field mapping. Extracted current Home minimum Android/version metadata.
- Created device branch `port/android11-bringup` at `4c557e6...`.
- Fixed wrong optional vendor inheritance (`vendor/douglas/douglas` →
  `vendor/amazon/douglas`) and made common BoardConfig inclusion mandatory.
  Saved the actual diff in `patches/0001-douglas-require-correct-vendor-and-common-paths.patch`.
  This prevents silently dropping device vendor files or common configuration.
- Probed all eight existing platform patches against pinned Android 11 touched
  files. Five failed, three applied. Initially Git skipped fixtures because it
  discovered the enclosing repository; corrected isolation with
  `GIT_CEILING_DIRECTORIES`, added a skipped-patch guard, and reran. Only the
  corrected results are retained as evidence.
- Rebased existing bitmap patch native paths to Android 11's `libs/hwui/jni/`.
  Its three-file applicability check passes. No new graphics behavior was invented;
  inherited workaround semantics still require review and hardware tests.
- Added restore, offline source checks, patch probe and host preflight scripts;
  pinned dependency manifests and an unbuilt Linux container recipe.
- User confirmed Fire OS 5.7.1.0, 12.33 GB internal capacity (16 GB SKU), separate
  30 GB SD card, CP4 lab on latest firmware, and full Home functionality required.

## Validation and limits

`python3 scripts/check_sources.py`: PASS for source pins, manifest paths, corrected
inheritance and six ARM/ARM64 graphics blob ELF headers.

`python3 scripts/probe_android11_patches.py`: saved independent applicability
results, including actual missing Android 11 bitmap paths and context failures.
The rebased bitmap patch passes. This is a partial source fixture, not a platform
checkout. It cannot validate module dependencies, compilation or runtime behavior.

`git -C sources/device-douglas diff --check`: passed.

`python3 scripts/preflight.py`: exit 2, expected; host is arm64 macOS, filesystem
is case-insensitive and free disk is ~42 GiB. RAM is 36 GiB.

Legacy kernel clone emitted case-collision warnings for netfilter headers/sources
and an rcutorture filename. Those apparent tracked modifications must not be
exported as development patches. Restore that repository on case-sensitive Linux.

No Android build, image generation, full repo sync, GApps download, APK download,
paid resource use, tablet connection, unlock, wipe, flash or physical test occurred.
The existing release ROM (~482 MB) was not downloaded. Inspection sources occupy
roughly 1.1 GB expanded before small source fixtures.

## Direction clarified after initial investigation

The user selected a current maintained Android kernel that moves with Android releases,
using the old kernel trees as hardware references. General-purpose tablet usefulness is
the primary goal; Crestron Home is one application requirement. Optional hardware-absent
features may be unavailable with accurate declarations. The prior old-kernel/intermediate-
Android progression is superseded. Updated README, maintenance direction, feasibility
conclusion and continuation notes to agree. No new porting/build/device work was started;
waiting for the user's next instructions.
