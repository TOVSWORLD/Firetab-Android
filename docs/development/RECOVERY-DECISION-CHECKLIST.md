# Douglas: decision before the first physical diagnostic load

**Decision: NO-GO for loading.** This is an evidence checklist, not a procedure
for operating the tablet. Parent issue106 remains open. A compiled kernel and
213 passing host tests do not establish a recoverable physical test.

## The proposed route and its alternatives

Investigate a separately reviewed bootstrap capable of read-back first. The
pinned MTKClient source is a candidate, not a qualified loader. Do not run the
archived unlock sequence as a way to discover whether it works: its installed
version gate rejects PL7/LK3/TEE262, and its alternatives modify boot/security
state before a complete recoverable escrow is established.

- **USB-only route:** current-build entry, security state, agent selection and
  return after failure are unknown. An OS connection or a source configuration
  entry does not prove BootROM access. No USB-only transition is established.
- **Owner hardware access route:** a planning preference is pending. Permission
  to open the case would not establish a safe short/test point, board revision,
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

The only pending owner input now is the already-asked planning choice: hardware
access acceptable or USB-only. No case opening, measurement, USB command or
other tablet operation is requested by this checklist. Do not ask for an
unreviewed mode/security probe just because those facts are missing.

Independent next work is to review an explicit minimal mode/security collection
plan and its exact effects from the pinned source, without executing it. Separate
necessary protocol reads from bootstrap/watchdog/reset actions, and determine
whether a bounded observation can avoid them. If it cannot, document that limit
and the concrete proposed effects for later owner review. Further synthetic test
counts cannot close the six physical evidence requirements above.
