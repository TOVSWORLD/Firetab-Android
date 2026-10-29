# Isolated SYM827 source port (#27)

This opt-in patch adds `silergy,sym827` to the pinned ACK FAN53555 driver
using a separate appended vendor value. Existing SYR827/828 continue to accept
only their original IDs 8/9 and 712500µV minimum. The pinned modern MT8163 donor
explicitly supports SYM ID 1/revision 12, minimum 600000µV, step 12500µV,
64 selectors (maximum 1387500µV). This is a source contract, not a chip observation.

The exact legacy driver checks manufacturer bits 7:5 equal 4. The new path
requires that manufacturer plus donor ID/revision before setup/registration.
It also requires exactly one explicit `fcs,suspend-voltage-selector` cell, 0 or 1,
and rejects legacy external VSEL/enable GPIO properties. Selector 1 declares
sleep bank VSEL1 and active bank VSEL0; selector 0 reverses them. Neither choice
proves which bank the physical GPIO34/DVS handoff selects. The legacy Douglas
DTS uses GPIO34 and the different `silergy,sym827-regulator` ABI; that spelling
is deliberately not added as an alias. Legacy GPIO/SPM/DVS and writable debug
interfaces are not imported. Existing generic register operations remain intact.

`inputs.json` locks original ACK, donor and legacy sources, patch and output.
`python3 scripts/apply_sym827_port.py SOURCE` checks all inputs, shadow-applies,
verifies the complete output, then replaces the one target. Wrong revision,
source, patch/output or repeated application fail before replacement.

Run `python3 -m unittest discover -s tests -p test_sym827_port.py` for actual C
RAM-only controls under ASan/UBSan: all 65536 raw ID/revision pairs; malformed,
missing, conflicting bank/GPIO properties; all 256 decoded ID/revision pairs;
64 voltage selectors and both banks. All 6144 prior-vendor/ID/revision/bank
combinations compare return values and complete state against original setup;
all other pre-existing integer C functions except the guarded probe are byte
identical. Probe source checks confirm read failures precede validation and
validation precedes setup/registration; this is not a full mocked kernel probe.

The separate `sym827-provider` CI mode runs the unchanged USB-off diagnostic
baseline, then patches the regulator, compiles actual `fan53555.o` with W=1,
and rebuilds Image/vmlinux. Only the final
`MT8163_SYM827_PROVIDER_IMAGE_COMPLETE_RUNTIME_UNQUALIFIED` marker and subsequent
normalized receipt qualify changed-source compilation. Earlier baseline Image
hashes precede this patch. Explicit object hashes are pre-Image probes, not final
linked-object assertions. No QEMU or device/regulator action runs in this scope.
Mixed USB/SYM source scopes are rejected instead of silently omitting a build.

Current DTBs, schema contracts and failed full contexts (canonical 33 diagnostics,
isolated USB 27) are unchanged. No matched SYM binding is claimed before the new
source Image build passes. Actual identity, active bank, GPIO34/DVS ownership,
voltage/ramp behavior and safe CPU supply handoff remain unqualified; no loading
or voltage operation is admitted by this source work.
