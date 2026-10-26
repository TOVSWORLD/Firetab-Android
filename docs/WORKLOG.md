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

## 2026-10-25 — Prepare #20 PMIC/power object integration

Prepared a minimal MT8163 wrapper/power-domain patch against actual pinned ACK
files. Wrapper donor differences are MT8163-specific. Power core keeps ACK's
implementation and imports only MT8163 include/match data and bus-protection
masks, excluding unrelated hardware-voter/SMC changes from donor 7.0. Eight-domain
header/binding retain donor licenses. Static wrapper register-offset comparison
against pinned legacy header is recorded; runtime sequencing is unverified.
Added bounded W=1 object probe; compilation result is not yet claimed.

Added a reproducible PMIC wrapper register-offset audit to ordinary CI; 79 shared
named offsets match the pinned legacy header. No initialization transactions or
power transitions are executed. This audit addition leaves probed driver source
unchanged from the initial #30 commit.

Power object run 40170813712 passed: actual wrapper and common power-domain
objects are AArch64 ELF, W=1, zero compiler warning/error lines. Hashes and
measured source/Git storage are recorded in evidence/power-port/object-result.json.
Full Image integration, binding dependencies and runtime power sequencing remain
open on #20. This does not advance any Android/douglas runtime validation gate.
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

Added explicit providers workflow mode for the next full Image integration:
clock, pinctrl, PMIC wrapper and eight-domain controller candidates together.
Checks all resolved config symbols, compiles each affected object set with W=1,
then links the full generic Image. Same existing resource gates; no Android or
bootable device package is produced. Results pending until actual CI completion.
## 2026-10-25 — Console/MMC reuse investigation (#22)

Captured exact ACK UART/MMC drivers and schemas (133,433 decoded bytes). Prior
successful Image run 40170429213 actually compiled both built-in drivers;
compiler excerpts and configuration hash are retained. Donor fallbacks and
clock names match driver interfaces, while voltage/timing/DMA and physical log
capture remain unverified. ACK schemas do not list the MT8163 compatibles: an
explicit #27 follow-up, not a driver or hardware validation pass. No new kernel
build was launched to duplicate already-recorded compilation.

## 2026-10-25 — Full ACK binding corpus diagnostic (#27)

Retrieved the exact ACK bindings archive: 3,275,172 bytes, 5,186 YAML files,
SHA256 4d1108f17127afcb03d3f1b45a3721195572c8048078ebe821eb0edb94d1e526.
Added bounded/hash-verified archive recipe and full-context wrapper. Actual run
with dtschema 2026.9 reports 36 validation errors and 61 unmatched-schema entries.
Both upstream tools return zero despite diagnostics; wrapper returns 1 and
passed=false. One upstream Gunyah YAML file fails parsing and is preserved, so
this remains provisional corpus processing, not a complete matched schema pass.
Logs/structured errors expose real PMIC/interrupt-node mismatches and compatible
coverage gaps. No diagnostics suppressed and no hardware test performed.

## 2026-10-25 — Narrow PMIC DT structural fix (#27)

Added a separate candidate renaming three PMIC child nodes to the pinned binding
names, retaining labels/compatibles and all properties. DTB compiles without
diagnostics: 26,275 bytes / 119b6666a3caf217675d5aead3e9b0e0b21287d3e21f9d36e7d047f26698eddf.
Binary comparison confirms identical 880 property values across 186 nodes after
only allowed path substitutions. Full-context validation changes 36->34 errors,
61 unmatched unchanged, zero added diagnostic signatures; still passed=false.
Did not add domain cells to the PMIC shutdown node: reviewed driver provides a
sys-off handler, not genpd. Stored source evidence and retained this diagnostic
for semantic review. Added four comparison rejection tests; 35 total tests pass.

## 2026-10-25 — Full provider Image succeeded (#20)

Run 40173436578 at e4e4468 completed 08:13 UTC (~37 min), with real clock,
pinctrl, PMIC wrapper and power-domain objects built W=1 and full Image linked.
AArch64 Image 41,363,968 bytes / SHA256
8b8db531704f2f895e752ba1e22f1b6920b85426e1768a37730041f695afb39e.
Zero compiler warning/error lines. Config hash equals the retained pinctrl
combined config; provider source changes are real and Image/vmlinux hashes differ.
Result metadata retained. This generic configuration has no appended board DT,
qualified loader/ramdisk contract or hardware/Android runtime validation.

## 2026-10-25 — Prepare user-run read-only stock facts (#37)

Added explicit-serial/wrong-device refusal, fixed metadata command collection,
cmdline allowlisting, binary DT property handling, no serial/stderr persistence,
and enforced pipe/runtime limits. Six fake/host-only tests added; 41 total tests
pass. No real device transport executed. Checked installed SDK adb version only:
36.0.2-14143358 on shared Mac; this host-only command does not query devices.
Documented connection/debugging authorization separately from collector scope.
Actual stock facts remain needed for #21; no boot/test package is ready yet.


## 2026-10-25 — Classify PMIC shutdown schema selection (#27)

