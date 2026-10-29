# MT8163 IOMMU/SMI source-matched contracts — #27

PR407 integrates the actual MT8163 IOMMU/SMI descriptors into pinned ACK.
Exact-head run40794335163 compiled both provider objects, Image and passed the
generic QEMU userspace diagnostic. `evidence/iommu-smi-port/build-result.json`
records object/config/Image hashes. QEMU does not probe MT8163 hardware.

Three opt-in hash-locked binding proposals match that source: MT8163 M4U has one
bank and requires its larb list, without an unrelated bclk or4GB-mode infracfg
requirement; GEN2 SMI-common uses apb/smi clocks; larbs use their common supplier
and IDs0..3. Existing SoC policies are preserved structurally. The fresh-DTB
source dependency guard independently checks phandles, resources, clock IDs and
power domains. Schema selection alone cannot establish those relationships.

The60 actual decoded-node controls include expected failures. All four actual
candidate larbs declare interrupts, which the selected binding rejects and the
selected ACK/donor SMI driver does not consume. We preserve these errors. A
counterfactual node with that property removed passes; no actual DTB is edited.
The range control uses the decoded scalar larb ID, not an incorrectly typed
array. Old-SoC positives preserve the existing wider larb-ID policy.

Full context changes40→38 diagnostics: six unmatched nodes are selected, exposing
four validation errors for the larb IRQ declarations. Counts are22 unmatched and
16 validation errors. No other diagnostics change. Full wrapper still exits1
with `passed:false`; matching schemas is not a six-node acceptance pass.

Reproduce:

```sh
work/dtb-tool/venv/bin/python evidence/iommu-smi-binding/check-controls.py
python3 -m unittest discover -s tests -p test_iommu_smi_bindings.py -v
```

The exact full-wrapper argv is `evidence/iommu-smi-binding/command.json`.
Receipts, portable processed-schema closures, decoded nodes, full diagnostics
and comparison are retained beside it. No driver/DTB/device change is made by
this binding scope. DMA correctness, power transitions, display, failed-boot
return and retained logs remain unqualified.

Next acceptance: trace the origin and ownership of the four larb IRQ declarations
using cached donor/legacy IRQ definitions and consumers before a separately
justified DT correction. Do not accept an unused declaration just to reduce errors.
