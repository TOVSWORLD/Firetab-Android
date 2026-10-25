# Douglas maintained-kernel audit — issue #5

Source inspection dated 2026-10-25. This answers the first kernel-candidate/support-matrix
task under issue #4. No kernel, Android image or device boot was tested. A local clang
preprocessing probe reproduced an actual device-tree dependency failure.

## Recommendation and exact candidate

Use the **Android 17 / Linux 6.18 ACK family** for the first maintained-kernel integration
experiment. Pin `android17-6.18-lts` at
`d9318bdb4c34e8b2d997b4f67ced56b120b22b87` for that experiment, with the community
MT8163 work below as a source donor. This is an engineering candidate, not a supported
firmware baseline or evidence that its security coverage is current.

Google's [ACK matrix](https://source.android.com/docs/core/architecture/kernel/android-common)
includes Android 17 on 6.18 and lists the family through 2030-07-01. It also tests older
ACK families with Android 17; the selection of 6.18 follows this project's maintained,
release-appropriate kernel direction. The [upstream Linux maintenance list](https://www.kernel.org/releases.html)
currently projects 6.18 and 6.12 through December 2028. These upstream dates do not
establish this project's support commitment. Linux 6.12/Android16 is a possible comparison
baseline, not an automatic older-kernel detour.

A newer upstream major kernel exists, but Android 17's matched maintained ACK family is
a more bounded integration starting point than adding Android changes to an arbitrary
mainline release. Mainline MT8163 improvements should still be reused/upstreamed.

The actual refs matter. Captured Makefiles and commit metadata show:

- `android17-6.18`: `533c1b80b8a9556fea6728bd85fa3a276bccbd15`, 6.18.32, commit dated Oct 23.
- `android17-6.18-lts`: `d9318bdb4c34e8b2d997b4f67ced56b120b22b87`, 6.18.34, commit dated Oct 22.
- September release branch: `7ff4606f62347129a94e3dcd1f32c274c2356107`, 6.18.32, commit dated Oct 23.
- September `_r9` peeled tag: `e23aa8e8ab337ee88518a7fad4b175d8d68890c8`, 6.18.32, commit dated Oct 20.
- Linux upstream `v6.18.58`: peeled commit `2926d88bb7fc4608fd942453d929c39e4e5ec006`.

Consequently, neither an ACK branch name nor a version suffix proves latest upstream
security coverage. Before release, reconcile the selected ACK's actual merged fixes
against newer upstream stable and Android security changes. Do not replace these pins
with a moving branch and call the result reproducible.

See [captured refs](../../evidence/kernel-audit/refs/) and
[source index](../../evidence/kernel-audit/sources.json) for exact URLs/content hashes.

## Existing work to reuse before writing drivers

Ben Grisdale's repository now resolves as `bengris32/linux-f` (the old `linux-mtk` URL
redirects there). Its `mt8163/7.0` branch is pinned at
`20951722df6ae1f6fecbfcea0a7d585118a06f3f`; its Makefile says **7.0.0-rc6**, not Android 7.
It contains an explicit
[douglas DTS](https://github.com/bengris32/linux-f/blob/20951722df6ae1f6fecbfcea0a7d585118a06f3f/arch/arm64/boot/dts/mediatek/mt8163-amazon-douglas.dts),
a shared Amazon board file, MT8163 clocks/pinctrl/power domains, PMIC-wrapper integration,
and display-controller/SMI/IOMMU work. Those are concrete reusable sources, not proof of
working douglas hardware. Backporting them to 6.18 requires API/config/binding review.

The separate
[initial upstream series](https://github.com/bengris32/linux-f/commits/84fae418d21ba2f7b92215834cfe4708305954c8/)
is pinned at `84fae418d21ba2f7b92215834cfe4708305954c8`. It is a smaller CPU/timer/IRQ/UART/
watchdog subset for Echo Dot `biscuit`, not the full community branch or a Fire tablet port.
Its cover commit `1bad661bc12d497958943b7d1a15fe83426a356c` describes custom TF-A, U-Boot
and OP-TEE prerequisites and remaining clock/pinctrl/power-domain work. Do not transplant
its Echo reserved-memory/firmware arrangement onto douglas without a boot-chain audit.

[LibreEcho's Linux 6.1 source](https://github.com/aslater3/LibreEcho-Linux-6.1/tree/23721f56408fb4c4fe1a368abf06caa98edaecfa)
is another reference, pinned at `23721f56408fb4c4fe1a368abf06caa98edaecfa` (6.1.178). Its
README explicitly builds an **ARM32 kernel** and separates kernel from product packaging.
Its tree retains vendor-style MT8163 bindings. It may provide forward-port examples for
connectivity/audio/legacy interfaces; it is not an ARM64 Android 17 solution or proof of
Fire tablet compatibility. Echo validation claims remain upstream claims, not our tests.

The older `mt8163-mainline/linux` head is `370c4edea18a90d3f2e63ea87b8c0a5afb03acfc`,
last pushed in 2020. Prefer evaluating the newer explicit douglas work rather than
restarting solely from that older effort. Legacy 3.18/4.9 trees remain hardware references.

## Component evidence and integration work

The [machine-readable support matrix](../../projects/firetabs-android/kernel/support-matrix.json)
contains twelve component records with local source anchors and next tests. Status means
source evidence/reuse potential, never hardware support. The following are the critical
findings from the pinned files.

### Boot firmware, CPUs and memory

Legacy `mt8163.dtsi` specifies `enable-method = "mt-boot"`. Its `mt_psci.c` wraps PSCI
CPU boot with `spm_mtcmos_ctrl_cpu()` power sequencing; the old CPU-operations table
registers that vendor method. ACK's `arch/arm64/kernel/cpu_ops.c` registers spin-table
and PSCI, not `mt-boot`. This is a verified contract mismatch for an unchanged legacy
DT on ACK. It does not prove that the hardware cannot run a current kernel.

Choose between a narrowly ported vendor boot/power contract and an audited modern
firmware path. Changing secure firmware carries device-specific boot/recovery implications;
no such change is authorized or attempted. A single-core console would not validate SMP,
suspend or firmware compatibility. Firmware behavior still needs owner-supplied evidence.

The community douglas file is a small identity wrapper. Its common board file declares
512 MiB memory and enables selected GPU/MMC/PMIC paths; that is not a validated description
of the user's 1.5 GB tablet. Identify bootloader memory fixups and all actual secure,
radio, framebuffer and reserved regions before using it. Do not infer available RAM
from an inherited static DT alone.

The legacy device tree uses a header-v0 Android boot envelope, `Image.gz-dtb`, and a
16 MiB boot partition. `BOARD_KERNEL_PAGESIZE=2048` describes that image envelope;
it is not the ARM64 kernel's 4 KiB/16 KiB memory page-size choice. A stock GKI boot image
is not a drop-in replacement. Compression, DTB placement, load addresses and total size
need actual image checks. No packing, flashing or bootloader change occurred.

### Clocks, pins, PMIC, power and storage

The ACK directory listings have no MT8163-named clock/pinctrl/SoC DT entries. The community
branch supplies split MT8163 clock drivers, pin tables and power-domain data. ACK already
has MT6323 slave/regulator support, but not the community MT8163 PMIC-wrapper host match.
Import both platform data and framework integration, not only a board DTS.

The community MMC nodes use an `mt2701-mmc` fallback that ACK matches in `mtk-sd.c`.
That provides a plausible reuse path. It does not prove equal timing, clocks, pin drive,
regulator sequencing or suspend behavior. Begin conservative; validate eMMC integrity
and recovery before enabling high-speed modes. SD/card detect is separate work.

### Display, touch and graphics

The community DRM driver includes MT8163 paths. Its douglas/common files do not complete
a panel endpoint/power sequence. Legacy douglas uses the NT35521 vendor LCM driver;
port the actual panel initialization/timings/regulators/reset/backlight and DRM graph.
A framebuffer or DRM-controller symbol does not establish usable display output.

Legacy `goodix,gt9xx` and ACK's Goodix-family driver suggest reuse. Reconcile actual
controller variant, compatible, firmware/config, IRQ/reset pins and supplies; do not
rename the compatible and assume all hardware variants work.

ACK Panfrost recognizes the Mali T720 GPU. It still needs board clocks/power/SMI/IOMMU,
Android EGL/gralloc/composer/buffer integration and usable userspace rendering. The old
proprietary Mali stack uses different kernel contracts and cannot be assumed compatible.
[Mesa's current matrix](https://docs.mesa3d.org/drivers/panfrost.html) lists T720 at GLES 2.0
with no Vulkan support. That leaves a real feature/compatibility gap against
[Android 17 CDD graphics requirements](https://source.android.com/docs/compatibility/17/android-17-cdd#7_1_4_graphics_acceleration),
including GLES 3.1. It is not proof that an experimental UI cannot render: the captured
AOSP 17 `EglManager.cpp` requests a GLES 2 context. Android rendering/app behavior and
CDD/GMS compatibility require separate tests and cannot be inferred from that one file.

### Wireless, audio, cameras and peripherals

Legacy config selects the MT8163 CONSYS vendor combo stack. ACK's `mt76` directory is
not evidence of support for this integrated radio. Identify exact transport, firmware,
NVRAM, userspace controls and suspend/power requirements. A reusable current driver is
not established by this audit. LibreEcho source may be useful; the Echo board differs.

Audio machine routing, codec/AFE, cameras/media/ISP, charging/thermal, sensors, USB and
wake/suspend still need board-specific inventory beyond these twelve initial components.
They are not silently waived by choosing a current kernel. Do not advertise them or
reuse a proprietary hardware interface without identifying its actual ABI requirements.

### ARM32 apps and modern Android kernel interfaces

ACK arm64 Kconfig retains `COMPAT` for ARM32 EL0; its gki_defconfig enables COMPAT, Binder,
BinderFS, BPF, cgroups and SELinux. A 4 KiB kernel-page configuration is the conservative
initial candidate for old ARM32 blobs. A resolved board configuration and runtime tests
are still required. Android 17 retains `init.zygote32.rc`; that does not establish that
our full ARM32 product, HALs or each required app builds/runs.

The Android 17 CDD's handheld RAM/ABI rules require a single app ABI below 2 GB. Therefore,
64-bit kernel + ARM32-only Android userspace is worth evaluating for the 1.5 GB device
and the inspected ARM32-only native panel APKs. It is not the same thing as a 32-bit
kernel. A dual-app-ABI experiment would need to disclose its CDD conflict. An ARM64-only
product would instead exclude those inspected native APKs. Verify required mobile app
ABIs independently. CDD compliance and Google services approval remain separate from
compilation and boot, and are not claimed.

## Reproduced dependency failure and continuation commands

```sh
python3 scripts/kernel_audit.py
python3 scripts/kernel_audit.py --probe-cpp
```

The default checks 81 captured source/listing/notice hashes and twelve matrix anchors offline.
The optional probe uses local clang, community board/SoC files and actual ACK headers.
It exits the compiler with code 1 at:

```text
fatal error: 'dt-bindings/clock/mediatek,mt8163-audsys.h' file not found
```

[Recorded command/result](../../evidence/kernel-audit/cpp-probe.json) is from Apple clang
21 on the inspection host. The probe intentionally reports the expected source gap; a
zero exit from the probe script means it reproduced that failure, not that a DTB or
kernel compiled. Sixteen MT8163-specific binding-header paths returned 404 at the pinned
ACK revision, recorded in the source index. They must come from a reviewed donor patch
set or a new implementation; do not generate empty headers to hide the problem.

`--download` explicitly restores only missing already-locked source evidence (<10 MB
allowed decoded total). It refuses modified files and verifies hashes. It does not
clone a kernel, obtain a toolchain or sync AOSP. A 404 is evidence about the exact URL/
revision at retrieval time, not proof that equivalent code never exists elsewhere.

## Smallest useful next compile and resource envelope

1. Resolve the transitive DTS/binding closure for the pinned donor on ACK. Import with
   authorship/licenses, reconcile macros and board memory assumptions, then compile
   **only the douglas DTB** with current dtc and run binding checks. A DTB compilation
   establishes syntax/dependencies, not that the board boots.
2. Backport the required clock/pinctrl/PMIC/power and CPU-method integration, retaining
   separate patches. Build a minimal ARM64 kernel plus DTB for console/interrupt/timer
   diagnostics; inspect actual resolved config, symbols, sizes, logs and hashes.
3. Only after a reviewed image/recovery plan, request owner-run early boot logs. No
   serial access, unlock, flash, wipe or device commands occur in these source tasks.

Before step 2, provision a case-sensitive Linux x86_64 build host. Planning estimates,
not measurements: roughly 1–3 GiB network transfer for a shallow source/toolchain set,
15–25 GiB free disk for checkout/output/toolchain, 8–16 GiB RAM, and 10–60 minutes for an
initial minimal build on an 8-core host. DTS-only source fixtures/tooling are much smaller
(order of a few MiB) and should be isolated as the first experiment. Resolve and pin the
actual compiler before transferring it; no toolchain/build environment has been provisioned.

The current Mac has about 35 GiB free and a case-insensitive filesystem; it is an
inspection host, not that environment. A later complete Android sync/build still needs
the substantially larger Linux environment described in CONTINUE.md (400 GiB free,
64 GiB RAM preferred). Neither AOSP nor a whole new kernel/toolchain was downloaded here.
