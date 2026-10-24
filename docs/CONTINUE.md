# Continue the douglas port

## User-confirmed device and acceptance scope

- Fire HD 8 (2017), douglas / KFDOWI.
- Fire OS **5.7.1.0**, reported by user, 24 October 2026.
- **16 GB model**, inferred from reported 12.33 GB internal capacity; separate SD
  card reports 30 GB. RAM is 1.5 GB per Amazon's specification, not 12.33 GB.
- User reports a CP4 lab processor on latest firmware; exact processor suffix and
  firmware string are not recorded. Verify Home runtime/model from the processor
  when testing; a generic CP4 label alone does not verify CP4-R/Home compatibility.
- **Full Home app functionality required**, not a lighting-only panel. Include
  applicable camera feeds, intercom/audio and media controls in acceptance tests.
  A remote camera feed tests networking/decoding; it does not inherently require
  the tablet's own camera. Two-way video may introduce that additional requirement.

No physical tablet changes are authorized. Do not run any amonet, unlock, flash,
format, sideload, reboot-to-exploit, repartition or installer script.

## Resource gate before a complete build

This machine: Apple Silicon arm64 macOS, 36 GiB RAM, ~42 GiB free after inspection
clones, case-insensitive filesystem. `python3 scripts/preflight.py` records this
and exits 2. The kernel checkout generated real filename-collision warnings;
its apparent dirty files are case collisions, not intentional source edits.
Do not use this checkout to build or copy files into a case-sensitive tree.
Re-fetch from Git on the build host.

Google's [AOSP host requirements](https://source.android.com/docs/setup/start/requirements)
call for a 64-bit x86 Linux host, at least 400 GB free (250 GB source + 150 GB build),
and at least 64 GB RAM for current AOSP. For the older Android 11 candidate, budget
32–64 GiB RAM and 400–500 GiB free; 64 GiB is preferred. These are planning values,
not measurements of this specific build. The preflight's 32 GiB threshold is a
candidate floor, not a claim of meeting current AOSP's full recommendation.

Expected downloads, **not started**: roughly 80–150+ GB network transfer for a
shallow Android 11 platform sync (highly variable), plus compiler/JDK/prebuilts and
package-manager dependencies. Current Android source may require more. Reserve
250+ GB for checkout, 150+ GB for output, and optionally 25–50 GB for ccache.
The container image may consume several additional GB. GApps/browser packages
are separate; versions, architecture and sizes must be selected and reported.

Planning build time on a Linux x86_64 SSD host with 16–32 CPU threads and 64 GiB
RAM: several hours (roughly 2–8) for a clean older-platform build, potentially
longer with swap, emulation, slow disks or repeated failures. No local benchmark
exists. Porting/debugging time is separate and may span weeks or more.
No paid machine was provisioned. A future cloud host requires cost approval.

Unavailable/unvalidated dependencies here: suitable Linux build host and volume,
full Android source/prebuilt toolchains, a resolved all-project platform manifest,
a validated 4.9 douglas kernel build, current Home APK ABI/feature manifest,
matching GApps, stock firmware/preloader hashes, hardware logs and a backup/recovery
plan verified by the user before any later physical work. No proprietary source
for the old GPU/HAL blobs was found; binary copies are present in upstream vendor
repositories. Redistribution/license status was not assessed.

`Dockerfile` is an **unbuilt environment recipe**, not a provisioned or verified
container. It uses Ubuntu 22.04 amd64 with the usual Android 11 build tools/JDK 11.
Its image tag and apt package versions are not digest/snapshot locked. Record
those if building it, then pin the resulting image digest. It does not install
repo, sync Android, apply patches or interact with USB automatically. Running an
x86 container under macOS emulation does not solve the disk/case-sensitivity
problem and is not recommended for the full build here.

## Reproduce the completed inspection

From the FireTabs project root:

```sh
python3 scripts/restore_sources.py
git -C sources/device-douglas switch -c port/android11-bringup
git -C sources/device-douglas apply ../../patches/0001-douglas-require-correct-vendor-and-common-paths.patch
python3 scripts/check_sources.py
python3 scripts/probe_android11_patches.py
python3 scripts/preflight.py
```

On this existing workspace the branch and device patch already exist: do not apply
them twice. `restore_sources.py` preserves existing checkouts and refuses revision
mismatches; it does not reset local changes. On a fresh machine it fetches shallow
inspection clones at exact commits. That includes ~1 GB expanded legacy kernel
and ~133 MB common vendor tree; it does **not** fetch the full Android platform.
No helper executes source repository install scripts automatically.

The patch probe downloads only files touched by eight existing patches, plus
two moved bitmap files, into `work/patch-probe`. It checks each original patch
independently, not as an integrated series. It saves diagnostics and SHA-256
hashes. The isolated Git invocation rejects silently skipped fixtures. A passing
`git apply --check` proves neither compilation nor correctness.

## Development tracks and concrete next steps

