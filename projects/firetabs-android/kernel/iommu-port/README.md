# MT8163 IOMMU/SMI source integration — #27

Apply minimal MT8163 data/OF additions to pinned ACKd9318bdb4c34e8b2d997b4f67ced56b120b22b87.
Donor20951722df6ae1f6fecbfcea0a7d585118a06f3f supplies the IOMMU descriptor,
SMI GEN2 init data and MT8173-style larb port configuration. The80-line patch
excludes unrelated APU/newer-SoC changes and shared probe/cleanup/refcount policy
changes. Hashes for original/donor/patched files and patch are in inputs.json.

The two official ACK source inputs were acquired with capped small Gitiles reads,
retained under evidence/iommu-smi-port/ack with source URLs/hashes. No local full
kernel download was performed. The existing provider compile workflow applies
this patch in providers/diagnostic modes, checks resolved MTK_IOMMU/MTK_SMI=y,
compiles both objects and the generic Image, and prints object/config/image hashes.
Its generic QEMU smoke does not probe MT8163 hardware. Only successful exact-head
CI establishes this build scope; neither source inspection nor host tests does.

## Probe and candidate dependencies

The MT8163 IOMMU descriptor uses one bank/IRQ, linear larb0..3 mapping and a single
IOVA domain. It does not request bclk or the4GB-mode infracfg lookup. Probe
allocates protected memory and maps registers; multimedia component binding needs
all linked larb drivers and their common SMI supplier. SMI requires apb/smi clocks;
selected GEN2 common needs no gals/async clocks. Runtime resume programs init,
bus-selection and MMU port registers, so a device probe is not passive observation.

validate_iommu_dependencies.py resolves the fresh candidate graph: four larbs,
one SMI-common, five clock-role pairs and power-domain associations. It checks
actual phandles and header-derived clock IDs, including intentional duplicate
clock roles. Larb1's reviewed resource is64KiB; the other reviewed windows are4KiB.
Four negative-control groups reject topology, domain, clock and bank-resource drift.
This validates declarations, not DMA correctness, rates, page-table placement or
runtime recovery. The candidate DTB and full40-diagnostic baseline are unchanged.
No matched binding is added before source/build integration evidence.

```sh
python3 scripts/apply_iommu_port.py /path/to/disposable/pinned/ack
python3 scripts/validate_iommu_dependencies.py --dtb work/dtb-compile/pwrap-pmic-node-name/douglas.dtb
python3 -m unittest discover -s tests -p 'test_iommu*.py' -v
```

No firmware/helper or tablet execution occurs. Next acceptance after build checks:
matched IOMMU/SMI binding contracts and actual decoded-node controls, preserving
remaining diagnostics. Board DMA/display, power transitions, independent failed-
boot return and retained failure logs remain open.
