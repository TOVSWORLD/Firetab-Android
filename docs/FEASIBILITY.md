# Evidence-based feasibility

Assessed 24 October 2026. “Verified” below means source or published-release evidence,
not a test on this tablet. “Candidate” means engineering work remains.

## Releases and the actual objective

Android 17 is released, API 37. Google's [AOSP build-number reference](https://source.android.com/docs/setup/reference/build-numbers)
lists `android-17.0.0_r1` and build `CP2A.260605.016`. The corresponding current LineageOS
release is **24.0**, announced 11 October 2026 in [Changelog 32](https://lineageos.org/Changelog-32/).
The official announcement was retrieved with curl and its article saved in
`evidence/lineage-changelog-32.html`; the web reader returned 403. The `lineage-24.0`
manifest branch resolved to `b51a0c449a3279ca55fb6d4d91d2143e42e2fff5`.
LineageOS 17.1 is Android 10, 18.1 is Android 11, and 22.2 is Android 15.

The useful near-term goal is an Amazon-ad-free control panel. A Lineage build removes
the Fire launcher/ad software, but reliable operation still depends on Crestron, Wi-Fi,
graphics, suspend/resume, and Google services. A recent Android number alone does not
establish any of those properties.

## Crestron Home, Play, and browser

The exact [official Play listing](https://play.google.com/store/apps/details?id=com.crestron.phoenix.app&hl=en_US)
was fetched directly. Its embedded `ds:5 / 1 / 2 / 140` metadata reports version
**4.12.18+pr**, minimum **API 26 / Android 8.0**, and target API 35. The extracted
structure and interpretation are preserved in `evidence/crestron-play.json`.
The path for the Android version is independently documented by
[google-play-scraper's mapping](https://github.com/facundoolano/google-play-scraper/blob/master/lib/app.js),
saved as `evidence/play-app.js`. This is official store metadata, not a downloaded
APK manifest or a guarantee about every device-specific variant. No APK was downloaded.
Older indexed metadata reporting Android 5.0 belongs to earlier releases.

This is **Crestron Home**, `com.crestron.phoenix.app`. Crestron Go and Crestron App
are separate clients for other Crestron project workflows; Crestron ONE is another
product. Their minimum versions and specifications were not substituted for Home's.
The Home listing requires an installed and licensed Crestron smart-home system from
an authorized dealer. An arbitrary SIMPL project does not establish Home compatibility.
The user reports a CP4 lab on latest firmware and requires full app functionality.
The exact model suffix and firmware string remain unrecorded; camera/intercom and
media paths must be included when used by that Home system.

No authoritative tablet RAM, GPU, or resolution minimum for the current Home app was
found in the inspected listing. Its native library ABI set, mandatory manifest hardware
features, Play Integrity behavior and actual GMS dependency remain **unverified**.
An APK manifest/library inspection and on-device install are needed to close these gaps.
Do not infer that a 64-bit CPU guarantees delivery of the app on stock 32-bit Fire OS.

[Chrome's current official requirement](https://support.google.com/chrome/a/answer/7100626)
is Android 10+. [Chromium's supported platforms](https://chromium.googlesource.com/chromium/src/+/HEAD/docs/supported_platforms.md)
still include ARM and ARM64 Android. Thus the existing Android 10 port clears the
published OS floors for Home and Chrome. That does not make its 2023 image or kernel
fully security-maintained. Browser support duration into the future is unknown.
WebView provider availability and rendering need testing separately from Chrome.

## Hardware and existing source

[Amazon's KFDOWI specifications](https://www.developer.amazon.com/docs/fire-tablets/ft-device-specifications-firehd-models.html?v=firehd8_2017)
identify MT8163V/B Cortex-A53, Mali-T720 MP2, 1.5 GB RAM, 1280×800, 16/32 GB storage,
and stock Android 5.1/API 22 with a 32-bit ABI. This confirms the user's model.
The user confirms Fire OS 5.7.1.0 and 12.33 GB usable internal capacity, identifying
the 16 GB SKU. The exact build string and preloader hashes remain unknown.

All locally cloned sources and revisions are in `evidence/sources.lock.json`.
The [douglas tree at 4c557e6](https://github.com/mt8163-dev/android_device_amazon_douglas/tree/4c557e6b83c62d41ff10090d5ff25dda1caba784)
uses a shared MT8163 board configuration, `douglas_defconfig`, and boot image header 0.
The common tree's `BoardConfigCommon.mk` targets **arm64 plus ARM32**, an ARM64 kernel,
GCC 4.9, flattened APEX, permissive SELinux, and numerous blob shims.
Both ARM32 and ARM64 Mali, gralloc, and composer blobs are present and their ELF
headers were checked. Stock userspace bitness is not an inherent CPU limitation.

The [published releases](https://github.com/mt8163-dev/android_device_amazon_douglas/releases)
most recently provide `17.1-7.0`, 20 May 2023, a 482,286,621-byte ROM archive.
Release notes describe GApps fixes, Wi-Fi fixes and low-memory improvements, but
also incomplete FBE/lockscreen support. Initial notes identify permissive SELinux,
limited camera behavior and software video codecs. These are maintainer reports;
they have not been reproduced here. See `evidence/douglas-releases.json`.

The upstream [local manifest](https://github.com/mt8163-dev/local_manifests) uses SSH
and includes giza unnecessarily for a douglas-only build. It references device,
common device, vendor, common vendor, kernel, and MediaTek hardware repositories.
The new manifests use HTTPS, immutable device dependency revisions and only douglas.
The complete Android platform still needs a resolved `repo manifest -r` after sync.

Direct device forks and common-tree forks were enumerated through GitHub's API;
their metadata is saved in `evidence/*forks.json`. No newer douglas ROM emerged from
that search. This is not proof that no private or unindexed port exists.

## Newer work worth reusing

The active [amazon-oss MT8163 common tree](https://github.com/amazon-oss/android_device_amazon_mt8163-common)
targets Android 11 with a 4.9 kernel, 32-bit userspace/64-bit binder, revised HALs,
and a different vendor layout. Its default configuration is **not** a replacement
for the older common tree without adapting douglas.

More significantly, [amazon-oss's kernel](https://github.com/amazon-oss/android_kernel_amazon_mt8163)
contains `douglas_defconfig`, `douglas.dts`, `douglas_hvt.dts`, the douglas NT35521
LCD driver and thermal/battery settings. The initial defconfig commit is
[`6d3f54d`](https://github.com/amazon-oss/android_kernel_amazon_mt8163/commit/6d3f54d35debcdb0a6b9d3dcbb348f3501d2b7c3),
dated 22 October 2025. The Android 11 branch was pinned at `9ca9d53b90fe1e8271a30ad135d4d645c4b03e63`;
its Android 15 branch at `a81e526957ef342c4ea0c7ff5a3e95366427d0cd` reports Linux 4.9.337.
Selected files and provenance are saved in `evidence/`. A defconfig and branch name
do not establish a complete, booting Android 15 douglas port.

The [giza Android 11 tree](https://github.com/amazon-oss/android_device_amazon_giza)
is active as of October 2026. Related Echo MT8163 Android 11 projects and
[mustang work](https://github.com/GuestyMC/android_device_amazon_mustang) offer
HAL, fdsan and kernel integration references, not interchangeable ROMs. The
amazon-oss patch set has a targeted fdsan compatibility change worth evaluating
against actual douglas logs. [Initial upstream MT8163 support](https://lists.openwall.net/linux-kernel/2026/10/19/32)
demonstrates an Echo Dot UART shell with replacement firmware; it does not yet
demonstrate a douglas display, Wi-Fi or Android stack.

## Android 17: verified obstacles and open questions

**Boot chain — a route exists, exact-device prerequisite unverified.** The original
[chaosmaster amonet douglas branch](https://github.com/chaosmaster/amonet/tree/mt8163-douglas)
contains device-specific exploitation/install code. Its README still says suez;
do not rely on that README as douglas instructions. The existing common tree's
`recovery/root/fix-bootpatch.sh` preserves an amonet boot payload, so generic recovery
packaging cannot be substituted casually. Newer
[amonet-koboreru](https://github.com/R0rt1z2/amonet-koboreru) explicitly includes
`devices/douglas.c` and `include/devices/douglas.h`; its README says newer preloaders
are patched. Neither source proves the user's Fire OS 5.7.1.0 installation can
follow a specific unlock procedure. The provided XDA threads returned 403/502;
their full current instructions were not verified. No unlock/install scripts were run.

**Kernel — hard blocker for unchanged baseline.** The mt8163-dev kernel is
3.18.19 (`Makefile`), and its `include/uapi/linux/bpf.h` has only the UNSPEC map
and program type entries. BPF files existing in the tree do not mean modern eBPF
works. [LineageOS Changelog 26](https://lineageos.org/Changelog-26/)
documents the old-kernel networking problem for 3.18 and below.

There is also a precise modern runtime gate: Android 17's
[`NetBpfLoad.cpp`](https://android.googlesource.com/platform/packages/modules/Connectivity/+/refs/tags/android-17.0.0_r1/bpf/loader/NetBpfLoad.cpp)
checks kernel capabilities/versions in `doLoad`, including a `<4.9` rejection
at lines 1551–1553, then stronger release-dependent gates. A copy is saved in
`evidence/NetBpfLoad-android17.cpp`. The LineageOS 24 file at
[`7c04d86`](https://github.com/LineageOS/android_packages_modules_Connectivity/blob/7c04d866538e6f689823b769fb5c1e614ca0e295/bpf/loader/NetBpfLoad.cpp)
retains those gates. A compatible effective kernel-version mechanism would still
need the real BPF functionality; renaming the kernel or deleting checks is not a
networking implementation. No loader was executed on hardware in this investigation.

The discovered 4.9 douglas kernel removes the need to begin that work from 3.18,
but its fully resolved config, backport coverage, driver compatibility and boot
remain untested. Changelog 32 explicitly permits official 4.4/4.9 submissions
only for LineageOS 22.2, while acknowledging unofficial 23.2/24 ports. This is
a support policy and a warning about engineering scope, not proof of impossibility.
Modern Lineage kernels require extensive BPF backports and builds without GCC.
The existing GCC-based douglas build does not meet that condition.

**32-bit userspace — not a verified hard blocker.** LineageOS 24 retains an
ARM64+ARMv7 board configuration (`evidence/los24-armv7.mk`). That is evidence of
multilib build definitions, not proof that all old 32-bit vendor processes work.
The most credible candidate preserves ARM64 with ARM32 support or deliberately
adapts the newer ARM32 reference stack; the latter needs separate app ABI checks.

**Graphics/HALs — substantial, verified legacy dependencies; runtime outcome unknown.**
`proprietary-files.txt`, `extract-files.sh`, `libshims/ui/`, `configs/ld/ld.config.txt`,
and the HWC2-on-HWC1 patch show dependence on old Mali EGL/gralloc/composer,
libui/libgui/binder interfaces, customized namespaces and modified blobs. Android
17 is not ABI-compatible merely because both builds are ARM64. Existing HAL1
camera, legacy audio, keymaster and OMX paths also need auditing/replacement.
No Vulkan requirement or blanket “old GPU cannot boot” claim is established here.

**SELinux — unsuitable for an assessed secure panel today.** The current board
sets `androidboot.selinux=permissive` and `SELINUX_IGNORE_NEVERALLOWS=true`.
Enforcing policy needs per-service domains, labels and actual AVC logs. Old
vendor security patch metadata does not imply vendor fixes have been backported.

**Memory/storage — constrained, not a proven boot blocker.** 1.5 GB RAM must hold
Android, Home, browser and GMS; app switching, media and long uptime may cause OOMs.
Existing zram and reduced-memory settings help but are not measurements. The
tree reserves 1,692,925,952 bytes (~1.58 GiB) for system, 16 MiB for boot, and
17,340,416 bytes for recovery. Modern system+GApps size must be measured before
packaging. Userdata is hard-coded for the 16 GB variant; actual GPT must be checked
before image generation. No repartitioning is authorized or proposed here.

**Google services — possible baseline route, no certification guarantee.** The
Android 10 release reports a GApps installation fix. For that ARM64 build use
matching Android 10 ARM64 packages; a deliberately ARM32 Android 11 build instead
needs ARM packages. microG signature spoofing is not Google Play. Google licensing,
Play certification/Integrity, package availability, partition fit and current Home
behavior are separate gates. No GApps archive was downloaded or validated.

**GSI — not a shortcut on the current source layout.** The board launched at API
22, mounts a monolithic system partition, places vendor files under system, uses
private platform shims and does not establish cross-version VNDK isolation. A HIDL
manifest alone is insufficient. Google's [GSI eligibility documentation](https://developer.android.com/topic/generic-system-image)
requires Treble compliance and vendor-interface compatibility. A separate vendor
partition is not alone a sufficient or necessary test; this tree's system coupling
is the material issue. Treblizing it would itself be a port involving linker,
VINTF, HAL, boot and partition work. Do not download/flash an ARM64 GSI on the
assumption that installing Android 10 makes the tablet Treble compliant.

## Practical version assessment

- **Android 10:** published douglas baseline and the shortest route to testing Home
  and a currently supported browser. Hardware/reliability still need verification.
- **Android 11:** the best-supported next development milestone. Existing douglas
  4.9 board support, current adjacent-device work, and initial compatibility work
  make this a credible attempt. No successful local compilation is claimed.
- **Android 12/13:** reasonable subsequent investigation on a validated 4.9 kernel,
  requiring resolved BPF config and substantial graphics/HAL modernization.
- **Android 15:** the newest defensible *stretch target* found, because a related
  4.9 kernel branch includes douglas files and Lineage supports this kernel family
  on 22.2. This is not an established achievable ceiling or a functioning douglas ROM.
- **Android 17:** blocked with the unchanged 3.18 stack. A 4.9/backport/platform
  compatibility route or a newer-kernel board port is conceivable, but current
  evidence cannot justify promising it or choosing it over kernel-first bring-up.

An absolute newest achievable Android version cannot honestly be established before
kernel boot and HAL tests. Android 11 is the practical initial target; Android 15
is a staged research destination. Nothing found proves Android 17 is fundamentally
impossible on the silicon.
