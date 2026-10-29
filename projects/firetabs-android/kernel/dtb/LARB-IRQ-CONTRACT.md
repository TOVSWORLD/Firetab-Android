# MT8163 larb IRQ resource contract — #27

Preserve the four vendor-declared larb interrupts as optional hardware resources.
Lack of a driver handler is insufficient reason to delete a hardware declaration.
The exact legacy Git revision e0a3a2b2378ae4c7494ffdfea34d2a9e04a5fb74 declares
one low-level SPI on each matching address: larb0/0x14016000/205,
larb1/0x16010000/213, larb2/0x15001000/217, larb3/0x17001000/207.
The selected donor retains them. This is source provenance, not measured wiring.

The legacy larb probe matches mt8163-smi-larb, maps its memory resource, obtains
apb/smi clocks and links common SMI. It does not request an IRQ. The legacy M4U
probe separately maps its own node's IRQ and requests MTK_M4U_isr; that node
declares SPI147. Neither the selected ACK nor donor SMI driver requests larb IRQs.
An optional binding property therefore describes the existing resource without
promising handler support or equating it with the M4U fault interrupt.

The opt-in MT8163 binding allows at most one interrupt. Its new conditional else
continues to prohibit interrupts on other SoCs, preserving their prior policy.
All other prior MT8163 clock/supplier/ID constraints remain unchanged. Forty
actual decoded-node controls check the four unchanged nodes, optional absence,
extra IRQ rejection, unrelated-property rejection and old-SoC prohibition.
The fresh-DTB dependency guard additionally checks any declared IRQ against the
exact vendor SPI/type/polarity; missing optional IRQ does not require a handler.
Schema cardinality and board-specific metadata checks are distinct.

Full context38→34 diagnostics removes exactly the four larb property errors,
with no other changes:22 unmatched and12 validation errors remain. The wrapper
still exits1 with passed:false. No DTB/driver/device change or IRQ/runtime proof.
The preceding60-control receipt remains historical evidence of the pre-correction
contract and its expected rejections, rather than being rewritten.

Evidence under evidence/larb-irq-contract retains exact source paths/hashes and
line-range excerpts, decoded nodes, processed schema closure, controls, full
output and diagnostic delta. Reproduce:

```sh
work/dtb-tool/venv/bin/python evidence/larb-irq-contract/check-controls.py
python3 scripts/validate_iommu_dependencies.py --dtb work/dtb-compile/pwrap-pmic-node-name/douglas.dtb
```

Next source acceptance is the remaining USB MUSB/T-PHY driver match and probe
prerequisites under #27, before any matching binding claim. This is relevant to
future device diagnostic transport; current loading, independent failed-boot
return, retained logs and actual USB runtime remain unqualified.
