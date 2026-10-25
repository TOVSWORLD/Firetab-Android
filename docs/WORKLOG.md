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

## Crestron panel-mode scope

User added a separate question about native Crestron panel behavior and clarified that
the setup interface selects an application/use, then runs one app at a time. Official
TSW-70 documentation confirms this model. Added a panel-mode research track to the
maintenance document, distinguishing supported Android/web clients from an unverified
native-runtime port. Found official Android clients for Smart Graphics (Go) and
HTML5/Construct (ONE, documented Android 14+), plus Android browser Web XPanel support.
No claim that arbitrary native panel applications can run on douglas; no prototype,
firmware extraction, large download or device operation was undertaken.

## Crestron research completed after user authorization

- Verified the native single-selected-app model against TSW-70 documentation.
- Located the real public app-update manifest. Initial `70series` URL attempts
  returned 404; corrected `70-series` spelling using official release-note evidence.
- Checked archive sizes with HTTP HEAD and reported the approximately 79 MiB total
  before downloading HTML5 host, General Web and touchscreen Home archives.
- Preserved download/source metadata, hashes and extracted manifests under
  `evidence/crestron/`. APKs and full selected disassembly remain ignored under
  `work/crestron/`. No APK or native library was run or modified.
- Used installed Android SDK `apkanalyzer` and Java 25.0.2 for static inspection.
  Identified ARM32-only bundled native libraries, explicit loads of missing
  `cresstore_jsonJNI`/`SecureStorageJNI`, localhost signal transport, and General
  Web's signal bridge. These are observed dependency contracts, not runtime results.
- Public firmware manifest was readable and advertised `3.003.0021.001`; its exact
  firmware URL returned HTTP 404 on HEAD. An older tested URL also returned 404.
  Did not download a full PUF, BSP or emulator image. No emulator is configured here.
- Checked official Home/Go/ONE/Web XPanel deployment paths, native CH5 video
  architecture, Android lock-task APIs, Microsoft certification documentation,
  Zoom Android controller requirements, and current Crestron mobility-license status.
- Searched public repositories and inspected CrestronKeeper at pinned commit
  `6546f94d2864614c8cc5ca069fad0c39b3b75f69`; it targets the old mobile app and is
  a launcher/lifecycle reference, not a native-runtime port.
- Added `scripts/inspect_crestron_apps.py` to reproduce archive verification,
  manifest/native-library inventory and selected class inspection. Added
  `docs/CRESTRON-PANEL.md` with a project direction and gated native-service milestone.
- Retained the current-kernel/general-purpose Android objective. No OS/kernel
  implementation, physical testing, processor program change, account messaging,
  paid-resource provisioning or native compatibility prototype was performed.

## 2026-10-24 — GitHub project split and CI

User supplied TOVSWORLD/Firetab-Android and authorized publishing the starting repository.
Added two project entry points with separate scope, acceptance and validation records:
`projects/firetabs-android` and `projects/crestron-panel`. Shared evidence and tools retain
existing paths to preserve reproducible commands. These are repository projects, not
separate GitHub repositories or GitHub Projects boards.

Read actual Valethon AI guidance and CI checks as reference. Adapted verification,
anti-vaporware, canonical evidence, truncation detection, and focused blocking checks.
Added three read-only GitHub Actions jobs, offline checker and rejection-path tests.
No paid model service, privileged runner, large build/download or physical device action.
Firmware and panel execution stages remain explicitly `not_run`.

Published initial main revision `82c7fc4`; GitHub run 40158159017 passed all three
jobs and six rejection-path tests. Updated checkout to the pinned v6 revision after
reviewing the hosted runner warning about the v4 Node runtime.

## 2026-10-24 — Development-to-main release policy

User required main to be locked except for development-to-main releases. Created
`development`, enabled CI on integration pushes and added a metadata-only source-branch
check. Main requires release PRs from the same repository's development branch.
No PR code executes in the privileged-event workflow; token permissions stay read-only.
