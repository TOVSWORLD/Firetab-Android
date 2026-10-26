# Opt-in forced diagnostic command line

This compile experiment provides a kernel-side alternative to relying on LK to
preserve DT bootargs. It is not enabled in the default diagnostic workflow and
has not been compiled, booted or electrically qualified. No firmware is packed.

At pinned ACK d9318bdb4c34e8b2d997b4f67ced56b120b22b87, arm64 Kconfig2447–2484
supports CMDLINE_FORCE. In drivers/of/fdt.c1094–1164, FORCE disables reading the
DT bootargs and copies CONFIG_CMDLINE on the normal chosen-node path. EXTEND
would append loader arguments after defaults, leaving conflicting arguments
possible. The candidate diagnostic has a chosen node. The branch with no chosen
node skips the copy; do not claim this is independent of all DT requirements.
Exact source URLs/hashes are in evidence/commandline-policy/source-index.json.

The optional fragment requests unique nr_cpus=1/maxcpus=0, the same early UART0
MMIO mode/base present in the statically identified stock LK buffer, and normal
console ttyS0 framing921600n8. This is an experiment parameter, not an observed
physical UART setting. Current LK's original buffer already contains earlycon
and several console tokens, including n1 framing strings; DT absence therefore
does not establish final absence. Static bytes and runtime delivery are distinct.
The existing exact-LK report's hash is rechecked before extracting allowlisted
console-only tokens; no per-device arguments are published.

Generic earlycon parsing maps mmio32 to regshift2; with no explicit baud option,
8250 early setup assumes firmware already initialized the UART. It masks
interrupts; it does not prove clocks/routing are usable. Source: earlycon.c103–115
and8250_early.c153–171. This route avoids an early dependency on stdout alias
resolution but does not solve physical pads, voltage, clock state or loader entry.

**FORCE discards all incoming bootargs.** Before a device test, audit every
required firmware memory/security/platform parameter and explicitly preserve any
needed constraint. The isolated initramfs does not need a stock root filesystem,
but that is insufficient to conclude all incoming arguments are dispensable.
DT memory/initrd/reservation handling is separate; forced arguments neither
repair unsafe RAM placement nor disable all firmware calls. Recoverability and
usable physical logs remain open. Do not apply this to a general-purpose ROM.

For a future separately gated compile, first apply the existing diagnostic
policy, then this optional fragment using the kernel config tooling, resolve with
olddefconfig, and run:

`python3 scripts/check_diagnostic_commandline.py /absolute/path/to/resolved.config`

The fragment alone is not a resolved config and must fail that checker because
it lacks the other required built-ins. This step does not build or run anything.
After any compile, identify the exact resulting Image/initramfs/config hashes;
the prior generic QEMU result does not cover this profile. Then prove effective
arguments through the existing sanitized init reporter and live kernel console.
No new compile/download/paid job was started for this PR. Tests use config text
only and cannot establish the kernel-source semantics or runtime execution.

## Generic mechanism experiment (#119)

The build helper now accepts ARGUMENT_PROFILE=generic-force only in diagnostic
mode. This separate profile uses QEMU PL011 (ttyAMA0), not the device UART
address. It retains generic initramfs/earlycon/panic parameters plus unique
nr_cpus=1/maxcpus=0. Kernel config tooling applies it before olddefconfig and a
resolved-config check runs before compilation. Manual workflow dispatch defaults
to argument_profile=none; compile-triggering PR smoke tests select generic-force
so the changed mechanism receives actual runtime coverage. The device profile
is never applied automatically.

The VM receives deliberately conflicting nr_cpus=4/maxcpus=3 in its incoming
arguments. --force-argument-test verifies the resolved generic profile before
launch and requires the actual sanitized init verdicts to report both intended
limits valid. One online CPU alone cannot pass. PSCI status and primary-only
contract remain separately reported; generic virt need not disable PSCI and
therefore this proof is not a primary-only firmware-call qualification.

This is a new compile/runtime experiment, not covered by prior QEMU evidence.
Expected existing resource gate:~0.3GiB source fetch (postfetch hard cap3GiB),
15GiB free disk,7GiB host RAM,60-minute CI timeout,512MiB VM,120-second VM limit.
Prior compile took~24minutes. No paid host or tablet operation is involved.
Exact source/config/Image/initramfs/console hashes are emitted in CI/report.
Keep119 open until the actual compiled run passes and its evidence is retained.
