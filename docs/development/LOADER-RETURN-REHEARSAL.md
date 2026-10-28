# Douglas loader and supported-stock return rehearsal

The [LK handoff coverage inventory](LK-HANDOFF-COVERAGE.md) consolidates nine
pinned source receipts and five explicitly unqualified runtime evidence gates.

## Target and present decision

Exact lab unit: douglas/KFDOWI, stock incremental50.6.5.9_user_659664620,
PL7/LK3/TEE262. Other Fire7/revisions are excluded. Owner accepts wipe/security
changes for planning and permits low-brick-risk lab operations; this is not
approval for a high-brick-risk unlock/firmware sequence.

**Current executable boundary: R0 read-only stock baseline only.** R0 passed.
R1/R2 below describe qualification gates; they are not commands to run. No loader,
brick, downgrade, flash or electrical action is scheduled by this document.

## R0: qualify the current stock observation/return baseline

Acceptance evidence already obtained:

- Owner-observed stock recovery entry and ordinary Android return, with actual
  menu and kernel-log viewer photographs; no upload/wipe/helper used.
- Stock Android reconfirmed during this rehearsal preparation: douglas, exact
  incremental build, sys.boot_completed=1. Scoped shell metadata shows cache
  owned system/cache, recovery directory inaccessible to this shell for the
  selected last_kmsg file; `test -r` is false. No raw block read attempted.
- Tag-only Android USB archive export works. Two acquired entries, second matching
  photographed markers, partial coverage0..29.865148seconds. Exact packaged
  BootReceiver caps this archive at320KiB. Complete log/freshness are unqualified.

[Normalized R0 baseline](../../evidence/douglas-original-route/rehearsal-stock-baseline.json)
records the scoped read outcome without household fields.

R0 demonstrates ordinary stock operation and a partial diagnostic path, not
recovery after modified storage, a crash or failed diagnostic load. Do not
substitute sys.boot_completed or a generic build for those gates.

## R1: prove a bounded loading and independent failure-exit contract

Before any first persistent mutation, a reviewer must be able to answer all of:

1. Which exact original package/member hashes and maintainer route apply to this
   PL/LK/TEE combination? Full/minimal stages cannot be interchanged. Later
   maintainer full-stage correction supersedes stale brick-launcher guidance.
2. Which storage region is selected and how is its identity independently checked?
   The host selector lacks a framed acknowledgement; candidate native source and
   shipped-binary equivalence remain separate. User GPT geometry is observed,
   but boot0/boot1 sysfs sizes are not physical EXT_CSD proof.
3. What is the first destructive operation and which later operations restore
   forward bootability? Original full stage changes GPT before later boot checks,
   clears headers/changes RPMB and writes components. Its max-size argument is
   dropped; do not treat supplied maxima as an enforced write fence.
4. At each interruption boundary, what independent mechanism remains reachable,
   what precise stock material can it write, and how will success be observed?
   Ordinary stock recovery before mutation is not an answer after those writes.
5. What diagnostic boot artifact, CPU/memory/callback contract and maximum load
   extents are being tested? Identify which early markers the partial logger can
   preserve and how they remain attributable after failure and ordinary return.

Acceptance: a pinned route/effect inventory plus demonstrated compatible entry,
region identity and failure exit for the intended boundary. Source plausibility
alone does not pass R1. If a bounded RAM-only route can be established without
persistent writes, evaluate it first; existence/support/signature acceptance of
such a route has not been demonstrated on this locked stock unit.

## R2: intended failure and return observations

The intended failure is an experimental diagnostic image failing to reach its
bounded ready marker or failing to return control/boot normally. Rehearse return
before using an unqualified experimental image, with an explicit owner-present
window if physical interaction is necessary. For each approved trial record:

- Pretrial exact unit/build/state, artifact/loader/source hashes and selected route.
- First mutation, stage reached, expected timeout from the selected reviewed route
  and one allowed return action. If no defensible timeout exists, the trial is not
  ready; do not invent a repeated reboot or flash loop.