Traced the missing domain-cells diagnostic to the pinned generic power-domain
schema's node-name selector. The MFD binding itself calls the sys-off child
power-controller but does not require cells. Preserved the generic schema with
source hash and documented the selection overlap, MFD-provided memory resource,
and sys-off driver semantics. No permissive schema or DT change; counts remain
34 errors/61 unmatched. Actual stock-data collection still awaits the user's
computer choice; no tablet transport or settings change performed.

## 2026-10-25 — Sysirq node-name structural fix (#27)

Added isolated sysirq-node-name candidate on the PMIC candidate, preserving all
interrupt properties and compatibles. Clean DTC result 26,279 bytes / SHA256
78fd34cbe0c129da23dd2e296be0db9180e7d8b464e719b59304f09d01456bea.
Actual binary comparison retains 880 values across 186 nodes, permitting only
four reviewed path renames. Schema run removes one naming diagnostic with none
added after path normalization: 33 errors/61 unmatched remain, passed=false;
upstream YAML parse issue remains. Added CI compilation/property comparison and
rejection tests; 44 local tests pass. No physical device access or firmware pack.

## 2026-10-25 — Minimal diagnostic userspace experiment (#41)

Created separate freestanding AArch64 /init and deterministic newc/gzip builder.
Only console output, bounded kernel metadata reads, read-only virtual mounts and
controlled idle; no block nodes/storage mounts or reboot interface. Local Apple
Clang cross-object compile passes strict warnings; no local Linux linker present,
so full ELF/archive compilation is delegated to the existing Linux CI toolchain.
47 unit tests pass, including ELF rejection and actual archive metadata/content
parsing. Build is not a firmware package or a boot/runtime result. No tablet
transport or physical changes. Stock loader/memory/recovery gates remain #21.

Linux CI run 40181473575 at cb82cb8 passed the static ELF/archive build with
Ubuntu Clang 18.1.3; ELF checks confirm AArch64 ET_EXEC with no interpreter or
dynamic segment. Gzip/newc archive 1,248 bytes, SHA256
8d68234297e9ed50e025cb321d066b2d4ff8a4a09c57a654e09d9467c10e6ff4.
Exact command/compiler/source and artifact hashes retained in
 evidence/diagnostic-initramfs/compile-result.json. No runtime execution occurred.

## 2026-10-25 — Narrow local UART binding proposal (#27/#22)

Added opt-in mt8163-uart-proposed binding profile, preserving the original ACK
profile. Proposal adds only the exact MT8163 first compatible with required
MT6577 fallback, backed by pinned donor DT and matching ACK driver source.
Original schema/patch/proposed schema hashes checked before applying in a fresh
corpus extraction. Meta-validation clean; full-context diagnostic delta removes
four compatible errors and four unmatched entries without added signatures:
29 errors/57 unmatched remain, upstream YAML parse issue remains, passed=false.
49 tests pass, including real isolated patch application and rejection of changed
original schema input. No compatible deletion, permissive schema or hardware claim.

## 2026-10-25 — Restricted diagnostic kernel compile setup (#44)

Prepared separate diagnostic fragment and fail-closed resolved-config check.
Requires implemented providers/UART/initramfs, disables block/storage/network,
USB/display/audio/watchdog and power-policy subsystems. Adds deterministic gzip
Image size/hash reporting without packing firmware. Provider workflow defaults
to this integration mode; resource gate unchanged and reported before starting.
53 local tests pass including rejection of modular storage and missing console.
No configuration/compile success claimed until actual Linux CI resolves/builds
it; stock memory/loader/recovery/logging remain #21, no tablet access occurred.


## 2026-10-25 — Diagnose hidden BLOCK configuration prompt (#44)

Actual run 40183576290 at 14d1b21 failed policy check before Image compilation:
BLOCK resolved y. Pinned block/Kconfig makes its bool prompt conditional on
EXPERT, with default y; generic defconfig has EXPERT=n. Captured source/hash and
failure evidence. Added EXPERT=y, retained strict storage-disabled check, improved
all-mismatch diagnostics and rejected-config logging. Rebuild required; no
kernel/boot result claimed, no tablet access or firmware packing occurred.


## 2026-10-25 — Remove ACPI idle-policy selector (#44)

Second actual run 40184459476 resolves storage disabled but rejects CPU_IDLE=y
before Image compilation. Captured the rejected config from CI stdout and pinned
Kconfig source proving ACPI_PROCESSOR -> ACPI_PROCESSOR_IDLE -> CPU_IDLE. Fragment
now disables ACPI/processor idle policy for the donor-DT experiment; the strict
CPU_IDLE=n gate remains. No ARM_PSCI_FW/DT/stock-loader changes. Corrected build
still pending; no physical tablet access, firmware packing or runtime claim.


## 2026-10-25 — Restricted diagnostic Image compile succeeded (#44)

