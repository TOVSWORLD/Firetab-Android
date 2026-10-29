# Separate static PID1 source package

Updates #27. `init.c` and `memory.c` now link a standalone freestanding AArch64
PID1 through the accepted ACM adapters. `build_usb_acm_initramfs.py` builds and
inspects a deterministic separate archive. It never executes the AArch64 binary,
packs firmware, changes a DT or accesses a device. The existing minimal PID1 and
its archive builder are unchanged. CI compiles both packages separately.

**The current package denies gadget admission.** Seven source gates are all zero:
qualified loading, independent return, retained logs, device role, enforcing policy,
immutable namespace and assigned USB descriptors. No boot argument/token or builder
option enables them. The archive builder rejects edits enabling any gate or setting
physical VID/PID. These are unresolved runtime dependencies, not approvals supplied
by a successful build. 0xffff values exist only in native RAM test fixtures.

PID1 opens only a nonblocking console, reports a fixed admission result and idles
when denied. Failure to open console does not fall back to an unknown blocking fd.
It never prints cmdline, UDC name, descriptors, memory contents or household IDs.
Output is bounded to128 bytes/16 syscall attempts and tested against EINTR/short/
zero/oversized/error returns. This is **console status output**, not ACM serial
transmission, boot-log export or a host receipt.

The actual admitted source path is exercised only through RAM callbacks:

1. Mount only proc/sysfs/selinuxfs read-only with nosuid/nodev/noexec.
2. Require exact enforcing readback in addition to the separate qualified-policy
   gate. Readback alone does not prove a policy is loaded or permits this workflow.
3. Discover exactly one expected USB0/peripheral UDC before mounting configfs.
4. Mount configfs nosuid/nodev/noexec, perform the owned configuration transaction,
   emit a fixed console status and perform one-shot cleanup.
5. Unbind before deleting resources. Preserve the primary error. Never retry failed
   setup cleanup implicitly; retain mounts if gadget cleanup fails. Unmount only
   successfully owned mounts in reverse order, stopping on the first error.

No lazy/forced unmount, writable sysfs, role change, permissive SELinux, policy
loading/bypass, shell, ADB, storage function, block device, reboot or watchdog
interface is provided. Pre-existing/busy mounts fail rather than being adopted.
The external immutable-namespace assumption and physical rollback are unqualified.

Compiler support `memset`/`memcpy` is explicit and tested with guarded buffers;
GNU initially exposed a missing memset during static linking. The implementations
use volatile accesses to prevent recursive builtin folding, without relaxing warnings.

Reproduce native sanitizer controls with
`python3 -m unittest discover -s tests -p test_usb_acm_pid1.py -v`.
Build the separate Clang18 archive with `python3 scripts/build_usb_acm_initramfs.py`.
Local GNU alternative: `--compiler /opt/homebrew/bin/aarch64-linux-musl-gcc
--compiler-kind gcc`; this is separately identified and does not substitute for CI
Clang evidence. ELF checks reject dynamic/interpreter segments and invalid entry;
newc checks enforce exactly five directories, console and PID1, fixed permissions,
zero ownership/time and no extra endpoints. No admission file is packaged.

Next actual implementation: bounded ACM serial endpoint discovery/output and
associated failure/cleanup controls. Assigned physical descriptors, loading,
peripheral-role experiment, runtime enforcing policy, analog/clock behavior,
independent failed-load return and retained-log tests remain separate gates.
