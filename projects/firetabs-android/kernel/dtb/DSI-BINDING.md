# Disabled MT8163 DSI metadata

Updates #27. PR433 merged6f670e0346a278857eff946e5ab6bc82d6b168f1 after five
exact-head host checks and Linux run40871693672/job123440089189 at2109781. Actual
DSI/DRM translation units, builtin config and final29374976B Image passed. Receipt
`evidence/dsi-kernel-integration/build-result.json` distinguishes final DSI output
from earlier staged Images/gzip and W=1 pre-Image object probes. No panel/runtime
or physical rollback qualification follows from compilation.

The opt-in `mt8163-dsi` proposal adds the exact standalone compatible and requires
one reset on this variant. The source requires reset before encoder creation.
Older compatible/fallback, optional-reset and graph policies remain structurally
unchanged. Generic metadata cardinalities are not board resource/IRQ/clock proof.

Forty frozen actual decoded-node controls replay the selected schema plus the
full type/select pipeline. The closed56-schema bundle retains52 relevant selectors
and is checked against the full5186-YAML validator on these instances. It is not
a full-corpus pass. The actual disabled node has no `port`/`ports` graph and is
**rejected** by the selected schema. A synthetic graph-shape control is only a
negative/positive metadata test, not invented panel data or an installed graph.

Full registered wrapper contexts change canonical31→30 (18 unmatched/12 validation)
and isolated25→24 (15/9), exactly removing the DSI unmatched identity. Both wrappers
exit1/passedfalse; existing Gunyah processing warning and disabled AFE unmatched
remain. The full validator suppresses required/unevaluated-property failures for
disabled nodes, including this missing graph. This unmatched removal therefore
must not be presented as graph acceptance. Direct selected-schema controls keep
the omission visible. No graph requirement was relaxed, no DT node was changed.

Fresh source-DTB guards pin the actual disabled controller/PHY and consumer edges:
DSI0x14012000+4KiB (source bound0x400), SPI195 level-low, MMSYS clock IDs34/35,
MIPI-TX HS clock and PHY, MMSYS reset23, MM power-domain0 and provider widths.
They reject wrong tuples, activation, assigned clock overrides and unexpected
new graph children. These declarations and compiled source are not measured
clock/reset/domain delivery. Canonical b837e6cb and isolated4480f085 DTB hashes
remain unchanged. Existing MIPI guards also run without modifying their pins.

MT8163 MMSYS DRM master/pipeline data and the actual panel graph remain absent.
Analog/PLL/lane/panel/clock/reset, thermal calibration/banks, regulator handoff,
loading, independent failed-return, retained logs and beta QA stay unqualified.
All seven PID1/host serial admission gates remain denied. No device, display,
PHY, firmware, mode, reset or electrical action was executed.
