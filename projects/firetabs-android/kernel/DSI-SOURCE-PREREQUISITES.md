# MT8163 DSI source prerequisites (#27)

The pinned ACK DSI OF table lacks MT8163. The pinned donor has an explicit variant
with command queue0x200, VM command0x130, bypass_rack and no_vm_done_irq flags.
This is source provenance for a distinct variant, not an MT8173 alias or physical
IRQ proof. The legacy queue pointer also uses0x200, but its uncommented code enables
VM_DONE. Its apparent bypass helper is inside a C comment. Do not cite that helper
as an active legacy write or infer interrupt absence from the donor flag.

Run `python3 scripts/audit_dsi_source.py --check`. Actual selected ACK/donor C is
compiled with ASan/UBSan and bounded RAM/framework callbacks. Protocol enums/flags
come from the pinned headers. No source driver, command, panel or device code runs
against hardware. Kernel frameworks, clocks, PHY, bridge/component registration,
reset, MMIO and formats are mocks; no physical failure/leak/rollback is observed.

The compiled witnesses establish:

- Invalid pixel-format failure retains refcount1. A second poweron returns0 via
  the refcount shortcut without powering/configuring. Sequential actual bridge
  pre-enable/enable callbacks can then proceed using the nonzero reference.
- ACK and donor discard a failed `phy_power_on` return and continue clock/
  controller configuration. Rate/engine/digital error branches do unwind their
  existing reference/clock paths; a PHY-off error on cleanup is discarded.
- Component bind initializes the encoder before optional reset. Failed reset
  returns an error with no local encoder cleanup. The separate unbind callback
  can clean it, but this audit does not assume framework unbind runs after failure.
- Host attach commits lane/format/mode fields before bridge lookup/component
  success. The selected callback accepts lane0 with mocks; caller/framework
  validation remains separate. Defer returns immediately; other first-port errors
  try the legacy second endpoint. Component-add error removes the added bridge
  but leaves the selected fields. Detach calls component-del then bridge-remove.
- Probe has nine tested failure stages. Host registration precedes IRQ request;
  IRQ-request failure unregisters the host. Successful probe does not add the
  component. Bridge/component registration belongs to host attach, reset/encoder
  initialization belongs to component bind, and panel lookup is a dependency.
- Legacy declares128 queue words. Given command-header plus payload,508 bytes
  fit that declaration; the actual writer reaches the next word at509 bytes.
  At1020 bytes the byte-sized command count wraps to0. This is a conservative
  source-layout bound, not a measurement of physical queue depth or corruption.
- Twelve synthetic packet-builder cases show the donor globally adds HSTX when
  USE_LPM is absent. It also globally forces initial command mode. These changes
  must be isolated from existing SoCs. These are not panel command transactions.

The ACK DRM master also lacks MT8163 MMSYS match data and a matching DSI component
entry. Adding the controller does not admit a whole display pipeline. Its master
rejects an unknown MMSYS match; do not copy MT8173 path data to force acceptance.
The current build profile did not establish DRM_MEDIATEK enabled. The next actual
source build must resolve DRM/DRM_MEDIATEK/MIPI/PHY dependencies and compile real
DSI/master translation units before final Image; the flattened mediatek-drm.o
aggregate is not a standalone builtin object target.

`dsi-port/variant-definition.json` records bounded implementation intent, not an
implemented driver. Next is actual isolated MT8163 descriptor/quirk/lifecycle/
packet/error/ownership handling: preserve old behavior, reject unsupported inputs
before side effects, track successful references/cleanup, prevent later false
success after failure, handle bind reset/encoder order and host rollback, guard
queue length and integer widths, preserve primary errors and expose unresolved
cleanup faults. Cover bridge atomic, DDP and host paths with actual C tests. Add
only source-backed component identification; MMSYS/panel/pipeline admission stays
separate. Require atomic all-target patch preflight and an explicit builtin
object/config/Image build before any matching binding claim. No more model-only
scope is needed for the settled layout/error findings.

The controller/PHY stay disabled. DTBs and full failed binding contexts31/25,
thermal source blockers and physical loading/return/log/beta gates are unchanged.
No display/PHY/IRQ/reset/firmware/helper/device/electrical operation is authorized
by this source audit, and no security mechanism is relaxed for diagnostics.
