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
