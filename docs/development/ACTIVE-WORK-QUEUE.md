# Active work queue toward beta QA

2026-10-29 #27: PR430 merged9c3f4a81 after six exact-head checks atb5e12688 and
actual builtin MIPI run40859970271. Three actual PHY objects/config/final28645888B
Image passed; exact normalized receipt evidence/mipi-kernel-integration/build-result.json.
Prior staged Images excluded; W1 objects pre-Image only, no physical admission.

Source-matched MIPI metadata implemented:35 actual decoded/type-policy controls,
olderSoC structural preservation and fresh-DTB actual reference/reset/disabled DSI
consumer graph checks pass. Full5186-YAML canonical32→31 (19unmatched/12validation),
isolated26→25(16/9): only MIPI unmatched removed/no additions; wrappers exit1/false,
Gunyah warning/disabled AFE unmatched retained. Source/DTBs/disabled states unchanged.
New exact-head host/metadata checks required before merge. No extra kernel build
for schema-only work. Physical PLL/reset/clock/lane/panel and recovery/beta open.
Next independent #27 source after metadata acceptance: actual MT8163 DSI controller
variant/IRQ/clock/power/resource/probe prerequisites, not guessed MT8173 alias.
Thermal source remains unadmitted on actual calibration/bank/conversion lineage.
No PHY/display/device/mode/firmware/helper/reset/electrical operations.

Updated 2026-10-28 at owner request. This is an execution queue under the existing
Epic → Feature → Phase → Task hierarchy, not a replacement issue tracker.

Current #347 route review: no cached physical trial is admitted. Actual MT8163
USB2 port0 source PR413 mergeda387d729 after exact-head USB-enabled object/config/
Image run40805824866 and five PR checks; no QEMU or device USB test. Canonical
pwrap-parent DTB remainsb837e6cb with the prior failing34-diagnostic context.

The explicit disabled usb-frequency-resource experiment now adds only parent
reg/reg-names, preserves186 nodes/all other values/phandles/child order/reservations
and keeps USB0, USB1 and PHY disabled. Matched opt-in MUSB/T-PHY metadata controls
pass25 cases with old-SoC policies preserved. Paired isolated context reports28
(19unmatched/9validation), wrapper exit1/passedfalse; canonical baseline unchanged.
Schema matching disabled USB1 does not qualify port1, rejected by the initial
kernel xlate. Source, build, metadata and physical transport remain separate.

Completed finite USB0 analog/role/clock review: source expressions differ at RX
mask0x5, role-device mask0x3c08 and role-OTG mask0x3e0a; explicit eye7/7 only
matches the isolated legacy eye operation. Legacy CCF prepares ICUSB but the PHY
CCF enable path does not enable it; CLKMGR is a distinct branch. Reproduce
scripts/audit_usb0_transitions.py and kernel/USB0-TRANSITIONS.md.
PR416 merged6ef265b after final-head checks and exact-head dad8de0 USB-enabled
object/config/Image run40813924079 passed.402 host tests include actual C RAM
mocks over131072 states and strict one-cell override negatives. No device test.
MT8163-only eye const7 binding now matches the accepted source guard;30 actual
decoded controls pass and prior SoC policies remain intact. Paired isolated28
(19unmatched/9validation) and known Gunyah processing warning remain failed;
canonical34 context/DTB and all disabled states unchanged. Prior414 receipts retained.
Finite gadget role/config/package acceptance completed: exact416 config has
CONFIGFS/LIBCOMPOSITE/F_ACM/U_SERIAL=m, no modules/gadget setup in current static
initramfs. Actual cached role function RAM mocks (18 transitions/error cases)
return success/update role despite called PHY failures. Source audit in
kernel/USB-GADGET-PREREQUISITES.md and scripts/audit_usb_gadget_prerequisites.py;
require-ready rejects current package. No transport admission or DT changes.
PR419 merged37256b1 after six exact-head checks and USB provider/Image
run40822461567 at93e62f8 passed.409 RAM/source tests and all-target preflight;
physical rollback/concurrency/reprobe remain unqualified. Receipt usb-role-errors.
Active #27 package phase: actual separate usb-acm-diagnostic config/build scope
implemented, builtin ACM/component policy and forbidden-function/security guards.
414 host tests pass; new exact-head Linux resolved config/ACM objects/Image build
required before acceptance. Old provider/USB-off diagnostic/QEMU scopes unchanged.
First ACM resolution caught absent generic SECURITY_NETWORK/SELinux/LSM selection;
strict guard retained, explicit enforcing-capable security dependencies requested.
Replacement passed actual ACM/security resolution but failed invalid aggregate
object probe; corrected to nine hash-locked real component targets, rerun required.
Gadget PID1 not implemented; independent next source work is explicit opt-in
static configuration/output path with actual RAM failure/cleanup controls. Keep
minimal init/security/storage boundaries, both DTs disabled, canonical34/isolated28
failures and all physical USB/loading/return/log/runtime gates open.

