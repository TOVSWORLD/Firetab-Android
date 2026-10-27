# Douglas: decision before the first physical diagnostic load

**Decision: NO-GO for loading.** This is an evidence checklist, not a procedure
for operating the tablet. Parent issue106 remains open. Compiled kernel/agent images and passing host tests do not establish a
recoverable physical test.

## The proposed route and its alternatives

Investigate a separately reviewed bootstrap capable of read-back first. The
pinned MTKClient source is a candidate, not a qualified loader. Do not run the
archived unlock sequence as a way to discover whether it works: its installed
version gate rejects PL7/LK3/TEE262, and its alternatives modify boot/security
state before a complete recoverable escrow is established.

- **USB-only route:** current-build entry, security state, agent selection and
  return after failure are unknown. An OS connection or a source configuration
  entry does not prove BootROM access. No USB-only transition is established.
- **Owner hardware access route:** owner accepts hardware access if needed
  for planning (2026-10-27). This does not establish a safe short/test point, board revision,
  voltage or UART connection. Those need independent evidence before action.
- **Existing modified recovery/fastboot:** no such installed state is established
  on this stock tablet. Instructions requiring it cannot serve as the initial
  route. The destructive brick path is not a substitute for recovery evidence.

Source basis: [route inventory](../../evidence/recovery-material/sequence-gates.json),
[entry review](../../evidence/entry-transition-source-audit/report.json),
[agent review](../../evidence/recovery-agent/report.json).

## Required evidence, in dependency order

1. **Starting state and entry.** Record the actual protocol mode, hardware
   version tuple and security flags using a separately reviewed, owner-approved
   collection plan. These are not supplied by the existing OS properties. Before
   collection, review every candidate initialization effect, including watchdog
   and register writes; do not label initialization a passive read. Determine
   how to exit a failed attempt without deliberate storage corruption.
2. **Agent and memory contract.** Use that tuple to select exact agent records
   and hash every stage. Resolve signature/security acceptance and RAM placement
   before execution. Current official PL7 supplies the same188-byte format0x10
   EMI data as the older official image; sourcing that data needs no downgrade.
   It does not prove agent acceptance or RAM geometry. Unknown replies, length
   disagreements, timeouts and incomplete status must invalidate the session.
   The DRAM checksum algorithm remains unknown in reviewed source.
3. **Read-back provenance.** Qualify acknowledged region selection and raw sizes
   for user and both boot regions, then obtain independent consistent private
   reads. Apply the offline hash/GPT verifier. Its success cannot establish
   actual region origin, recover security state or prove a restore mechanism.
4. **Restore after the intended failure.** For each proposed changed region,
   identify the original artifact and reachable restoration mechanism after
   that component fails. Explicitly exclude RPMB/key/counter/fuse changes until
   independently understood; ordinary image escrow cannot promise to undo them.
   Verify installed signature/rollback compatibility. No first diagnostic write
   is justified solely by having a backup file.
5. **Usable failure logs.** Establish either a board-specific electrically
   qualified UART capture, or a persistent log buffer whose reserved memory,
   retention and post-failure readout are demonstrated. UART0 source/pinmux is
   known; accessible pads/levels/capture remain unknown. The existing modular
   pstore configuration and proprietary legacy RAM console are not a working
   retrieval path. A black screen alone does not distinguish loader from kernel.
6. **Exact package and owner test instructions.** Only after the above, publish
   the kernel/DT/initramfs/package digests, safe placement rationale, expected
   first marker, timeout, failure exit, recovery steps and sanitized log return
   instructions. Label build, loader handoff, boot, hardware and apps separately.
   The current project has no qualified package meeting these conditions.

Details and source links: [recovery/log qualification](RECOVERY-AND-LOG-QUALIFICATION.md),
[escrow verifier limits](OFFLINE-ESCROW-VERIFICATION.md),
[boot contract](DOUGLAS-BOOT-CONTRACT.md).

## Smallest owner input and independent next work

The owner answered the planning choice on 2026-10-27: hardware access is
acceptable if needed. Do not ask this choice again. No case opening, measurement, USB command or
other tablet operation is requested by this checklist. Do not ask for an
unreviewed mode/security probe just because those facts are missing.

