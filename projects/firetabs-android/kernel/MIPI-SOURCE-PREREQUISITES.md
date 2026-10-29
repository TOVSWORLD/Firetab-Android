# MT8163 MIPI-TX source prerequisites (#27)

The pinned ACK has no MT8163 match. The donor has a distinct prepare function,
PCW-change register0x60, preserve value2 and an MT8163 descriptor. This is evidence
for a separate variant, not an MT8173 compatible alias. The PHY stays disabled.
No kernel variant or matching binding is added by this audit.

Run `python3 scripts/audit_mipi_source.py --check`. It hashes the actual sources,
compiles selected C functions/helpers with ASan/UBSan RAM register callbacks,
and runs the following finite controls. The register file is only0x6c bytes;
all actual prepare/unprepare accesses fit that model. These are not device reads,
physical PLL rates, timing guarantees or whole-sequence equivalence.

- All1201 whole-MHz rates50..1250 produce PCW matching the active legacy byte
  arithmetic. Fractional-Hz equivalence is not claimed from integer-MHz inputs.
  Legacy and donor thresholds select divisors1/2/4/8/16; the strict62MHz boundary
  is preserved as source intent. Both PCW formulas assume26MHz reference.
- All65536 low16-bit initial preserve-register states are compared in an isolated
  little-endian word/declared C bitfield model. Legacy field is bits7..14,
  donor bits7..11. Only8192 results agree; difference mask0x7000. This is not a
  probability or a measurement of which initial states hardware produces.
- The reused ACK unprepare clears bits8..15. In a synthetic case it clears bit15,
  outside the donor field. A separate MT8163 cleanup must use its chosen field;
  this does not prove a physical cleanup failure occurred.
- Below50MHz donor prepare rejects before RAM I/O. Above1.25GHz it still writes
  if called directly, although the rate-rounding callback clamps. Future scoped
  set/prepare validation must reject unsupported rate/reference before MMIO.
- Actual PCW-change writes are0 then1. The donor requests delay ranges30..100us,
  30..100us and20..100us; active legacy uses1ms at the corresponding settle steps.
  No scheduling or electrical-equivalence claim follows from either source.
- A compiler negative control confirms the pinned donor MT8163 ops references
  `mtk_mipi_tx_pll_round_rate`, whose definition was replaced by determine_rate.
  Retaining the actual ACK round-rate definition makes the selected fixture
  compile. Do not copy this broken callback change into the port.

The generic donor also adds `device_reset_optional` for all SoCs. The future port
must isolate reset/error behavior to MT8163 and keep existing functions/ops intact.
The generic probe owns resource0, reference clock, PLL clock registration, PHY
and clock providers. Candidate declares its reset/reference and no calibration
cell. Existing generic calibration ignores cell/read errors (including deferral),
while the donor MT8163 prepare uses fixed lane RT8, not its rt_code array. Reject
unqualified calibration/drive overrides initially rather than claiming they work.

`mipi-port/variant-definition.json` records the source-backed implementation
intent: legacy declared bits7..14/value2 and1ms delays, fixed RT8,26MHz formula,
range50..1250MHz,0x6c extent and0→1 PCW change. No runtime policy, implemented C
variant or binding acceptance is asserted by this definition. SSC starts disabled
as in the donor; legacy SSC is parameter-dependent, so full sequence equivalence
remains unqualified. Electrical tuning/panel/lane/PLL-lock behavior stays open.

Next task is actual isolated kernel implementation against the cached ACK files,
not another planning scope for these settled fields: MT8163-only match/descriptor,
checked rate/reference/reset/resources, specialized prepare/unprepare, unchanged
old paths, atomic all-target patch preflight, actual C RAM negatives and a separate
explicit builtin PHY object/config/Image build. Bindings must wait for source build.
Do not touch the disabled DT or enable PHY/panel/display. Current full binding
contexts32/26 remain failed. No helper/firmware/device/reset operation executes.
