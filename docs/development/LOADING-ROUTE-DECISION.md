# Douglas diagnostic loading route decision

Decision2026-10-26: continue developing an observation-first, separately reviewed
RAM-bootstrap route. No physical loading route is qualified. This decision
selects the engineering investigation; it does not select a working exploit,
agent, load address or owner test. Parent106 remains open.

## Route ranking from retained evidence

**First: minimal observation, then a constrained RAM bootstrap.** The owned host
adapter has fake-device transfer/cleanup tests and process supervision. The exact
Mac libusb candidate loads and returns its version without a context. Actual
backend initialization scans devices, so it was not executed. These host pieces
can support a future observation test after entry/return effects are qualified.
Observation must establish fresh mode/version/security facts before agent
selection; it does not itself load a kernel or acquire escrow.

A RAM bootstrap remains plausible source-level work because the pinned candidate
has agent/stage upload paths and matching current-stock EMI data is available.
No persistence-free guarantee follows: bootstrap firmware, MMIO/security effects,
placement, agent acceptance and interruption handling still need review. A tool's
stage2 is its protocol environment, not the Linux kernel or a proven ARM64 boot
trampoline. The next scope is the smallest stage path's actual effects and exit,
not the complete archived unlock script.

**Second: stock fastboot as an observation/return candidate.** Exact-stock LK
registers download/continue/reboot operations in the selected region, but not a
boot command there. Continue reaches a boot-labelled named-record/device-callback
image path with combined16MiB and later verification constraints. Download plus
continue is not an established RAM-boot route. Static registration also does not
prove the current command filter permits the operation. Keep it as a candidate
for a separately reviewed stock-return test, without claiming it loads diagnostics.

**Defer: persistent boot-chain/recovery changes.** The archived software route
intentionally bricks and subsequently modifies boot/security-related storage.
The minimal path assumes prior changes and touches GPT, boot headers, RPMB and
other areas. It lacks the qualified original-state escrow and independent restore
needed here. Modified recovery/fastboot can be useful later, but cannot be assumed
as the current starting state. No downgrade or persistent change is selected now.

## Storage and logging implications

Any route changing boot-chain storage must first preserve original user and both
hardware boot regions with independently verified selection/geometry. The record
store mapping gives a specific reason to include the second boot area; generic
firmware is not a substitute. RPMB/key/counter/fuse state is a separate boundary,
not covered by ordinary image files. A RAM-first route reduces intended writes
but must still establish its actual effects and failure return.

Usable first-kernel logs remain a parallel physical prerequisite. UART routing
source is known, but accessible pads/electrical levels are not qualified; pstore
retention/readout is also not established. Host observation protocol reports are
not kernel boot logs. No package is ready merely because host tests pass.

## Next bounded implementation/research scope

Trace the pinned stage/preloader-stage path from entry through memory writes,
execution transfer and its shutdown/reboot handling. Record exact source hashes,
external firmware dependencies, whether code can restrict itself to observation
and RAM loading, and which failure exits require reboot or persistent changes.
Do not execute it, include payload bytes or patch firmware. Reuse existing source
caches. If the path cannot support a recoverable minimal test, document the exact
reason and compare another path instead of expanding host-policy wrappers.