Actual run 40185547611 at 3bf1010f3f007bd3fd202da30b3483ca12933531 passed
in 23m16s with zero compiler warning/error lines. Resolved strict policy passes;
real clock/pinctrl/power objects W=1 and full Image/vmlinux compiled. Retained
complete resolved config reconstructed from CI and matched original SHA256
f5da34605d2ebc5f279269e59d56027acfefbfb346819d945c7dd7a6c3209eed.
Image 28,576,256 bytes; Image.gz 9,187,928 bytes / SHA256
a6ecd7444c9ffc8f47c4954902b23e15fd1f861b924ae9a082157652dc2ab1c1.
Report/log checksum and policy evidence retained. No DT/ramdisk integration,
firmware packing or published test package; stock #21 prerequisites and #27
schema validation remain. No tablet access or runtime result claimed.

## 2026-10-25 — Bounded stock OTA model/boot-image inspection (#46/#21)

Found discovery index HD8/HD10 5.7.1.0 links swapped; verified actual package
identity from CRC-checked properties, rejecting suez/KFSUWI and selecting
candidate douglas/KFDOWI/MT8163 build659664620. Marketing-version/installed-build
match remains unverified (embedded Fire OS property says5.3.7.3). Initial two
metadata probes used204800 bytes; reusable opt-in extractor used8612864 bytes,
within20MiB response-body budget, rather than whole907705758-byte OTA. Boot.img
8689664 bytes / SHA2568982fa50193acc764be69ee51027ee92e83614cee4b8235b07439d1f9e2db363.
Existing inspector confirms2KiB pages/header fields; bounded gzip-prefix check
finds AArch64 magic behind512-byte kernel prefix. Unclassified2KiB trailer and
all signatures remain unverified. Report/ranges/hashes retained, binaries ignored.
59 tests pass with synthetic archives/fake transport. No archive execution,
firmware packing, tablet access or physical change; no test package ready.

## 2026-10-25 — Actual candidate DTB memory/PSCI evidence (#21)

Added bounded local wrapped-gzip/concatenated-DTB inspector. Actual candidate
kernel gzip decompression16584856 bytes; suffix is exactly two DTBs pre_evt/hvt
(82277/82641 bytes), hashes and selected facts retained. Both corroborate static
512MiB memory, legacy explicit-ID PSCI and CPU0 mt-boot, plus all legacy firmware
and log reservations omitted from newer donor. Header reservation maps empty;
body reservations and dynamic CONSYS remain authoritative static declarations,
not runtime measurements. Collector now reads individual DT version property;
only fake transport tests ran. 63 tests pass, including gzip cap/truncation and
invalid wrapper/DT suffix rejection. No downloads, firmware changes, packing or
device access; #21 runtime/loader/log/recovery gates remain open.

## 2026-10-25 — Prepare generic ARM64 VM runtime test (#49)

Added bounded QEMU virt8.2/Cortex-A53/one-CPU/512MiB diagnostic userspace runner,
using existing restricted kernel/initramfs inputs. No disks/network/host shares,
software TCG,120s/2MiB console caps, required init/mount/metadata/idle markers and
5s continued execution; reject panic/read errors/early exit. Dependency installer
requires disposable Linux GitHub runner and <=200MiB APT package archive plan
before install; package versions logged. Existing ACK build resources unchanged.
68 local tests pass, including incomplete/panic/error console rejection and
package gate. Actual VM execution still pending; no douglas boot/hardware/Android
runtime claim. No tablet access, firmware packing or paid provisioning.

## 2026-10-25 — Generic diagnostic execution passed (#49)

Reviewed successful CI 40193403656 at project 2fc0da6d65371783c13bfd800b3a1630f7fa3511,
pinned ACK d9318bdb4c34e8b2d997b4f67ced56b120b22b87. QEMU virt8.2/Cortex-A53
ran restricted kernel plus unchanged diagnostic initramfs: proc/sysfs mounted,
four metadata reads completed, idle survived five seconds. Exact hashes/command,
ARM64 header and CI-log hash retained in evidence/qemu-diagnostic. All routine
checks also passed; 68 tests. Generic execution only; #21 physical loader/memory,
recovery and log qualification remain open. No tablet access or firmware packing.

## 2026-10-25 — Resolve conditional Image placement mismatch (#21)

Compared actual executed Image header with model-verified candidate boot header
and official ARM64 boot ABI. New text_offset=0 requires 2MiB-aligned entry; old
0x40080000 field is misaligned if honored unchanged. Recorded arithmetic and
pinned amonet LK source hashes; payload is not complete loader evidence and
MISC transitions can write persistently. No chosen addresses, firmware assembly,
helpers executed or tablet access. Actual loader relocation remains unresolved.

## 2026-10-25 — Include loader version identifiers in stock facts (#21)

The read-only collector omitted three preloader/LK/TEE version properties used
by pinned amonet step-1.sh. Added only those fixed names and internal Fire OS
version for later installed/candidate matching; serial remains excluded. Fake
transport verifies preservation and no serial query. No real ADB/device access
or helper execution. Property values alone do not authenticate loader binaries.

## 2026-10-25 — Audit diagnostic RAM logging gap (#21/#22)

Resolved config has PSTORE_RAM=m with console/pmsg disabled, while minimal init
cannot load modules. QEMU success is live PL011 output, not retained RAM logs.
Pinned legacy source has a custom multi-stage buffer and optional eMMC write
path; no wholesale logging backport or reservation reuse is justified yet.
Recorded exact hashes and requirements for an isolated backend/retention/reader
or qualified UART path. No config/device changes or helper execution.

