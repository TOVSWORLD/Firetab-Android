# Four direct MT8163 gate-provider binding contracts (#27)

The IMG/MFG/VDEC/VENC clock drivers each have an exact MT8163 OF match and use
the common simple probe, which requires a register mapping. Captured DT nodes
supply the exact compatible+syscon tuples, one register range and one clock cell.
This is independent of the unresolved platform-child MMSYS integration in #18.

The [opt-in locked profile](../../projects/firetabs-android/kernel/dtb/bindings/mt8163-gate-clocks.json)
adds only those four exact tuples to the common syscon-clock schema and requires
reg for those new providers. It preserves the old MT8183-specific power-domain
policy in its own conditional and does not broaden existing constraints. It
changes no gate bits, clock rates, driver code or media/GPU behavior.

[Actual full-context report](../../evidence/gate-clock-bindings/report.json) and
[delta](../../evidence/gate-clock-bindings/delta.json) show all four target nodes
matched with no added diagnostics.47 diagnostics remain (35 unmatched/12 validation)
and wrapper exit1 remains. This is not complete validation or hardware support.

[Thirty-one processed-node controls](../../evidence/gate-clock-bindings/controls.json)
exercise each exact tuple, missing/multiple regs, wrong clock cells, invented
fallbacks and existing power-domain rules. Removing the four added enum values
and the new reg-required conditional restores semantic YAML equality with the
original. [Source](../../evidence/gate-clock-bindings/sources.json) and
[control provenance](../../evidence/gate-clock-bindings/controls-provenance.json)
retain exact driver/common-probe hashes, inputs and commands. No device/new corpus
operation occurred. CCF registration, actual parent creation, reset/clock behavior
and board boot remain separate acceptance gates.
