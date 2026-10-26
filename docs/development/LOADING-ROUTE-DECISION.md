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