## 2026-10-25 — Reject CRLF diagnostic error lines (#49 follow-up)

Found VM verdict parser matched UNAVAILABLE/READ_ERROR only between LF bytes;
serial CRLF translation could bypass that fatal override in an otherwise
complete transcript. Normalize CRLF only for verdict parsing, preserving raw
console bytes and hashes. Regression exercises both errors with LF and CRLF.
No kernel/initramfs/config changes, new heavy build or tablet access.

## 2026-10-25 — Reproducible offline Image placement audit (#21)

Added report-based auditor with cross-report stock hash checks, exact raw/decoded
new header consistency, bounded local JSON input and uint64 arithmetic guards.
Actual old text_offset=0x80000 aligns at the old address; new offset=0 does not.
Retained exact result plus input/auditor hashes. No replacement address selected,
loader behavior authenticated or firmware packed. All 72 tests pass.

## 2026-10-25 — Harden legacy ADB metadata reads (#21/#22)

Classify known remote shell error prefixes as unavailable even when old ADB
returns host status0; do not retain error text. Traverse the device-tree symlink
with a trailing slash and add proc/version for systems without uname. Fake
transport covers status-zero permission/missing-command failures and privacy
filtering. 73 tests pass. Device-specific evidence remains private locally.

## 2026-10-25 — Publish owner-approved sanitized runtime evidence (#21)

Owner explicitly approved sanitized publication. Selected firmware/build/loader
identifiers, runtime DT memory properties and provenance hashes reviewed; no
hardware serial, household data, raw logs or full local report published. Actual
runtime hvt DT reports two banks totaling1430MiB; installed build identity agrees
with inspected OTA candidate, not binary/signature equivalence. PL7/LK3/TEE262
exceed pinned helper6/2/259 maximums. No helper/device operation performed here.

## 2026-10-25 — Decode actual runtime memory handoff (#58)

Implemented strict offline decoder for big-endian DT reg and native little-endian
ARM64 vendor structs; pinned source and compiler layout retained. Actual ranks
total1536MiB, usable reg/mblocks agree at1430MiB, excluding106MiB at top. No
ownership inference or DT enlargement. Five malformed/actual-data test groups
added, all78 tests pass. Next: source-audit excluded/reserved intervals under#21.

## 2026-10-25 — Reservation interval/source audit (#60)

Added reproducible static-vs-runtime inventory and boundary tests. Four fixed
regions total5.3125MiB inside usable banks and have zero overlap with106MiB top
exclusion; dynamic CONSYS location unknown. Pinned memory/ATF/display consumers
identify missing tee/lca/framebuffer runtime fields; accounting equality check
is disabled. No ownership inferred. Exact residual remains#21; next independent
task#27 upstream schema parse/selector failures. All81 tests pass. No device
queries, firmware assembly, helper execution, downloads or paid resources.

## 2026-10-25 — Opt-in corpus YAML lexical repair (#62)

Three Gunyah indentation tabs replaced only in hash-locked opt-in extracted
corpus. Original preserved; no semantic relaxation/suppression. Actual full
context still29errors/57unmatched, passed=false/exit1. YAML parser issue removed,
but schema now explicitly ignored for invalid compatible shape; separate meta
errors retained. All82 tests pass. Next#27 semantic/schema-selector repair.

## 2026-10-25 — Exact PMIC sys-off/domain selection fix (#64)

Opt-in hash-locked generic-domain selector excludes only MT6323 sys-off compatible;
all original domain constraints and MFD binding unchanged. Actual meta-validation
clean; YAML/jsonschema controls preserve missing-cells rejection for real domains
and MFD wrong-compatible/unknown-property rejection. Full-context delta removes
one false domain-cells requirement, adds none:28errors/57unmatched remain.83
unit tests pass. Next#27 remaining schema failures; no device/hardware claims.

## 2026-10-25 — MT8163 sysirq binding coverage (#66)

Pinned ACK/legacy fallback driver evidence retained. Opt-in enum adds MT8163
first compatible requiring unchanged MT6577 fallback; no other constraints
changed. Meta clean; actual processed tuple negative controls reject wrong/
missing/extra fallback. Full delta removes2diagnostics/adds0, now27errors plus
56unmatched, overallfailed.84 tests pass. Next#27 timer or RDMA selector work.

## 2026-10-25 — MT8163 timer binding coverage (#68)

Source-backed exact first-compatible enum proposal requires existing MT6577 GPT
fallback. Pinned ACK/legacy source hashes retained. Meta clean, processed tuple
negative controls reject invalid fallbacks. Actual full delta removes2/adds0:
26errors/55unmatched remain, overallfailed.85 tests pass. Next#27 display-RDMA
node name/generic DMA selector conflict. No tablet access or firmware assembly.

## 2026-10-25 — Display RDMA node-name candidate (#70)

Canonical rdma@ name prevents generic DMA-provider misselection. Compiled alias
path rewrite explicitly checked; other879 property bytes across186nodes unchanged
after reviewed path substitutions. Clean DTC26259B hashc1824152...; CI fourth
variant added. Full delta removes1/adds0:25errors/55unmatched remain.88 tests
pass. No cells invented, schema relaxed, hardware tested or device accessed.
Next#27 RDMA compatible coverage/remaining boot-relevant gaps.

