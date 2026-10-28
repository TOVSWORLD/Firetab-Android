# MT8163 wrapper contract and PMIC parent-name candidate — #27/#20

The opt-in `mt8163-pwrap` proposal matches the real MT8163 wrapper and its
PWRAP_CAP_RESET/no-BRIDGE descriptor: one named mapping/reset and a PMIC child.
Existing SPI/wrapper clock and interrupt constraints remain; all old compatible
policies are structurally preserved. The parent schema does not establish
first-child compatible support, PMIC transport or voltage. Captured MT6323 and
its separate matched MFD schema remain necessary parts of the full context.

Matching the existing RDMA candidate exposes two errors: its `mt6323` parent
name is not allowed by the original binding's `pmic` property, and the required
`pmic` is missing. The raw46-diagnostic result and two errors are retained in
`evidence/pwrap-binding/original-name-validation.json`.

The isolated `pwrap-pmic-node-name` DT experiment changes only the PMIC parent
node name, retaining its label and compatibles. Compared with the RDMA candidate,
all880 property values across186 nodes, including phandle values, are identical;
only the parent path and descendant paths relocate. Baseline source evidence and
other experiments remain unchanged. DTB26259bytes, SHA256
b837e6cb439d43778527c834e534abddb271170fd29cb6b13b174272214d1411.

With this candidate, the full cached profile has44 diagnostics (32 unmatched/
12 validation), one unmatched wrapper removed and no new diagnostic against the
prior45-diagnostic context after normalizing only the candidate filename and
reviewed PMIC path. The wrapper still exits1 and `passed` remains false.
Twenty-two processed-node controls use actual dtschema validation, checking
missing reset/PMIC, unsupported bridge resources, wrong names/counts, preserved
old bridge/reset/power-domain policies and the exposed parent naming error.

Reproduce with:

- `python3 scripts/build_douglas_dtb.py --experiment pwrap-pmic-node-name`
- `python3 scripts/compare_pmic_dtb.py --experiment pwrap-pmic-node-name`
- `work/dtb-tool/venv/bin/python evidence/pwrap-binding/check-controls.py`

The evidence report retains the full validation command, locked source/patch/
DTB/corpus hashes and tool version. No driver, regulator value, voltage, physical
device or firmware changed. Power/wakeup ordering, actual wrapper traffic and
experimental failure return remain unqualified.
