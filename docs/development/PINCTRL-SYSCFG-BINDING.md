# MT8163 pinctrl syscfg provider/resource contract — #27

The pinctrl consumer's GPIO configuration registers come through
mediatek,pctl-regmap, not its separate EINT reg resource. The cached common probe
supplies no direct regmap; init must resolve the syscon phandle. Its optional
second map is unused by the selected MT8163 type1 interval [155,155).

## Pinned candidate/source agreement

The unchanged candidate DTB SHA256 is
b837e6cb439d43778527c834e534abddb271170fd29cb6b13b174272214d1411.
Its pinctrl@1000b000 consumer references phandle14, resolving to
/soc/syscon@10005000 with compatible mediatek,mt8163-pctl-a-syscfg/syscon and
reg0x10005000+0x1000. Phandle14 is a local declaration, not a hardware identity.
The fresh-DTB guard resolves it rather than treating that number as permanent.

The source layout uses locked donor commit20951722df6ae1f6fecbfcea0a7d585118a06f3f
and pinned ACK common source. It checks155 pins,119 drive entries,46 pull entries
and92 IES/SMT ranges, plus selected generic GPIO/mux formulas. Maximum reviewed
base offset is0xf50; conservatively including set/clear aliases and a32-bit access
requires0xf5c bytes. The declared0x1000 extent covers that model. This is not a
whole-driver dataflow, physical MMIO or pin/interrupt qualification.

## Implemented checks

The opt-in locked mt8163-pctl-syscfg proposal adds only this compatible to both
syscon selection and exact provider tuple enums. Existing required-reg and other
SoC policies are preserved. Twelve actual decoded-node Draft201909/typeSize
controls cover tuple/order/region failures, unknown properties and existing SoCs.
Disabled status remains schema-valid; the stricter reviewed-candidate guard rejects
it. That distinction keeps generic schema validity separate from our test model.

validate_pinctrl_syscfg.py checks actual consumer/provider linkage and resource
extent from a fresh DTB. It rejects missing/wrong/extra regmaps, disabled provider,
wrong base, undercoverage or unreviewed region growth. CI runs this after candidate
DTB compilation. Four host controls also verify patch isolation and drift rejection.

The full matched context changes41→40 diagnostics (28unmatched/12validation),
only the provider's unmatched diagnostic removed and no additions. The wrapper
still exits1/passedfalse. No DTB/driver or device state was changed.

```sh
work/dtb-tool/venv/bin/python evidence/pinctrl-syscfg-binding/check-controls.py
python3 scripts/validate_pinctrl_syscfg.py --dtb work/dtb-compile/pwrap-pmic-node-name/douglas.dtb
python3 -m unittest discover -s tests -p test_pinctrl_syscfg.py -v
```

Exact schema/source inputs, decoded node/pair, output hashes and full-context
command/report are in evidence/pinctrl-syscfg-binding. Local executable full argv
is retained in out/pinctrl-syscfg-command.json; the cached archive is sufficient.

Next #27 source acceptance: inspect the actual IOMMU/SMI driver/probe and display
DMA dependencies against candidate DT resources. Add matched bindings only after
source support is established; preserve all40 remaining diagnostics. GPIO87 delta,
actual EINT delivery, boot/recovery and general hardware gates remain open.
