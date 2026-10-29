# Source-matched MT8163 eye override contract — #27

PR416 merged6ef265b37da10f329f3a4d3b961791ce2b55ac2a after final-head PR checks
and USB-enabled run40813924079 atdad8de0ee4992b13c0bdd230315b05f10c79caba.
Actual MUSB/T-PHY objects, resolved USB/GADGET/dual-role/Inventra-DMA config and
Image pass. The object hashes are from the explicit W=1 pre-Image probe; they are
not asserted final linked-object hashes. Normalized source/run/artifact receipt:
evidence/usb-analog-policy/build-result.json. This is generic ARM64 compilation,
without QEMU or physical USB execution.

The opt-in MT8163 T-PHY contract now permits absent eye-vrt/eye-term properties
or explicit7, matching the implemented cold/recovery analog operation. It rejects
conflicting values and malformed/multi-cell metadata; eye-src stays forbidden.
The kernel separately requires exactly one u32 cell before reading a present
property, rather than accepting the first cell of a longer array. Existing SoC
contracts and all other MT8163 resource policies remain unchanged.

Thirty actual decoded-node controls cover absent/equal/both7 values, conflicts,
malformed lists/strings, a two-cell array beginning7, slew bypass and an older
SoC's non7 tuning. Removing just the two new MT8163 conditional properties
reproduces the previous proposal structurally. The earlier PR414 receipts and
25-control results remain historical and are not rewritten as current acceptance.
The portable schema closure was extracted after full matched5186-YAML processing;
single-file processing was not used for the accepted controls.

The full isolated context still reports28 diagnostics:19 unmatched and9 validation.
All diagnostic identities are unchanged from PR414. The pre-existing Gunyah
schema-processing warning is retained; the wrapper exits1 and passed:false.
The canonical34-diagnostic baseline and DTB are unchanged, as is the disabled
isolated resource DTB. This scope adds no kernel/DT change or new kernel build.
Static matching of disabled USB1 still does not qualify unsupported PHY port1.

Reproduce the actual controls with:

```sh
work/dtb-tool/venv/bin/python evidence/usb-analog-binding/check-controls.py
```

Exact full-wrapper argv, diagnostic reports, hash receipts and decoded-node/schema
inputs are in evidence/usb-analog-binding. Next source acceptance is the finite
USB0 gadget/device-role handoff: pin the actual controller role-switch/init path,
resolved configuration and initramfs/gadget prerequisites before choosing any
disabled device-mode experiment. No physical mode changes or activation are
authorized by this receipt. Analog timing, clocks, USB transport, loading,
independent failed-load return, retained logs and beta runtime gates remain open.
