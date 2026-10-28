# Exact MT8163 topckgen binding proposal (#27)

The captured DT names standalone mediatek,mt8163-topckgen with reg0x10000000/0x1000
and one clock specifier cell. The actual maintained donor clock driver matches
that compatible directly and uses mtk_clk_simple_probe. The pinned full ACK
binding corpus lacks that exact compatible in its topckgen schema.

[Opt-in profile](../../projects/firetabs-android/kernel/dtb/bindings/mt8163-topckgen.json)
adds only the exact standalone compatible to the existing single-compatible enum.
It changes no node data, fallback, property constraints, clocks, rates or hardware.
The wrapper applies it only with --extra-binding mt8163-topckgen and checks exact
ACK revision, input schema, patch and result hashes. Default validation is unchanged.

[Actual full-context report](../../evidence/topckgen-binding/report.json) uses the
cached complete ACK corpus plus the previously recorded proposals. The new
[delta](../../evidence/topckgen-binding/delta.json) removes the unmatched diagnostic
for /soc/clock-controller@10000000 and adds none.53 diagnostics remain (41 unmatched,
12 validation); wrapper exit1 is preserved even though dt-validate itself returns0.
This is a qualified local exact-compatible proposal, not a full schema pass or
upstream/hardware acceptance.

[Seven processed tuple controls](../../evidence/topckgen-binding/controls.json)
accept exact MT8163 and existing MT8173, reject invented MT8163 syscon/fallback/
extra tuples and unknown compatibles, and preserve existing MT8167+syscon.
Removing only the new enum value makes the proposed YAML equal the original:
all other constraints remain identical. [Source provenance](../../evidence/topckgen-binding/sources.json)
and [control provenance](../../evidence/topckgen-binding/controls-provenance.json)
record hashes and actual commands.

No device operations or new binding-corpus download occurred. The attempted
uncached MMSYS routing source read was rate-limited; it was not retried and was
not guessed. This cached exact topckgen driver/schema pair supplied independent
work while #29's provider compile ran. Next investigate the matched infracfg
compatible/reset contract using cached source; complete binding/hardware gates
remain open.
