# Douglas recovery and first-log qualification

Status: **no physical test authorized by this document; loading/restore/logging
are not qualified**. This plan defines the evidence needed for #106/#21/#22.
Generic kernel compilation, QEMU execution and synthetic backup checks are
complete scopes. None establishes tablet entry, boot, hardware or app operation.

## Current route decision

Prioritize a separately reviewed read-back bootstrap over the archived unlock
sequence. MTKClient is a source candidate, not a selected working tool. Its exact
agent provenance, bootstrap effects, backend and acknowledged region selection
must be resolved before trusting a backup. The legacy reader currently ignores
failed region selection; this must fail closed in any future collector.

The archived rooted path rejects the observed PL7/LK3/TEE262. The minimal path
assumes prior changes and writes GPT, boot-region headers, RPMB and other regions.
The brick route intentionally changes boot storage. Neither is an acceptable
first read-back procedure. Existing source evidence is inventoried in
[sequence-gates.json](../../evidence/recovery-material/sequence-gates.json).
The older preloader/LK byte identity is now resolved against Amazon-hosted build
50.6.3.6_user_636558520. That formerly missing identity is not an open gate;
installed rollback/signature acceptance and recovery remain open.

No downgrade, unlock or erase is proposed by this plan. If a later route requires
persistent change, it needs an explicit affected-region inventory and a concrete
owner-reviewed recovery procedure before execution.

## Ordered acceptance evidence

1. **Entry and bootstrap:** pin the chosen source, agent binary hash and origin;
   determine the actual backend, required starting state and every executed
   stage. Review indirect protocol/MMIO effects. Specify a failure/timeout exit
   that does not intentionally damage storage. Evidence must explain why this
   installed security state can use that route. A douglas configuration comment
   is insufficient.
2. **Escrow acquisition:** demonstrate acknowledged selection and raw geometry
   for user, both boot regions and every other state the route might change.
   Stop on selection failure, short reads or inconsistent geometry. Preserve
   independently acquired reads and a private acquisition record. Avoid writing
   to establish whether a read path works. Use the offline verifier for lengths,
   digests and both GPT locations; it cannot certify collector correctness.
3. **Restore compatibility:** map each proposed change to an original artifact
   and an available restore mechanism that remains reachable after the expected
   failure. Verify component identity, signatures and rollback constraints for
   that exact installed state. State which steps depend on a running OS, a
   modified fastboot, preloader or BootROM. Escrow that can only be restored by
   the component being replaced is not sufficient evidence of a fallback.
4. **Security-state boundary:** explicitly resolve RPMB/key/counter/fuse handling.
   A user/boot-region backup does not cover those states. Reject a sequence that
   zeroes security state while claiming ordinary partition images undo it. No
   such restoration capability is established here.
5. **Host/re-entry:** separately qualify native Mac CLI dependencies, USB backend,
   reconnect/timeout behavior and the actual direct/dock cable topology. No host
   security change is justified merely by generic FUSE installation guidance.
   A source-level fallback import is not a completed Mac runtime test.
6. **Logs before image test:** qualify one of the paths below, including retrieval
   after the failure class being tested. Then qualify image placement, loader
   acceptance and runtime handoff. A black screen is not a useful first result.

Keep the collection record private: source/agent revisions, component hashes,
region geometry, byte counts, command transcript, return codes, timing and USB
state transitions. Publish only reviewed allowlisted facts. Do not publish raw
logs containing device identities or household information.

## Log paths and exact missing evidence

**Live UART:** source boot arguments and MMIO constants suggest a console, but
verified pad mapping, electrical levels, routing and accessible connection are
missing. Early console and runtime driver must agree on the actual UART. Capture
must begin before entry and persist on the host if the kernel dies. Do not infer
pad voltage or prescribe wiring from an SoC register address. No wiring or
physical operation is requested yet.

**Retained RAM:** the generic diagnostic config has PSTORE_RAM=m and lacks a
module loader; its backend is unavailable in that initramfs. Making it built-in
alone does not solve memory ownership, buffer format, reset retention or reading
it after failure. The legacy MediaTek console format differs and contains an
optional eMMC write path. Required evidence is a collision-free firmware-agreed
reservation, a built-in selected backend, bounded compatible reader, and a
verified reset/read-out lifecycle. Do not reuse legacy reserved bytes by guess.
Source/config details: [log-path-review.json](../../evidence/boot-contract/log-path-review.json).

**USB/initramfs:** the current isolated diagnostic has no qualified douglas USB
transport, and it cannot report a crash occurring before that transport starts.
A later USB logger needs matching controller/PHY/gadget support, initramfs setup,
host reconnect behavior and a defined earliest observable checkpoint. A live ADB
session in stock Fire OS does not establish any of those on the new kernel.

Choose a path only when its complete capture/retrieval chain is supported. The
existing sanitized CPU reporter can produce verdicts once userspace executes;
it does not supply the missing physical transport.

## Required diagnostic attempt record

Before requesting an owner-operated attempt, provide a concrete package with
kernel/DT/initramfs/package hashes, exact source/config revisions, selected load
method and addresses, memory ownership evidence, known persistent effects, log
capture instructions, expected checkpoints, timeout/stop criteria and qualified
return-to-stock steps. Do not mark the package ready without those prerequisites.

During a future separately authorized attempt, distinguish loader acceptance,
kernel entry, early console, DT/memory/timer/interrupt setup and the initramfs
marker. Record the actual recovery outcome separately. Secondary CPUs, storage,
display, Android, Google services and Crestron reliability remain later gates.
No diagnostic package meeting these conditions exists yet.

## Next bounded development task

Resolve the candidate's DA selection and agent source/binary provenance using
pinned repository metadata and bounded source inspection. Produce the required
artifact/version/hash inventory and identify any binary-only dependencies before
installing tools or downloading large payload sets. In parallel only where
independent, derive the exact UART source/driver contract from cached sources;
physical pad/electrical evidence remains a separate owner-assisted gate. Do not
return to peripheral/schema cleanup while these recovery blockers remain open.
