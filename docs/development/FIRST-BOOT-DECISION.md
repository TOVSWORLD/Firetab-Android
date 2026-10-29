# First recoverable diagnostic boot decision — #439

29 October2026. **NO-GO for loading an experimental kernel on the current unit.**
This completes an entry decision, not entry, recovery, logging or hardware
qualification. #347/#346/#348 remain blocked. No device/helper/mode/firmware,
watchdog, reset, GPIO, voltage or electrical action was performed for this decision.

## What actually prevents a boot

The observed installed versions are PL7/LK3/TEE262. The retained
[route admission receipt](../../evidence/route-admission/review.json) admits zero
cached nonpersistent trials. Its historical suggestion to work on watchdogs and
its percentage estimate are superseded by the ordered roadmap. This decision
reuses that evidence rather than repeating LK disassembly or stock captures.

Stock recovery accepts the demonstrated stock path; it is not demonstrated to
accept our kernel. Cached stock-fastboot registration has no boot command in the
reviewed region; download/continue is not a qualified RAM loader. The legacy
software-unlock version gates are6/2/259, below this unit; its newer-version branch
changes preloader/LK/TEE. Full and minimal BootROM helpers both have persistent
storage/security effects. The modern bootstrap can crash or touch DA/MMIO and has
no qualified failure exit. Generic stage/direct DA lacks a matched CPU/argument/
transport/return contract. None is selected for execution. Owner acceptance of a
wiped lab unit changes preservation goals, but does not validate those mechanisms.

Therefore more peripheral builds cannot unlock first boot. Nor would replacing
one host error loop turn an unreviewed entry chain into a safe loader.

## Minimum package for the first trial

Use a single-core, storage-free diagnostic payload, not Android or the new USB
ACM path. Reuse the minimal diagnostic PID1 design: fixed technical status only,
virtual filesystems, console output and idle; no shell, ADB, block mounts or
automatic reboot. Require `nr_cpus=1` and `maxcpus=0` to be checked after handoff;
those command-line declarations alone are not evidence of CPU state.

There is **no admitted integrated candidate** today. The existing restricted
Image and static archive receipts are separate historical build proofs, not a
matched boot bundle. Before any GO, record one source commit/compiler/config,
Image+initramfs+post-fixup DTB hashes and exact container, plus a loader-accepted
layout. Rebuild only that route-compatible bundle after the route exists. The
latest peripheral-enabled Image is not automatically the smallest diagnostic
candidate. No new download/build is necessary to reach today's NO-GO decision.

The required loader contract must establish entry ISA/exception state, actual
boot CPU and parked secondaries, DT argument, MMU/cache/interrupt state, RAM and
reserved ranges, payload/DT/initramfs placement and non-overlap, and transfer/
readback completion. No executable addresses or guessed trampoline are selected.
Existing generic-stage arguments and the owned agent's context do not match;
Linux/Image calling convention compliance cannot be inferred from a successful
host transfer or arbitrary function call. Existing DT validation still fails;
post-fixup resource/reservation truth is not supplied by a schema match.

## Return and observation before GO

Ordinary stock recovery entry/return has been observed. The exact-build signed
OTA and reconstructed recovery are retained; their receipt hashes are pinned in
[decision inputs](../../evidence/first-boot-decision/decision.json). A recovery
image on the host is not an independently reachable rescue after a broken loader.
A proposed route must name a return path independent of the modified experiment,
its failure boundaries and any owner menu interaction. Do not intentionally fail
or write a boot chain to discover whether that fallback exists.

Choose a log channel that can observe the first payload and survive its specified
failure: qualified UART acquisition, or independently proven retained logging
with a retrieval path. Neither is qualified here. UART source routing does not
identify safe accessible pads or voltage. The stock USB SYSTEM_RECOVERY_KMSG
export is capped320KiB and does not prove fresh experimental logs. ACM admission
has seven zero gates and no physical descriptors; do not flip them to obtain a
log channel. No SELinux/security bypass is acceptable. A fixed host status frame
would establish receipt only, not kernel boot or failure retention.

Before any trial, document unit-specific supply/battery condition and stop limits
from qualified hardware evidence, an attended observation window, and a safe
independent abort/return action. No numeric thermal limit, clock/voltage change or
watchdog kick is invented. Unknown supply/thermal behavior, unexpected identity,
route/version mismatch, transfer/readback disagreement, unreviewed write/MMIO,
missing logs, or loss of the independent return path means **do not begin or do
not continue the trial**; never retry automatically. The abort itself must be
specified before entry—idle or closing USB is not proof of a safe device exit.

## One owner decision

**Recommended scope decision: allow preparation of the exact-board mechanical
inspection and independent recovery/logging proposal in existing #345.** The
software-only route inventory is exhausted at its current evidence boundary;
this is a prerequisite of entry, not an unrelated hardware task.

This decision would authorize preparation of a reviewable plan only. It does
not authorize opening the tablet, disconnecting a battery, contacting a pad,
shorting, soldering, applying power or executing an unlock/firmware helper. #345
must identify exact-generation mechanical provenance, tools/isolation, what can
be learned without energized contact, remaining uncertainty and stopping points
before any physical action is proposed. No new photos or cable checks are being
requested. If the owner declines that planning scope, keep the project blocked
at entry; do not resume peripheral work to fill the gap.

Closing #439 with NO-GO does not satisfy #347's explicit GO condition. #345 stays
conditional pending this owner scope decision. Approval to prepare a plan is not
approval of a later high-risk procedure, nor proof the hardware route will work.
