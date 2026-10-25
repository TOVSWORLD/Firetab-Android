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
#18–#20. Current kernel builds are generic compile experiments, not this diagnostic
configuration or an Android/douglas boot result.

The [candidate's actual appended DTBs](STOCK-DTB-CONTRACT.md) now corroborate the
legacy source: two versions(pre_evt/hvt), static512MiB memory, legacy explicit-ID
PSCI with CPU0 mt-boot, and ATF/RAM-console/mdump/low-log/CONSYS reservations.
Selection, runtime fixups and secondary-CPU behavior remain unverified. Read-only
stock collection includes the individual DT version property for later evidence;
no device transport was executed.