## 2026-10-25 — Storage/UART-DMA compatible coverage (#72)

Pinned ACK fallback evidence retained; two strict opt-in compatible proposals
keep all other constraints. Meta clean; processed controls reject invalid pairs
and preserve existing SoCs. Full delta removes8/adds0:21errors/51unmatched,
overallfailed.89 tests pass. No device/driver/DT/firmware or hardware claim.
Next#27 remaining peripheral fallback or display binding gaps.

## 2026-10-25 — Strict peripheral fallback coverage (#74)

Four opt-in compatible profiles preserve all other constraints; pinned fallback
drivers/source hashes retained. Meta clean, processed controls pass. Actual full
delta removes12/adds0:15errors/45unmatched remain, overallfailed.90 tests pass.
No bus/ADC/RNG hardware/security qualification. Next#21 cached loader/recovery
alternative audit to advance the physical diagnostic boot blocker.

## 2026-10-25 — Loader/recovery alternatives audit (#76)

Source/hash/line inventory distinguishes stock recovery, handshake, old software
unlock, BootROM chain, newer preloader exploit and post-unlock custom loaders.
Newer fork has explicit douglas target but requires older vulnerable preloader;
old minimal chain still modifies GPT/RPMB/preloader/boot. No qualified safe route
yet. Offline assessor and3tests added;93tests pass. Next bounded OTA preloader/LK
static inspection planned383684compressed bytes plus metadata, no fullOTA.
No helper/payload compiled/executed, reference modified or tablet accessed.

## 2026-10-25 — Bounded build-matched loader inspection (#78)

Explicit loader whitelist/model/build gate,2MiB transport body cap,1MiB entries
and capped static marker/header reports added. Actual452322B fetched; preloader
139352B/LK485552B hashes retained, binaries ignored/notexecuted. Heuristic marker
absent; exploitability remains unknown. LK wrapper485040B payload equals file
minus512.98 tests pass. Next#21 static entry/format audit, no tablet operations.

## 2026-10-25 — Exact loader container/address audit (#80)

GFH declaration gives preloader code view0x201000..0x222c34; LK prefix uses default
address sentinel, so old4bd00000base is unverified. Strict hash/bounds parser and
source-based hypothetical patch windows retained with compatibility=false. Old
helper donor binaries absent in pinned git.102 tests pass. Next#21 stock LK
control-flow analysis using existing LLVM, no new dependency or device operation.

## 2026-10-25 — Actual LK K64/secure-monitor instruction trace (#82)

Startup instructions substantiate linked4bd00000base. Checked Thumb chain passes
entry-slot/current-r5/0/1 through K64-labelled wrapper to ARM SMC#0 service82000200.
Exact offsets/bytes, PC-relative references, disassembly and hashes retained.
r5 lineage, upstream header/decompression producer and monitor behavior remain
unverified. Non-loadable static-analysis object only;106 tests pass. Next#21
trace entry-slot producer. No code/firmware execution, new download or tablet IO.

## 2026-10-25 — Header entry/decompression producer (#84)

Exact cached LK static trace joins three GOT references to header-pointer global
4bd841b0. Selected header+0xc supplies entry and gzip output; K64 checks512KiB
alignment and loops on failure; decompression call supplies28MiB capacity. Modern
diagnostic image_size equals that capacity (no margin, not success/failure proof).
Selected bytes/disassembly/hashes and mutation negative controls retained. No
firmware execution, downloads or tablet IO. Next: staging/input length and DT
handling before considering any test package; recovery remains unqualified.

## 2026-10-25 — Selected LK compressed input/DT sizing (#86)

Retained exact LK instruction windows connect staging45000000, prefix-present
read adjustment-512, backward FDT scan/suffix rounding and separate inflate
input/output lengths. Conditional stock DT-match arithmetic retained without
claiming actual selection. Stock gzip output16584856 leaves12775272 of28MiB
capacity. Clarified image_size is runtime memory requirement, not decoded file
length; modern actual byte length remains unmeasured here. No device/firmware
execution/download. Next: measure cached modern Image output versus reserved
runtime footprint; recovery and physical boot remain unqualified.

## 2026-10-25 — Exact keypad fallback schema coverage (#90)

While PR89's generic compile runs, independently validated cached donor keypad
fallback against pinned ACK driver/schema. Added opt-in single-enum binding
proposal with hashes and six processed-schema positive/negative controls.
Full-corpus diagnostic count60→58 (14validation/44unmatched), zero new diagnostics;
overall still fails, as expected.113 offline tests pass on this branch (PR89
measurement tests remain on that separate pending branch). No hardware DT/node
status change, device access or hardware claims. Parent27 remains open; next
independent binding candidate is efuse fallback coverage after source inspection.
## 2026-10-25 — Actual modern Image length evidence (#88)

