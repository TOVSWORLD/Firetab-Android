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

## Download-agent selection provenance result

The pinned MTKClient MT8163 `loader` field identifies the 600-byte security
bootstrap payload, **not** the stage1/stage2 storage download agent. Bypass
security uses that payload; DAconfig independently scans Loader for matching
filenames. Confusing them would leave the actually executed storage agent
unidentified. Git metadata establishes repository blob identity only; neither
this payload nor any DA binary was downloaded or executed in this audit.

At revision7cb40e727727dfe3faa065eefb29b16ed29bbdf1,
[DAconfig](https://github.com/bkerler/mtkclient/blob/7cb40e727727dfe3faa065eefb29b16ed29bbdf1/mtkclient/Library/DA/daconfig.py)
lines104–112 recursively collect filename candidates and parse them in reverse
lexical order. Lines207–218 choose the first matching DA code with permitted
hardware/software versions (zero runtime version permits any); setup does not
check subcode. A v6 record can also switch configured mode to XML. An explicit
file alone still needs a recorded matching record and stage identities.

The parser's duplicate filtering at line196 compares the incoming subcode to
itself. This is a verified tautology, not a confirmed tablet compatibility
failure. With equal hardware/software versions, distinct subcode records may
be discarded by this filter. Selection cannot be called device-qualified merely
because a filename or SoC code matches. Our AST audit records this fact without
executing or publishing copied upstream helper code.

The pinned Git tree has six default filename candidates totaling51,627,415 bytes.
Their paths, sizes and Git blob SHA1s are in `evidence/recovery-agent/report.json`;
these are not downloaded-content SHA256s, vendor signatures or compatibility
proofs. No exact DA record/stage bytes for the actual device have been identified.
The source/metadata read was bounded:9558 source bytes plus308770 Git-tree bytes.
No full loader pack or dependencies were downloaded.

Next resolve actual available DA records by capped metadata/header inspection,
only if the remote supports bounded ranges. Identify candidate record versions,
stage lengths and provenance before choosing a binary or running any tool. Stop
instead of silently retrieving a full file when ranges are ignored. Runtime
hardware/software/security facts and signature acceptance remain separate
evidence; no tablet query is authorized by this document. Source UART analysis
remains useful independent work if agent provenance needs unavailable material.

Reproduce the syntax/metadata audit from ignored pinned caches with
`python3 scripts/audit_recovery_agent_selection.py`; synthetic tests are included
in `python3 -m unittest discover -s tests -q` (154 passing). Full Git-tree and
source response hashes are in source-index.json; raw helper source stays ignored.

## Bounded DA record inventory result

Exact HTTP206 header/table ranges work at the pinned raw GitHub URLs. The
reproducible probe read36,080 bytes across all six containers (plus an initial
108-byte range-support probe), instead of51.6MB. It aborts before reading a
non206/wrong-range response, caps requests at512KiB and total metadata at3MiB,
and never requests stage code. The parsed record and range hashes are in
`evidence/recovery-agent-records/report.json`. Four parser/network-policy tests
bring the offline suite to158 passing.

Only two containers declare MT8163 records: MTK_DA_V5 record40 and
MTK_AllInOne_DA_mt6590 record19. Both declare hardware version0xCA00, software
version0, subcode0 and three regions. V5's stage1/stage2 declared lengths are
65,352/254,872 bytes; the mt6590 container declares72,552/260,920 bytes. Each
of these stages declares a256-byte signature tail; presence/length does not
verify its signature or acceptance. Record page size4096 is DA metadata, not
evidence of the tablet's raw logical sector size.

Under the audited default reverse-filename scan and version checks, V5 is the
first eligible matching record if runtime hwver permits0xCA00 (or is0), swver
permits0, and no explicit loader overrides the inventory. V6 has no MT8163
record in this pinned tree. This narrows the likely default container/stages;
actual runtime selection and backend capabilities remain unobserved. Pinning
repository files alone does not establish vendor provenance, stage-content
digests, signature validity or a safe bootstrap.

Next bounded work can hash and statically identify just the two candidate V5
stages (~320KiB total) after preserving their declared extents; never execute
them. Avoid retrieving the whole container. Agent side effects and current
security acceptance remain unqualified independently of identity. No physical
operation, loading address or test package is authorized by this inventory.

Reproduce metadata only with
`python3 scripts/probe_recovery_agent_records.py --download-metadata` (network
required; stdout is the metadata report). Cache/report changes should be reviewed
against the pinned source and exact range receipts before any later stage probe.

## Original V5 stages identified; uploaded identity still open

Read only the declared V5 record40 stage1/stage2 extents:320224 bytes total.
Cached binaries remain ignored/private and were never executed, emulated or
patched. `evidence/recovery-stage-identity/report.json` records exact ranges,
whole-stage SHA256 and separately hashed declared code/signature portions.
Stage1 SHA256 is662bae417999c33930bcd68d7e7b41af6da0c1da0cf776b9202b3fb5e8c16915;
stage2 isaf41a0bdd7162c272f317fb9960977d2e62c0829a9f4d7a60b7c7720e24a6c35.
These pin original bytes at the selected URL/extents; full-container Git blob
verification and vendor signature validation have not been performed.

The audited legacy uploader (dalegacy_lib.py lines576–608 at the same pinned
revision) conditionally passes stage2 through the extension patcher and updates
stage1's matching hash before sending/jumping to stages. Thus original file
hashes alone cannot identify what an eventual invocation uploads. This audit
parsed the extension source as AST only; no patch functions were invoked and
no modified stage was generated. Its source hash and nonoperational call-site
summary are retained. The patcher operates on byte buffers; this does not prove
the eventual binary agent/bootstrap has no persistent effects. Other extension
commands include storage modifications and key handling and must not be invoked
as incidental discovery steps.

Reproduce the original identity checks with
`python3 scripts/verify_recovery_stage_identity.py`. If the ignored cache is
absent, `--download-original-stages` retrieves only the pinned320224 stage bytes
and22383-byte extension source under bounded reads, verifies expected SHA256
before caching, and still never imports/executes the helper or stages. Published
files contain only our verifier/tests and metadata/call summaries. Two new
synthetic tests (160 total) check digest boundaries and parse-without-execution.

The binary identity subtask is now bounded and complete for these original
candidate extents. Safe entry, actual uploaded identity, security acceptance,
indirect storage effects and restore are unresolved; guessing from names or
embedded diagnostics cannot close them. Next independent development is the
cached UART source/driver contract and a precise physical-interface evidence
request once that source contract is established. No tablet action is requested
or authorized by this identity report.

## UART source/diagnostic DT contract result

Audited the exact reviewed primary-only DTB
ef23af15f7136613a98b450f3d1db7c860f581024d194e88e2ef8c3116f2eb43 against the
pinned ACK driver and resolved diagnostic config. `evidence/uart-log-contract/`
records source/config/DT hashes and source facts; no device transport was used.
The serial0 alias resolves to enabled /soc/serial@11002000 with921600n8 options,
mt6577 fallback, baud/bus clock names and DMA/pinctrl properties. These are
properties of our donor-derived diagnostic DT, not proof of board routing.
The corresponding legacy douglas source also enables uart0 at11002000; its
console string is source intent, not observed wire framing.

EARLYCON,8250,8250_CONSOLE and8250_MT6577 are already built in. **The reviewed
DT's bootargs contain neither an explicit earlycon nor console request.** The
resolved built-in CMDLINE is empty. This is a concrete configuration gap for an
explicit early-console experiment; it is not proof no runtime console can ever
appear, because runtime OF-console selection and loader-provided arguments are
separate paths. The prior LK audit shows bootargs may be replaced, so adding a
DT argument alone cannot establish its actual delivery. No argument/DT was
changed or image packed by this audit.

The ACK driver (8250_mtk.c lines664–676) maps its early path to MEM32/regshift2
and generic8250 early setup. That small setup does not enable the runtime baud/
bus clocks or establish physical pin routing. The normal probe separately
requires clock/resource/interrupt setup (lines480–566); console-related source
handling assumes firmware-initialized UART settings in relevant paths. Thus
compiled-in support, schema-compatible fallback and enabled status alone do not
qualify first-byte output. Early capture requires the correct actual UART left
usable by firmware, a delivered activation request and a verified electrical
connection. Runtime handoff requires the normal probe's providers as well.

Two synthetic tests (162 total) verify alias/config assessment, unresolved-target
rejection and that source support cannot promote physical qualification.
Reproduce from the existing reviewed DT/tool cache with
`python3 scripts/audit_uart_log_contract.py`; it reads and snapshots, never
mutates the DT or contacts the tablet. No new downloads or dependencies.

Next investigate authoritative douglas-specific pad/electrical evidence before
proposing a physical UART connection. If unavailable, record the exact missing
board evidence and continue the independent safe-entry/USB read-back source
work. Do not ask the owner to guess pads or voltage, and do not present a source
MMIO base as a wiring instruction. A first diagnostic still needs both a safe
recoverable loading route and a complete log transport.
