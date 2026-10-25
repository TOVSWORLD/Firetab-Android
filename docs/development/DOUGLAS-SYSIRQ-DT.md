# Sysirq node-name candidate — issue #27

The pinned ACK sysirq binding references the generic interrupt-controller
binding, whose node-name requirement rejects the donor's
`intpol-controller@10200620`. This candidate renames it to
`interrupt-controller@10200620`, keeping the `sysirq` label. The source binding
is retained with its exact revision and hash in
[evidence/sysirq-dt](../../evidence/sysirq-dt).

The candidate includes the three reviewed PMIC child-name fixes. Its manifest is
projects/firetabs-android/kernel/dtb/sysirq-node-name.json. Reproduce with the
existing pinned DTC tooling and schema environment:

```sh
python3 scripts/build_douglas_dtb.py
python3 scripts/build_douglas_dtb.py --experiment sysirq-node-name
python3 scripts/compare_pmic_dtb.py --experiment sysirq-node-name
python3 scripts/validate_douglas_bindings.py --experiment sysirq-node-name
```

The comparison walks the actual binary trees and permits only the three PMIC
path substitutions and this exact sysirq path substitution. All 880 property
values across 186 nodes remain identical, including interrupt cells, parents,
phandles, register addresses and board memory/PSCI declarations. No compatible
string is removed to make validation pass.

DTC produces no diagnostics. Result: 26,279 bytes, SHA256
78fd34cbe0c129da23dd2e296be0db9180e7d8b464e719b59304f09d01456bea.
Full-context schema diagnostics change from 34 errors/61 unmatched to
33 errors/61 unmatched. After normalizing only the reviewed node-name change,
one naming diagnostic disappears and no diagnostic signatures are added.
MT8163 compatible coverage remains missing. The upstream Gunyah YAML parse
failure also remains, so the validation command deliberately exits 1 and records
`passed=false`. CI repeats the DTC build and binary property comparison; it does
not claim a full schema pass.

This is structural validation only. No kernel rebuild is necessary to establish
that this DT candidate compiles, but a qualified kernel-plus-DT diagnostic image
still requires the stock boot/memory contract and recovery/log procedure in #21.
No boot image is packed and no tablet access or hardware validation is performed.

## Strict MT8163 sysirq compatible coverage (#66)

The unchanged donor declares mediatek,mt8163-sysirq followed by
mediatek,mt6577-sysirq. Both pinned legacy and ACK drivers register the MT6577
compatible; the proposal adds only MT8163 to the existing first-string enum.
Retained driver snapshots/hashes are in evidence/sysirq-binding. This is support
for the already declared fallback contract, not verified IRQ inverter behavior
on hardware. Node naming repair from#40 remains separate.

Reproduce full-context validation with the prior UART, Gunyah lexical and PMIC
selector flags plus `--extra-binding mt8163-sysirq`. Default ACK remains unchanged;
proposal input/output/patch hashes and ACK revision are locked. Meta-validation
is clean. The actual processed compatible schema is retained: local controls
accept the exact pair, reject missing/wrong/extra fallback strings and preserve
previous MT8173 compatibility. All other original schema constraints are unchanged.
Run controls with `work/dtb-tool/venv/bin/python evidence/sysirq-binding/check-controls.py`.
Use dtschema-processed tuple constraints, not a draft2020 validator on raw YAML
list-items syntax; the latter is a different JSON Schema dialect.

Full-context delta removes exactly one incompatible-pair error plus one unmatched
entry and adds none:27 validation errors/56 unmatched remain (83 total), overall
passed=false/exit1. Logs/result, exact delta, processed-schema provenance and
controls are retained.84 unit tests pass including isolated locked patch apply
and refusal of changed source. No DT/driver/hardware behavior changed or device
queried. Next#27 board-relevant task: timer compatible coverage or display-RDMA
node naming versus generic DMA-provider selection, with strict negative controls.
