# USB source prerequisites — #27

The selected ACK drivers match the candidate's fallback compatibles:
`mediatek,mtk-musb` and `mediatek,generic-tphy-v1`. A match is insufficient to
qualify the MT8163 variant. Two bounded official source reads total60518bytes;
exact revision/URLs/hashes and cached legacy source receipts are retained under
`evidence/usb-prerequisites`.

There is a concrete source bank mismatch. Under CONFIG_OF, legacy MUSB maps its
second resource (declared SIF0x11210000) into the PHY io_priv pointer. The PHY
access macro adds0x800; calibration accesses0xf00-0x800+0x0c. The resulting
source-derived frequency-value address is0x11210f0c. Selected ACK generic V1 uses
SIF+0x100+0x0c, yielding0x1121010c for the candidate. The legacy formula uses
FRA48/PARA28, while generic V1 defaults to reference26/coefficient28. These are
source differences, not observed MMIO or proof of installed-driver equivalence.
The legacy computed slew value is not applied: its variable write is commented
out and active code writes byte0x60 to0x15 (SRCTRL6). ACK normally writes its
computed field. The formula reference difference must therefore not be mistaken
for the legacy applied slew setting. No guessed offset/reference or skipped
procedure is used to hide the discrepancy.

Actual controller probe requires main/mcu/univpll clocks and PHY index0, chooses
its mode with Kconfig overrides, registers a generic USB2 transceiver and creates
the musb-hdrc child. It enables clocks and runtime PM; PHY init/power operations
write registers, so a probe is not passive. T-PHY probe obtains version match
data, maps the V1 shared SIF bank, creates child PHYs and obtains optional ref /
da_ref clocks. Xlate requires one argument and selects USB2 for candidate value3.
No reset-controller API dependency is invented from a sibling SoC; these sources
use PHY operations and MMIO sequencing. This does not prove every reset/power
prerequisite of the actual hardware is satisfied.

The candidate controller and PHY parent are both disabled. The diagnostic fragment
also requests USB and USB_GADGET disabled; this is a source fragment observation,
not a new resolved-config build result. Prior generic QEMU evidence does not
establish USB gadget transport. There is no USB build-integration qualification
in this scope, and no USB/PHY binding proposal is added. Full34 diagnostics and
the candidate DTB remain unchanged.

The fresh-DTB audit verifies actual fallback tuples, disabled state, declared
controller/PHY resources and IRQ, port0 USB2 phandle/argument, clock supplier
phandles and header-derived clock IDs. It reports metadata success separately
from source-variant/build/device readiness, all of which remain false. It rejects
unreviewed activation and resource/clock/link drift. This is a baseline review
guard, not a permanent prohibition on a future reviewed USB integration change.

```sh
python3 scripts/audit_usb_prerequisites.py --dtb work/dtb-compile/pwrap-pmic-node-name/douglas.dtb
python3 -m unittest discover -s tests -p test_usb_prerequisites.py -v
```

Next bounded source acceptance: reconcile USB2 frequency/common register banks
and calibration arithmetic/timeouts against the pinned legacy implementation;
choose a justified MT8163-specific variant and required resource extent before
source/build integration. Keep the candidate disabled, do not claim support from
generic matching, and do not bypass calibration to obtain logs. Subsequent object /
Image build, source-matched bindings and device transport tests are distinct gates.
Loading, independent failure return, retained logs and physical USB remain open.
