# USB0 analog, role and clock comparison — #27

PR413 compiled the actual USB providers and PR414 registered an isolated disabled
frequency-bank experiment. Those scopes do not reproduce the whole legacy PHY
initialization. This finite comparison identifies the remaining differences using
the cached exact legacy and ACK sources, without device access or another download.

The legacy non-FPGA `usb_phy_recover()` clears bit3 and sets bits2:1 at common
offset0x18. ACK `u2_phy_instance_init()` sets the four-bit SQTH field to2. Across
all256 possible byte states the operations never agree; difference mask0x5.
Legacy preserves bit0, so replacing the generic field with the constant6 alone
would still lose a legacy-preserved bit. Legacy cold poweron also sets0x06 but
does not clear bit3, so cold/recover ordering must remain explicit.

At common+0x05, legacy ORs0x77, setting both three-bit VRT/TERM fields to7 while
preserving the other bits. Current candidate port0 declares no eye properties;
the generic property path therefore leaves these fields alone. Those operations
agree in only1024 of65536 isolated low-word states. Explicit eye-vrt7/eye-term7
field updates reproduce the legacy operation for all65536 states. This establishes
an expression-level option, not voltage accuracy, signal integrity, efuse ordering
or a decision to inject board properties. The accepted EYE slew bypass prohibition
remains separate; no eye-src property is introduced.

Legacy recovery clears bit4 then ORs0x2e into DTM1's low byte and0x3e into its
next byte. ACK power_on sets VBUSVALID/AVALID and clears SESSEND; set_mode then
controls IDDIG and FORCE_IDDIG according to host/device/OTG. For the device case,
the isolated low-word operations agree in2048 of65536 states, difference mask
0x3c08. For the candidate's declared OTG mode they never agree, mask0x3e0a.
Legacy's forced bits must not be copied unconditionally into generic OTG handling.
Role-switch/controller events and force-signal ownership need an explicit device
policy before any future gadget activation. Comparisons are possible register
states, not observed samples or probabilities; they exclude intervening callbacks,
concurrent accesses, upper-word behavior and whole-sequence equivalence.

The exact legacy probe has four CCF lookups/prepares: usbpll, usb, usbmcu, icusb.
Its first CCF enable path enables usbpll, usb, then usbmcu. There is no
clk_enable/disable(icusb_clk) in the pinned PHY file. The alternative CLKMGR branch
does gate INFRA_ICUSB; that is not evidence the CCF branch enables a fourth gate.
ACK MUSB owns main/mcu/univpll as a bulk; the separate PHY obtains optional ref
and da_ref and enables them during PHY init. Candidate main/mcu/univpll are
INFRA_USB7, INFRA_USB_MCU23 and APMIXED_UNIVPLL2. PHY ref is the separate
APMIXED_REF2USB_TX14 provider. Its source registers ref2usb_tx against clk26m.
Matching logical names does not prove identical sequencing or clock waveforms.

`evidence/usb0-transition-review/inputs.json` pins all input hashes and the exact
legacy Git object/full-file hash/retained lines1325..1383. The private extraction
command was `git -C sources/kernel-mt8163 show
e0a3a2b2378ae4c7494ffdfea34d2a9e04a5fb74:drivers/misc/mediatek/usb20/mt8163/usb20.c`;
only the technical probe excerpt is retained publicly. Existing tracked sources
retain full legacy PHY and ACK source. `port0-properties.json` records the actual
compiled isolated DT property inventory, rather than inferring absence from a
filtered graph. Reproduce the report with:

```sh
python3 scripts/audit_usb0_transitions.py
```

Next implementation acceptance: add an isolated MT8163 analog recovery policy
that preserves the vendor RX bits and applies the justified VRT/TERM operation;
leave existing SoCs unchanged, reject conflicting overrides, test actual C with
RAM-only mocks, and require exact-head USB provider/Image build. Keep role-force
handling separate until an explicit device-mode policy and callback ownership are
qualified. Keep both DT controllers and PHY disabled. No physical USB, loading,
independent failed-load return, retained logs or beta runtime gate passes here.