Independent next work is to review an explicit minimal mode/security collection
plan and its exact effects from the pinned source, without executing it. Separate
necessary protocol reads from bootstrap/watchdog/reset actions, and determine
whether a bounded observation can avoid them. If it cannot, document that limit
and the concrete proposed effects for later owner review. Further synthetic test
counts cannot close the six physical evidence requirements above.

## Minimal observation source-effect review

Pinned [initialization lines142–260](https://github.com/bkerler/mtkclient/blob/7cb40e727727dfe3faa065eefb29b16ed29bbdf1/mtkclient/Library/mtk_preloader.py#L142-L260)
shows `skipwdt` suppresses one conditional watchdog-disable call, not the whole
initialization sequence. It still handshakes, can fall back to memory reads,
queries versions/identifiers, mutates host settings and may authenticate under
configuration. `display=False` is not a side-effect suppression contract. Neither
option is accepted as a passive observation recipe. Entry itself remains unknown.

The [target-config query](https://github.com/bkerler/mtkclient/blob/7cb40e727727dfe3faa065eefb29b16ed29bbdf1/mtkclient/Library/mtk_preloader.py#L675-L707)
returns all security flags False when its command echo is unsupported. That
means unsupported evidence can look like disabled SBC/SLA/DAA. This is a source
finding, not observed device behavior. A collector must preserve unknown/failure
instead of using this default as bootstrap authorization. The method also accepts
status values through0xff; the meaning of nonzero statuses is not established
here. The own offline decoder requires zero status and an exact six-byte supplied
reply, reports only the three flag bits and always denies bootstrap readiness.
No transport/helper is bound or executed. Unknown higher bits are surfaced.

[Source receipt](../../evidence/minimal-observation-effects/source-review.json)
records the exact cached file. Hardware getters have fixed unpack sizes but do
not prove protocol mode or entry reachability. A future observation-only adapter
needs separately reviewed bounded handshake and explicit query failure handling,
without calling the monolithic initializer. No runnable physical collection plan
is qualified yet; no new tablet action is requested.

## USB handshake effect boundary

The pinned [Port handshake](https://github.com/bkerler/mtkclient/blob/7cb40e727727dfe3faa065eefb29b16ed29bbdf1/mtkclient/Library/Port.py#L147-L230)
is an active protocol exchange. It sets line coding/control state, sends sync
traffic, reads echoes and may drain input between retries. Although the main
exchange supplies per-call timeouts, the preliminary write on one product-ID
branch omits an explicit timeout. Its backend default is not a reviewed total
session bound. `handshake(maxtries=None)` has no attempt cap; even finite attempts
do not by themselves impose a wall-clock deadline on all underlying operations.
A previously connected transport also skips the while body and returns False.
Do not interpret these Boolean results as a reliable mode/security observation.

The pinned [USB connect path](https://github.com/bkerler/mtkclient/blob/7cb40e727727dfe3faa065eefb29b16ed29bbdf1/mtkclient/Library/Connection/usblib.py#L325-L448)
can set configuration, select a fallback backend, detach a kernel driver and
claim interfaces. It is not descriptor-only observation. Some interface-claim
errors are ignored; a returned connected state alone does not establish exclusive
ownership or validated endpoints. Actual macOS effects remain untested.
[Close](https://github.com/bkerler/mtkclient/blob/7cb40e727727dfe3faa065eefb29b16ed29bbdf1/mtkclient/Library/Connection/usblib.py#L449-L475)
may attach a driver and dispose resources; reset=True additionally requests a
USB device reset. Calling close without reset is not proof that the whole prior
session left firmware unchanged. No reset/close was executed in this review.

[Metadata source receipt](../../evidence/handshake-effects/source-review.json)
pins both files. A bounded observation-only implementation must explicitly choose
backend/interface/endpoints, document configuration/control-line changes, bound
every read/write and total worker lifetime, validate the mode independently and
stop on claim/query failure. It must exclude full initializer, fallback MMIO,
authentication, watchdog/reset, payload and storage paths. The existing owned
worker supervisor is a host containment component, not proof of physical undo.

**Route decision:** no reviewed drop-in candidate CLI currently satisfies this
minimal observation contract. Building an owned callback-only orchestration can
be done offline, but binding it to USB still requires a separate exact-effects
review and owner test plan. Hardware access is acceptable for planning; exact board and electrical evidence
are still required for entry/log options. Next prepare the
owned observation orchestration with synthetic callbacks and no command bytes,
then review the exact live binding separately. Do not run helper discovery/init.

## Owned observation orchestration, offline only

`scripts/offline_observation_session.py` now invokes exactly three symbolic
query callbacks: hardware code, hardware versions and target configuration.
It requires exact reply sizes and zero version/security statuses. A shared
positive budget is checked before/after each call and each callback gets a
positive bounded timeout. Failures invalidate the session with no retry,
fallback memory read, initializer, reset or bootstrap call. No USB command bytes,
backend, handshake, native imports or live callback are included.

Four synthetic tests cover query order/timeouts, every short reply boundary,
late callback and failed version status;219 tests pass. The budget is cooperative,
not native-call preemption. Live use would require the separately tested worker
supervisor and an exact effects-reviewed binding. Hardware words and security
flags are reported data; mode/provenance/bootstrap readiness stay false. This
cannot establish BootROM mode or reachability from the currently running OS.
Next review the exact getter response/status and command framing contract against
the pinned source before implementing any live binding. No tablet action asked.

## Getter framing and mode inference

The pinned [getter aliases](https://github.com/bkerler/mtkclient/blob/7cb40e727727dfe3faa065eefb29b16ed29bbdf1/mtkclient/Library/mtk_preloader.py#L136-L140)
use Port echo/mtk_cmd and backend reads. Hardware code uses a four-byte payload;
hardware versions use eight bytes unpacked into four big-endian words. The
initializer consumes the first three version words without checking the fourth;
our offline session deliberately requires the fourth word zero as a stricter
acceptance policy, not as a proved complete protocol specification.

[mtk_cmd](https://github.com/bkerler/mtkclient/blob/7cb40e727727dfe3faa065eefb29b16ed29bbdf1/mtkclient/Library/Port.py#L232-L256)
writes a command, reads its echo and indexes the response before an explicit
length check. An empty reply may raise. The direct target-config getter instead
uses echo plus a six-byte payload. A future binding must enforce exact echo,
exact payload, write completion and positive deadlines independently; calling
these methods does not satisfy the owned observation contract automatically.
The own `offline_query_frame.py` validates supplied echo/payload fields with
synthetic tests. It contains no protocol command values or transport.

[Mode detection](https://github.com/bkerler/mtkclient/blob/7cb40e727727dfe3faa065eefb29b16ed29bbdf1/mtkclient/Library/mtk_preloader.py#L657-L673)
uses a separate bootloader-version query: a particular echo sets is_brom True.
Its other branch does not explicitly clear a previously True value. Reused config
must not be treated as a fresh mode observation. A USB product ID, hardware code
or three-query session alone cannot supply this missing mode evidence. Returned
version bytes, exact echo semantics and session freshness need qualification.

[Source receipt](../../evidence/observation-framing/source-review.json) pins the
reviewed files. No helper was imported or executed. Next add a fresh explicit
mode-evidence result to the offline contract, preserving unknown rather than
reusing mutable helper state; no live mode query is authorized by these notes.

## Fresh mode-reply evidence, with no mode promotion

`offline_mode_evidence.decode_mode_reply` now returns a new independent result
for each explicit supplied one-byte query/reply pair. A matching reply records
only the pinned source's BROM-echo candidate. A different reply stays unknown;
it is not automatically classified as preloader. Missing or extra data raises,
and no previous result or mutable helper configuration is consulted. Even an
echo leaves mode/provenance/authorization false. Two synthetic tests cover
successive echo/non-echo isolation and missing/malformed evidence (223 tests).

This deliberately does not add a fourth query to the existing observation
collector: no actual command/transport contract or safe physical entry has been
qualified. It can later classify a separately reviewed fresh capture without
promoting a stale `is_brom` flag. No helper execution or tablet operation occurred.
The remaining useful step is an end-to-end synthetic observation package joining
exact frames, fresh mode reply and deadline/session checks, with a manifest of
owned source hashes. After that, live entry and electrical/logging facts remain
external requirements, rather than more Boolean-policy extensions.

## Runnable synthetic observation package

Run `python3 scripts/synthetic_observation_package.py --mode success`, then
`--mode bad-echo` and `--mode late`. These built-in scenarios join the owned
frame validator, observation collector, security decoder and fresh mode decoder.
Commands/replies are invented fixture symbols, not device protocol values.
No arbitrary callback, helper path or device option is accepted by this CLI.

[Retained scenario output](../../evidence/synthetic-observation-package/success.json)
and its sibling fault reports include SHA256 for all five owned components.
Success decodes all three synthetic queries; bad echo and simulated late return
stop at the first query, discard results and invalidate the session. The late
case advances a fake clock: it does not demonstrate native-call preemption.
Two integration tests bring the suite to225. All scenarios were run locally;
no native library/helper/device was loaded and no downloads were needed.

This closes offline component integration only. The next engineering task is
an explicit live-binding design review listing required protocol framing,
interface/control effects, process lifetime and logging output allowlist. Do
not add another synthetic readiness layer or call the package a tablet test.
Physical entry, actual security state, restore reachability and UART/log retrieval
are still unknown; an owner test cannot be scheduled until its concrete effects
and recovery exit are reviewable.

## Owned agent initial invocation gate

The owned agent now links and has supervised synthetic host framing, but the
pinned generic jump passes zero where the owned agent requires its nonnull IO
context. Direct JUMP_DA's host address/status exchange does not establish a
firmware register/return ABI. See
[initial loader ABI evidence](../../evidence/initial-loader-abi-gap/report.json).
Require a separately qualified bridge supplying context, Thumb entry, safe memory
and bounded callbacks before any physical proposal; this gate is still open.


## Current integrated build boundary (2026-10-27)

The owned agent, context bridge and opt-in sanitized UART logging now link in
Linux CI. [Exact build/gate receipt](../../evidence/recovery-readiness-boundary/report.json)
records an earlier build. It is superseded for image selection by the
[two-base receipt](../../evidence/owned-agent-link-bases/report.json): the corrected
3000-byte direct and 3040-byte bridge images agree at two synthetic link bases.
The older images contained the address-dependent marker pointer table caught by
#311/#312; do not select them from the earlier receipt. This remains a build
check, not arbitrary runtime relocation or a qualified physical package.
The six source-cited physical gates remain open: initial entry/exit, callback
semantics/restoration, physical memory contract, original-state restore, real log
capture and exact owner test/recovery instructions. Boot, hardware and app tests
have not occurred. Keep parent #106 open; close only bounded completed child scopes.

Further host test counts and marker features are not the next milestone. The
next investigation must address current-build initial-entry alternatives and
reachable return/restore, using cached sources and explicit effect inventories.
Hardware access is acceptable if needed for planning; no specific physical
action is authorized or requested by this build receipt.


## Recovery evidence handoff after #323

The central decision remains **NO-GO**. Source and host-file progress does not
supply the missing physical observations. Carry these specific gates forward:

- Loading: exact current-build initial security entry, caller/callback semantics,
  actual memory ownership and reachable failure exit remain unqualified. Neither
  synthetic link-base agreement nor source address declarations selects placement.
- Restore: two matching offline capture sets and supplied geometry can check bytes,
  not original acquisition or writable post-failure recovery. #315 distinguishes
  host read-only flags, card protection and actual region selection/readback.
  Original RTC/RPMB/security state is outside ordinary image coverage.
- Retained logs: #317 identifies a configured DRAM-console candidate; #319 shows
  initialized-node output alone does not prove reservation success. #320 found no
  standard embedded configuration in the exact packaged kernel. Obtain build-matched
  resolved configuration and runtime ownership/retention evidence before selection.
- Retrieval: #321 records restricted packaged permissions; #323 resolves declared
  removal-before-copy ordering and possible repeated copying. Neither filename
  presence nor policy declarations proves fresh readable logs or authorized access.
- UART: exact PCB identity, isolation, pads, signaling level and captured output
  remain unqualified. Hardware planning is allowed, but no physical action is
  authorized by that preference. The owner confirmed no existing board photos/revision records on 2026-10-27;
  that question is resolved. Qualify an inspection proposal before requesting
  any specific physical action.

Next useful evidence is qualified exact-board inspection evidence or build-matched configuration/
sanitized prior runtime record with provenance. Do not substitute more marker features
or host test totals for these gates. Do not repeat the resolved board-record question. Source-qualify a concrete bounded
inspection proposal and review any supplied evidence before a capture step.
No loading, configuration, boot, hardware or app-reliability runtime gate is closed.
