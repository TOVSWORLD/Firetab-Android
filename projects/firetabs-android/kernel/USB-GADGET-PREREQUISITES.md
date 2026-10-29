# USB0 gadget role/config/package prerequisites — #27

The successful PR416 USB provider/Image build does not establish a packaged
diagnostic gadget. This finite source/host audit identifies the remaining gates
without operating USB, loading firmware or changing the disabled DT.

The pinned ACK MUSB probe reads dr_mode. With the current OTG declaration and
dual-role build it initializes PHY_MODE_USB_OTG and USB_ROLE_NONE. Its OTG init
registers a role switch allowing userspace control. That makes a control path
available in source; it does not demonstrate cable detection or automatic device
role selection. Choosing a future peripheral-only experiment is a distinct
policy decision. Legacy forced-device register bits must not be injected into
the generic OTG path.

The actual cached mtk_otg_switch_set function was compiled and executed with
RAM-only register/PHY mocks. Eighteen combinations cover all three prior/target
roles with successful or failing PHY backends; invalid role rejects EINVAL.
For changed roles, PHY power/mode return values are ignored: the function updates
glue->role and returns0 even when a called backend returns EIO. Repeated roles
return0 without backend calls. This is a source-level error-propagation finding,
not an observed device fault. The initial init path checks phy_init and
phy_power_on, but its final phy_set_mode return is also ignored. Role API success
therefore cannot currently serve as PHY/transport proof.

Exact PR416 resolved symbols show USB_ROLE_SWITCH=y and USB_CONFIGFS_ACM=y, but
USB_CONFIGFS, USB_LIBCOMPOSITE, USB_F_ACM and USB_U_SERIAL are all m. USB_F_FS is
also m. The pinned Kconfig selects the component symbols; the Makefiles map them
to libcomposite, usb_f_acm and u_serial objects. The bool ACM option alone does
not make those components builtin. The existing workflow builds Image/vmlinux
and explicit provider objects, not a gadget module installation/package.

The current diagnostic builder packages only dev, proc, sys, dev/console and
the static init. Current PID1 mounts proc/sysfs with flags15, prints bounded
diagnostic output to its console descriptor and idles. It does not mount configfs,
configure/bind a gadget, select a role, load modules or write a gadget serial
endpoint. Sysfs is mounted read-only. No module tree, loader or gadget setup is
present. Adding builtin configuration alone would still leave that work absent.
Any future USB diagnostic userspace should be an explicit opt-in scope preserving
the existing minimal diagnostic path and its security/storage boundaries.

For a fresh package inventory, the current source was cross-compiled with the
already installed GNU AArch64 compiler and archived using the existing builder's
newc implementation. GNU O2 linked without added runtime helpers; GNU Os emitted
an unresolved memcpy. This is separately identified in package-result.json and
is not asserted to be the canonical Clang CI binary. The artifact was inspected
as static AArch64 ET_EXEC and parsed without extraction or execution. CI also
audits its freshly built Clang archive with the same inventory guard.

The audit reports source_package_ready:false and transport_qualified:false.
Its optional require-ready gate exits1. The ordinary audit command exits0 only
when the pinned diagnostic analysis/package contract remains intact; that is not
transport acceptance. Negative controls reject truncated/unsafe/duplicate archive
entries, configuration ambiguity and unexpected package additions. Even an
injected all-builtin config cannot pass the current package readiness gate.

```sh
python3 scripts/audit_usb_gadget_prerequisites.py --initramfs <diagnostic.cpio.gz>
python3 scripts/audit_usb_gadget_prerequisites.py --initramfs <diagnostic.cpio.gz> --require-ready
```

Receipts in evidence/usb-gadget-prerequisites pin the actual resolved symbol
snapshot to PR416's private-log hash and original config hash receipt; all source,
compiler/package and audit inputs are identified. Three capped official ACK reads
total19703 bytes: gadget Kconfig, gadget Makefile and function Makefile. No archive
download or device action was needed. Canonical34/isolated28 failing binding
contexts and disabled DT are unchanged.

Next actual kernel acceptance: MT8163-scoped role transition/init error handling,
with actual C RAM failure/rollback tests, other SoCs unchanged, and exact-head
USB provider/Image build. Keep packaging separate: an opt-in builtin ACM profile
and explicit diagnostic gadget userspace are still needed afterward. No role,
analog/clock timing, physical transport, loading, independent failed-load return,
retained log or beta runtime gate closes here.
