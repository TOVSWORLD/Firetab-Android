# Exact MT8163 PLL provider binding (#27)

The captured standalone mediatek,mt8163-apmixedsys node names one register range
and one clock cell. The matched clock driver has that exact OF match and registers
real PLL descriptors. The locked opt-in proposal adds only its compatible to the
existing single-compatible schema enum. It changes no PLL/register/rate behavior
or invented fallback; all other constraints stay identical.

[Profile](../../projects/firetabs-android/kernel/dtb/bindings/mt8163-apmixedsys.json),
[actual full-context report](../../evidence/apmixedsys-binding/report.json),
[delta](../../evidence/apmixedsys-binding/delta.json),
[nine processed-node controls](../../evidence/apmixedsys-binding/controls.json),
[source provenance](../../evidence/apmixedsys-binding/sources.json) and
[control provenance](../../evidence/apmixedsys-binding/controls-provenance.json)
record exact inputs and outcomes. The target unmatched diagnostic disappears
with no additions;51 diagnostics remain (39 unmatched/12 validation), wrapper
exit1 preserved. No full validation or hardware pass is claimed.

Adding this reviewed profile would exceed the255-byte result-directory component
limit. The wrapper now preserves all existing names within that limit and uses a
full SHA256 profile-name component beyond it, keeping distinct exact profiles
separate. Three path tests cover boundary preservation, stable distinct long
profiles and byte-length handling. The complete proposal set actually ran under
its compact name; no corpus download was needed.

## Separate actual provider-instantiation gap (#18)

[Matched ACK source review](../../evidence/clock-port/mmsys-instantiation-gap.json)
finds a more consequential integration prerequisite: MMSYS clocks match a platform
child named clk-mt8163-mm, created by a SoC MMSYS parent. ACK creates its child
from match data but has no MT8163 parent match; the current clock port patches do
not add one. Thus the reviewed normal OF path does not instantiate this clock
provider even when its C object compiles. This is not fixed by adding a schema
compatible or resolving two parent strings. A matched parent/routing/reset port
and actual probe evidence are required. Cached donor DRM display-path data is a
different contract and must not be copied as SoC parent data. Alternate unseen
platform creation has not been exhaustively excluded; no hardware was accessed.
