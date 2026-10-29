# MT8163 USB2 bank/calibration definition — #27

This is a source-derived definition for the next kernel implementation, not an
implemented or runtime-qualified PHY variant. It reuses the sources
pinned by USB-PREREQUISITES.md plus one capped official phy-mtk-io.h read to
verify actual mask/field RMW semantics; the helper URL/hash receipt is retained. No DT, driver, USB mode or device is changed.

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

## Next implementation acceptance

Implement the isolated MT8163 bank/calibration definition against pinned ACK,
verify missing-bank/unsupported-PHY-type/error paths and preserve all other SoC
policies. Add bounded source/build integration with actual object/config/Image
results before binding or transport claims. Keep the candidate disabled. Remaining
analog threshold/tuning, role-dependent init and clock/power sequences still need
qualification; this definition does not assert whole legacy/ACK equivalence.
No device/firmware/helper/reset or calibration-bypass execution is authorized here.
