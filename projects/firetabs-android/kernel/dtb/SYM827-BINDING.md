# SYM827 metadata contract (#27)

PR426 merged `4e358045fd6a2fe2fa882100314c0b0f81e06084` after five host checks
and exact-head Linux run40847835013 at `dec1a898f0f49782cff96daaa61b6f364d6930b4`.
Actual changed FAN53555 source, W1 object, builtin config and final 28645888-byte
Image passed. `evidence/sym827-port/build-result.json` distinguishes the final
post-patch Image from earlier baseline outputs and the pre-Image object probe.
This establishes source compilation, not physical regulator qualification.

The opt-in `mt8163-sym827` profile adds only the exact `silergy,sym827` compatible
and a conditional requiring explicit `fcs,suspend-voltage-selector`. Existing
0/1 scalar validation applies; `vsel-gpios` is forbidden for SYM because the
accepted new source rejects unowned external bank control. Unknown legacy
`vsel-gpio`/`en-gpio` remain rejected by existing unevaluated-property policy.
The different `silergy,sym827-regulator` ABI is not an alias. Existing SoC
policies are structurally identical after removing the new enum/conditional.

The actual decoded candidate node passes 22 positive/negative controls: both
selectors, missing/out-of-range/list/string/multicell selectors, external GPIO
properties, required compatible/address and old-device optional-selector behavior.
Reproduce with:

```
work/dtb-tool/venv/bin/python evidence/sym827-binding/check-controls.py --check
```

Exact full-corpus commands are in canonical-command.json and isolated-command.json.
Both use the pinned 5186-YAML corpus and the accepted other binding proposals.
Canonical diagnostics33→32 (20 unmatched/12 validation), isolated27→26 (17/9):
only this regulator's unmatched entry is removed, no diagnostic added. Both
wrappers exit1/`passed:false`; the Gunyah warning and disabled unmatched MT8163
AFE child remain. DTB hashes and every disabled state remain unchanged.

The current node declares suspend bank1, hence driver active register VSEL0.
This declaration does not prove physical GPIO34/DVS selection or a safe CPU
supply handoff. Manufacturer/ID/revision checks, selector range and voltage tables
are source contracts; schema matching cannot observe identity, voltages, ramp,
probe success or CPU reliability. No I2C/GPIO/regulator/voltage/device action runs.
Physical identity, active-bank ownership and voltage handoff remain runtime gates.
