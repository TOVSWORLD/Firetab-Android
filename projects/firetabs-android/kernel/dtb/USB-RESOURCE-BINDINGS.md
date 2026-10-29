# Isolated disabled USB resource/binding candidate — #27

PR413's actual USB-enabled object/config/Image build passed at179c920 in
run40805824866. Its normalized receipt is in evidence/usb-kernel-integration;
it is compilation evidence, without QEMU or physical USB execution.

The explicit usb-frequency-resource experiment adds only a separate frequency
reg tuple and reg-names sif/u2-frequency to the existing disabled PHY parent.
It compiles from26 locked source inputs/seven patches, without diagnostics, to
26307bytes SHA4480f085cfb03c2cb6a1b2c9b0c6a7619f3f4c0e395833b93d623deffe65c5c4.
The canonical pwrap-parent candidate remains unchanged atb837e6cb...; the default
experiment and prior full34-diagnostic context are not replaced.

The complete comparison checks186 node/property maps, all other values/phandles,
PHY child order (which determines driver indices) and reserve table. USB0, USB1
and PHY remain disabled. Negative controls reject memory/version injection,
clock/PHY/property drift, activation, swapped names, wrong resources, changed
child order and reservations. The frequency interval is disjoint from retained SIF and both child windows;
no contiguous-window expansion is used.

Two opt-in hash-locked schemas match the implemented source interface. MUSB keeps
the three source-required clock roles and fallback tuple. MT8163 T-PHY requires
two named resources and prohibits its ignored reference/coefficient overrides
and EYE bypass property. Generic V1 one-resource and V2 optional-reg policies
remain intact. Explicit top-level minItems1 prevents dtschema inferring a global
two-resource minimum. Twenty-five actual decoded-node controls and structural
old-SoC preservation pass.

Schema metadata acceptance includes the second disabled MUSB-compatible node at
0x11270000. It references port1, which the initial MT8163 driver deliberately
rejects. This is not a two-controller support claim. The complete delta guard
rejects enabling either instance. Actual port0 operation is also untested; source
compilation and matching metadata do not qualify analog/role/clock behavior.

The paired isolated full context reports28 diagnostics (19unmatched/9validation),
removing exactly six USB matching/compatible diagnostics with no additions. The
wrapper still exits1 with passed:false. This is a separate failing diagnostic
context, not a silent canonical-baseline promotion or full binding pass.

```sh
python3 scripts/build_douglas_dtb.py --experiment usb-frequency-resource
python3 scripts/compare_usb_resource_dtb.py
work/dtb-tool/venv/bin/python evidence/usb-resource-binding/check-controls.py
```

Exact full-wrapper argv, corpus reports, processed-schema closures, decoded nodes,
source-DTB comparison, build reference and hashes are retained in the evidence
folder. Next acceptance is finite USB0 analog/role/clock prerequisite comparison
against cached legacy/ACK sources before any activation or transport claim.
Physical loading, independent failure return, retained logs and beta admission
remain blocked on their actual runtime dependencies.
