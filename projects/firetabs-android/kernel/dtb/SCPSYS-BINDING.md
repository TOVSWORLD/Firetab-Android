# Captured MT8163 scpsys/power-controller contracts — #27/#20

Two opt-in proposals match the exact syscon/simple-mfd parent and MT8163 power
controller child. Pinned ACK OF population recognizes simple-mfd and recursively
creates the child platform device with its parent; the actual common power
probe reads that parent syscon regmap. This is a reviewed source path, not an
observed device probe. The22,288-byte OF source and SHA256 receipt are retained
in `evidence/scpsys-binding/`.

The MT8163 child proposal requires controller cell declarations, bounds domain
IDs0–7 and domain cells0/1, and requires legacy INFRACFG references for protected
IDs0/4/6. It rejects `access-controllers`: the current MT8163 descriptor has no
block list/count, so the core's modern mode would reject a nonempty declaration.
It also rejects `domain-supply`, which the current descriptor lacks the capability
to request. These declarations cannot stand in for implemented support. All old
SoC constraints remain structurally unchanged.

Twenty-four actual dtschema controls use the decoded locked candidate, checking
parent/child pairing, bounds including nested domains, missing protection maps,
unsupported mode/supplies and preserved old SoC policies. The separate captured
candidate guard requires eight unique IDs, MFG under MFG_ASYNC, the actual
INFRACFG phandle target and consistent clock/name counts. It rejects quietly
disabled domains. That guard describes this reviewed candidate, not every valid
MT8163 configuration. It runs against the freshly compiled DTB in CI using
fdtget; it does not use an attached tablet or infer live register state.

The full cached profile has42 diagnostics (30 unmatched/12 validation), two
matched nodes removed without new diagnostics. Wrapper exit1 and `passed:false`
remain. Source/DTB/schema/tool hashes, full command, decoded fixture and controls
are in `evidence/scpsys-binding/`.

Reproduce:

- `work/dtb-tool/venv/bin/python evidence/scpsys-binding/check-controls.py`
- `python3 scripts/validate_power_provider_tree.py --dtb work/dtb-compile/pwrap-pmic-node-name/douglas.dtb`

Six semantic drift tests reject wrong INFRACFG, flattened MFG, duplicate IDs,
disabled domains and clock/name count changes. Legacy/candidate active-wakeup,
MFG clock placement and partial-failure cleanup differences remain unqualified.
These checks establish neither voltage/timing nor safe experimental failure
return. No driver, DT property, firmware or device behavior changes here.
