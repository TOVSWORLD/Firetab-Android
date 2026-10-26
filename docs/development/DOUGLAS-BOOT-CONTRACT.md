# Douglas diagnostic-boot contract — issue #21

This is source evidence and a test design, not a bootable image or permission to
modify the tablet. No temporary-boot route has been established for the user's
Fire OS 5.7.1.0 tablet. Do not execute unlock/recovery helpers as a discovery step.

## CPU firmware contract

Legacy [mt8163.dtsi](../../evidence/kernel-audit/legacy/arch/arm64/boot/dts/mt8163.dtsi)
uses `arm,psci`, SMC and explicit function IDs. Its CPU nodes use `mt-boot`.
Legacy [mt_psci.c](../../evidence/kernel-audit/legacy/drivers/misc/mediatek/base/power/mt8163/mt_psci.c)
first calls the common PSCI CPU-on implementation, then vendor
`spm_mtcmos_ctrl_cpu`; prepare also initializes vendor MTCMOS state. ACK's
[cpu_psci_cpu_boot](../../evidence/boot-contract/ack/arch/arm64/kernel/psci.c)
calls firmware CPU_ON without that vendor power sequence.

The donor [SoC DT](../../evidence/dtb-compile/inputs/arch/arm64/boot/dts/mediatek/mt8163.dtsi)
instead declares `arm,psci-0.2`. ACK's [PSCI implementation](../../evidence/boot-contract/ack/drivers/firmware/psci/psci.c)
supports BOTH the older explicit-ID binding and version-probed 0.2/1.0 bindings.
Thus the old binding itself is not an established kernel blocker. Firmware
version/conduit and CPU power ownership are unresolved on the actual tablet.
Do not infer that changing the compatible string upgrades firmware.

A later single-CPU diagnostic is a possible way to isolate CPU_ON/MTCMOS work.
It would still require valid initial CPU state, memory/DT handoff and interrupt
initialization. It would not validate secondary CPUs, idle, suspend or poweroff.
No such configuration or physical test has been qualified yet.

## Memory and reservations

Both the legacy douglas source DT and donor common Amazon DT declare RAM at
0x40000000 with size 0x20000000 (512 MiB). This contradicts using that source
value as the complete 1.5 GiB hardware map. It does not prove the running stock
kernel only sees 512 MiB. Legacy [mtk_memcfg.c](../../evidence/boot-contract/legacy/drivers/misc/mediatek/mem/mtk_memcfg.c)
reads the runtime flattened DT `reg`, `orig_dram_info` and `mblock_info` properties.
That demonstrates an input format, not the bootloader mutation that produced it.
Memory nodes with `device_type = "memory"` are accepted regardless of node name;
a fallback checks `memory@0` when device_type is absent. The loader's own node
lookup behavior remains unknown.

The legacy source reserves ATF at 0x43000000/0x30000, RAM console at
0x44400000/0x200000, mdump at 0x4bd00000/0x300000, log memory at
0x44600000/0x20000, and a dynamically placed/aligned 2 MiB CONSYS allocation.
These are source declarations, not verified current firmware reservations.
The log node's unit address says 46600000 while its reg says 44600000: preserve
this discrepancy for investigation rather than choosing the node name as truth.
The donor retains the ATF region and adds an audio DMA pool but omits several
legacy reservations. Its ATF comment says 128 KiB while reg is 192 KiB.

Before diagnostic boot, establish the runtime memory regions and firmware/log
reservations from matched boot artifacts and later authorized read-only device
evidence. Do not merely enlarge reg to 1.5 GiB or discard firmware reservations.

## Loader, image and recovery prerequisites