Recovered original generic run40193403656 size/hash lines from1.47MB CI log:
Image28576256bytes, gzip9187924bytes, rawSHA08df8a73166bf5bd3a0fefdd9394d8f5d54b2822255e728c2c3873f2e1c56909.
Raw file fits selected28MiB output capacity with783872bytes margin; declared
runtime image_size is separately28MiB. Historical binaries remain absent, so no
new historical gzip round trip claimed. Added bounded single-member measurement
and exact Image comparison to existing diagnostic build/VM reports;115 offline
tests pass. Integration CI uses existing reported kernel resource gate. No tablet
IO, firmware assembly or physical destination. Recovery/entry alignment and
secure-monitor qualification still block a user test package.

## 2026-10-25 — Measurement integration validated; ordered PR merges

PR89 headb1f3c1fc2652f249db744f8997021ea7d7649fdb passed all required checks and
actual compile/QEMU run40250576526 (24m2s CI job). New rawSHA16c9e5e6947231070888dcba5467b79df20ef6eee060edd86b36ec6fd336bcb3,
28576256bytes; gzip9187928bytes, round trip verified; capacity margin783872bytes.
QEMU markers/read-only proc/sysfs reads and5s idle passed in5.94s. Retained exact
report plus full1.47MB log hash in evidence/image-measurements/validated-runtime-result.json.
Build hash differs from historical output; no bit-identical rebuild claim.
PR89 merged; issue88 closed. Merged development into keypad PR91, explicitly
preserving both appended WORKLOG sections, then added this validation evidence.
Tablet boot/hardware/app stages remain untested. Next merge91 after refreshed
required checks; independent efuse scope92 remains queued.

## 2026-10-25 — Generic efuse compatible and calibration constraints (#92)

Audited cached pinned ACK generic efuse driver against donor calibration cell.
Generic match has no MT8186 speedbin postprocessing; legacy fixed cells enabled.
Added opt-in exact tuple proposal preserving all other constraints. Nine actual
processed-schema controls pass; full-corpus diagnostics58→56 (13validation and
43unmatched), zero additions. Overall validation remains failed/exit1;117 offline
tests pass. Source/patch/schema hashes and complete delta retained. No calibration
correctness, efuse IO or hardware support claimed. Parent27 remains open. Next:
return to21's secure-monitor/CPU handoff source contract before more display work.

## 2026-10-25 — CPU startup / monitor source contract (#94)

Compared cached legacy mt-boot/PSCI and ACK CPU ops plus stock/donor DT contracts.
Legacy wrapper adds host-side MTCMOS power sequencing after PSCI; ACK DT table
has no mt-boot method. ACK still supports explicit legacy PSCI IDs, so old DT
format alone is not a hard blocker. Donor v0.2 ARM64 CPU_ON C4000003 differs from
stock explicit84000003; monitor acceptance remains unknown. LK primary82000200
is separate. Source hashes/line anchors and mutation controls retained. Legacy
reference not binary-matched to stock. Proposed primary-only diagnostic limit
requires boot-CPU path audit; no device/SMC/firmware execution. Next bounded task:
trace boot-CPU versus secondary setup and maxcpus=1 effects before choosing DT
CPU changes. Physical recovery/logging and hardware/runtime gates remain open.

## 2026-10-25 — Isolated primary-only DT/source experiment (#96)

Traced pinned setup_arch early parsing→PSCI discovery→boot-CPU ops/enumeration.
maxcpus=1 alone still probes PSCI and prepares secondaries. Added opt-in compiled
DT-only experiment: PSCI node disabled, chosen nr_cpus=1 maxcpus=0; preserves all
186nodes/880original properties and default experiments. Compiles cleanly to
26324bytes/SHAef23af15f7136613a98b450f3d1db7c860f581024d194e88e2ef8c3116f2eb43.
Source/hash guards and full semantic comparison/negative controls retained.
Loader preservation, boot MPIDR, other firmware paths, donor RAM and physical
boot remain unverified. No firmware packing/device/SMC/helper execution. Next:
trace actual LK bootargs rewriting before treating the limits as effective.

## 2026-10-25 — Actual LK chosen/bootargs replacement trace (#98)

Exact cached LK static trace connects file-backed command buffer4bd74cb8 and
header+40 format input to selected FDT bootargs write. Writer usesstrlen+1,
resizes existing property, sets new length and copies new buffer; DT bootargs
alone are not a preservation guarantee. Initial static150-byte buffer lacks
diagnostic limits; runtime mutations/all boot modes remain unqualified. Retained
instruction/call/string/hash evidence plus126 passing offline tests and mutation/
argument negative controls. No PSCI-status preservation or physical boot claim,
firmware/helper execution or tablet IO. Next: sanitized effective command-line/
CPU-count diagnostic reporting, keeping loader/recovery/logging gates open.

## 2026-10-25 — GCE fallback binding coverage (#102)

While PR101 actual init/kernel VM validation runs, audited pinned GCE fallback
pdata and cached legacy thread-count/security definitions. Added opt-in exact
MT8163/MT8173 tuple coverage preserving other schema constraints. Seven actual
processed-schema controls pass; full-corpus diagnostics56→54 (12validation and
42unmatched), zero additions; overall still fails/exit1.127 offline tests pass
on this independent branch; PR101's parser/runtime changes remain separate.
Source hashes/delta retained. No CMDQ execution, DT/hardware enablement or device
access. Merge after PR101 to avoid invalidating its expensive compile head, then
reconcile appended WORKLOG and rerun inexpensive required checks.
## 2026-10-25 — Sanitized CPU-contract init reporting (#100, runtime pending)

