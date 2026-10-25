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
