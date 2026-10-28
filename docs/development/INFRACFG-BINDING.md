# Exact MT8163 infrastructure clock/reset binding (#27)

The maintained MT8163 infracfg driver matches mediatek,mt8163-infracfg and
registers a real reset-controller descriptor (two banks at0x120/0x140 plus index
mapping) before its clock providers. The captured DT declares the exact
MT8163+syscon tuple, one clock cell and one reset cell. The cached ACK infracfg
schema lacks MT8163 in both compatible coverage and the reset-required condition.

The [locked opt-in proposal](../../projects/firetabs-android/kernel/dtb/bindings/mt8163-infracfg.json)
adds that exact syscon tuple and requires its one-cell reset declaration. This is
not a relaxed wildcard or invented fallback. No register data, driver behavior,
existing compatible policy or unrelated constraint changes. The wrapper checks
ACK/schema/patch/result hashes and applies it only with extra-binding
mt8163-infracfg; default validation remains unchanged.

[Actual full-corpus report](../../evidence/infracfg-binding/report.json) using the
cached corpus and prior locked proposals accepts the captured infracfg node.
[Delta](../../evidence/infracfg-binding/delta.json): target unmatched removed,
no new diagnostic;52 remain (40 unmatched/12 validation), wrapper exits1.
This is not full binding or hardware qualification.

[Eleven actual processed-node controls](../../evidence/infracfg-binding/controls.json)
reject standalone/invented tuples, missing/wrong reset cells, wrong clock cells,
missing/multiple registers. Exact MT8163 and existing MT8173 pass; prior MT8173
reset requirement and MT8167 optional-reset policy remain intact. Removing only
the two MT8163 enum entries restores YAML equality with the original.
[Source](../../evidence/infracfg-binding/sources.json) and
[control provenance](../../evidence/infracfg-binding/controls-provenance.json)
retain exact hashes and commands. No device or new corpus download.

Generic provider compilation, exact integrated binding coverage, reset behavior
and actual douglas boot remain separate gates. Continue cached provider-contract
work while the actual parent-fix compile runs; do not interpret fewer diagnostics
as an experimental boot/recovery improvement.