Implemented bounded private cmdline/CPU-online/live-DT status reads in minimal
init with allowlisted verdict-only output. Added shared C parsers exercised by
native host tests and distinct generic-observer/primary-contract evidence checks.
130offline tests and local AArch64 object compile with Werror pass. Builder
records header/source hashes; linked initramfs and generic VM integration remain
pending existing gated CI. No raw private argument emission, tablet/device access
or firmware assembly. Do not close100 until actual init/runtime integration is
validated. Recovery, usable physical logging and loader contract remain open.

## 2026-10-25 — Actual sanitized CPU init integration passed

PR101 head84c0392393eacf9dfef2b1d4e6b17d6bcc9c017b passed compile/initramfs/QEMU
run40259254917 in23m55s. Actual verdicts: both limits missing (expected generic
command line), one online CPU/CPU0 alone, PSCI status unavailable. Generic
observation passes; primary-only contract remains false. Retained exact runtime
report/artifact/log hashes in evidence/sanitized-cpu-report/generic-runtime-result.json.
PR101 merged/100 closed. Reconciled GCE PR103 against development preserving both
WORKLOG sections. Recovery work104 has started: declared PL7 mapping places an
old USB-descriptor patch address in a referenced string-literal pool and another
old entry in an interior block; exact trace/evidence is being prepared separately.
No tablet/helper/firmware execution or hardware qualification.

## 2026-10-25 — Recoverable loading priority / exact PL7 code (#104)

Prioritized recovery over more schema cleanup. Exact cached PL7/GFH mapping shows
old USB patch site217420 is a referenced string-literal word; old DA/TEE entry
sites lie in selected interior blocks. ARB entry201934 corroborated by diagnostic
strings and conditional caller20a7ce, not complete policy/compatibility. Retained
bounded static bytes/disassembly/hash/call controls;134 offline tests pass.
No replacement patches/payloads, helper/firmware execution, tablet IO or downgrade.
Compatible load/restore route remains unqualified. Next recovery task: qualify
older reference preloader/restore-material provenance and precise entry/restore
prerequisites rather than reuse stale offsets or infer exploitability from a
marker.100/102 completed with actual generic VM evidence and required checks;
physical boot/recovery/hardware/app gates remain open.

## 2026-10-25 — Reference material located, recovery not qualified (#106)

Located pinned mirror22.3MB archive; fetched only519984response bytes using strict
ranges. Older preloader138924B/SHAcefc66528a56626e65a553b7f97e0521e7939c195ce72794e7c4e14eab04619d
and LK485988B hashes retained; binaries ignored. Original author/Amazon-build
identity unverified (XDA403). Minimal mode still changes persistent GPT/boot0/
RPMB/boot/recovery/MISC; complete escrow/restore not established. Added bounded
probe and hash-only comparison;138offline tests pass. Approval review rejected
publication of copied helper code; removed it and raw code windows from public
changes, keeping only nonoperational summaries/metadata/hashes.106 remains open;
next official older OTA/original attachment match plus entry/restore validation.
No tablet/helper/firmware execution or physical changes.

## 2026-10-25 — Official-hosted older component provenance matched (#106)

Initial659658220 Amazon URL denied HEAD; retained status observations, no body.
Located other pinned index records and probed actual Amazon-hosted build metadata
before capped loader extraction.636558520 preloader+LK match older mirror hashes;
657611720 retains older preloader/current LK;659662320 has same PL/LK as current.
Read1356647body bytes total across three probes, no full~900MB OTA. Public reports
contain properties/metadata/digests/range hashes only, no helper/firmware code.
Added offline host/model/resource/digest verifier;141tests pass. Component source
provenance resolved, not signatures/antirollback/helper authenticity or restore.
106 remains open; next separate safe entry/backup escrow from persistent writes.
No tablet/helper/firmware execution, downgrade, flashing or device changes.

## 2026-10-25 — Recovery entry/escrow source audit (#106)

Merged PR108 after exact-head required checks passed (reran stale validation
job); development base03da5d38e477fc79ca7506512bc3d3dcb7191b34. Added AST-only
source audit and two regression tests:143 offline tests pass. Old minimal route
is not backup-first; conditional early writes and dropped size bound recorded.
Located pinned MTKClient MT8163/douglas configuration and Mac documentation as
a possible independent read-back alternative. Read APIs alone do not qualify
bootstrap/indirect persistence behavior; duplicate GPT filenames reuse data.
Retained source hashes/line summaries only, with helpers ignored locally.
No payload/dependency install, helper execution, tablet access or firmware changes.
106 remains open: next audit legacy DA/bootstrap side effects and minimal Mac
CLI requirements, then independent escrow/restore/log qualification.

## 2026-10-25 — Legacy backup selection/bootstrap audit (#106)

