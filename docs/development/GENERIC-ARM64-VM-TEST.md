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