#20 source prerequisite update: pinned modern genpd core acquired at its relocated
`drivers/pmdomain/core.c` path. Finite wakeup branch comparison is in
`kernel/GENPD-WAKEUP-COMPARISON.md`; missing-source blocker is resolved.
No active-wakeup capability change or runtime equivalence is claimed.

## Execution contract

- Continue useful authorized work within the active turn. The 15-minute heartbeat
  resumes interrupted/idle work; it is not a reason to end a work session.
- Briefly reconcile current issues/PRs/CI, then select the first executable item.
  Give it a bounded outcome and acceptance criteria. Finish checks and publish
  evidence through an issue-linked PR to development where repository work is needed.
- A task blocked on CI, owner observation, equipment or permissions does not block
  the queue. Record the exact condition once and take an independent item below.
- No repeated waiting-only runs while a ready independent item exists. No duplicate
  cable/approval/photo requests, artificial micro-issues, or low-value cleanup to
  inflate progress. Preserve real hardware/runtime gates.
- Before yielding, record completed result, exact revisions/commands/hashes, next
  executable action and unresolved blockers here or in WORKLOG with an issue link.
  Say whether work is active, queued or awaiting external input; never imply a
  continuous background process. If all ready work is exhausted, audit this queue
  and ask for the specific external action rather than silently polling.

## Ordered ready work

1. **#348 — locate the 320KiB collection limit (completed source scope).**
   Exact packaged BootReceiver user LOG_SIZE65536 multiplied by positive5 matches
   both measured327680byte payloads. See stock-recovery-archive-limit.json and
   WORKLOG; installed equivalence/source-file completeness remain open.
   Next executable item is2. Historical investigation acceptance: inspect the exact
   cached framework BootReceiver/DumpBox implementation and recovery log-copy
   paths using bounded static decoding; no firmware execution. Compare with both
   acquired archive boundaries after CRLF normalization. Acceptance: identify the
   truncating stage with pinned byte/source evidence, or explicitly distinguish
   candidate stages and the missing observation. Do not rerun the same transfer
   expecting missing bytes. Raw captures remain private under
   `out/recovery-log-export`; current dump SHA256 is
   `25a703e1315c636794d26a586153d4051f4569bbf008e429eccff197bd3ba256`.
2. **#348 — qualify archive attribution and usable capture coverage (completed
   bounded analysis).** Second entry covers0..29.865148seconds and all photographed
   markers, first entry is not monotonic; collection headers are not boot identity.
   Exact freshness/failure retention remain open. Next executable item is3.
   Historical acceptance: Independently
   compare existing entry headers, kernel/build markers, uptime spans and
   photographed markers; publish sanitized attribution/coverage only. Acceptance:
   define exactly which stock boot evidence is supported and which freshness or
   failure lifecycle is untested. A full log and experimental failure retention
   are not implied by the demonstrated USB archive export.
