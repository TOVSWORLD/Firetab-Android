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

## 2026-10-24 — Public contribution and release process

Added public contribution, conduct, governance, security, support and provenance docs;
architecture, setup, testing, troubleshooting, roadmap, decision and release guides.
Defined independent product SemVer streams and source-workspace tags, with a conditional
monthly first-Tuesday window and explicit stable/LTS acceptance. No release was published.

Implemented release-manifest checks and rejection tests; added tracked documentation-link
and form/taxonomy checks to Repository integrity. Created seven issue forms, CODEOWNERS,
release-note categories and monthly Actions dependency PR configuration. License selection
is awaiting the owner; external code/doc merge acceptance is explicitly held meanwhile.

Applied 27 labels, three milestones and eight bounded native parent/sub-issues.
Seed identities are recorded in projects/github-setup.json; the reconciliation script
preserves existing issue bodies and states. Enabled private vulnerability reporting.
Active tag ruleset 25808738 blocks updates/deletion for all three release tag prefixes.
No model service, full build, firmware upload or physical test was performed.

## 2026-10-25 — Actual GitHub Projects

The earlier split created folders and parent issues, not GitHub Projects. Created
FireTabs Android (#4) and Crestron Panel (#5), linked both to the repository, and
added project-specific issues plus shared repository tasks. Recorded board identities
and preserved them across metadata reconciliation. Public visibility awaits explicit
owner approval after automatic approval review rejected that separate visibility change.

## 2026-10-25 — Issue #5 maintained-kernel candidate/support audit

Inspected pinned Android 17 ACK, recent bengris32 MT8163 work (including an explicit
douglas DTS), its separate upstream submission and LibreEcho 6.1 source references.
Recommended the Android 17 / 6.18 ACK family with an exact LTS-integration candidate,
recording development/release-ref version differences rather than claiming latest
security coverage from the name. Added twelve source-anchored component records.

Captured 78 source/listing records plus three upstream license/notice records with hashes; 16 MT8163 binding-header paths are absent
at the inspected ACK pin. Reproduced a clang preprocessing failure at the first missing
clock header and recorded the actual command/error. Added offline source verification
and rejection tests to CI. No complete kernel checkout/toolchain/AOSP sync or paid
resources; no kernel compilation, image packing, APK execution or physical device actions.

Documented stock mt-boot vs PSCI/power sequencing, memory/boot-envelope concerns,
32-bit EL0/userspace distinctions, graphics/CDD gaps and the next minimal compile/resource
plan. Hardware validation records remain not_run; this closes an audit, not a port.

## 2026-10-25 — Issue #14 DT dependency closure and actual compilation

Resolved 26 real pinned DTS/header inputs (20 donor, six ACK); built dtc 1.8.1 in an
isolated workspace with pinned small bootstrap inputs. The unmodified source failed
on missing thermal constants. Two patches add the real include and correct memory
unit naming/cooling declarations. The patched tree compiles without diagnostics to
a 26,283-byte DTB; fdtget inspection verifies board identity and preserves explicit
512 MiB/PSCI donor assumptions. These are not validated physical hardware facts.

Added a reproducible offline build/inspection command, Linux CI compilation and input/
artifact-integrity tests. No compiled DTB is committed or published. Kernel and device
validation stages stay not_run. A separate schema attempt used incomplete binding
context and is explicitly not passed despite the validator's zero exit code.
The tool-specific SWIG incompatibility was fixed by a compatible pinned dependency,
not by suppressing C errors. No full kernel/AOSP download or physical device action.

## 2026-10-25 — Issue #16 generic ACK compiler baseline

Reconciled closed issue #9's stale status and moved Android root #2 and task #16
into progress on the Android board. Added an isolated Linux CI experiment for
ACK d9318bdb4c34e8b2d997b4f67ced56b120b22b87 with Ubuntu LLVM 18.
The source's scripts/min-tool-version.sh requires LLVM >=15; Kconfig.ext is an
existing intentionally empty upstream placeholder, so no source stub is added.
Uses ARM64 defconfig, not GKI/douglas config. Source fetch shallow/no tags,
3 GiB post-transfer budget, 15 GiB free-disk and 7 GiB RAM gates, 60 minute timeout.
Runner compiler/package versions are recorded, not hermetically pinned. The
experiment logs the resolved config, ELF architecture, artifact sizes/hashes.
No boot image packaging, upload/release or device access. Compilation outcome
must be read from CI before marking any validation gate complete.

First Linux run 40168107152 stopped in host-tool preflight: pahole absent.
No kernel source was fetched. Added Ubuntu dwarves/libelf-dev/libssl-dev host
packages with installed versions logged; apt repositories remain host-dependent.

## 2026-10-25 — Start issue #18 source integration

#16 kernel compile is still pending; it remains open. Started #18's independent
source comparison on kernel/mt8163-clock-port, based on the unmerged #17 branch.
Retrieved 15 pinned source/API files (98,463 decoded bytes). Prepared nine real
clock drivers and eleven binding headers, donor build wiring, and lifecycle/factor
registration corrections documented in the overlay README. Added a clock compile
mode that verifies seven enabled symbols, builds affected objects with W=1 and
then a full generic Image. No clock compilation or hardware pass is yet claimed.
The Linux run uses the previously reported per-run 3 GiB source budget and host
resource gates; no full Android checkout, paid host or device access is involved.

Clock run 40168938776 reached real compilation and failed on missing direct-update
mux macros/ops and flags-selectable composite initializer. Backported the donor's
actual direct-update operations as a minimal ACK patch, leaving existing ACK ops
and allocation implementation intact. Preserved audio composite flags=0 rather
than silently substituting ACK's rate-propagating macro. Rebuild pending.

Generic ACK compile run 40168232549 succeeded: ARM64 4 KiB Image 41,286,144
bytes, vmlinux 440,617,560 bytes; ~16 min 34 sec including fetch/config/build.
Recorded result metadata and recovered the full config from CI logs; its SHA256
matches the compiler-run checksum. No compiler warning/error lines were found.
This generic config does not enable Android Binder/SELinux; it is not the target
Android/douglas config and does not advance that kernel validation record.
PR #17 merged to development. Full matching binding/schema work is now tracked
explicitly in #27; driver/configuration work in #18–#25. Exact transfer and
expanded checkout sizes were not emitted and remain unknown.

Rebuild 40169238323 compiled all nine MT8163 clock objects with W=1 and advanced
into the full kernel build before being superseded by the evidence-recording
commit. Full Image linkage with the overlay is still pending. A git-apply blank
line warning in generated Kconfig wiring was fixed; no warning flag was disabled.
Added per-PR concurrency cancellation to avoid duplicate obsolete builds.

## 2026-10-25 — Clock reference follow-through

Added a bounded source audit of nine provider files and 102 literal DT clock
references. Provider header/ID checks pass; three literal HDMI parents remain
unresolved and documented, not hidden with aliases/dummy clocks. This is not a
schema/register/runtime validation. Heavy kernel experiments now run on PR open,
ready-for-review or explicit workflow_dispatch, rather than on every documentation
push. Source-affecting updates require an explicit rebuild at the new revision;
repository validation continues on every PR update. Run 40169479688's clock source
is unchanged by this audit/documentation/workflow-trigger update.

## 2026-10-25 — Prepare pinctrl/EINT object probe (#19)

While the #18 full kernel compile runs, prepared the next source integration as
a separate stacked change: three unmodified donor files and real Kconfig/Makefile
wiring. ACK common APIs/data fields exist; donor declares 155 pins, six EINT
ports/169 AP interrupts/64 debounce entries. These are not hardware measurements.
A bounded Linux W=1 object-only probe will record actual ELF/hash/config results.
Full Image linkage, legacy routing comparison and schema/runtime tests remain
required. No pinctrl compilation pass is claimed before CI executes.

Pinctrl reference audit: all 155 donor pin names, literal mux functions and EINT
mappings match the pinned legacy Git object; 15 unique captured modern DT mux
references map to descriptor entries. Original legacy table and hashes retained.
This is a source comparison, not register/schema/electrical validation.

Pinctrl object run 40169973832 passed with W=1 and zero compiler warning/error
lines. ELF64 AArch64 object SHA256 recorded in evidence/pinctrl-port/object-result.json.
Git storage measured 291,136 KiB; source including Git 2,066,692 KiB. Transfer bytes
remain unknown. Source is unchanged by the subsequent audit/evidence/CI additions.
Added both bounded reference audits to ordinary repository CI. #19 remains open:
full Image integration, complete schema/register review and all runtime evidence
are still pending.

Expanded pinctrl audit: drive groups (3), pin-drive entries (119), special pulls
(46) and Schmitt entries (57) match legacy. The donor adds one input-enable entry
for GPIO87/MSDC2_DAT0, 0xcf0 bit 4; retained as an unvalidated donor delta and
recorded explicitly. No register value was changed to force an audit pass.

Added explicit workflow_dispatch mode clocks-pinctrl for full combined Image
integration after the object probe. It applies both pinned overlays, verifies
PINCTRL_MT8163=y and all clock symbols, compiles both directories with W=1 and
links Image/vmlinux. This is still a generic config, not a douglas boot claim.
## 2026-10-25 — Begin diagnostic boot-contract investigation (#21)

Captured pinned legacy runtime-memory readers and ACK PSCI implementation.
ACK supports old explicit-ID arm,psci as well as version-probed bindings; the
legacy vendor MTCMOS sequence remains a separate unresolved delta. Both legacy
and donor source DTs say 512 MiB; runtime DRAM/mblock inputs and actual loader
fixups must be resolved rather than guessing a RAM replacement. Recorded reserved
region discrepancies and a staged diagnostic/log/recovery plan. Inspected amonet
source only; no unlock/helper/device operation or image packing performed.
#21 remains open pending actual firmware/memory/loader and recovery evidence.

Clock Image run 40169479688 succeeded at 07:09 UTC, about 36 minutes including
setup/fetch/object/full build, with no compiler warning/error lines. Actual
AArch64 Image is 41,351,680 bytes; SHA256 and vmlinux/config metadata recorded in
evidence/kernel-compile/clock-image-result.json. Clock source is unchanged by
the later audit/documentation update. PR #26 merged to development. Schema #27
and parent resolution #29 remain open; no target boot/runtime gate is promoted.

## 2026-10-25 — Local boot image inspector (#32)

Implemented a regular-file-only, read-only header-v0 layout/hash/partition-fit
inspector supporting #21. Rejects ambiguous formats, malformed pages, oversized
or truncated input; counts unclassified tail bytes. Does not decompress, extract,
pack, access device nodes/USB or claim signatures/bootability. Ten synthetic
boundary/rejection tests added; 31 total tests pass. No real stock image inspected.

## 2026-10-25 — Combined clock/pinctrl Image passed

Run 40170429213 at c61bc28 completed at 07:26 UTC (~38 minutes): full AArch64
Image 41,363,968 bytes, with clock and pinctrl objects compiled under W=1 and
zero compiler warning/error lines. Result/hashes and recovered full config are
in evidence/pinctrl-port; config hash matches CI output. Later branch updates
are evidence/docs/CI/base synchronization, leaving these driver sources intact.
PR #28 refreshed against development for required checks; no policy bypass used.
No douglas boot, Android configuration, schema or hardware pass is claimed.