- Entry/failure screen or protocol evidence without identifiers, observed exit,
  stock recovery reachability and normal Android identity/boot-complete result.
- Tag-only kernel archive hashes, bounded coverage, truncation, intended marker
  and boot/session attribution. A missing/old archive is a failed logging gate.

**Unqualified return boundaries:** after intentional preloader-header clearing,
BootROM re-entry is proposed but unobserved; after GPT/RPMB/component changes,
BootROM enumeration alone does not restore state; after headers are restored,
prior cleared-header entry is no longer guaranteed. Modified fastboot/TWRP and
unit-specific physical fallback are unobserved. Original return ZIP requires a
working rooted Android/GPT path and is not an independent rescue. Therefore R2
cannot presently be run as a low-brick-risk trial.

## Supported-stock material and persistent effects

Exact full stock package907705758bytes SHA256
`6e70792b002d5274286a8cd7e66da4b80e748a545b3303ab466795548d00f9ab`:
whole-file CMS checked with candidate recovery signer material. This does not
prove the installed verifier accepts it. Reconstructed exact recovery9299968bytes
SHA256 `4de74a18736f3652a96db33453b230b72b91a7dbbec7a4d046ee5c9408a167e2`
matches the signed recovery target and fits observed17MiB slot; actual boot/flash
acceptance is not proved. Firmware bytes remain private/cached, not in this package.

The stock OTA writes selected system/boot/LK/TEE/preloader material but is not a
promise to restore arbitrary GPT, RPMB, security state or original user data.
Wipe acceptance removes the original-data preservation requirement, not correct
region selection or reachable supported-stock return. Proposed exploit GPT shrinks
userdata by231194112bytes; original boot/recovery cannot hold the exploit sector
payload without the reviewed layout transformation. No such change was executed.

## Stop conditions and authorization boundary

Stop before mutation if target identity/build/hash differs, source/binary relation
is unproved for a relied-on safety control, capacity/region identity is ambiguous,
independent return is unreachable, the route requires an unreviewed helper,
remaining power/physical prerequisites are unknown, or the operator cannot observe
and perform the selected exit. Stop after any unexpected screen/USB transition,
write-range mismatch or timeout; preserve evidence and do not try another image,
minimal/full pairing or downgrade to make progress.

Bootloader/preloader/security writes, downgrades, unreviewed unlock helpers and
unqualified electrical fallback can carry high brick risk. Owner explicit approval
is required for such a concrete reviewed trial, and approval alone does not fill
missing technical prerequisites. No approval is requested for an incomplete trial.
Continue independent source/board work while these runtime gates remain open.

## Review sources and next action

Use the [diagnostic evidence index](DIAGNOSTIC-EVIDENCE-INDEX.md) for pinned receipts.
R1/R2 remain blocked on actual compatible bounded entry/independent failure return,
not on another cable reseat or ordinary recovery-menu photograph. Next independent
work is the dependency-ready board task selected from the active queue; next route
investigation must narrow one of the five R1 questions rather than repeat generic
compilation or reclassify the partial log as complete.


## Observed clock ABI constrains any experimental DTB handoff

The sanitized [stock DT clock receipt](../../evidence/power-port/transition-order/observed-stock-clock-abi.json)
confirms MFG70/MM67 while the candidate provider uses54/51. In the candidate,
70/67 identify different clock functions. The stock parent tuple also differs
from the candidate parent/child model; this selected-property capture is not a
full DTB compatibility analysis. A qualified R1 plan must identify and verify the
actual matching DTB passed to the candidate kernel. Stock-DTB substitution and
unobserved loader selection are not acceptable evidence of compatible handoff.
The host guard checks fresh candidate clock IDs/providers, but cannot prove what
a loader passes. R1/R2 and independent failure return remain unqualified.
