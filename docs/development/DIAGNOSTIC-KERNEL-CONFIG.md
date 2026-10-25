# Restricted diagnostic kernel compile — issue #44

The earlier provider Image used generic ARM64 defconfig. Even a storage-free
initramfs does not stop a kernel from probing block devices before `/init`.
The separate `diagnostic` build mode starts from the same pinned ACK/compiler
baseline, applies the same clock/pinctrl/power-provider overlays, then applies
projects/firetabs-android/kernel/diagnostic/fragment.config before olddefconfig.

The fragment requires the implemented MT8163 providers, UART/early-console and
initramfs/ELF/proc/sysfs support. It disables BLOCK, MMC, MTD, SCSI, ATA, NVMe,
networking, USB, DRM/FB, sound, watchdog, CPU frequency/idle policy, suspend and
hibernation. This is a compile experiment, not a final Android configuration.
Resolved disabled symbols must not be built-in or modular; enabled requirements
must resolve to built-in. Missing/disabled symbols do not compile; the policy
checker does not claim every disabled symbol is independently available on ACK.

The kernel still initializes clocks, pinctrl, PMIC and power domains and other
remaining subsystems. Disabling block access does not establish hardware safety,
correct voltage/power sequencing, a working UART or recovery. The experiment
changes no DT memory declarations, PSCI compatibility or loader arguments. It
uses no maxcpus/console command-line assumption to imply stock compatibility.

Reproduce on the previously documented Linux LLVM18 host, from a clean workspace
without work/ack-baseline/source:

```sh
bash scripts/build_ack_baseline.sh diagnostic
```

As in prior provider builds: single pinned ACK fetch (observed ~0.3 GiB Git
storage, 3 GiB post-transfer storage gate), at least 15 GiB free disk and 7 GiB
RAM, hosted timeout 60 minutes. Build time is unmeasured for this configuration;
previous full generic provider builds took about 37 minutes. No new toolchain,
full Android download or paid host is provisioned. The builder never packs,
uploads, flashes or boots firmware.

The workflow's automatic provider compile now uses this diagnostic integration
mode. Other explicit modes remain available by workflow_dispatch. Actual
provider objects compile W=1; Image/vmlinux and deterministic gzip Image size and
hashes are logged, followed by the complete resolved config. Gzip size alone
cannot establish partition fit: DT, initramfs, header, padding, loader acceptance
and matching stock image evidence remain necessary. A separate initramfs build
exists in #41, but is not appended or packaged by this experiment.

Kernel compilation, DT validation, boot, hardware operation and Android/app
reliability remain separate gates. No physical test instructions are authorized
or provided here; #21 still needs actual stock memory/loader and recovery/log
facts before a qualified test package can be prepared.
