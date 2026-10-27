# Douglas recovery and first-log qualification

Status: **no physical test authorized by this document; loading/restore/logging
are not qualified**. This plan defines the evidence needed for #106/#21/#22.
Generic kernel compilation, QEMU execution and synthetic backup checks are
complete scopes. None establishes tablet entry, boot, hardware or app operation.

## Current route decision

Qualify the original-author USB-first full-stage route described in
[the current entry/return review](CURRENT-STOCK-ENTRY-RETURN.md) as the primary
loading candidate. The February 2026 maintainer clarification distinguishes the
full stage from the incompatible brick-plus-minimal pairing. Exact installed
build success and original-state restoration are still unverified. Hardware
access is fallback planning, not the sole blocker or an approved operation.

A separately reviewed read-back bootstrap remains a preservation alternative,
not a prerequisite already known to work. MTKClient is an unqualified source
candidate: agent provenance, bootstrap effects, backend and acknowledged region
selection remain unresolved. The historical investigations below retain those
findings; they do not supersede the current USB-first research priority.

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
5. **Host/re-entry:** use the available native Linux host for this candidate.
   Host-only checks verified Ubuntu 24.04.5 LTS x86_64, Python 3.12.3,
   PySerial, Ubuntu adb/fastboot package 1:34.0.4-1build3 and dos2unix 7.5.1-1.
   Binary presence is not USB transport qualification: no adb/fastboot or device
   command was invoked. ModemManager is active/enabled and unchanged; any
   temporary pause belongs to a separately approved session with restoration
   of its prior state. Direct USB topology, permissions, reconnect behavior and
   bounded failure exits remain untested. Keep private host access details out
   of public records. Mac research/download access is a separate capability.
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

Acceptance for the next source task: obtain the three original-author archives
within the owner-approved combined 31 MiB download cap, record source URL,
actual size and SHA256, and compare selected script/component identities with
our pinned mirror. Inspect only; do not execute or import archive code. The
approved local destination is ignored `out/recovery-originals/`. Approval covers
static retrieval only, not firmware execution or transfer to a tablet.

The browser download timed out and direct attachment navigation reported
`net::ERR_BLOCKED_BY_CLIENT`; no original archive was found in the destination
or checked download/temp locations. Earlier CLI HEAD requests returned 403.
Original-package matching remains blocked by retrieval, not missing owner
resource approval. Do not claim mirror identity establishes original identity.

Independently reconcile the complete write/restore inventory, including GPT,
RPMB, preloader, TEE, LK and userdata effects. Before any executable proposal,
resolve either qualified pre-change preservation/restore or an explicit owner
choice of test unit and accepted loss limits. Keep #346, #347 and #348 open.
UART or retained-log qualification still requires actual capture/retrieval
prerequisites; launcher terminal output does not demonstrate kernel boot logs.

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

## UART pinmux resolved; PCB/electrical evidence still missing

The reviewed diagnostic DT's UART pinctrl-0 resolves through its actual phandle
to /soc/pinctrl@1000b000/uart0-pins/pins. Decoded values select SoC GPIO79 and80,
both mux function1. Cached legacy MT8163 source sets UART0 RX to the GPIO79
URXD0 function and TX to GPIO80 UTXD0. The legacy driver/header also defines a
swapped function2, and the pin-function header has alternate UART0 functions on
other GPIOs. Thus port identity alone would not establish the pinmux; this audit
follows the actual compiled DT reference. Source hashes and decoded facts are
retained; no pinctrl write or DT modification was performed.

These numbers are **SoC GPIO indices, not accessible PCB pad numbers**. No board
test point, connector location, signal voltage, safe adapter setting or measured
waveform has been established. Do not wire an adapter based on GPIO79/80 or
assume a voltage from another MediaTek board.

