# Explicit builtin ACM diagnostic compilation — #27

This is a separate opt-in usb-acm-diagnostic Linux build mode. The older
usb-providers mode, USB-off minimal diagnostic fragment and generic/QEMU scope
remain unchanged. This mode does not build a boot image, select a physical USB
role, configure a gadget or execute PID1 on a device.

The requested fragment makes configfs/libcomposite/ACM/u_serial builtin, retaining
the existing USB provider/dual-role path and explicitly enabling SELinux with its
security-network dependencies.
Other configfs gadget functions, including mass storage, networking and FunctionFS,
are disabled, along with optional Android configfs uevents. The initial generic baseline lacked SECURITY_NETWORK/SELinux and its LSM list
excluded SELinux; the first run correctly failed the security guard. The revised
profile adds SELinux to the preserved baseline LSM order and disables its boot
disable/permissive build switches. Security is not disabled to obtain logs. The checker rejects modular or missing required
symbols, enabled forbidden functions, ambiguous symbols and missing SELinux compile
state or an LSM list excluding it. It does not establish runtime enforcement or a usable gadget.

The actual apply path runs before olddefconfig; the checker runs afterward. Linux
CI must compile MUSB/T-PHY plus the seven libcomposite component translation
units, f_acm.o and u_serial.o, retain
their explicit W=1 pre-Image hashes and resolved config, then build Image/vmlinux.
USB_ACM_BUILTIN_OBJECT_COMPILE_COMPLETE is separate from the provider marker.
Only an actual successful exact-head run establishes those claims; host policy
fixtures are synthetic and are not Kconfig resolution. Resource gates are unchanged.
Source-path selection chooses one ACM build for this profile, never a duplicate
provider build or a generic QEMU claim. Forced generic arguments/QEMU requests
are rejected for this mode.

PR419 merged37256b14f619b34018817ed0ac1fb11a7c5d6451 after six exact-head checks
and successful USB provider/Image run40822461567 at93e62f8. Its normalized receipt
is evidence/usb-role-errors/build-result.json. That accepted MUSB error-handling
source is reused; its earlier modular gadget config does not qualify this changed
profile. A new exact-head ACM build is required.

The current minimal PID1/initramfs remains unchanged and lacks gadget setup.
Static opt-in gadget PID1/configuration code, actual RAM failure/cleanup controls,
and any separate disabled device-mode experiment are subsequent package work.
No shell/ADB/storage export, security weakening or unattended device/mode action
is authorized by this profile. Both DTs remain disabled; canonical34/isolated28
binding failures and physical USB/loading/independent return/log gates stay open.

The first run40826710226 at6bbdd03 resolved ACM components builtin but failed before
object compilation at the strict SELinux check. The corrected profile explicitly
requests SECURITY/SECURITY_NETWORK/AUDIT/NET/INET/SELinux and LSM membership;
actual replacement resolution/build is still required. Build-time security
selection is not runtime policy/enforcement proof; policy/permissions remain
prerequisites for any future diagnostic userspace, without bypasses for logging.

Replacement run40827564991 ataade0fa passed the actual ACM/security/LSM resolution
and provider object checks, then rejected the nonexistent builtin aggregate
libcomposite.o probe. The probe now derives/hash-locks nine actual component C
object targets from the pinned Makefiles. Requested configuration is unchanged;
new exact-head component/Image validation is required, not a claimed prior pass.