Sources: [route inventory](../../evidence/recovery-material/sequence-gates.json),
[bootstrap audit](../../evidence/recovery-bootstrap/report.json),
[entry audit](../../evidence/entry-transition-source-audit/report.json),
[current-stock analysis](CURRENT-STOCK-ENTRY-RETURN.md),
[host binding limits](OBSERVATION-BINDING-DESIGN.md),
[pinned stage usage](https://github.com/bkerler/mtkclient/blob/7cb40e727727dfe3faa065eefb29b16ed29bbdf1/README-USAGE.md#L363-L406).

## Pinned stage/plstage review: unmodified helper is not a qualified RAM loader

At the pinned revision, [cmd_stage](https://github.com/bkerler/mtkclient/blob/7cb40e727727dfe3faa065eefb29b16ed29bbdf1/mtkclient/Library/mtk_main.py#L193-L291)
calls the monolithic initializer and crasher before uploading its first payload.
Its second-stage write loop advances only when a write succeeds, without a total
deadline or abort after failed writes. A bad transfer marker is logged; optional
read-back mismatch writes a host file and logs an error but does not return before
the later execution-transfer request. Therefore requesting verification does not
make this exact helper fail closed. These are conditional source findings, not
observed failures or executed transitions on the tablet.

[plstage](https://github.com/bkerler/mtkclient/blob/7cb40e727727dfe3faa065eefb29b16ed29bbdf1/mtkclient/Library/mtk_main.py#L537-L660)
can invoke security bypass, watchdog handling, preloader extraction/patching and
RAM execution depending on configuration. A custom preloader path can be patched
in memory. This is distinct from writing it to flash, but the resulting executed
firmware's indirect effects remain unreviewed. No persistence-free claim follows.
The code's USB close/host exit is not an established return to stock operation.

The [metadata receipt](../../evidence/ram-stage-effects/report.json) verifies
exact cached source identity. Required stage payload code/effects are not reviewed
by this host-method analysis. No payload was downloaded or executed, no helper was
imported, and no firmware patch was produced. Keep the route as an investigation,
not a drop-in test procedure. A Linux/ARM64 handoff is still a separate contract.

Next locate pinned payload source/build provenance for generic stage1, stage2 and
preloader-stage before deciding which can form a minimal RAM-only trampoline.
Audit memory/storage/MMIO/reboot handlers and entry prerequisites together. If
payload source is unavailable, record that exact dependency rather than assuming
that a RAM upload implies no persistent effects. Fixing the host transfer loop
alone would not resolve these firmware and recovery gates.

## Payload source/build provenance and first-stage protocol mismatch

Fetched48202B of four exact-revision source/build files, verifying each Git blob
identity and SHA256. [Public receipt](../../evidence/payload-source-provenance/source-index.json)
contains metadata/links only; source stays in ignored cache. No payload binary,
compiler dependency or full checkout was downloaded. No build/helper was run.

The pinned [stage1 Makefile](https://github.com/bkerler/mtkclient/blob/7cb40e727727dfe3faa065eefb29b16ed29bbdf1/src/stage1/Makefile)
includes generic_stage1 and uses ARM Thumb/Cortex-A9 settings with a bare-metal
GCC/linker script. That is first-stage protocol code, not an ARM64 Linux entry
implementation. Its declared output directory differs from the packaged payload
path; build metadata alone does not prove the shipped1000B artifact corresponds
to the reviewed C source. Stage2 and pl binaries have tree metadata, but matching
source/build recipes were not located in this non-truncated pinned tree. This
is a repository-scoped finding, not proof sources do not exist elsewhere.

The reviewed [generic first-stage C](https://github.com/bkerler/mtkclient/blob/7cb40e727727dfe3faa065eefb29b16ed29bbdf1/src/stage1/generic/generic_stage1.c)
scans BootROM functions, can alter watchdog state and provides memory-write/jump
and watchdog operations. Its read-back command block is commented out, while the
previously reviewed host verifier can request that operation. That is a
source-level protocol mismatch requiring binary/source equivalence or a matched
rebuild before relying on verification. No observed device hang is claimed.
Its jump is a function call with a simple argument, not a proved Linux DT/EL/CPU
handoff. Its reboot command programs watchdog registers and waits indefinitely;
it is not a validated stock-return procedure on douglas.

The [stage2 host tool](https://github.com/bkerler/mtkclient/blob/7cb40e727727dfe3faa065eefb29b16ed29bbdf1/stage2.py)
connects/retries and sends a reboot request; this is not the firmware implementing
that request. Next locate upstream stage2/pl source provenance, or treat those
binaries as unavailable dependencies for the proposed auditable route. A minimal
owned first-stage transfer path can be investigated separately, but must retain
watchdog/entry/verified read-back and ARM64 handoff requirements. Do not execute
these payloads to discover their missing behavior.

## Upstream source search and actual stage1 object compilation

A bounded primary GitHub search checked upstream history for src/stage2 and
src/stage2_static and repository/code-search leads. No matching source recipe
was established. The packaged stage2 binary history lead is
[initial-release commit65d8c4a](https://github.com/bkerler/mtkclient/commit/65d8c4aa8912e5f5d152466362c78ab1fbbfcd47).
This does not supply a reproducible payload source/build mapping. Search failure
is not proof of universal absence; stage2/pl remain unaudited dependencies for
this route. Do not substitute an unrelated fork's binary without provenance.

Useful local development result: the exact generic_stage1 C source **compiled
to an ARM ELF object on this Mac** using bundled Apple clang, without installing
a toolchain or downloading anything. The [object probe receipt](../../evidence/stage1-object-probe/report.json)
retains compiler version, exact command, source/object hashes and size. Three
non-prototype warnings occurred. This is an alternative compiler object probe,
not the upstream GCC build, a linked payload or shipped-binary equivalence.
No object/firmware was executed, packaged or offered for physical testing.

Next complete a bounded reproducible link-tool feasibility check using pinned
startup/linker sources, reporting any missing linker before downloads. If that
works, compare the rebuilt first-stage protocol with its host using static
analysis. The missing stage2/pl source and actual entry/return/logging requirements
still block an auditable complete diagnostic loader; compiling first-stage C
alone does not remove them.

## Local link feasibility: startup assembles, ELF linker is missing

Fetched only562B of pinned startup/linker source, verified against Git blob/SHA256
identities. Startup assembly compiled successfully to an ARM object with bundled
clang. The attempted link failed with exit1: the selected Apple linker rejected
GNU/ELF options (`-Bstatic`, `-EL`, `--build-id=none`, `-T`, `--target2=rel`).
`arm-none-eabi-gcc` was absent from PATH and `ld.lld` was absent from PATH/xcrun
and the checked standard package prefixes. This is a bounded tool inventory,
not a whole-disk proof that no compatible linker exists.

The [retained receipt](../../evidence/stage1-link-feasibility/report.json)
contains source/startup-object hashes and the exact diagnostic. No linked payload
was created or executed. No compiler/toolchain install, large download or paid
resource was started. Reproduce from the existing ignored source cache:

```sh
xcrun clang --target=arm-none-eabi -c out/ram-stage-source/src/stage1/common/start.S -o out/ram-stage-source/start-clang.o
xcrun clang --target=arm-none-eabi -nostdlib -Wl,--build-id=none -Wl,-T,out/ram-stage-source/src/stage1/common/generic.ld out/ram-stage-source/generic_stage1-clang.o out/ram-stage-source/start-clang.o -o out/ram-stage-source/stage1-link-probe.elf
```

Next use an existing Linux CI runner for a small standalone build probe after
checking preinstalled clang/lld availability. Proposed job limits:5minutes,
1GiB free disk, no Android/kernel checkout, no dependency installation and at
most16KiB pinned source inputs. Publish metadata/hashes only, not firmware. If
the linker is absent there too, report exact package/archive requirements before
any toolchain download. Successful linking would still not establish shipped
binary equivalence, ARM64 handoff, safe execution or recovery.

## Standalone Linux CI compile/link probe

`build_stage1_link_probe.py` and the stage1-link-probe workflow now implement the
bounded Linux alternative: preinstalled clang/lld only,1GiB free-disk preflight,
five-minute job limit, three pinned sources totaling11628B, per-download and
compiler timeouts. No package install, Android checkout, binary download or
firmware execution occurs. Missing tools fail with an explicit dependency result.

The driver compiles C/startup, links using the pinned script and checks that the
result is a bounded ARM ELF executable. CI prints source/tool/output hashes and
qualification limits; raw payload objects remain unuploaded in the runner's out/.
A successful link is still not a loadable-device package, GCC/shipped equivalence
or ARM64 Linux handoff. Run status must be recorded separately before claiming
this new probe succeeds. Existing kernel baseline workflows are unaffected.

## Observed Linux link result

The [standalone CI job](https://github.com/TOVSWORLD/Firetab-Android/actions/runs/40386637095/job/121796533606)
compiled and linked successfully using preinstalled clang/LLD 18.1.3. The three
hash-verified inputs total 11,628 bytes; compilation emitted three warnings.
The resulting ARM ELF was 68,672 bytes, SHA256
`1508a0dd3979548cca178ee9f15c7492fd9a4a080ee8118ca884dfef8e7bae48`.
Its entry value zero is relative to the linker script, not a qualified physical
load address. This establishes a working Linux build path for the inspected
first-stage source, resolving the Mac ELF-linker limitation for this probe.

The [metadata receipt](../../evidence/stage1-linux-link/report.json) records the
PR head, base and actual synthetic merge checkout separately. The job executed
`python3 scripts/build_stage1_link_probe.py`; its exact compile/link arguments
are retained in that script at tested merge
`15abe7c2eeb22554802ce3105321c883a75d9e1c`. PR #220 merged as
`5256cb0c1a15a5271e0fd2a801d6a3e1cd9d2e5b` after all five checks passed.
Only metadata is retained here: the runner ELF was not uploaded or recovered.
No firmware ran and no tablet was accessed.

Next inspect ELF load segments, executable entry coverage and section layout
through bounded metadata from another build. Linking alone does not prove a
flat transport payload, equivalence to the packaged 1,000-byte binary, the
readback protocol, safe RAM placement, ARM64 handoff, stock return or boot-log
capture. Recovery issue #106 remains open until those applicable gates have
actual evidence; this result supplies no physical test authorization.

## ELF load-layout gate (#223)

The build probe now calls our static `inspect_stage1_elf.py` parser before
reporting link success. It validates bounded ELF32 ARM headers, program-table
bounds, PT_LOAD file/memory extents and alignment, and requires the entry
(with the ARM Thumb-state bit removed) to fall within executable file-backed
bytes. An entry only in zero-filled memory fails. CI emits load-segment metadata
without code bytes or disassembly. Physical-address fields are reported as ELF
fields, not verified hardware placements. Sections are not analyzed by this gate.

Synthetic tests cover a Thumb entry, BSS extent, non-executable entry, malformed
tables/extents and alignment. Actual layout values await the new Linux CI run;
the earlier successful link receipt predates this stronger check. Neither this
parser nor a passing result qualifies flat payload extraction, readback protocol,
RAM placement, return to stock or boot-log availability.

## Observed footprint and initialization prerequisite (#225)

[Linux layout job](https://github.com/TOVSWORLD/Firetab-Android/actions/runs/40390989927/job/121811611547)
passed the stronger gate at tested merge
`9e33f04f31493384f5e654d394a2e504ac22249a`. The ELF hash matches the prior
build. Its 68,672-byte container contains three load segments: executable bytes
at virtual [0,1456), read-only bytes at [1456,1566), and writable file bytes at
[1568,1576) with a memory extent ending at 1600. Entry zero is covered by the
executable segment. The [receipt](../../evidence/stage1-elf-layout/report.json)
retains exact offsets, flags, alignment and hashes. These are linked coordinates,
not hardware addresses or an authorized memory reservation.

This reveals a concrete loader prerequisite: the last segment requires 24 bytes
of zero-filled memory beyond its file bytes. The inspected
[startup source](https://github.com/bkerler/mtkclient/blob/7cb40e727727dfe3faa065eefb29b16ed29bbdf1/src/stage1/common/start.S)
only switches ARM to Thumb before falling into the linked main routine; it
contains no BSS-clearing loop. The pinned
[Makefile](https://github.com/bkerler/mtkclient/blob/7cb40e727727dfe3faa065eefb29b16ed29bbdf1/src/stage1/Makefile)
uses objcopy to form a flat binary, while the
[linker script](https://github.com/bkerler/mtkclient/blob/7cb40e727727dfe3faa065eefb29b16ed29bbdf1/src/stage1/common/generic.ld)
places BSS after data. A flat byte sender does not by itself establish ELF
zero-fill semantics. This is an unqualified initialization requirement, not
proof that the shipped payload fails: its bytes/build and actual loader state
have not been matched.

Next inspect the pinned sender's exact input/padding and entry assumptions to
establish whether it supplies this memory initialization or requires a separate
owned startup implementation. No flat payload was generated or executed by this
layout investigation. Recovery, physical RAM placement and log capture remain
open gates regardless of footprint size.

## Sender initialization source boundary (#227)

Cached source identities were verified against the pinned Git tree; the
[metadata receipt](../../evidence/stage1-sender-initialization/report.json)
records hashes and selected review ranges. No helper was imported or executed.
[PLTools file reading](https://github.com/bkerler/mtkclient/blob/7cb40e727727dfe3faa065eefb29b16ed29bbdf1/mtkclient/Library/pltools.py#L70-L80)
passes raw file bytes, with no ELF program-header or BSS interpretation.
[Shared preparation](https://github.com/bkerler/mtkclient/blob/7cb40e727727dfe3faa065eefb29b16ed29bbdf1/mtkclient/Library/exploit_handler.py#L50-L108)
can patch the final two words based on sentinel values, pads to four bytes and,
for the insecure DA branch, appends a separate 256-byte signature tail. The
security/exploit branch requests preparation without that signature tail.
The selected
[kamakiri2 sender](https://github.com/bkerler/mtkclient/blob/7cb40e727727dfe3faa065eefb29b16ed29bbdf1/mtkclient/Library/Exploit/kamakiri2.py#L63-L78)
passes the supplied byte count to its write operation. These selected paths
contain no memory-size/BSS input; this is not an audit of every backend.

For the linked probe, a hypothetical flat image ending at 1576 is already
four-byte aligned, so that alignment adds zero bytes and does not supply the
24-byte zero-fill tail needed to reach 1600. We have not generated or transferred
that image. The DA branch's signature tail is protocol data, not proof of an
ELF loader's initialization semantics or accepted device memory layout. The
shipped 1000-byte payload is still not equivalent to this clang-built probe.

The next implementation should own its entry/initialization contract and test
zero-tail construction entirely on the host, before selecting a device loader.
It must also avoid blindly applying the upstream final-word patch convention to
a differently linked image. Such a host image contract cannot qualify security
entry, physical RAM placement, recovery or boot logs by itself.

## Owned host image construction (#229)

`prepare_stage1_host_image.py` constructs an in-memory image from validated
PT_LOAD file bytes and zero-initializes memory tails and gaps. It accepts only
zero-based layouts up to 64KiB with matching physical/virtual address fields,
rejects overlapping memory extents, preserves input bytes and does no upstream
sentinel patching. Synthetic tests cover preserved bytes, zero tails/gaps and
rejected layouts. The Linux build probe now emits its image size/hash and
initialization counts, without saving/uploading that image or executing it.

This is a host layout construction contract, not a selected physical loader.
Actual probe-image measurements await CI. Position independence/relocations,
CPU/cache state, safe physical placement, security entry, transport compatibility,
stock restoration and useful logs are not established by this constructor.
No device command or helper execution path is attached to it. Next inspect the
actual CI image receipt, then qualify relocation and entry assumptions before
any physical loading proposal.

## Actual host image and relocation/entry boundary (#231)

The [Linux image job](https://github.com/TOVSWORLD/Firetab-Android/actions/runs/40397672319/job/121834928446)
constructed a 1600-byte host image, SHA256
`fba4681457cdcf32a0a1541ff7a3dc429b35341ef97d1c1e05eddde40985e79e`,
including 24 segment-tail zeros and two gap zeros. The
[receipt](../../evidence/stage1-host-image/report.json) records the actual tested
revision and source ELF hash. Image bytes were not uploaded or retained locally.
This resolves host construction only, not device loading.

The constructor now additionally requires a bounded ordinary ELF section table
and rejects nonempty REL, RELA or DYNAMIC sections and malformed file extents or
relocation record layouts. CI emits counts only. A stripped image without a
section table fails this host gate. Absence of relocation records is not proof
of position independence: already-resolved absolute addresses can remain in
machine code or data. Actual section-gate results await the new CI run.

The pinned [startup](https://github.com/bkerler/mtkclient/blob/7cb40e727727dfe3faa065eefb29b16ed29bbdf1/src/stage1/common/start.S)
sets neither a stack nor a CPU exception level/mode; it switches instruction
state and falls into the linked main routine. Thus the current source relies
on inherited stack and processor state. The
[main routine](https://github.com/bkerler/mtkclient/blob/7cb40e727727dfe3faa065eefb29b16ed29bbdf1/src/stage1/generic/generic_stage1.c#L176-L198)
also reads the BootROM mapping at zero and scans it. A successful host constructor
cannot establish those runtime mappings, memory permissions, stack bounds or
cache state. No actual entry-state contract has yet been obtained from a
qualified loader. Next inspect emitted address references/entry requirements
statically before proposing an owned startup or relocation contract; stock
restore and usable boot logs remain separate prerequisites.

## Emitted address references and immediate stack dependence (#233)

The [Linux relocation-gate job](https://github.com/TOVSWORLD/Firetab-Android/actions/runs/40399916804/job/121842687478)
passed: ten sections, zero nonempty relocation sections and zero nonempty dynamic
sections. Its initialized host-image hash remains
`fba4681457cdcf32a0a1541ff7a3dc429b35341ef97d1c1e05eddde40985e79e`.
The [combined receipt](../../evidence/stage1-entry-address-review/report.json)
retains exact CI checkout/head/merge and the separate local object review.

Static `llvm-objdump -dr` inspection of the existing hash-verified Apple clang
ARM object found 31 R_ARM_REL32 and ten R_ARM_THM_CALL references. These include
relative references to globals and local calls, supporting position-relative
code generation for those selected references. This object was built by Apple
clang 21, while Linux used clang 18; it is not byte-equivalence evidence for the
Linux image and does not prove every address reference is position independent.
Raw disassembly stays in the ignored cache; only counts/hashes are published.

More concretely, the local emitted main routine immediately reserves eight
bytes from inherited SP and writes through that stack before establishing any
owned stack. The pinned startup contains no SP assignment. Eight bytes is the
initial local reservation, not maximum stack usage: calls, other paths and
external BootROM routines need additional analysis. Merely zero-filling the
1600-byte image therefore does not supply a safe execution context.

Next implement a bounded diagnostic entry experiment with an explicit owned
stack and observable entry marker, compiled and inspected only. Its stack must
be image-relative and kept distinct from unqualified physical placement. It
must not call the upstream hardware-scanning main or attach a USB loader until
its CPU state, security entry, restore and log prerequisites are qualified.

## Owned diagnostic entry experiment (#235)

`diagnostic/entry/entry.S` is our compile-only ARMv7 experiment. It computes its
own image base, assigns SP to an eight-byte-aligned in-image 1KiB stack, writes
`0x46544b31` to an in-image marker and loops. It has no external calls, peripheral
access, USB binding or upstream main. It clobbers registers/SP and deliberately
does not implement return; it is not a recoverable test package.

Actual local Apple clang compilation succeeded. Static object inspection shows
SP assignment before the marker store; the marker is at offset 36 and stack top
at 1064. The [compile receipt](../../evidence/owned-entry-compile/report.json)
retains hashes and observations. The linker script asserts zero entry, stack
alignment/size and marker separation. Linux CI now compiles/links the owned
source and runs the existing bounded image/relocation gates, printing metadata
only. Actual Linux link/image result is pending; no binary execution occurs.

The experiment assumes ARM instruction-state entry and readable/writable/executable
mapping for the image, including its stack. It changes no exception mode, MMU,
cache or interrupt state. The memory marker is not yet a log channel: no qualified
reader observes it, and a final loop cannot return to stock. Next inspect the
actual Linux link and design an explicit caller-state/return ABI plus bounded
host marker decoding before any physical loader proposal. Safe RAM placement,
original restore and usable boot-log capture remain unresolved.

## Callable entry ABI experiment (#237)

The original owned loop entry now has an actual successful
[Linux link receipt](../../evidence/owned-entry-link/report.json), from
[job 121864827490](https://github.com/TOVSWORLD/Firetab-Android/actions/runs/40406304083/job/121864827490).
It linked and passed the image/relocation gates without execution. The separate
`diagnostic/entry/callable.S` experiment now provides a caller-return sequence:
save inherited SP in r3, establish the private stack, write the marker, restore
SP, set r0 to zero and branch through unchanged LR. r4-r11 are untouched;
r0-r3 are scratch. No external calls or hardware access occurs. Local compile
and static ordering inspection passed; the
[receipt](../../evidence/owned-callable-compile/report.json) retains source/object
hashes. Linux CI now builds both variants; callable link results remain pending.

This ABI requires a caller that entered ARM state with a valid return LR and
allows ordinary scratch-register clobbering. The caller must provide a writable,
executable image mapping and a processor/interrupt context in which this leaf
sequence is valid. The code does not change CPU mode, interrupt masks, MMU or
cache state; it cannot recover from an invalid mapping or exception. Restoring
SP and branching through LR is not a verified return to stock firmware: no
qualified loader has established these preconditions or invoked it. The marker
still has no qualified readback or visibility guarantee.

Next add a bounded host decoder for the marker and its image identity, using
supplied synthetic snapshots only, and identify which loader can establish the
caller ABI. Do not attach a device transport to this experiment from a successful
compile/link result. Original-state restore and boot-log transport remain gates.

## Supplied marker snapshots and actual callable link (#239)

Both owned variants linked successfully in
[Linux job 121871790870](https://github.com/TOVSWORLD/Firetab-Android/actions/runs/40408334717/job/121871790870).
The loop image is 1064 bytes, SHA256
`bcff63cef809b27760596e4fef6812eee4f87d6f08f09e67d2e40ace51f27a88`;
the callable image is 1080 bytes, SHA256
`da9b6db9e957624a75e1420605e311aeef15221d5b86ab65a7aea91f8e68a2c5`.
The [receipt](../../evidence/owned-callable-link/report.json) records exact source,
compiler, tested revision and image gates. Neither image was executed.

`decode_diagnostic_marker.py` accepts only supplied immutable bytes: reviewed
image identity, pristine before snapshot and exact-size after snapshot. It checks
code/padding equality outside the marker/stack, accepts zero or the known marker,
and reports the supplied transition plus stack-byte differences. Variant offsets
are explicit for these owned layouts. CI now mutates a host copy of each linked
image to exercise the decoder; those synthetic mutations are not execution.
Tests cover both variants, wrong identity, changed before/code, unknown marker,
wrong sizes/types and unchanged snapshots. The expected image hash must come
from a separately reviewed build receipt; caller-supplied bytes/hashes do not
prove acquisition origin, freshness, runtime execution or caller return.

Next investigate an actual loader's ability to invoke and regain control from
this callable ABI and acquire a bounded marker snapshot. A decoder cannot supply
that transport. Existing upstream generic-stage readback is commented out in
source, so assuming its host read request works would leave the central logging
gap unresolved. Keep that source/protocol dependency ahead of new diagnostic
features; physical security entry, safe RAM mapping and restore remain open.

## Loader return/readback protocol incompatibilities (#241)

The hash-verified pinned
[generic-stage command loop](https://github.com/bkerler/mtkclient/blob/7cb40e727727dfe3faa065eefb29b16ed29bbdf1/src/stage1/generic/generic_stage1.c#L281-L400)
invokes its supplied jump target as a C function. If that function returns,
control breaks out of the switch and resumes the command loop. It emits no
call-completion ACK. The existing
[host stage command](https://github.com/bkerler/mtkclient/blob/7cb40e727727dfe3faa065eefb29b16ed29bbdf1/mtkclient/Library/mtk_main.py#L247-L290)
waits instead for a stage2 startup ACK after jumping. Our callable leaf only
writes memory and returns; it cannot satisfy that host expectation. A C return
to a command loop also does not return to stock firmware.

Readback has two distinct source mismatches. The read handler is entirely
commented out; unknown commands fall through without consuming an address or
length. Sending the host's read request would leave those words to be interpreted
as the next command-loop magic, potentially exiting into the final infinite
loop. Separately, even the commented read handler has its completion ACK
commented out while the host expects one. Merely enabling the read block would
not by itself make that host transaction compatible. These are source-level
inferences, not observations of the packaged binary or tablet.

The [receipt](../../evidence/loader-return-readback-gap/report.json) retains source
hashes/ranges and explicit limits. No helpers were imported, no firmware ran,
and no read/jump request was sent. Do not attach the owned leaf or marker decoder
to this unqualified host route. Next implement a small owned, bounded host-only
call/read transaction specification with explicit completion and exact read
lengths, then establish a matching auditable agent implementation before physical
entry qualification. This leaves original-state restore and log transport open.

## Owned offline call/read specification (#243)

`offline_diagnostic_protocol.py` defines an owned, incompatible-with-upstream
byte protocol and state model. It has no USB/backend imports, firmware agent,
acquisition or execution. Requests use 16-byte little-endian headers:
`<4sBBHIHH>` = magic, version, operation, reserved/status, sequence, offset,
length. Request magic is FTDQ; response magic FTDR; version is one. CALL=1 has
zero offset/length and targets only a prequalified fixed slot, never an arbitrary
address. Its explicit matching zero-status completion must arrive before READ=2.
Reads are relative to a fixed 1080-byte callable image, at most 256 bytes each;
responses must echo operation, sequence and range with exactly the stated bytes.

A session permits one pending transaction and one completed CALL. Malformed,
nonzero-status, replayed or mismatched responses poison it. `abandon()` records
partial I/O/timeout and prohibits reuse. This model supplies no clock, deadline,
I/O cancellation or agent implementation; a future transport must establish
those separately. Sequence echoes are transaction matching, not authentication
or physical freshness proof. Matching completion bytes are not evidence that a
real call returned until a separately qualified agent supplies them.

Synthetic tests cover completion-before-read, bounds, unknown operations,
status/length/replay rejection and abandoned sessions. Next implement the matching
owned command dispatcher against injected host-only callbacks and then compile
an agent for static inspection. Do not graft this format onto the existing
upstream generic stage; security entry, RAM placement, original-state restore and
usable boot-log acquisition remain open physical gates.

## Matching host-only dispatcher (#245)

`offline_diagnostic_dispatcher.py` validates complete supplied request frames
before invoking injected synthetic callbacks. CALL completion is constructed
only after the fixed-slot callback returns integer zero; READ completion requires
exact immutable bytes. Invalid headers, ordering, ranges, callback failures,
replays and reentrancy poison the dispatcher. Both host and dispatcher now limit
a session to sixteen transactions, enough for one CALL plus five <=256-byte
reads covering the 1080-byte image. Neither provides a clock or cancellation.

The integration test changes a synthetic memory marker in a Python callback,
then reads the full synthetic image through matching framed completions. It also
tests failures before callbacks, short reads, replays, budget exhaustion and
reentrancy. This is host model execution, not ARM firmware or device execution.
There is no physical callback/backend/transport binding and no proof of loader
entry or return. Next implement the same bounded request dispatcher in owned
freestanding C, compile for ARM only and compare protocol vectors on the host
without executing firmware. Original-state restore and log acquisition remain
separate unresolved requirements.

## Owned freestanding C dispatcher core (#247)

`diagnostic/protocol/dispatcher.c` implements the owned bounded frame contract
with injected fixed-slot call/read callbacks and no entry, transport, USB, MMIO
or memory-map binding. It validates header/order/range/output capacity before
callbacks, limits sessions to sixteen transactions and publishes completion only
after successful callback return. Read callbacks must return the exact requested
count; errors invalidate the context and publish zero response bytes. Callers
must supply separate valid request/response/context storage, zero-initialize the
context and discard any output bytes after errors. Callback memory safety and
bounded completion remain caller obligations; this core cannot preempt callbacks.

Actual ARM Thumb/Cortex-A9 object compilation passed with warnings-as-errors;
static symbols showed no undefined dependencies. The
[receipt](../../evidence/owned-c-dispatcher/report.json) retains source/header/
object hashes and exact compile command. The ARM object was not executed.
Separately, a native host C unit executable uses synthetic arrays/callbacks to
exercise call completion, a full 1080-byte read, replay/order/capacity/short-read
and session-budget rejection. It does not use hardware, firmware or device I/O.
The repository host suite now has 264 passing tests.

This is a protocol core, not a bootable agent. Next compare native C response
vectors directly with the Python contract, then integrate an owned entry context
and statically link with explicit callback/transport requirements. No callback
may be bound to live tablet access during automatic runs. Qualified security
entry, safe physical placement, original restore and log acquisition remain open.

## C/Python protocol response vectors (#249)

The native host vector runner compares the C core against the Python dispatcher
for 76 synthetic sessions/171 request frames: complete image read, 64 header
mutations with sticky followups, read boundaries, truncated requests and the
transaction budget. Status, response length and every returned byte match.
Valid responses also pass the host-side protocol model and reconstruct the
1080-byte synthetic image with its changed marker. The
[receipt](../../evidence/diagnostic-protocol-vectors/report.json) records exact
source hashes and counts; all 267 host tests pass. This is selected-vector
agreement, not exhaustive equivalence, ARM execution, native/target ABI equality
or actual call-return evidence. No device transport is used.

Next statically link the owned C core with an explicit agent entry/context and
injected transport ABI, keeping callback addresses and image bounds outside the
wire protocol. Establish bounded framing/cleanup requirements before any live
binding. Security entry, safe placement, original restore and usable boot-log
capture remain unresolved regardless of these host protocol results.