The existing device tree's BoardConfig identifies a 16 MiB boot partition; older
build references use Image.gz-dtb/header-v0 packaging. They do not establish what
the untouched stock loader accepts. The early generic Image was 41,286,144
bytes uncompressed. The later [restricted diagnostic build](DIAGNOSTIC-KERNEL-CONFIG.md)
measured Image.gz at 9,187,928 bytes; the isolated initramfs also compiles (#41).
Combined DT/ramdisk/header/trailer fit and actual partition size remain unverified.
Raw Image size alone neither proves nor disproves fit.

A [model-verified OTA candidate](STOCK-OTA-INSPECTION.md) now supplies actual
boot-header evidence: KFDOWI/douglas/MT8163 build659664620, 2KiB pages, a
512-byte kernel prefix before gzip/AArch64 data and an unclassified2KiB trailer.
Installed-build equivalence, marketing-version mapping and signatures are not
verified. Those header fields are evidence for review, not validated new-kernel
load addresses or a recovery package.

Inspected chaosmaster/amonet revision
`2d8a4e6f73d9dab42d313c9cd751802b23ea7d31` contains persistent modifications in
modules/main.py, including GPT, preloader, LK, TEE and boot/recovery writes.
The name boot-fastboot.sh is not proof of a stock temporary-boot capability:
it invokes a handshake helper. No amonet script was run. Its compatibility with
this exact installed build and a verified recovery route remain unresolved.

Before proposing a physical procedure, record matching firmware/loader identities,
partition layout, entry point/exception-level expectations, DT and initramfs
placement/alignment, loader image format checks, available nonpersistent boot
mechanism (if any), and a tested recovery procedure appropriate to the actual
unlock state. Do not assume custom TF-A, U-Boot or recovery is already present.

## First discriminating test

Qualify a physical diagnostic image only after the above contracts are resolved.
Isolated restricted kernel and minimal initramfs compilation are complete; no
combined image has been packed or booted. Keep its userspace independent of
Android and internal storage: print
explicit initramfs progress markers, provide a controlled idle endpoint, and
avoid mounting/writing user partitions. Display, Wi-Fi and Google services are
not prerequisites for this early experiment. No diagnostic image is packed here.

Choose and validate a log path before testing. UART settings in old bootargs are
source hints, not evidence of accessible pads or compatible electrical levels.
Legacy RAM-console reservations do not establish ACK ramoops/pstore compatibility.
A black screen without logs cannot distinguish loader rejection, early crash,
console failure and a running kernel without display support.

Record checkpoints separately: loader accepts image; kernel entry; early console;
DT/memory and timer/interrupt initialization; diagnostic userspace marker; and,
later, secondary CPUs and storage. For every attempt record exact source/config,
DT/image hashes, command line, loader state, method, complete captured log and
recovery outcome. The user must separately authorize and perform physical tests.

## Still open

Source findings do not complete #21. Runtime firmware/memory handoff, exact image
contract, usable log capture and recoverability are prerequisites still lacking.
Coordinate storage/console #22, matched schemas #27 and provider integration
#18–#20. The restricted diagnostic kernel now compiles and executes its isolated initramfs
on a generic QEMU virt platform (#49). This is not an Android/douglas boot result.

The [candidate's actual appended DTBs](STOCK-DTB-CONTRACT.md) now corroborate the
legacy source: two versions(pre_evt/hvt), static512MiB memory, legacy explicit-ID
PSCI with CPU0 mt-boot, and ATF/RAM-console/mdump/low-log/CONSYS reservations.
Selection, runtime fixups and secondary-CPU behavior remain unverified. Read-only
stock collection includes the individual DT version property for later evidence;
no device transport was executed.

## New Image placement versus the stock candidate

The [executed generic kernel report](../../evidence/qemu-diagnostic/generic-runtime-result.json)
records text_offset=0, image_size=29360128 (28 MiB), flags=10 (little endian,
4 KiB pages, flexible physical placement). The [ARM64 boot ABI](https://docs.kernel.org/arch/arm64/booting.html)
requires the Image entry address minus text_offset to be aligned to 2 MiB and
at least image_size bytes available from entry. Flexible placement does not
remove that alignment requirement. The candidate boot header's kernel address
is 0x40080000. With this new Image, that yields a base misaligned by 0x80000.
Consequently, copying the old header address and loading/jumping there unchanged
would violate this kernel's ABI. This is a verified conditional mismatch, not
proof the stock loader actually uses that field without relocation.

The conditional occupied range would end at 0x41c80000, below the candidate's
static ATF reservation at 0x43000000. That arithmetic alone does not establish
safe RAM: compressed staging buffers, loader work areas, DT/initramfs placement,
firmware reservations and runtime RAM fixups remain unknown. Compressed partition
fit and decompressed runtime placement must be checked independently. No new
address is selected or boot image packed. Exact inputs/arithmetic/source hashes
are retained in `evidence/boot-contract/image-placement-review.json`.

The pinned [amonet LK payload](https://github.com/chaosmaster/amonet/blob/2d8a4e6f73d9dab42d313c9cd751802b23ea7d31/lk-payload/main.c)
redirects boot/recovery reads to renamed partitions, patches version-specific LK
addresses, and changes unlock/fastboot behavior. It is not the complete original
loader or proof of generic RAM boot support. Its MISC flag handling includes
persistent writes even for some boot-mode transitions. The UART flag branch
also declares disable_uart2 but calls the second strcpy with disable_uart again;
source intent is insufficient to qualify usable UART logging. No payload was
built, run or changed here. Continue by identifying the actual installed loader
and its decompression/relocation/entry behavior before selecting placement.

## Diagnostic log backend audit

The retained restricted `diagnostic.config` has CONFIG_PSTORE=y but
CONFIG_PSTORE_RAM=m, CONFIG_PSTORE_CONSOLE disabled and CONFIG_PSTORE_PMSG
disabled. Our isolated initramfs has no module loader or module files. Therefore
that configured RAM backend cannot provide logs in this diagnostic environment;
the successful QEMU test used the live PL011 console, not retained pstore logs.
This is a verified configuration limitation, not a claim that modern ramoops
cannot be developed for douglas. No module is loaded or config changed here.

The pinned [legacy MediaTek RAM-console implementation](https://github.com/mt8163-dev/android_kernel_amazon_mt8163/blob/e0a3a2b2378ae4c7494ffdfea34d2a9e04a5fb74/drivers/misc/mediatek/ram_console/mtk_ram_console.c)
defines its own multi-stage buffer layout at lines99–118 and signature at119.
It carries preloader/LK/Linux offsets plus a circular console. Its optional
CONFIG_MTK_EMMC_SUPPORT + CONFIG_MTK_AEE_IPANIC path includes
last_kmsg_store_to_emmc, which calls card_dump_func_write at lines176–180;
late initialization also starts an eMMC log-reader thread at659. This source
contains a persistent write path; whether that path is enabled/reached in the
installed stock firmware is unverified. Do not import the entire legacy logging
subsystem into the storage-free diagnostic just to obtain console output.

A RAM-console reservation alone establishes neither wire format compatibility
nor survival across reset or a readable recovery interface. A future RAM logging
experiment needs an explicit isolated memory area, agreement with firmware and
loader ownership, built-in backend and selected capture policy, a compatible
reader and a verified reset/retention path. It must account for the legacy
firmware reservations rather than overwriting them. UART instead needs verified
pad accessibility, electrical levels, routing and early/runtime driver setup.
Neither route is qualified yet. Hashes and resolved symbols are retained in
`evidence/boot-contract/log-path-review.json`; #21/#22 remain open.

## Reproduce header comparison without firmware assembly

The offline auditor compares both recorded AArch64 headers against the same
stock boot-header address and refuses mismatched stock image hashes, malformed
headers, inconsistent decoded fields and unsigned arithmetic overflow/underflow.
It selects no replacement address and does not claim memory safety or loader
compatibility. Reports are metadata inputs, not authenticated binary evidence.

```sh
python3 scripts/audit_image_placement.py \
  --runtime-report evidence/qemu-diagnostic/generic-runtime-result.json \
  --boot-report evidence/stock-ota-probe/boot-inspection.json \
  --stock-prefix-report evidence/stock-ota-probe/kernel-prefix-observations.json
```

The retained result is `evidence/boot-contract/reproduced-placement-audit.json`.
The stock header has text_offset=0x80000: at entry0x40080000 its required base
is0x40000000, satisfying 2MiB alignment. The new header has text_offset=0, giving
base0x40080000 and failing alignment under the same unchanged-entry assumption.
This demonstrates why the existing address can suit the old Image while requiring
loader investigation for the new one. Actual relocation remains unverified.
Input-report and auditor hashes make the calculation independently repeatable.
Unit tests exercise these actual reports, identity mismatch, header inconsistency
and arithmetic boundary refusal. No downloads, binary packing or tablet queries.

## First authorized stock collection: runtime facts

The owner's tablet was queried read-only after USB debugging and Mac authorization
were confirmed. Selected sanitized fields and raw-report/collector hashes are in
`evidence/stock-facts/runtime-contract.json`; full reports stay ignored locally.
The incremental build and fingerprint match the inspected OTA candidate's claims
(659664620). This establishes identity agreement, not installed binary hashes or
OTA signature verification. Internal Fire OS property remains5.3.7.3 despite the
owner-facing5.7.1.0; do not equate these version schemes.

Runtime DT version is hvt. With root address/size cells both2, memory reg decodes
to [0x40000000,0x80000000) and [0x80000000,0x99600000): total1430MiB. These differ
from the candidate's static512MiB declaration, providing direct evidence of a
changed runtime memory handoff. MemTotal=1406536KiB is usable Linux memory, not
the complete physical DRAM map. orig_dram_info and mblock_info bytes are retained
without assuming their native vendor struct layouts. Firmware/loader reservations
still need reconciliation; no DT enlargement or physical load address selected.
Kernel release is3.18.19-01784-g988b7c2ec57. uname is absent; /proc/version works.
The old ADB shell incorrectly returned status0 for some failed commands; the
collector now classifies those errors as unavailable. /proc/iomem and cmdline are
permission-denied. A trailing slash is required for ls to traverse the DT symlink.

Loader properties report PL=0x0007, LK=0x0003, TEE=0x0106 (7/3/262). The pinned
[amonet step-1 source](https://github.com/chaosmaster/amonet/blob/2d8a4e6f73d9dab42d313c9cd751802b23ea7d31/step-1.sh)
sets maximums6/2/259 and branches on any excess to a preloader-brick/downgrade path.
All three exceed that source's limits. No helper was executed; this is evidence
against treating that software path as a ready non-destructive boot route, not
proof every alternative unlock/recovery technique is impossible. No root,
reboot, raw partition read, unlock, flash or wipe was performed.

## Runtime memory reconciliation — issue #58

Run the strict offline decoder:

```sh
python3 scripts/decode_runtime_memory.py evidence/stock-facts/runtime-contract.json
```

Pinned legacy ARM64 `arch/arm64/include/uapi/asm/setup.h` defines native dram_info
and mblock_info structs. The retained source, hash/provenance and AArch64 compiler
layout are under `evidence/runtime-memory/`. Their u32 counts are followed by
four padding bytes, then four records: dram rank stride16/total72 bytes, mblock
stride24/total104 bytes. The legacy memory consumer casts the properties directly
to these structs; standard DT reg instead uses big-endian cells. No layout is
inferred merely from convenient values. Compiler input uses the exact upstream
struct declarations and explicit u64/u32 typedefs; command/version are recorded.

The actual rank entries describe [0x40000000,0x80000000) plus
[0x80000000,0xa0000000), totaling1536MiB. mblocks exactly match standard DT reg:
1024MiB plus406MiB, total1430MiB. A106MiB top interval
[0x99600000,0xa0000000) is excluded from that usable map. This is a measured
handoff distinction, not identification of that interval's owner. MemTotal is
smaller again; kernel allocations/reservations cannot be attributed from this
arithmetic alone. Never expose the106MiB gap to Linux based on physical rank size.

The decoder refuses wrong property sizes/cell widths, duplicate/unavailable
records, invalid counts/rank indexes, zero/overflowing/overlapping ranges,
mblocks outside their ranks and disagreement with standard reg. Padding/inactive
record bytes are ignored. Retained result includes exact input/decoder hashes.
Issue #58 completes this bounded decoding/reconciliation scope; #21 still owns
loader placement, reservation ownership, entry contract, recovery and logging.
Next actionable offline task: reconcile the106MiB exclusion and other retained
reserved-memory regions against pinned firmware/legacy memory sources, then
assess a board DT candidate preserving those regions. No physical query or boot
image assembly was performed for this work.

## Reservation inventory — issue #60

Reproduce with `python3 scripts/inventory_reservations.py`. It compares the actual
hvt candidate reserved-node facts with decoded runtime banks, retaining input
and script hashes in `evidence/reservation-inventory/result.json`. Four fixed
regions (ATF, RAM console, mdump, low log) total0x550000 bytes (5.3125MiB).
All lie inside runtime usable-bank extents; none intersects the excluded106MiB
at the top. These reservations must remain reserved within those banks; they
cannot explain the top exclusion and must not be subtracted twice. CONSYS is a
dynamic2MiB declaration with unknown placement, not a measured fixed interval.
The candidate declarations have not been verified as runtime reservation values.

Pinned source/hash snapshots in `evidence/reservation-inventory/sources.json`
provide a narrower investigation path than guessing from sizes:

- mtk_memcfg.c lines461–486 reads native mem_desc properties lca_reserved_mem
  and tee_reserved_mem and adds their sizes to mblock accounting.
- Its CONFIG_MTK_VIDEO path also adds framebuffer size at490–493; the comparison
  with physical-rank total is inside #if0, so source does not enforce equality.
- atf_logger.c at397 reads tee_reserved_mem but labels it ATF in its message.
  A log label alone does not equate this property with the static ATF node.
- mtkfb.c at2046–2080 reads chosen/chosen@0 atag,videolfb for VRAM size/base.
  Its fallback calculation at2102 uses a fixed low-memory end address; this
  cannot be treated as the current1.5GiB tablet's measured framebuffer placement.

No exact0x99600000 boundary/106MiB allocation was established by these cached
source paths. The whole top gap remains unattributed; no TEE/framebuffer size is
invented to make the arithmetic fit. Residual blocker under#21: obtain explicitly
reviewed read-only values of memory lca_reserved_mem/tee_reserved_mem and the
narrow framebuffer descriptor (which includes a panel name, requiring sanitation)
or matched loader reservation evidence, then reconcile overlaps and totals.
Automatic runs must not query the tablet. No available binary or source proves
loader placement/recovery either. This completes the bounded source/interval
audit, not reservation ownership or a safe boot-image contract. Independent next
work is#27 full binding-context failures, starting with the preserved malformed
upstream Gunyah YAML and PMIC schema-selection overlap.

## Loader/recovery alternatives audit (#76)

`python3 scripts/audit_loader_routes.py --verify-sources` reads only cached git
objects and approved facts; it never imports or executes device helpers. Exact
revisions, file hashes/URLs and line observations are retained in
`evidence/loader-routes/sources.json`; the route assessment retains source/facts/
auditor hashes.93 host-only tests pass. The upstream reference repositories were
read only; no changes, issues or comments were made there.

The distinction is between possible exploit families and a qualified procedure:

- Stock recovery can be a signed restoration route, but neither matching full
  restoration authentication nor arbitrary custom-kernel acceptance is established.
- Legacy boot-fastboot.sh runs handshake2, not a demonstrated stock fastboot RAM
  boot command. No helper name is evidence of nonpersistent recovery.
- Legacy software step-1 requires root and rejects PL7/LK3/TEE262 against6/2/259.
  Its newer-firmware branch explicitly clears preloader and writes LK/TEE. The
  supplied fastboot installation explicitly erases userdata. No such step ran.
- Legacy BootROM main is a distinct bootstrap family, so the software version
  gate alone does not prove BootROM infeasible. However, its host chain writes
  primary/backup GPT, preloader, RPMB, boot/recovery and loader images. Minimal
  mode still performs persistent writes; it assumes LK/TZ were already flashed.
  Physical BootROM entry and recoverability on this tablet are unqualified.
- The newer cached amonet-koboreru revision
  d51af735e5b95fa2c03c0b311d5c05f0f73461d4 includes an explicit douglas/MT8163
  target and custom-LK partition lk2. Its README says newer preloaders are patched
  and an older vulnerable preloader/downgrade is required; exact PL7 binary
  susceptibility is not proven by its version number alone. Installation requires
  persistent TEE/LK changes and a valid original LK. It is not a standalone safe
  escape from an untouched updated tablet. lk2 layout has not been verified.
  The README's general RPMB-clearing claim must not be applied blindly: douglas.c
  skips an ARB check using patch_ret, unlike several targets calling clear_rpmb_arb,
  and douglas.h does not define the RPMB access addresses used by arb.c.
- Custom TEE/LK is a later integration option once a bootstrap is established,
  not an independently verified initial entry method.

The old cached repository README still describes suez/HD10, despite the selected
source's douglas adaptations. Use per-file target evidence, not README labels,
for model compatibility. The starting XDA douglas thread returned HTTP403 during
this audit; no current pad/shorting or recovery instructions were inferred from
unread content. No physical action is proposed from these sources alone.

Result: no currently qualified nonpersistent diagnostic boot/recovery route.
This is not a proof that unlocking/current-kernel bring-up is impossible. The
next concrete offline task is model/build-identified OTA preloader/LK inspection:
the retained ZIP index lists images/preloader.bin (compressed89263, raw139352)
and images/lk.bin (compressed294421, raw485552), total383684 compressed bytes plus
bounded ZIP/property metadata. Use explicit bounded range fetches/CRC/identity
checks, local files only, no execution or redistribution. Inspect documented
vulnerability marker and header/load behavior, keeping string heuristics distinct
from proof of exploitability. Full907705758-byte OTA download is unnecessary and
not authorized by this task. Cached source audit is complete;#21 retains actual
entry, authenticated restoration, recovery, logging and explicit owner approval
for any future destructive unlock/wipe. No payload was built or tablet queried.

## Exact loader container/entry assumptions (#80)

The strict offline `inspect_loader_layout.py` requires regular local loader files
at most1MiB and verifies exact hashes from the retained build-matched report.
It writes nothing to firmware and executes no loaded bytes. Reproduce:

```sh
python3 scripts/inspect_loader_layout.py \
  --preloader out/ota-loader-inspection-659664620/preloader.bin \
  --lk out/ota-loader-inspection-659664620/lk.bin
```

The preloader's GFH v1 FILE_INFO declares load base0x200d00, content offset0x300,
file length139352 and signature-region length292. The source-defined code view
is [0x201000,0x222c34),138292 bytes, excluding the declared signature region.
The parser checks name/version, total/maximum/content/signature bounds and32-bit
address overflow. This declaration is not proof of authenticated execution at
that address. The GFH interpretation is anchored to the pinned newer fork's
preloader_text function; hashes/URLs are retained, without running its helper.

LK's512-byte prefix has magic0x58881688, nameLK and payload length485040. Its
maddr and mode words are both0xffffffff; pinned preloader.h defines this maddr
as PART_HEADER_DEFAULT_ADDR. Therefore this artifact does not independently
supply a concrete load base. The legacy exploit generator's base0x4bd00000 is a
source assumption, not a base authenticated by this current LK header.

The report maps four newer-fork preloader patch addresses to bounded16-byte
windows using the GFH-declared code view, and three old LK patch addresses only
under the explicit hypothetical legacy base. All are observations, never verified
function identities or compatible patch sites. Being in bounds is not proof
that current firmware has the expected function there. The pinned old helper
repository does not contain bin/lk.bin or bin/preloader.bin, so no expected donor
binary fingerprints are available there to compare against; metadata records
those missing git objects. No old patch was applied to the current files.

The modern Image's text_offset=0 still conflicts with unchanged0x40080000 entry
under the ARM64 alignment rule. Container inspection alone does not prove LK's
decompression/relocation branch or final jump address, nor register/EL/cache
handoff. Result/provenance/script hashes and bounded byte windows are retained
in evidence/loader-layout.102 tests pass, including malformed containers, wrong
hashes, address/window bounds and sentinel handling. No physical/kernel boot or
recovery qualification is claimed.

Next concrete#21 task: recover the stock LK kernel-header/decompress/jump flow
using the already installed LLVM objdump (no new dependency download), tying
instruction offsets to exact-hash bytes and labelling load-base/Thumb assumptions.
If complete flow cannot be established statically, record the exact missing
branch/assumption before proposing any physical test; do not treat string/literal
hits as control-flow proof. Existing native tools are available, but no payload
was built and no firmware instruction executed in this scope.

## Stock LK instruction trace — issue #82

The exact build's startup code now substantiates a linked base of0x4bd00000:
ARM payload offset0 branches to0x24; offsets0x40–0x6c compare the current image
base with literal0x4bd00000, copy toward the linked range when different, and
branch via literal0x4bd00080. This replaces the earlier source-only base assumption
with actual startup-instruction evidence. It does not prove a physical loader
runs this startup path or make legacy patch addresses compatible.

A bounded mixed ARM/Thumb trace establishes an actual K64-associated secure-monitor
call path. Offsets below are relative to the512-byte-stripped LK payload; file
offsets are512 higher, linked addresses are0x4bd00000 higher if startup executes
at its linked base:

- Thumb call0x3eb90 targets0x3de1c. That function saves incoming r0 at stack+0x28;
  a PC-relative reference in the function resolves to boot_linux_fdt.
- At0x3e738, the checked nonzero-flag path reaches0x3e73c: reload r0 from stack+0x28,
  move current r5 into r1, set r2=0/r3=1, and call0x3ddd0. r5 is modified elsewhere
  in this function; complete lineage of that argument is not yet proven.
- The forwarding wrapper resolves a PC-relative log reference to
  “[LK]jump to K64”, restores its four incoming arguments, then BLX at0x3ddec
  enters ARM code0x3c8e0. Standard callee-saved-register behavior is assumed for
  the intervening logging call; its implementation was not fully traced.
- ARM0x3c8e0–0x3c8f4 shifts arguments: r1 receives the entry-slot value, r2 the
  second wrapper argument, r3=0/r4=1. r0 loads literal0x82000200, then executes
  SMC#0. This proves the selected call-site/request structure statically; the
  secure monitor handler, exception-level setup and final AArch64 jump are not
  established by this LK-only trace.

The selected wrapper does not realign the entry value it forwards. The earlier
producer of that value, header handling and decompression destination still need
tracing before concluding the entire loader ignores the modern Image header.
The40080000/text_offset0 mismatch therefore remains conditional.

Reproduce with `python3 scripts/trace_lk_handoff.py --lk
out/ota-loader-inspection-659664620/lk.bin --output out/lk-handoff-replay` (one shell
command, fresh output). Existing LLVM objdump21 performs static decoding only.
The tool builds an ignored ET_REL analysis object with no entry/program headers;
it is not a firmware image, never executed and not redistributed. Only five
bounded disassembly excerpts, selected anchor bytes and hash-bearing report are
committed under evidence/lk-handoff. Instruction anchors/call targets are checked
independently of tool text. ARM and Thumb ranges are explicit; literal pools are
not treated as executable instructions. Preliminary broad linear decoding was
not accepted as control-flow proof.

106 tests pass, covering signed/cross-state branch targets, non-loadable object
headers, changed-instruction refusal and explicit unverified lineage/monitor/boot
flags. No firmware/helper instruction ran and no tablet was accessed. Next#21
work: trace the producer of the saved entry slot and its decompression/header
inputs. Preserve the current static conclusions without promoting them to a
physical boot or recovery result.

## Exact LK header producer and decompression destination (#84)

The build-matched LK SHA256 remains
`4ca0cca7ae9af6e959dc848b9ca002624c62e1bb93c83c0ecc89bae8d2186b08`.
This static trace follows selected header-present/K64 branches; it does not
execute firmware or establish a tablet boot/recovery method. Offsets below refer
to the payload after the 512-byte MTK prefix. Reproduce with cached bytes:

```sh
python3 scripts/trace_lk_header_producer.py \
  --lk out/ota-loader-inspection-659664620/lk.bin \
  --output out/lk-header-producer-reproduction
python3 -m unittest discover -s tests -q
```

Selected instruction bytes, decoded windows, string references and hashes are in
`evidence/lk-header-producer/`. The analysis object stays ignored in `out/` and is
ET_REL without an entry point or program headers. Apple LLVM21 decodes Thumb;
full firmware binaries are not published.

Three PC-relative table-base calculations (literal/add-PC pairs
24958/2477e, 3ef54/3ebb0, 3e994/3de30) resolve payload offset761f4. Each function
uses table index248; that table word contains linked address4bd841b0, the mutable
header-pointer global. This global is outside the file-backed payload. Its
runtime contents are unavailable; the table word is not a captured header.

At247aa the parser publishes its allocated header pointer. The read callback is
indirect. At247ee it compares eight bytes against the PC-relative `ANDROID!`
string, then branches on a nonzero result. The function logs header+0xc with the
literal `Android Boot IMG Hdr - Kernel Address`. Publication precedes validation;
this audit does not establish error propagation for every caller or every write
to this mutable object.

On the checked header-present caller branch,3ed86 loads header+0xc into r8;
3ed98 moves r8 into r0 and3eda0 calls3eb84. Combined with#82, this connects the
header kernel address to the saved entry slot and selected K64 SMC argument.
Standard ARM AAPCS callee-saved register preservation is assumed. Neither this
short producer sequence nor the checked downstream forwarding wrapper rounds
that address. This is not a whole-program proof that no other path can modify it.

The K64 gate at3de5e loads header+0xc, extracts its low19bits and rejects a nonzero
value. Its failure branch3e132 logs then loops at3e146. Thus this gate requires
**512KiB alignment**, not2MiB, and rejects rather than fixes misalignment. The
modern ARM64 Image's independent placement requirement still applies.

For the selected decompression call at3e11c, r1 is loaded from the same header
object's+0xc; r3 is explicitly1c00000 (**28MiB**). Adapter3f3f0 moves the output
pointer into r2 and calls the gzip-header parser3f364. That parser calls3f2b4;
the latter saves r2/r3 then assigns them to the inflate output-pointer and
capacity slots at3f2f8/3f2fe. This connects decompression destination and selected
entry to the same header field, subject to intervening mutable-state assumptions.
Function2578c returns45000000, the staging-address input to the checked load
calls; its returned constant alone does not prove the complete storage path.

The existing generic diagnostic Image declares image_size29360128, exactly the
observed28MiB decompression capacity. That equality proves no margin and is not
proof of compressed-byte output size, overflow, success or board compatibility.
We have not selected a physical destination. Remaining work: trace staging/input
length and appended-DT handling, enumerate relevant header mutations, qualify
secure-monitor behavior and find a recoverable loader/log procedure. Parent#21,
physical boot, hardware support and Android/app runtime gates remain open.

## Selected compressed-input and appended-DT audit (#86)

Reproduction uses the same exact-hash cached LK as#84:

```sh
python3 scripts/audit_lk_input_length.py \
  --lk out/ota-loader-inspection-659664620/lk.bin \
  --output out/lk-input-length-reproduction
```

`evidence/lk-input-length/windows.json` records selected raw instruction windows,
byte hashes and decoded-text hashes. Reproduce each text window using the
non-loadable analysis object from `trace_lk_header_producer.py` and:

```sh
xcrun llvm-objdump -d --triple=thumbv7-none-eabi --mattr=+trustzone \
  --print-imm-hex --start-address=0x3f2e2 --stop-address=0x3f33e \
  out/lk-header-producer-reproduction/analysis-only.o
```

Use each window's start/end for the other excerpts. Object pathname is normalized
to `<analysis-only.o>` in retained text. Firmware remains unexecuted.

The selected call sequence3edf4..3edfe obtains45000000 from2578c and passes it as
r1 to24ce8, where r6 receives it. The prefix parser246cc checks58881688 and a
32-byte name comparison, returning the word atprefix+4 on its accepted path.
After the initial512-byte read,24d88 subtracts512 from the destination on the
prefix-present branch. The subsequent indirect read at24dec receives this
adjusted destination and its separate length from a mutable size global.
This places the prefix below staging, leaving the gzip bytes at45000000 if the
read/transform paths behave as expected. Their indirect callback and security
transform1cf0c have not been qualified; other branches reread a wider interval.
No header kernel-address write was encountered in the selected snippets; this
is not an exhaustive alias/write inventory.

The FDT function saves header+8 as its initial size at3de58/3de5a, adds it to the
staging base at3de6e, and scans backwards for d00dfeed. On its selected match
route,3e170 retrieves the scan distance rounded **up** to four bytes;3dfa6
subtracts that value from the saved input size. The alignment acts on the suffix
length, not the output address. The unchanged initial-size value is therefore
not automatically the gzip-member length. This trace does not execute the
version-selection logic or prove which candidate is selected at runtime.

Conditional arithmetic using the already-inspected stock layout illustrates why
that distinction matters. Header kernel_size7191666 includes512-byte MTK prefix,
gzip7026236 and two DTBs. If the hvt DT atcomponent offset7109025 is matched with
those header values unchanged, the selected input length is7108510:82274bytes
past the gzip-member end. If the first DT is matched instead, the result is
7026234, two bytes short of the full gzip member. Neither case is a boot verdict:
the checked wrapper skips gzip headers and invokes raw DEFLATE; a full gzip
trailer is not the same requirement as a complete raw DEFLATE stream. Mutable
header/transform behavior can also change these inputs. These scenarios are
explicitly conditional and must not be substituted for captured runtime state.

At3f2f8/3f2fe, output pointer and **28MiB output capacity** occupy separate inflate
slots from compressed input pointer/length. A return value1 is required at3f30e;
3f316/3f31a writes `next_out-original_destination` back as produced-byte count.
Thus28MiB bounds decoded bytes rather than compressed file size or appended DT.
The cached stock gzip expands to16584856bytes, leaving12775272bytes of this
capacity. Its ARM64 declared image_size is18681856, demonstrating that declared
memory requirements and gzip output bytes differ.

**Clarification to#84:** modern declared image_size equals28MiB, so there is no
margin in that *declared memory requirement comparison*. We have not measured
the modern Image file/gzip output length in this audit. It can be smaller because
zero-initialized runtime memory need not be stored in the file. Consequently the
equality does not establish a tight decompression-output limit or blocker. The
modern actual output-length/memory-footprint comparison is the next bounded task.
Loader execution, complete header mutation and transform paths, recovery and
physical boot remain open under#21.

## Keypad compatible coverage experiment (#90)

The pinned donor mt8163.dtsi lines415–421 declare the disabled keypad node with
`mediatek,mt8163-keypad`, `mediatek,mt6779-keypad` and clock-name `kpd`.
Pinned ACK driver `drivers/input/keyboard/mt6779-keypad.c` line243 matches the
fallback; it parses matrix-keypad properties and debounce at runtime. The donor
fallback declaration is evidence for a local schema proposal, not proof of
register/interrupt/wakeup compatibility. No node status or hardware DT changed.

The opt-in `mt8163-keypad` proposal adds only that first compatible to the
existing exact two-string fallback branch. Original/proposed hashes and patch
are locked in `projects/firetabs-android/kernel/dtb/bindings/mt8163-keypad.json`.
`evidence/keypad-binding/` retains original/proposed schema, selected driver source
with URL/hash, real processed compatible schema and six accepted/rejected tuple
controls. Missing/wrong/extra fallback is rejected; existing tuples remain valid;
all other schema constraints are unchanged. This is not an upstream binding.

Reproduce with the existing cached corpus/tools and DTB:

```sh
python3 scripts/validate_douglas_bindings.py \
  --experiment rdma-node-name --binding-profile mt8163-uart-proposed \
  --repair-gunyah-yaml --repair-pmic-selector \
  --extra-binding mt8163-sysirq --extra-binding mt8163-timer \
  --extra-binding mt8163-mmc --extra-binding mt8163-uart-dma \
  --extra-binding mt8163-i2c --extra-binding mt8163-spi \
  --extra-binding mt8163-auxadc --extra-binding mt8163-rng \
  --extra-binding mt8163-keypad
work/dtb-tool/venv/bin/python evidence/keypad-binding/check-controls.py
```

Full-corpus diagnostics fall from60 to58: the keypad compatible validation error
and its unmatched-node diagnostic disappear, with **no new diagnostics**.
14validation errors and44unmatched nodes remain; wrapper exits1 as required.
The keypad schema's doc validation is clean. The preexisting Gunyah schema
semantic warning remains visible. Parent#27 stays open. The driver source fetch
was bounded128KiB encoded; no dependency/build/device operation was added.

## Generic efuse compatible/calibration constraint audit (#92)

Pinned donor mt8163.dtsi lines441–449 declares MT8163 plus generic efuse fallback,
4KiB region and a legacy thermal calibration cell atoffset0x100/size0xc. ACK's
`drivers/nvmem/mtk-efuse.c` generic fallback match (line115) uses
`uses_post_processing=false`; only the MT8186 match enables GPU speedbin decoding.
The generic path reads resource bytes and enables legacy fixed cells. These
sources justify assessing exact generic tuple coverage. They do not establish
correct calibration contents or the thermal driver's interpretation on hardware.
No efuse reads, writes or tablet operations occurred.

The opt-in `mt8163-efuse` proposal inserts only the MT8163 first compatible in the
existing generic fallback enum. It leaves MT8186/MT8188 decoding-specific and
deprecated branches, cells, required properties and all other constraints intact.
Source URLs/hashes, original/proposed schema, patch hash, processed schema and
nine accepted/rejected tuple controls are retained in `evidence/efuse-binding/`.
The proposal is local; upstream acceptance and hardware behavior are unqualified.

Reproduce the full command in the preceding keypad section with one additional
`--extra-binding mt8163-efuse`, then run:

```sh
work/dtb-tool/venv/bin/python evidence/efuse-binding/check-controls.py
python3 -m unittest discover -s tests -q
```

The full-corpus count falls58→56: one efuse compatible validation error and its
unmatched-node diagnostic disappear, with zero new diagnostics.13validation and
43unmatched diagnostics remain. Wrapper exits1; overall validation still fails.
The efuse schema's doc validation is clean. Parent#27 and all thermal/calibration
hardware gates remain open. No DT data or status was changed.

## CPU startup / secure-monitor contract source audit (#94)

The stock candidate's pre_evt/hvt DTs declare CPU method `mt-boot` and
`arm,psci`/`smc`, with explicit CPU_ON ID84000003. The modern donor DT instead
declares CPU method `psci` and `arm,psci-0.2`. These declarations select different
kernel paths; neither establishes installed monitor behavior.

Pinned legacy reference e0a3a2b2378ae4c7494ffdfea34d2a9e04a5fb74 registers
`mt_cpu_psci_ops` under CONFIG_MTK_PSCI. Its `mt-boot` wrapper:

- Prepares SPM MTCMOS when preparing CPU1, then delegates generic PSCI prepare.
- Calls generic PSCI cpu_boot, returns on error, then performs host-side
  `spm_mtcmos_ctrl_cpu(cpu, STA_POWER_ON, 1)`.
- Delegates CPU-off/die and adds host-side MTCMOS power-down in its kill path.

The retained mtcmos.c routes CPUs0–3 to register-level power functions. For
example its CPU1 power-on path sets PWR_ON/PWR_ON_2ND and polls power/L1 status.
Those polls have no timeout in the selected source. Blindly copying/executing the
old routine would not qualify its modern clock/power/locking dependencies.
This legacy source is a reference and **has not been matched to the installed
stock kernel binary**; it explains a source-level compatibility gap rather than
proving the exact installed implementation.

Pinned ACK d9318bdb4c34e8b2d997b4f67ced56b120b22b87's DT CPU operations table
contains spin-table and generic PSCI, without `mt-boot`. Thus the stock CPU method
is unsupported by this table as-is. Its generic secondary boot calls PSCI with
the secondary_entry physical address; it contains no equivalent MT8163 wrapper.
Changing only the enable-method string does not reproduce the reference power
sequence. Whether the installed monitor itself supplies that sequence is unknown.

ACK still supports `arm,psci` explicit v0.1 DT function IDs; an old PSCI DT format
is therefore **not itself a hard blocker**. The modern donor's v0.2 path queries
firmware version and, on ARM64, selects CPU_ON C4000003. The stock DT's explicit
84000003 is a32-bit calling-convention ID; that difference does not prove that
the monitor rejects the64-bit ID. LK's primary boot transition82000200 is a
separate service, and supplies no evidence about PSCI CPU_ON support.

`evidence/cpu-startup-contract/sources.json` locks source bytes/revisions and
`report.json` supplies exact line anchors, distinct call IDs and explicit unknowns.
New files are cached legacy MTCMOS source and one bounded ACK UAPI header fetch;
all other sources and stock DT evidence were already retained. Reproduce without
network/device operations:

```sh
python3 scripts/audit_cpu_startup_contract.py
python3 -m unittest discover -s tests -q
```

Conservative future diagnostic scope is primary CPU only (`maxcpus=1`, no CPU
hotplug, idle, suspend or power-off). This is a proposed limit, not an assembled
or tested tablet configuration. It removes secondary startup from an initial
experiment's scope, but does not solve primary entry, monitor setup, recoverable
loading or logging. A follow-up should trace modern boot-CPU versus secondary
initialization to ensure this limit actually avoids unsupported callbacks, then
qualify a recovery route before proposing a physical test. Multicore support
requires validated monitor behavior or an adapted, bounded MT8163 power sequence;
that work remains under#21 rather than being declared solved by this audit.

## Opt-in primary-only DT experiment (#96)

Pinned ACK setup_arch parses early arguments, then calls psci_dt_init, then
initializes boot-CPU operations and enumerates CPUs. **maxcpus=1 does not suppress
PSCI discovery**. smp_prepare_cpus only skips secondary preparation atmaxcpus=0;
otherwise it visits possible secondaries even when only one will later activate.
The nr_cpus early argument is a distinct hard limit on nr_cpu_ids, which bounds
the secondary setup loop. Boot-CPU operations select an operations table; this
step itself does not call CPU_ON. These source anchors/hashes are retained in
`evidence/primary-only/` and checked by the experiment script.

An isolated DT experiment adds exactly two properties to the reviewed RDMA DT:

- `/psci/status = "disabled"`: pinned psci_dt_init returns ENODEV before invoking
  its compatible-selected init function when that node is unavailable.
- `/chosen/bootargs = "nr_cpus=1 maxcpus=0"`: limits secondary setup and skips
  secondary preparation/bring-up if these are the effective early arguments.

All186nodes and original880properties are preserved, including CPU declarations,
RAM, addresses, clocks, interrupts and board identity. This avoids dangling CPU
phandles in PMU affinity/topology/thermal maps. It is a compiled **DT-only source
experiment**, not an assembled firmware or a global proof that no SMC occurs.
Other firmware services/RSI and driver paths have not been exhausted. No physical
load address was chosen. The donor512MiB RAM declaration remains unqualified for
this tablet; the experiment must not be used as a physical test package.

Reproduce with existing cached tools; neither command accesses the tablet:

```sh
python3 scripts/build_douglas_dtb.py --experiment rdma-node-name
python3 scripts/build_primary_only_dtb.py --output out/primary-only-reproduction
python3 -m unittest discover -s tests -q
```

The primary-only script verifies the base DTB, preprocessed-source and appended
DTS hashes; compiles using pinned DTC1.8.1 without diagnostics; then checks every
node/property against precisely those two additions. Negative controls reject
changed RAM, missing PSCI disable or a weaker command line. Default DT experiment
choices and full-board source files are unchanged. The experiment's DTB is26324
bytes, SHA256`ef23af15f7136613a98b450f3d1db7c860f581024d194e88e2ef8c3116f2eb43`.
No full binding-validation or hardware pass is implied.

This approach assumes the boot CPU matches donor MPIDR0, ACPI remains disabled
by diagnostic policy, and the loader preserves the intended DT/command line.
Those are not runtime facts. In particular LK may rewrite chosen/bootargs;
source-level constraints cannot be treated as effective until that mutation is
traced or later captured. The existing diagnostic init neither hotplugs CPUs nor
requests suspend/off, but its QEMU execution does not qualify this DT on douglas.
Next bounded task is to trace LK's chosen/bootargs mutation so a future packaging
contract can require and verify these limits. Primary entry, recovery and usable
logging remain separate blockers under#21.
