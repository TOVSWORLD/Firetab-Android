# Draft ACM userspace adapters

Updates #27. These unlinked C headers implement a bounded configuration transaction,
filesystem callback adapters and conservative UDC discovery. They are not PID1,
a syscall bridge, an initramfs or an admitted USB transport. The existing minimal
PID1 and both disabled DTBs are unchanged. PR420's matching builtin ACM/security Image build40828537870 passed atbd288c7;
that compilation result does not authorize runtime binding or qualify this package.

The transaction owns only `/config/usb_gadget/firetabs-diagnostic`, reverses its
successful creations and preserves the primary error. A failed bind attempts
newline unbind first; failed unbind stops deletion. ENODEV on unbind counts as
success only after a successful close and bounded empty-UDC readback. Attribute
writes must complete in one store; partial writes fail rather than being split.
Close is never retried after EINTR. Only allowlisted paths reach write callbacks.

Discovery requires exactly one UDC and exact USB0 compatible/reg/peripheral
properties through its controller parent. Missing metadata, OTG, USB1, multiple
UDCs, oversized reads and malformed/incomplete directory scans fail closed. This
strict source-derived path has not been exercised on a device. It does not solve
concurrent filesystem mutation, physical role ownership or runtime security policy.
A separately qualified immutable namespace and security admission are prerequisites.

The caller must supply admission; absent admission causes no transaction callback.
Test VID/PID 0xffff values are RAM syntax fixtures, not assigned descriptors.
No serial identifier, shell, ADB, storage endpoint, block mount, role write or
security-policy bypass is provided. Sysfs permissions and enforcing SELinux policy
remain real integration prerequisites. No mount or writable-sysfs setup is hidden here.

Run `python3 -m unittest discover -s tests -p test_usb_acm_userspace.py -v`.
The actual headers execute only with RAM-backed callbacks under ASan/UBSan.
`python3 scripts/validate_usb_acm_userspace_abi.py` verifies pinned ACK source,
generated ARM64 syscall-table provenance, flags, dirent and configfs semantics.
GNU AArch64 object compilation checks syntax/ABI only; no AArch64 binary runs.

Next: separate opt-in static PID1, mount/security admission, bounded diagnostic
output and archive inspection, then independent loading/role/recovery/log gates.

Subsequent accepted/source integrations: PID1.md describes the separate static
package; SERIAL.md describes the actual bounded fixed-frame adapters. Current
package admission remains denied, and physical USB/log transport is unqualified.
