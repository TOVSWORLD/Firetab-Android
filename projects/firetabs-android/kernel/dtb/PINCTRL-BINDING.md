# MT8163 GPIO/EINT binding contract — #27/#19

The opt-in `mt8163-pinctrl` profile adds the exact MT8163 standalone compatible
and requires its actual common-probe prerequisites: register mapping, syscon
regmap phandle, EINT controller declaration, parent interrupts and interrupt-cell
declaration. MT8163 has169 EINT lines, so common probe must initialize EINT.
Existing compatible policies and all pin-group constraints remain unchanged.

The full cached profile produces45 diagnostics (33 unmatched/12 validation),
removing the previously unmatched controller without new diagnostics. The
wrapper remains exit1 and `passed` remains false. Nineteen positive/negative
controls use dtschema's actual Draft201909/typeSize validator with four locally
registered processed dependency schemas. They check missing prerequisites,
wrong cells, invalid tuple/register/IRQ/phandle counts and preserved existing
MT8173 policy. Removing only the new enum and condition restores the original
YAML structure. No constraint is removed to obtain a passing result.

Run `work/dtb-tool/venv/bin/python evidence/pinctrl-binding/check-controls.py`.
The evidence directory retains the full command/report, corpus/DTB/tool hashes,
processed schema dependencies, diagnostic delta and driver requirement sources.

This does not prove GPIO87's input-enable delta, electrical routing, parent-line
ownership or interrupt delivery. Both legacy and ACK select only parent index0;
the preserved1–3 IRQ schema range does not assert all listed parents are used.
No driver/DT/device behavior changes or firmware operations are included.
