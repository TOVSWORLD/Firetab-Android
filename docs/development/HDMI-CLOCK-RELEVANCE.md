# MT8163 unresolved HDMI clock-parent relevance (#29)

This bounded source review advances provider ownership/consumer distinctions.
It changes no clock behavior and does not close the issue's integrated compile
or later runtime gates. [Pinned review receipt](../../evidence/clock-port/hdmi-consumer-review.json)
records exact donor/legacy revisions and file hashes.

## Distinct audio paths must not be substituted

Legacy topckgen declares `apll2_div0` and `apll2_div1` as1:1 factors of
`aud_2_sel`. The maintained donor MMSYS still names those aliases as parents of
`mm_hdmi_audio` and `mm_hdmi_spdif`. They remain unresolved in the current overlay.

The captured DT audio node instead names `CLK_AUDIO_APLL2_DIV0`, registered as
`aud_apll2_div0`: a real3-bit divider at shift28 and gate bit1 in AUDIO_CLK_AUDDIV_0
(offset0x05a0), parent `aud_2_sel`. This is not the legacy1:1 alias merely because
both names include APLL2. Reparenting HDMI audio to that divider would silently
change rate/gating semantics and is not an accepted fix. Shared upstream PLL/mux
ownership also prevents claiming broad audio irrelevance from a name search.

## CTS ownership remains unproved

Legacy `hdmitx_dig_cts` is a1:1 factor of `clk_null`; the current overlay omits
that dummy source but keeps dependent factors `hdmi_cts_ck`, `hdmi_cts_d2` and
`hdmi_cts_d3`, feeding `hdmi_sel` and `mm_hdmi_pllck`. Copying `clk_null` cannot
establish a hardware rate or usable HDMI path. A real HDMI/PHY source and its
registration/rate ownership must be traced before these dependent paths can be
claimed functional.

## What the captured consumer evidence does and does not say

The existing captured literal DT clock audit has no HDMI/DPI-symbol consumers.
The DSI node directly requests `mm_dsi0_engine` via `mm_sel`, `mm_dsi0_digital` via
`dsi0_lntc_dsick`, plus mipi_tx0 PHY. Those immediate parent edges do not name the
three unresolved HDMI parents. Audio does request the distinct real APLL2 divider.

This is not an exhaustive consumer proof: C driver requests, expanded DT overlays,
shared provider registration, enablement, mux propagation and future external
outputs remain outside that textual audit. It does not prove HDMI-related paths
are irrelevant to douglas or that DSI works. The donor's fixed DSI source/rate
also remains a separate hardware qualification, not established by this review.

## Legacy C consumer cross-check

The pinned legacy HDMI driver's clock probe requests every enumerated HDMI clock
with devm_clk_get and BUG_ON on lookup failure (lines1253–1273). Its name mapping
includes MMSYS HDMI PLL/pixel/audio/SPDIF. Legacy mt8163.dtsi has an hdmitx node
with actual HDMI clock phandles (lines1263–1283), unlike the captured maintained
candidate DT. Thus a real legacy C/DT consumer exists; absence from the captured
candidate audit cannot establish whole-board irrelevance.

Preserve a further source discrepancy: legacy phandles list PIXEL then PLLCK,
while corresponding clock-names list mmsys_hdmi_pll then mmsys_hdmi_pixel. Names
and phandle positions must be reviewed rather than copied as an accepted mapping.
No legacy/candidate driver equivalence or correct physical rates are inferred.

## Decision and next executable investigation

Keep dependent HDMI branches explicitly unqualified; introduce no dummy source,
rate placeholder or divider substitution. Next inspect matched maintained-driver consumers
and external HDMI PHY registration/rates, then determine which paths the integrated
candidate actually enables. Implement a valid parent relationship or justify a
bounded unavailable dependent path using that evidence, compile the actual change
and specify later runtime tests. #29 stays Active until its acceptance is met.

## Maintained PHY ownership and explicit consumer guard

The [pinned PHY ownership receipt](../../evidence/clock-port/hdmi-phy-ownership.json)
now identifies the maintained registration contract. The matched ACK common probe
is byte-identical to the pinned donor Git blob. It requires pll_ref and a
clock-output-names property, registers its PLL and publishes an OF clock provider.
Its match table lists MT2701, MT8173 and MT8195; no MT8163 compatible exists there.
The captured candidate DT has no HDMI PHY/output node. MT8173 rate calculations
are not an MT8163 hardware contract, and its ACK implementation is not identical
to the donor blob. Legacy vSetHDMITxPLL writes mode/deep-color tables directly;
a clk_null alias or assumed fixed CTS rate does not reproduce that ownership.

The existing CI clock audit now rejects literal captured DT consumers of the
seven unresolved dependent CTS/mux/HDMI audio-SPDIF-PLL gates until a reviewed
provider/rate contract replaces the restriction. It continues to allow the actual
DSI and audio-divider consumers; it does not blanket-suppress unresolved names.
This is an explicit source-policy decision to keep these dependent paths
unavailable, not removal of registered clocks or hardware validation. Numeric/
expanded DT and C consumers remain outside this bounded textual guard. Any
provider implementation still needs actual compile and later runtime checks.

Next source change to evaluate: replacing the two legacy1:1 alias references with
real aud_2_sel parent relationships while preserving their exact rate/gating
semantics, independently of the missing CTS PHY. Do not substitute the real
APLL2 divider or reopen HDMI consumer paths merely to remove orphan names.

## Resolve the two audio alias references without a dummy clock

The overlay now directly parents mm_hdmi_spdif and mm_hdmi_audio to aud_2_sel.
This contracts each missing legacy ungated1:1 alias edge without changing gate
IDs, register bank, bits11/12, gate ops or upstream aud_2_sel mux/PLL ownership.
It does not substitute aud_apll2_div0, introduce a fixed rate, or enable an HDMI
consumer. The legacy registration code passes CLK_SET_RATE_PARENT to its1:1
factors; their rate is exactly the upstream rate. This source contract supports
using the real parent instead of recreating orphan alias names.

The textual orphan set is now only hdmitx_dig_cts. The seven-consumer guard stays
in force, including HDMI audio/SPDIF: resolving two parent names is not complete
HDMI support. Actual compile evidence and subsequent runtime tests are separate;
no device was modified. Runtime validation must check aud_2_sel rate/gate behavior
with real audio consumers and any future qualified HDMI path before release.