PR109 merged only after all four exact-head required checks passed; new base
102cb12 (full revision available in Git). Read111117B across six pinned source
files, no payloads or installs. Added source-hash-checked AST method closure and
regression tests:145 offline tests pass. Legacy upload/read closures do not
reach named write/format methods, but external protocol/agents remain unaudited.
Found a concrete escrow failure path: readflash ignores failed partition-select
acknowledgement and can proceed against an unconfirmed region. Dynamic DA mode
can override the configured legacy choice. FUSE imports have guarded fallbacks;
complete minimal Mac CLI import closure remains unverified. No tablet access.
106 stays open. Next offline deliverable: fail-closed escrow geometry/hash/GPT
validation with synthetic fixtures; safe entry, restoration and usable physical
boot-log capture still unqualified.

## 2026-10-26 — Offline escrow verifier (#106)

Merged PR110 exact head02df4b85ab6e8c5f0d69147b535448ef3a79443d after all four
required checks passed; basea8940c6. Implemented regular-file-only three-region
length/SHA verification plus GPT headers/arrays from actual primary/final-LBA
locations, CRCs, reciprocal geometry, partition bounds/overlap and consistency.
Caps metadata memory; no device protocols or restore actions. Seven synthetic
tests bring suite to152 passing, repository guard/diff check pass. Qualification
flags stay false even on valid files: collection region identity, restoration
and physical-test readiness are not established by checksums. UEFI2.11chapter5
is the format reference. No new downloads, installs or tablet access.
Next: define precise restore/boot-log evidence checklist and resolve safe entry/
agent provenance; do not close106 or any physical gate on synthetic tests.

## 2026-10-26 — Restore and first-log acceptance plan (#106/#21/#22)

Merged PR111 exact c6417a293f3f8483bc3224b1294f7696af63758b after all required
checks passed. Reconciled stale sequence inventory: older Amazon component byte
identity is resolved; signature/rollback/restore are not. Added modern read-back
candidate and offline verifier limits. Defined ordered entry/agent, acknowledged
escrow, restore reachability, security-state, Mac/re-entry and log gates with
precise missing evidence for UART, retained RAM and USB logging. No operation
commands, package readiness or runtime claims. Next source task is DA selection/
agent provenance, then source UART contract; no tablet access or new downloads.

## 2026-10-26 — Candidate download-agent selection/provenance (#106)

Merged PR112 exact eac4a371a4df30ab992403961cf9ee225abf1c02 after required checks
passed; base2f5b708. Inspected9558B pinned source +308770B Git-tree metadata only.
Separated600B security bootstrap from independently selected storage DA. Default
selector scans six filename candidates51,627,415B total; no binaries downloaded.
Found subcode deduplication self-comparison at daconfig:196 and no setup subcode
check; actual device failure/selected record unverified. Recorded metadata/SHA1
versus signature/SHA256 distinctions. AST-only tests bring suite to154 passing.
Next bounded metadata/header inspection for DA records if range-supported, or
independent cached UART contract; no helper execution/tablet access/dependencies.
Recovery/restore/logging gates stay open.

## 2026-10-26 — Exact candidate DA record metadata (#106)

Merged PR113 exact6fd9fa468bf54fe62ad39becf2fef0872b4b6486 after all required
checks passed; base5f82131. HTTP206-only bounded probe read36,080B container
headers/tables plus108B initial support check; no stage code/full pack. Two
MT8163 records found: V5index40 and mt6590index19, bothHW0xCA00/SW0/subcode0.
V5 expected first eligible default under audited version/order assumptions,
not runtime-selected/qualified. Recorded stage lengths/signature-tail sizes and
range hashes, not target addresses. Four new tests including ignored-range/
pre-request budget failures:158 tests pass. Next bounded stage-identity probe
~320KiB, static/hash only; actual entry/restore/logging remain open.

## 2026-10-26 — Original V5 stage identities (#106)

Merged PR114 exact1c344dc397dc7fe597066d1435e94bc3294f5b66 after required checks
passed; base2f3983c. Read320224B exact stage ranges +22383B extension source.
Original stage/code/signature-tail SHA256s retained, binary/helper bytes ignored.
No signature validation, execution, emulation or patches. AST review confirms
conditional extension/hash transformation before upload, so original digests
do not establish future uploaded identity. Added pinned bounded-cache repro
verifier and two synthetic tests:160 tests pass. Next cached UART source/driver
contract; entry/agent effects/restore and physical logging remain unqualified.

## 2026-10-26 — UART first-log source/DT/config contract (#106/#22)

Merged PR115 exact3709268020f9a36a3eb35491707b6f259373ee1d after required checks
passed; base4d83c96. Audited reviewed primary-onlyDTB against cached driver/config:
enabledUART0/11002000/stdout921600n8/fallback and built-in drivers present, but
no explicit earlycon/console in DT args and built-inCMDLINE empty. Actual loader
argument delivery remains unverified. Early driver setup does not establish
clock/pin initialization; normal probe has separate provider requirements.
Added source/DT audit +two tests:162 passing, no DT mutation/download/device IO.
Next authoritative douglas pad/electrical evidence search, then safe entry/log
transport qualification. No physical wiring action requested.
