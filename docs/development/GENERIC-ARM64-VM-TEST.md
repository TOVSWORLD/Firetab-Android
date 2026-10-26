# Generic ARM64 VM diagnostic test — issue #49

The restricted kernel and diagnostic initramfs have compiled. Their runtime
interface can be exercised independently of the unresolved stock loader/memory
contract. [QEMU's virt board](https://www.qemu.org/docs/master/system/arm/virt.html)
is a generic virtual platform, not a real board model. This test uses its
versioned virt-8.2 machine, Cortex-A53 CPU model, GICv3 and PL011 UART.
It does not emulate MT8163 clocks/pinctrl/PMIC/storage/display, the stock loader,
its DT selection/fixups, firmware authentication or recovery. A passing result
must not mark douglas boot/hardware or Android/app validation gates as passed.

## Resource and dependency gate

Previous CI retained kernel hashes/config but not downloadable binary outputs,
so one restricted-kernel replay is required. It uses the same pinned ACK source
and provider overlays and the already reported resource gate: observed roughly
0.3 GiB Git storage, at least15 GiB free disk and7 GiB host RAM,60-minute timeout.
The QEMU dependency installer runs only with explicit --install on a disposable
Linux GitHub runner, prints an APT URI/size plan and rejects package archives
exceeding200 MiB before installation. Unknown URI-size formats fail closed.
APT signature/hash checks remain enabled and package versions are logged. Existing
kernel-host apt metadata refresh overhead is additional. No full Android sources,
new compiler/toolchain, dedicated paid host or physical-device access is used.

After compilation, the guest has one CPU,512 MiB RAM and a120-second lifetime
cap. It uses software TCG emulation; no KVM/host device passthrough is requested.
No guest disks, network or shared host filesystem are configured. Raw Image and
initramfs are read as VM inputs; no Android boot image is assembled. QEMU supplies
the generic guest DT. These inputs do not exercise the candidate douglas DTBs.

## Test and evidence

The provider workflow runs this test automatically on applicable new/ready PRs.
For an explicit workflow_dispatch use mode=diagnostic and emulated_boot=true.
Existing other compile modes remain available without emulation. Synchronizing
a feature branch does not automatically repeat the heavy build; dispatch it
explicitly after relevant changes, as for prior provider experiments.

On a prepared Linux host, after the restricted kernel and isolated userspace
builds, with an existing QEMU installation:

```sh
python3 scripts/run_qemu_diagnostic.py \
  --kernel work/ack-baseline/output/arch/arm64/boot/Image \
  --config work/ack-baseline/output/.config \
  --initramfs out/diagnostic-initramfs/initramfs.cpio.gz \
  --output out/qemu-diagnostic
```

Use a fresh output path. Resolved restricted policy and the PL011 console must
pass preflight. The runner requires init/proc/sysfs markers, completed bounded
metadata reads (including MemTotal) and the final idle marker. Panic/Oops or
metadata-read failure markers override apparent success. The VM must remain
alive for five seconds after those markers. Early process exit, a2 MiB console
limit or timeout fails the test. The host then terminates only its QEMU process;
the guest has no reboot interface in diagnostic /init.

Report/console remain ignored locally and are printed in CI logs. The report
records exact command, QEMU version, resolved-config/kernel/initramfs/tester and
console hashes, raw AArch64 header fields, limits and outcome. Package versions
are logged separately. This provides generic execution evidence, not hardware
identity, MT8163 driver exercise or a user physical-test package. No emulation
success is claimed until the actual CI run completes and its logs are reviewed.

## First executed result

[CI run 40193403656](https://github.com/TOVSWORLD/Firetab-Android/actions/runs/40193403656),
project `2fc0da6d65371783c13bfd800b3a1630f7fa3511`, passed on 2026-10-25.
The restricted kernel reached diagnostic PID1, mounted proc/sysfs, completed all
four metadata reads and remained alive for the five-second idle observation.
The guest reported MemTotal 486180 kB from its configured 512 MiB. QEMU 8.2.2
used software TCG; the entire VM check took 5.52 seconds. The full CI job took
11 minutes 6 seconds. See `evidence/qemu-diagnostic/generic-runtime-result.json`
for exact hashes, header fields, command and bounded package plan. Config and
initramfs hashes match the prior compiled inputs; the rebuilt kernel has its
own recorded hash. No binary was retained for distribution.

This completes only issue #49 generic execution. Issue #21 remains open for
installed-build identity, runtime RAM/DT fixups, CPU/loader contract and a qualified
recoverable boot/log route. The VM result does not select physical load addresses
or validate a douglas DT, SMP, MT8163 drivers, Android, graphics or applications.

## Image file length versus runtime memory requirement (#88)

`measure_arm64_image.py` now measures diagnostic build outputs before QEMU and
records the same measurements inside the runtime report. Diagnostic builds emit
`work/ack-baseline/image-size-report.json` to the CI log. Reproduce after the
existing build (no new source/dependency required by this tool):

```sh
python3 scripts/measure_arm64_image.py \
  --image work/ack-baseline/output/arch/arm64/boot/Image \
  --gzip work/ack-baseline/output/arch/arm64/boot/Image.gz \
  --output out/image-size-report.json
```

The gzip must be a single zero-timestamp member without optional filename/extra
headers, decode completely and match the raw Image exactly. The build generates
it with `gzip -n -9`. Lengths/hashes and gzip header bytes are measured, not
inferred from ARM64 header image_size. Compressed bytes, decoded file bytes,
declared runtime memory, text_offset and2MiB placement-base alignment remain
separate. No appended DT or physical destination is supplied by this tool.
Capacity comparison is diagnostic evidence rather than a firmware compatibility
check. Tests cover exact28MiB output and one byte above it, malformed/truncated
headers, wrong payload, extra gzip members and nonzero timestamps.

The original QEMU run retained useful size lines in its downloadable log even
though no binary artifacts remain. Run40193403656/job121169023632 at project
2fc0da6d65371783c13bfd800b3a1630f7fa3511 records:

- Raw Image28576256bytes, SHA256
  `08df8a73166bf5bd3a0fefdd9394d8f5d54b2822255e728c2c3873f2e1c56909`.
- Deterministic gzip9187924bytes, SHA256
  `b15d40b14345c5588c751481010f3d3bb1ef9e6cef1b99d5b656465f0e55faaf`.
- ARM64 declared image_size29360128bytes, as recorded by that generic VM test.

Thus the raw file is783872bytes below the selected LK28MiB output capacity. This
removes the suspected output-size blocker for **that exact historical Image**;
it does not qualify compression integration, DT assembly, memory placement,
secure monitor or tablet boot. The old stock address still fails the modern
Image's independent base-alignment requirement. New builds must be measured
again. The historical gzip round trip was not rerun without its binary.

Selected raw CI lines and hashes are in `evidence/image-measurements/`. The full
1471670-byte log was downloaded read-only, hashed and kept outside the repo:

```sh
env -u GH_TOKEN -u GITHUB_TOKEN gh run view 40193403656 \
  --repo TOVSWORLD/Firetab-Android --log > /tmp/firetabs-qemu40193403656.log
```

Integration changes trigger the existing diagnostic CI compile/QEMU experiment.
Its previously reported resource gate remains roughly0.3GiB Git transfer,
15GiBfree disk,7GiBhost RAM and60-minute timeout (prior compile about23minutes).
The measurement tool itself needs no downloads or paid service. No tablet or
firmware-loader execution is involved.
