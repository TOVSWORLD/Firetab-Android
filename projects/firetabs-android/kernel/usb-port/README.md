# MT8163 USB2 bank/calibration definition — #27

This directory retains the source-derived definition and the actual isolated
kernel patch. The definition/model predates implementation and keeps its historical
readiness flags; see the actual implementation/build section below for current
source status. Neither source nor host models qualify physical USB transport.
The sources are pinned by USB-PREREQUISITES.md plus the capped official RMW-helper
header receipt in evidence/usb-variant-definition.

## Applied register effects

Legacy recovery ultimately writes byte0x60 at common+0x15, then clears its
oscillator bit. That affects register0x14 bits15..8, not just SRCTRL14..12.
ACK init clears bit11. A hypothetical completed calibration producing field6
preserves bits10..8; the existing explicit eye-src6 path also skips calibration
and preserves the initial oscillator bit15. Neither is an exact replacement.

The validator enumerates all65536 isolated low16-bit input states in the
readl/writeb little-endian register view, with other
bits assumed stable. Field6 after completed calibration matches the legacy byte
write for8192 inputs, differing only on mask0x700. The eye-src6 shortcut matches
for4096, with difference mask0x8700. These counts are exhaustive expression checks,
not observed hardware states or probabilities. At input0x8700 the respective
results are legacy0x6000, field-after-measurement0x6700 and shortcut0xe700.
Whole PHY ordering, concurrent MMIO changes and hardware register semantics are
outside this model. The field-only/skip-measurement shortcut is not selected.

## Selected definition and resource ownership

The initial MT8163-specific implementation should retain measurement, frequency
control cleanup and the vendor full-byte write. Legacy uses a3*HZ valid-bit
polling deadline; the definition records3000000us as its source-derived intent,
not exact jiffies scheduling equivalence. ACK's generic10/200us polling remains
unchanged for existing SoCs. Legacy calculates an unused value and can divide by
zero if a valid result is zero; that dead calculation must not be copied. Record
zero/timeout and finish cleanup/fixed-byte policy, rather than skipping measurement.
Reject an unqualified explicit EYE override in the initial MT8163 path.

Use a distinct second parent resource for the frequency bank at0x11210f00+0x100,
with monitor/value/control accesses bounded within it. Keep SIF0x11210000+0x800
and child common windows0x11210800+0x100 and0x11210900+0x100 disjoint. The original
vendor SIF envelope contains these addresses. A missing separate bank must fail;
never silently use generic V1 offset0x100. Blindly growing the first parent range
to4KiB overlaps the separately claimed child resources and is rejected.

`variant-definition.json` expresses this MT8163-only USB2 policy and disallows
changes to existing variants or candidate activation. The future kernel patch
must use an exact MT8163 match, a dedicated resource mapping and an explicit
measure-then-fixed-byte path. It must not claim that a generic fallback, copied
reference value or existing EYE property implements the vendor sequence.

```sh
python3 scripts/validate_usb_variant_definition.py
python3 -m unittest discover -s tests -p test_usb_variant_definition.py -v
```

## Implementation criteria

The locked patch implements the isolated bank/calibration definition against
pinned ACK and is checked for missing-bank/unsupported-type/error paths and
unchanged generic policy. Actual object/config/Image results are still required
before build, binding or transport claims. Keep the candidate disabled. Remaining
analog threshold/tuning, role-dependent init and clock/power sequences still need
qualification; this definition does not assert whole legacy/ACK equivalence.
No device/firmware/helper/reset or calibration-bypass execution is authorized here.

## Actual source implementation and explicit build scope

The hash-locked mt8163-usb2.patch implements the definition against pinned ACK.
It adds an exact MT8163 descriptor, mandatory named u2-frequency mapping and
minimum extent checks, a mutex around shared measurement, source-derived byte
sequencing, bounded polling and cleanup/fixed-byte application for timeout/zero
results. It rejects an EYE override before provider registration. Only the
reviewed USB2 port0 is admitted by xlate; port1/other PHY types remain unsupported
for this new descriptor pending their own qualification. Existing descriptor data
and generic calibration body remain unchanged. This is not whole analog/role/
clock sequence equivalence and does not enable the current incomplete DT.

Host tests apply the actual locked patch, compare unchanged generic functions,
and compile the actual new C functions with RAM-only I/O/resource mocks. They
exercise missing/undersized/busy mappings and successful/zero/timed-out readings,
cleanup, locking and the full-byte write; no real hardware access is performed.

The usb-providers Linux scope explicitly enables USB/GADGET, the MUSB MediaTek
wrapper/dual-role core and Inventra DMA (not PIO-only), NOP transceiver and T-PHY. It requires the resolved symbols,
compiles both actual USB objects, prints their hashes and builds Image/vmlinux.
The existing USB-off diagnostic fragment is unchanged. PR source-path selection
chooses one USB-enabled build for this patch, otherwise retains diagnostic/QEMU;
manual scope requests are explicit. USB Image compilation is not USB transport
execution, and generic QEMU is not claimed for this new profile. Only successful
exact-head Linux CI establishes build evidence; source/host results do not.

```sh
python3 scripts/apply_usb_port.py /path/to/disposable/pinned/ack
bash scripts/build_ack_baseline.sh usb-providers # Linux host / existing resource gates
python3 -m unittest discover -s tests -p test_usb_port.py -v
```

Next acceptance after the actual build: isolated disabled-DT resource experiment
with the second disjoint frequency bank and matched MT8163-specific binding
controls. Keep current baseline/candidate unchanged until separately verified.
Actual IRQ/PHY timing, analog tuning, device role, USB gadget logs, loading and
independent recovery remain unqualified. The earlier definition/report captures
the pre-implementation model and is retained as historical evidence.