3. **#346/#347 — make the loading/return gate concrete (source plan complete;
   runtime gates open).** See LOADER-RETURN-REHEARSAL.md. R0 baseline passes;
   R1/R2 are blocked on compatible bounded entry and independent failure return.
   Historical acceptance: Reconcile authenticated
   exact stock package/reconstructed recovery, observed geometry, original loader
   write effects and available log route into one bounded rehearsal plan.
   Acceptance: explicit prerequisites, intended failure, reachable return path,
   persistent effects, stop conditions and high-brick-risk decision boundary.
   Source-complete planning may finish while physical gates remain open; do not
   execute helpers or close runtime gates on the strength of the plan.
4. **#340 — assemble the diagnostic evidence handoff (source-review index
   complete; beta package gate open).** See DIAGNOSTIC-EVIDENCE-INDEX.md.
   Next executable item is5, with live issue acceptance review.
   Historical acceptance: Use existing sanitized
   receipts, exact revisions, hashes and commands. Acceptance: one navigable
   package index differentiating verified stock entry/return/export, generic
   builds, candidate diagnostics and untested experimental recovery. Include
   reproducible bounded capture and private-data handling. Do not label it beta
   ready or close #340/#338 without their broader QA acceptance.
5. **#27/#18/#19/#20/#29 — independent board dependency work.** Current execution:
   #29 real audio-parent source scope is complete via merged PR384; #27 exact provider
   binding proposals proceed from cached source during that wait. Topckgen and
   infracfg scopes merged (#385/#386); apmixedsys scope merged (#387); four gate contracts are in #388. A real MMSYS parent-
   instantiation gap are recorded in #387. #18 real parent integration is in PR389 with explicit parent-object/Image CI.
   Its compact reset mapping corrects donor DSI and LCM mismatches. Parent object,
   generic Image and QEMU pass at5c02907 (run40763077737); actual runtime remains
   untested. #390/#391/#392 merged; pinctrl probe contract has19 controls and45
   remaining full-context diagnostics. Current #20 source review compares eight IDs/32 register-SRAM fields/three
   protection masks/two status offsets against actual legacy, all equal. Wakeup
   policy and MFG clock attachment differ; provider probe writes are documented
   in the diagnostic evidence index. Next queued source scope: matched pwrap/
   scpsys/domain binding prerequisites under #27 and explicit wakeup/order
   qualification. Pwrap contract/PMIC parent rename has22 controls and all880 property/phandle
   values preserved. Scpsys parent/child proposals have24 decoded-node controls;
   fresh-DTB topology guard rejects wrong INFRACFG, MFG flattening, duplicate or
   disabled domains. Full context42 diagnostics remains unpassed. Next queued #20
   source scope: compare legacy active_wakeup callback to ACK genpd flag semantics
   and establish an explicit MFG clock-order rationale. The clock trace now records
   same alias-resolved mux fields but different owner and OFF write order. Bounded
   stock USB metadata confirms legacy MFG70/MM67 vs candidate54/51; fresh-DTB
   guard rejects old IDs/wrong provider. #347 must qualify actual matching DTB
   selection/handoff before any experimental loading. Next queued source task is
   #347: trace image/DTB selection, address and trust boundaries from cached
   LK/FDT/load artifacts (out/lk-instruction-audit, out/lk-fastboot-review,
   out/lk-bootargs), pinning each artifact and distinguishing source from installed
   binary evidence. No helper execution; keep R1/R2 blocked until observed. do not claim runtime equivalence from equal register values.
   Acceptance: explicit source differences and probe prerequisites, targeted checks,
   and preserved runtime gates. Do not create placeholders or alter the device.
   If recovery work
   truly awaits external evidence, select one dependency-ready existing board task
   after reading its live acceptance criteria. Investigate or implement its actual
   board relevance, run matched checks and link the PR. Compilation/schema counts
   alone do not qualify device boot or displace executable recovery work.

## Confirmed state and external gates

- Stock recovery entry and ordinary Android return demonstrated; actual recovery
  selector and kernel text photographed. Normal recovery USB unavailable despite
  completed cable reseat. Stop asking for cable reseats.
- Android-side tag-only `SYSTEM_RECOVERY_KMSG` export demonstrated: two entries,
  663874 transport bytes; both normalized payloads stop at320KiB. No current owner
  photo, cable action or return-to-Android confirmation is outstanding.
- Actual stock ATF/consys placement reconciles DT/kernel memory. Console buffer
  initialization observed; old-valid contents/experimental retention untested.
- Experimental loader failure return, complete log retention, installed recovery
  image equivalence and beta QA admission remain open. No hardware action is
  currently scheduled; task1 can proceed entirely offline.

## Authorization and resource boundaries

Owner grants standing permission for lab-unit actions without high brick risk.
Scoped USB/ADB/host reads may proceed without repeated approval; assess the actual
risk before changes. High-brick-risk actions still require explicit approval.
Do not infer that permission for an unreviewed helper, bootloader/preloader write,
downgrade or electrical operation is established. Avoid unattended mode changes
requiring owner menu interaction; do independent work while the owner is absent.
Large/paid resource gates and private-data exclusions remain. Main changes only
through development-to-main releases; merge feature PRs only after required
exact-head checks. Every PR updates/closes an actual issue; physical gates close
only on their acceptance evidence.

### Latest #347 bounded source result

Cached exact-OTA LK selects a root version string; missing version resumes scan.
Current candidate b837e6cb has no version. See kernel/LK-DTB-SELECTION.md and
evidence/lk-dtb-selection/report.json. Do not inject a guessed stock version.
Next executable source task: selector runtime provenance, incoming FDT destination
address and late fixups/final handoff, with installed LK3 equivalence kept open.

### Latest #347 destination/fixup source scope

Header+0x20 supplies selected FDT destination; fallback is0x40000100. The suffix
copy precedes in-place open capacity checking. Selected /memory/reg and /chosen
atag writes are pinned in LK-FDT-DESTINATION.md/evidence/lk-fdt-destination.
Next executable source acceptance: identify memory-tuple producer and complete
reservation/PSCI callback effects, then selected r5 lineage/trust checks. Runtime
addresses, installed LK3 equivalence and failed-boot return/logs remain blocked.

### Latest #347 memory source scope

Selected helper0x25ac4 consumes runtime count/24-byte records and emits16-byte DT
tuples; metadata/framebuffer callback0x25bbc is pinned. See LK-MEMORY-FIXUPS.md
and evidence/lk-memory-fixups. Next executable source acceptance: identify writer
and lifetime of runtime pointer-global0x4bd874c0, then alternate tuple branch and
remaining reservation/PSCI callbacks/r5 lineage. Installed LK3 and physical
handoff/return/log qualifications remain Blocked.

### Latest #347 entry-pointer source scope

Selected writer proven: entry r4 saved at0x4bd00020; initializer assigns local
buffer and matching-magic384-byte copy (LK-MEMORY-POINTER.md/evidence receipt).
Absolute store precedes relocation, so arbitrary-placement preservation is open.
Next executable source acceptance: alternate tuple branch0x3e17c and remaining
reservation/PSCI callbacks, then selected FDT lineage/trust checks. Full lifetime,
actual entry state/installed LK3 and runtime return/log gates remain Blocked.

### Latest #347 alternate/dispatcher source scope

Pinned GOT function presence selects mblock helper; alternate rank branch is not
selected absent later mutation. Its arithmetic and r5 restore are traced. One
optional-dispatcher setup targets IDME writes, so raw post-fixup DTB stays private.
See LK-ALTERNATE-MEMORY.md/evidence/lk-alternate-memory. Next executable source
acceptance: selected dispatcher setup source, remaining PSCI/reservation edits,
then complete FDT lineage/trust inventory. Runtime loading/return/log gates open.

### Latest #347 CPU source scope

Pinned callback removes out-of-limit CPU nodes and caps retained clock-frequency;
source tests do not qualify actual CPU boot/rates or PSCI. See LK-CPU-FIXUP.md and
evidence/lk-cpu-fixup. Next executable source acceptance: consolidate finite final-
DTB mutation/entry/handoff coverage inventory, unresolved dispatcher setup/trust
boundaries and minimum missing installed-LK3 evidence. Physical loading, failure
return and retained-log gates remain Blocked.
