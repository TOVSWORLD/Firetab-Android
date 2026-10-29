# Douglas software-unlock proposal for owner review — #439

29 October2026. **Prepared for review; execution is not authorized.** The selected
candidate is the original case-closed external-brick → **full** BootROM → hacked
fastboot → TWRP sequence. This is persistent boot-chain modification, not a RAM-only
kernel trial. Opening is not a planned step. If it fails, software-only rescue is
not guaranteed; physical recovery might become the only remaining option.

This is the concrete next decision requested by#439, using the
[original authors' instructions](WORKING-PROJECT-ENTRY.md), not a new exploit or
another source-readiness wrapper. No device, unlock/root helper, firmware or mode
change has run. #345 is conditional, not an automatic hardware prerequisite.

## Exact retained package and host

Use only the three original attachments already cached and verified against the
retained archive inventory:

- amonet-douglas-v1.2.zip:17,930,182B,
  SHA256 `6647dd0b5b9d2c04a2f167f6ccc7a2cfbcaa6f1f93f8251c7a39455db77119b2`.
- brick-douglas.zip:4,399,395B,
  SHA256 `ba017f1c4fc2f003924912a9099d18c94dd82401a2ad12881b7e7e158a4bc06b`.
- amonet-douglas-return-to-stock.zip:9,132,032B,
  SHA256 `a9f8d3df1f42c1e135820024bd1020386bc6c2abd7c08a60fcdc17dc898dd370`.

[Offline preflight](../../evidence/software-unlock-proposal/preflight.json) verified
all three whole archives and12 relevant script inputs. No new download occurred.
Original attachment identity is not an author signature or current-build support.

**The bundled brick host executable cannot run natively on this Mac.** Its64-bit
file is Linux/x86-64 ELF; the32-bit alternative is Linux/x86 ELF. Current host is
Darwin/arm64. The script's `uname` substring check would select by64-bit naming,
not the actual executable architecture. A Linux/x86-64 environment with direct,
reliable USB access must be available before a trial is scheduled. A VM USB
handoff is not assumed reliable; no VM, Linux image or replacement fastboot has
been downloaded, installed or executed. Host preparation is not tablet mutation.

## Scope and procedure to be approved

Approval must cover the following sequence as one high-risk change, with an
attended owner session. A description here is not an instruction to run it now.

1. Prepare an isolated Linux/x86-64 workspace from the pinned archives. Preserve
   originals and record the resolved files/tool identities; do not mix other-model
   packages, a third-party copied guide, or changed payloads. Disable conflicting
   host modem handling only in that reviewed Linux environment. Confirm package
   pairing and identify exactly one Douglas privately before any mode change.
2. Enter the unit's stock fastboot in the attended session. The proposed external
   script is `brick-9820.sh`, not rooted `step-1.sh`. Its operation invokes the
   bundled fastboot against the brick image. This is the **first destructive
   boundary**, not a read-only test. The screen can go black by design; neither
   black screen nor a failed transport status proves successful BootROM entry.
3. For this external-brick branch, use v1.2 `bootrom-step.sh` (**full**, no minimal
   argument). Ignore the brick script's stale minimal-step message; the author's
   expanded warning specifically prohibits that pairing. Do not execute
   `bootrom-step-minimal.sh` and do not run `step-2.sh` after this external branch.
   If observed state is inconsistent with the planned transition, stop and assess;
   never switch scripts or repeat the brick operation automatically.
4. Only after the full stage reaches its expected hacked-fastboot endpoint, the
   separate v1.2 fastboot stage writes TWRP to the remapped recovery target, clears
   userdata and requests recovery. Actual TWRP entry, its partition mapping and
   usable host logs must be observed; script exit alone is insufficient.
5. Stop at TWRP. Do **not** install LineageOS/GApps/Magisk, a new kernel, another
   bootloader or a security/policy bypass. First capture the recovery/host outcome
   privately and review stock-return reachability. The maintained-kernel bundle
   remains a separate exact-build admission after this transition is understood.

The rooted step1/minimal route is a different branch that first installs older
components itself. It is not an alternative recovery command to try if the
external-brick/full route fails. Exact script/image hashes and historical full
write extents are retained in the linked source receipts; no helper is modified.

## Effects and acceptance limits

The selected full stage can transform/write GPT, clear exploit headers, change
RPMB anti-rollback state, replace preloader/TEE/LK, install exploit payloads and
request reboot. TWRP installation wipes data and uses modified partition names.
These effects cannot be undone by merely closing a host process. Ordinary stock
images do not restore arbitrary RPMB/security state. The wiped-unit agreement
resolves data preservation preference, not permission for these writes.

Observed PL7/LK3/TEE262 exceeds the rooted script's old-component branch limits;
that explains the downgrade path, not a universal incompatibility conclusion.
The current original thread's5.7.1.0 question was unanswered on the reviewed page.
We have **no verified same-version success on this unit**. The separate brick
image's installed-loader acceptance and the full stage's failure behavior remain
uncertain. This proposal does not turn the published method into a guaranteed
supported procedure or infer that consent validates it.

Existing source findings also matter: the Python flash helper ignores its supplied
maximum-size argument, and the selected region-switch method lacks an explicit
response check. Retained geometry/size arithmetic is useful but not an atomic
rollback guarantee. No new tests of a model are offered as a substitute.

## Independent return and useful logs

The exact signed stock OTA and reconstructed current recovery are already
available; ordinary stock recovery return is observed. Their identities and
limits are in the existing first-boot decision. The old bundled stock recovery
is **not** the reconstructed current one. Do not silently substitute artifacts.

After a working modified recovery exists, the documented stock-return route can
restore a stock recovery/GPT and then sideload stock. It depends on reachable
ADB/root or hacked fastboot/TWRP at its stated stage; it is not an independent
rescue before those exist. Repeating the full BootROM sequence is also not a
proven rescue after arbitrary partial writes. If initial entry fails and none
of those modes remains reachable, there is no guaranteed case-closed return.
This is the principal residual risk the owner must accept or reject.

Save complete attended host output, timestamps, exact artifact identities and
observed mode transitions privately. If TWRP becomes reachable, collect its own
recovery log and determine whether kernel evidence is accessible there, without
weakening permissions. Host progress text is not kernel boot evidence. The stock
320KiB export and a ROM author's last_kmsg suggestion do not qualify experimental
retention; those runtime gates remain open. No UART wiring or ACM-gate changes.

Stop before starting if host/identity/package/pairing is uncertain, adequate power
or owner attendance is absent, or the owner requires guaranteed software rescue.
During a changing device state, do not treat unplugging as universally safe.
Unexpected disconnects/writes or unverified progression require assessment at that
boundary; no automatic retry, fallback downgrade, guessed electrical action or
new command improvisation. Existing helpers are not shown to provide transactional
rollback or a universal abort. No invented temperature/current threshold applies.

## Decision to record

**Approve or reject the persistent software-unlock attempt above, accepting data
wipe, boot-chain/RPMB changes, uncertain5.7.1.0 applicability and the possibility
that failure leaves no software-only rescue.** It would be an attended trial on a
prepared Linux/x86-64 host; no tablet opening or electrical action is included.

Until explicit approval and host preparation, disposition is **HOLD—no execution**.
If the owner requires guaranteed case-closed recovery, this candidate cannot meet
that requirement from current evidence. State that tradeoff plainly rather than
claiming opening is required or returning to peripheral work. Approval may select
an attended qualification attempt; it is never evidence of a passed runtime gate.