A bounded public evidence search on2026-10-26 did not establish a douglas-specific
pad/electrical map. Searches covered douglas/KFDOWI/2017 UART, RX/TX and voltage.
The original [XDA unlock thread](https://xdaforums.com/t/unlock-root-twrp-unbrick-fire-hd-8-2017-douglas.3962846/)
returned403; the [postmarketOS device page](https://wiki.postmarketos.org/wiki/Amazon_Fire_HD_8_2017_(amazon-douglas))
redirect could not be read by the web tool. Those access failures are not proof
that relevant evidence does not exist. General model/regulatory indexes and
other Fire generations are not accepted as wiring/electrical evidence. No
physical opening, measurement or connection is requested at this stage.

The precise missing UART evidence is a traceable board-revision-specific mapping
from routed UART0 signals to accessible points plus established electrical
levels/routing and a validated capture path. Source-level routing analysis is
complete for the reviewed DT; physical qualification remains blocked on that
board evidence. Record it once rather than repeating a negative search each run.
Continue independent recoverable-loading work and resolve early-console request
delivery through the loader. An optional host-only logging DT experiment can be
prepared later, but cannot qualify argument delivery or the physical transport.

The audit now rejects unresolved/ambiguous pin-control phandles. The additional
regression test brings the offline suite to163 passing. Run
`python3 scripts/audit_uart_log_contract.py` to regenerate source/DT findings
from the existing pinned cache. No new downloads, installs or tablet access.

## Kernel-side alternative for argument delivery

An opt-in [forced diagnostic command-line experiment](../../projects/firetabs-android/experiments/commandline-force/README.md)
now supplies a source-supported alternative to LK preserving diagnostic DT args.
It is not compiled or selected by default. FORCE avoids loader argument conflicts
on the audited chosen-node path but discards all incoming args, so firmware
constraints must be audited before use. Its config checker cannot promote
runtime or physical readiness. Static current LK already contains a matching
earlycon token; previous DT-only absence was not final command-line evidence.
Next resolve discarded firmware constraints and use a separately gated compile
only after that profile review. Board electrical/recovery gates remain open.

## Current-stock DRAM initialization data source

The bounded offline inspector `scripts/inspect_preloader_emi.py` finds the same
188-byte EMI data in cached official current build659664620 (PL7) and older
build636558520 preloaders. Both use EMI format16 (0x10), unrelated to Android
version numbering. The data SHA256 is
`4daa46c2e26ed49f94da66088b59f7a8bcdcb2998fd0f0338c3bf5d47cceae97`.
Full input identities, offsets and nonqualification flags are retained in
[evidence](../../evidence/current-preloader-emi/report.json); no raw data is published.

The pinned [extraction implementation](https://github.com/bkerler/mtkclient/blob/7cb40e727727dfe3faa065eefb29b16ed29bbdf1/mtkclient/Library/DA/daconfig.py#L120-L147)
locates this data using the declared signature boundary and loader-info footer.
The [legacy initialization branch](https://github.com/bkerler/mtkclient/blob/7cb40e727727dfe3faa065eefb29b16ed29bbdf1/mtkclient/Library/DA/legacy/dalegacy_lib.py#L345-L391)
includes format0x10, exchanges a length, sends EMI and reads initialization status
and reported memory geometry. Those protocol responses have not been observed.

This resolves the data-source dependency: obtaining this identical configuration
does not itself require flashing the older preloader. It does not resolve entry,
security/bootstrap compatibility, agent acceptance, installed-image equivalence,
actual RAM geometry or recovery. Do not use another board's fallback configuration.
The inspector executes neither firmware nor upstream helper code. Two synthetic
parser tests cover valid metadata and malformed bounds/tags/version;205 tests pass.
Next qualify the source-level initialization response contract and fail-closed
handling before considering any live binding. Physical gates remain open.

## DRAM initialization response contract: source gaps

Static review of the pinned [legacy branch, lines316–407](https://github.com/bkerler/mtkclient/blob/7cb40e727727dfe3faa065eefb29b16ed29bbdf1/mtkclient/Library/DA/legacy/dalegacy_lib.py#L316-L407)
finds four conditions that a future binding must address before it can accept
a successful initialization. The [source receipt](../../evidence/dram-response-contract/source-review.json)
records exact source identity; upstream code was neither copied nor executed.

- The version reply handles ACK and NACK separately. An empty or unexpected
  reply bypasses both branches and can reach the method's final True. This is
  a control-flow finding, not an observed device failure. A binding must accept
  only an exact expected reply and reject every other reply or transport error.
- For format0x10, the agent-requested DRAM length is logged; the local data
  length is sent independently, with no equality check. Current data is188B,
  but the actual request is unknown. Require a separately reviewed length
  agreement before transmitting data; a source comment is not an observation.
- The returned two-byte checksum is logged without comparison. Its algorithm
  remains unqualified; do not label data integrity verified from receipt alone.
- A nonzero initialization status is rejected in the ACK branch. Subsequent
  type, chip-select and size fields use indexing/unpack without explicit exact
  length checks. Truncation may raise; it must invalidate the entire session,
  never leave a reusable success state. Zero status and plausible geometry
  would still be agent reports, not independently verified physical memory.

This review establishes requirements only. No live adapter was installed or
patched. The own exact-reader and supervised synthetic acquisition contracts
address transport boundaries separately; they are not bound to this initializer.
Next inspect the caller's propagation of False/exceptions and whether later
stage loading is gated by a qualified initialization result. Entry/security,
restoration and boot-log capture remain open under106.

## Initializer-to-stage transfer propagation

The own AST audit `scripts/audit_dram_caller_gate.py` pins the reviewed source
identity and verifies every `brom_send` call in `upload_da1` is contained within
the initializer's truthy branch. The [retained report](../../evidence/dram-caller-gate/report.json)
locates the gate at638 and transfer at641. The
[pinned caller](https://github.com/bkerler/mtkclient/blob/7cb40e727727dfe3faa065eefb29b16ed29bbdf1/mtkclient/Library/DA/legacy/dalegacy_lib.py#L638-L678)
returns False when initialization returns False. There are no local try handlers
in this method: exceptions propagate out of this scope rather than reaching
its normal success return. This is not proof of cleanup in outer layers.

The unexpected-version-reply fallthrough identified above is consequential:
it produces True from initialization, so this caller can proceed to stage2
transfer without the successful DRAM status/geometry exchange. The caller does
not independently validate that exchange. This remains a conditional source
path; no such reply or transfer was observed on the tablet.

The [legacy wrapper](https://github.com/bkerler/mtkclient/blob/7cb40e727727dfe3faa065eefb29b16ed29bbdf1/mtkclient/Library/DA/legacy/dalegacy_lib.py#L885-L899)
returns the upload success through a truthiness check. The
[generic dispatcher](https://github.com/bkerler/mtkclient/blob/7cb40e727727dfe3faa065eefb29b16ed29bbdf1/mtkclient/Library/DA/mtk_daloader.py#L315-L319)
sets up configuration/extracts EMI/selects the agent and returns its upload
result. Neither cited wrapper repairs the missing initializer evidence.

Required next implementation is an owned offline initialization-evidence
state gate that cannot authorize stage transfer from a bare Boolean: require
exact replies, reviewed length agreement, complete zero-status geometry report
and separately qualified integrity handling. It must invalidate on timeout or
malformed response. Test with synthetic events only; no live callbacks until
entry, agent selection, RAM placement, restore and logging gates are resolved.

## Owned offline initialization-response decoder

`scripts/offline_dram_evidence.py` now decodes an explicitly delimited response
field mapping without a transport, helper import or stage sender. It requires
an explicit single-byte expected ACK, all seven exact-size fields, requested
length equal to the bounded local EMI length, zero status and nonzero reported
RAM size. Missing/extra fields, unknown replies and truncated/oversized values
raise errors. This is a decoder, not a wire framing parser or ordered session
state machine: the caller supplies field boundaries and their origin is unknown.

Even a complete response returns stage-transfer authorization false. The checksum
algorithm is still unknown, geometry is merely agent-reported, and no provenance
or physical readiness is inferred. There is no opt-in flag to promote these
claims. Three synthetic tests cover every field's size faults and semantic
failures; the full offline suite has210 passing tests. Actual capture, framing,
timeout invalidation and integration with a supervised worker remain separate
work. Next resolve the checksum's source evidence or explicitly reject that
candidate integrity contract; do not silently invent an algorithm.

## Ordered synthetic response-session integration

`OfflineDramSession` in `scripts/offline_dram_session.py` collects the seven
response events in the reviewed order and invokes the strict decoder only after
all are present. Duplicates, reordered/malformed fields, unexpected replies and
failed status invalidate the session and erase partial fields. Explicit abort
models timeout/cancellation; an invalid or already consumed session cannot be
reused. Three synthetic tests cover complete decoding, malformed event order
and abort at every incomplete boundary (213 full-suite tests pass).

This models received-field order only. It has no sender, transport, timer or
helper binding; it cannot enforce native deadlines or prove the intervening
host commands occurred. Integration must use the existing deadline reader and
worker supervision and call abort on every interruption. No result authorizes
stage transfer; this is an engineering guard against accepting partial evidence.

A bounded search of the pinned cached DA Python sources for ENABLE_DRAM and
its sending path found the legacy initializer plus its command declaration.
The initializer logs the returned checksum without deriving/comparing it.
The separate flash-write additive checksum is not evidence for this exchange.
The DRAM checksum algorithm therefore remains unavailable from this reviewed
source path; no algorithm is guessed or treated as verified. This does not prove
that no specification or agent-side source exists elsewhere.

Next consolidate the remaining physical entry/agent/restore/logging prerequisites
into one explicit go/no-go checklist and identify the smallest owner-supplied
evidence needed. More synthetic validation cannot qualify those physical gates.

## Supplied fixed-marker transcript interpretation (#313)

`python3 scripts/decode_offline_uart_markers.py SUPPLIED_HOST_FILE` reads at most
1 MiB from a regular host file and prints only its hash, length, marker counts and
qualified text outcome. It opens no serial port and performs no acquisition.
Only complete exact LF/CRLF lines `FTD1 ENTRY` followed by `FTD1 RETURN` or
`FTD1 ERROR` form a valid single pair. Missing/truncated, repeated, reversed or
malformed marker lines leave the outcome unqualified. Unrelated lines are not
published; source files themselves must remain private unless owner-sanitized.

A valid pair is a statement about supplied text, which can be fabricated or stale.
It proves neither device origin/freshness nor executed agent, drained UART output,
stock return, kernel boot or restore. Even an ERROR pair only reports marker text.
Existing board identity, electrical level, entry/exit and original-state restore
gates stay open. No owner collection action is requested by this parser.

## Cached douglas retained-console route (#317)

The pinned kernel's ARM64 douglas defconfig enables MTK RAM console using DRAM.
This is a configured source candidate, not an installed-config match or an observed
retained log. Exact source hashes and ranges are in the
[receipt](../../evidence/retained-console-route/report.json). Its configured region
must not be reused as a proposed load address; actual memory ownership and cross-boot
retention remain unverified.

The DRAM initialization branch maps the configured region. Initialization checks
signature/size, can clear an invalid-signature buffer, copies the old region into
allocated host-kernel memory, then resets the current Linux log area. The printk
console registration is conditional on CONFIG_PSTORE being absent; the read path
has a separate CONFIG_PSTORE_CONSOLE branch. The symbol combinations must be
established for the actual binary rather than inferred from the feature name.

Late initialization creates `last_kmsg` only if the old-valid flag permits it.
Readout uses the old snapshot, validates header/layout and may fall back to raw
buffer output on corruption. That fallback can include sensitive data and is not
sanitized boot evidence. No raw buffer was acquired or published here.

This route requires a surviving agreed memory region across the relevant failure,
a compatible writer/layout, a later kernel reaching initialization, allocation and
proc creation, and an authorized retrieval path. It cannot presently replace
first-byte UART capture or qualify logs from a kernel that never reached a writer.
Reboot/power retention, recovery accessibility and freshness are untested. No proc
read, reboot, memory access or device operation is requested. Next resolve actual
configuration/layout and retention evidence before selecting this as a capture route.

## Exact packaged stock ramdisk log access (#321)

Static inspection of the cached hash-matched stock boot image adds binary-package
policy evidence beyond the source defconfig. The gzip ramdisk decoded to a bounded
newc archive under a 16 MiB cap; only rc/context text was searched. Component,
archive and matching-file hashes/line references are retained in the
[metadata receipt](../../evidence/stock-log-access/report.json); no raw archive,
init file or log text is published.

The packaged init.rc declares a pstore mount and restricts console-ramoops and
last_kmsg to mode 0440 with system/log ownership. It also declares copying
last_kmsg to `/data/system/SYSTEM_LAST_KMSG`, then mode 0600 and system/system
ownership. The douglas init file separately declares removing this copied file
in post-fs. Actual import/action ordering and operation success have not been
established; do not assume this path survives or contains a fresh log.

These are policy declarations, not proof of available pstore, retained memory,
readable proc entries, a successful copy, permitted shell access or an accessible
recovery environment. Retrieval must account for the active identity, SELinux,
init/data availability, file lifecycle and provenance without changing permissions
or weakening policy. No device read, chmod, mount, reboot or init execution occurred.
Next establish actual lifecycle/access evidence from existing sanitized records;
the kernel configuration/retention and board UART gates remain open.
