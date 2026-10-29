# MT8163-only analog callback policy — #27

The actual patch now selects the vendor RX and eye operations under the exact
MT8163 descriptor. Other descriptors, generic calibration, role-force handling,
clock ownership and disabled DT experiments remain unchanged.

The init callback uses the cold operation: OR0x06 into common+0x18, preserving
bit3 and bit0. It replaces the generic four-bit SQTH2 write for MT8163, rather
than trying to repair bit0 after the generic write has already cleared it.
The power_on callback uses recovery: clear bit3, then OR0x06, preserving bit0.
Both OR the VRT/TERM masks0x7700 into common+0x04, equivalent to the vendor byte
OR0x77 at common+0x05. Full-word RMW preserves unrelated fields; the source's
existing MMIO/concurrency assumptions remain applicable.

This is an explicit modern callback mapping, not a claim of whole legacy ordering.
Legacy mt_usb_enable calls usb_phy_recover when power is off; the retained excerpt
and exact full-source hash are in evidence/usb-analog-policy. Legacy cold
usb_phy_poweron and recovery have distinct RX masks. A normal modern init then
power_on therefore runs cold policy followed by recovery policy. Repeated
power_on invokes recovery again; re-init invokes cold policy again. This does
not establish installed-stock behavior, rail delays, signal integrity or suspend
equivalence. Role-force bits are deliberately unchanged pending their own policy.

Before provider registration, absent eye-vrt/eye-term properties are accepted;
explicit values7/7 are accepted because they match the selected operation. Any
present conflicting value, malformed scalar or multi-cell array returns EINVAL.
The guard requires exactly one u32 cell before reading the value; reading only
the first cell would silently accept an array beginning with7. Eye-src presence
still returns EINVAL, including explicit zero: the measured-slew policy must not
be bypassed. The earlier opt-in schema allows broader generic eye values; that
metadata acceptance does not override this narrower source guard. Current DT
declares no eye properties, so no DT/schema adjustment or activation is made in
this source scope. Matching negative binding controls are the next independent
metadata task after source build validation.

The actual new C functions compile with Wall/Wextra/Werror and execute with
RAM-only I/O/property mocks. Both phases enumerate all65536 low-word states,
checking expected RX/eye operations, upper-word preservation and every unrelated
byte. Tests also cover absent/equal/conflicting/malformed properties and slew
bypass rejection. Existing calibration/resource error tests remain active.
Branch-removal comparisons prove the remaining generic callback bodies and
descriptor definitions unchanged. This is host-source evidence only.

The new patch/inputs trigger the explicit usb-providers Linux scope. A successful
exact-head provider-object/config/Image run is required separately; the older
PR413 build cannot qualify this changed source. No QEMU or physical USB execution
is requested. Both DT controllers and the PHY stay disabled; canonical34 and
isolated28 failing binding contexts are unchanged. Loading, independent failed-load
return, retained logs and beta runtime gates remain open.