1. **Baseline reproduction (Android 10).** On the resource-qualified Linux host,
   initialize the LineageOS 17.1 platform, put `manifests/baseline-17.1.xml` under
   `.repo/local_manifests/`, then sync. Apply the tracked device-path patch under
   `device/amazon/douglas`. Check the old platform patch series with `git apply
   --check` before applying it. Do not run upstream `patches/uninstall.sh`: it
   contains destructive checkout/clean operations. The signature-spoofing and
   global stack-protector-disable patches need explicit review, not blind reuse.
   Record the platform lock with `repo manifest -r -o resolved.xml`, tool versions,
   build command and log. Build a baseline before changing kernel and userspace
   together.

2. **Android 11 integration.** The platform manifest head inspected here is
   `88e370827501474db8f1905128fdea2e8128ead4`. Initialize this revision in a new
   build directory, then resolve all nested project revisions at sync time.
   `manifests/candidate-18.1-kernel49.xml` pins device dependencies and substitutes
   the newer kernel at `kernel/amazon/mt8163`. This is an experimental dependency
   selection, **not a complete buildable Android 11 manifest**. The older common
   tree still declares kernel 3.18/GCC and old HAL/linker/APEX settings. Adapt those
   deliberately; do not mistake manifest installation for completed integration.

3. **Kernel-first option.** Build the amazon-oss 4.9 douglas defconfig, preserving
   both douglas DT variants and boot-image limits. Derive the actual `.config`
   using the reference build's Android config fragments; a savedefconfig alone
   cannot establish enabled BPF/SELinux/binder features. Compare touch controller
   coverage (old tree includes Goodix and FT5526; the inspected new defconfig lists
   Goodix), panel, regulator, PMIC, Wi-Fi module ABI and suspend. Keep boot-header
   offsets and amonet packaging until their contract is understood. A kernel-only
   test with baseline userspace, later performed by the user, isolates failures.

4. **Finish the Android 11 patches.** A bitmap workaround has been rebased to
   `libs/hwui/jni/Bitmap*.cpp` in the tracked `patches/android11/` directory and
   passes a source applicability check. This preserves upstream workaround
   behavior, including questionable bitmap resizing/semantics; test it with Home
   and Chrome before retaining it. Four other original failures remain. Determine
   whether the audio presentation-position suppression is still necessary, rebase
   CPU-rendered VSync changes only if logs justify them, omit microG spoofing when
   building for real Google services, and investigate blob failures before
   globally disabling stack protection. Consider the newer reference fdsan patch
   only with evidence of that failure. Review Android 11 linkerconfig generation,
   legacy shim injection, moved/removed modules and HIDL services next.

5. **Build commands, after integration.** Source `build/envsetup.sh`, select
   `lunch lineage_douglas-userdebug`, then `mka bootimage` and `mka bacon` as
   appropriate. These are continuation commands, not commands already run.
   Use a bounded job count based on memory. Record every failure verbatim. Before
   transferring anything, inspect target-files/image contents, expanded image
   sizes, vendor inclusion, init/SELinux/VINTF, and boot patch preservation.

6. **Newer Android.** Only after the 4.9 kernel and Android 11 HAL baseline is
   validated, evaluate Android 13 then 15. Android 17 adds stronger BPF, compiler,
   linker/APEX and hardware-interface requirements; maintain an inventory of real
   required kernel backports and API removals, not a changed version label.

## Separate acceptance gates

**Compiles:** completed platform/kernel build, included blobs, matching ABI,
image/partition fit and a recorded source/toolchain lock. Not reached.

**Boots:** user-supplied kernel/serial/pstore/logcat evidence, working init, mounted
data and stable SystemUI. No physical test performed.

**Hardware works:** display/touch accuracy, Wi-Fi reconnect, suspend/wake, rotation,
charging/thermal behavior, speaker/microphone, media decode and relevant camera
paths. Camera-feed decoding and the tablet camera are separate tests.

**Crestron is reliable:** current exact package installed, correct Home processor
identified, pairing/authentication, all configured control types, feedback updates,
room/navigation transitions, media metadata/artwork, camera/intercom as applicable,
TLS and remote/local access, repeated wake/reconnect and a 48–72 hour powered soak.
Capture app crash/ANR, OOM and network logs. Test Home and browser switching with
GMS active. Define acceptable latency with the user; do not invent a pass result.

**Deployable panel:** enforcing SELinux, documented security limitations, repeatable
recovery, charging/screen behavior and acceptable long-run performance. An app
launch or one successful light toggle is insufficient for the full-function goal.

Later read-only diagnostics the user can supply include `getprop`, `uname -a`,
`/proc/meminfo`, `wm size`, `wm density`, partition symlinks, `dumpsys media.codec`,
`dumpsys SurfaceFlinger`, installed Home package metadata and relevant logcat.
These have not been run. Logs can contain household names, addresses or tokens;
redact those before sharing. Do not enable or connect ADB without a separate request.
