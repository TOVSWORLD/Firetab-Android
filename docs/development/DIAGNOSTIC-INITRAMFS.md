# Isolated diagnostic userspace — issue #41

This is a build experiment supporting #21, not a boot image or a user test
package. It is not integrated with a kernel, DT or bootloader. No firmware
packing, device transport, unlock helper or block-device access is involved.

`projects/firetabs-android/diagnostic/init.c` is a freestanding AArch64 PID 1.
It opens `/dev/console` for output and prints `FIRETABS_DIAGNOSTIC_INIT_V1`.
It mounts proc and sysfs with read-only/nosuid/nodev/noexec flags, reports each
mount result, and reads only `/proc/version`, `/proc/meminfo`, `/proc/iomem` and
`/proc/uptime`, each capped at 16 KiB. It prints a final
`FIRETABS_DIAGNOSTIC_IDLE` marker and sleeps indefinitely. It has no storage
mount, block node, network, reboot, shell or application interface. It does not
collect command lines, CPU serials or household app data.

The small newc archive contains only `init`, `dev/console` (character 5:1) and
`dev`, `proc`, `sys` directories. UID/GID/timestamps and gzip metadata are fixed.
No devtmpfs is mounted. This avoids exposing storage nodes to the diagnostic
userspace; it does not prevent the kernel's own drivers from probing hardware.
It does not establish power sequencing or driver safety on the tablet.

On an existing Linux LLVM 18 environment:

```sh
python3 scripts/build_diagnostic_initramfs.py --clang clang-18
```

Outputs remain ignored under `out/diagnostic-initramfs`: static `init`,
`initramfs.cpio.gz`, and a JSON report with command, compiler, source and artifact
hashes. Builder requires Clang and LLD; it downloads nothing. CI uses the existing
Ubuntu hosted toolchain. Resource scope is a single tiny C compilation, well
under 100 MiB working space; no full Android sources, dedicated machine or paid
resources are needed. Compiler/version changes can change the ELF/hash; matching
source, toolchain and flags are required for binary reproducibility. ELF checks
reject interpreters/dynamic segments, wrong architecture and an invalid entry.

The earlier full provider kernel config has BLK_DEV_INITRD, RD_GZIP, BINFMT_ELF,
PROC_FS and SYSFS enabled (retained combined config in evidence/pinctrl-port).
That is configuration evidence, not proof of initramfs handoff or execution.
The entry code and syscall numbers are AArch64-specific and cannot run as a
32-bit kernel process. No emulation or hardware runtime test has occurred.

A console marker would establish only that the kernel loaded this userspace
and reached that point. It would not establish storage, graphics, Android or
Crestron functionality. Missing markers could mean console routing, loader,
firmware, memory or kernel failure; a black screen is not diagnostic evidence.
Qualified logging, actual memory reservations, stock loader acceptance and
recovery remain gates in #21 before any boot image or physical test instructions.
