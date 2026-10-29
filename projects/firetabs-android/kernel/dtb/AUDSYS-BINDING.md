# MT8163 AUDSYS parent contract

Updates #27/#18. This opt-in hash-locked proposal adds the exact MT8163+syscon
parent tuple and requires its register resource. It does not add an AFE child
binding, driver, activation or clock-rate policy. Parent/source/build prerequisites
are pinned in evidence/audsys-binding/source-contract.json.

The integrated driver registers13 gates and6 composites with IDs0..18. Gate offsets
are0; composite registers0x5a0/0x5a4 require a conservative32-bit extent0x5a8,
inside the declared0x1000 resource at0x11220000. ACK simple probe maps resource0
with devm_platform_ioremap_resource for composites and publishes the one-cell
provider. Gates call device_node_to_regmap, whose create path does not manage
optional clocks/resets. The selected no-override syscon defaults to32-bit/stride4.
Fresh-DTB guard rejects width/endian/resource overrides, invalid IDs/phandles and
unqualified AFE activation; it checks15 actual AUDSYS references. This is metadata,
not an observed MMIO mapping or safe power-domain access. The descriptor does not
request runtime PM; actual AUDIO-domain/register/rate behavior remains unqualified.

Only after successful clock registration does the wrapper invoke managed child
population. A populate error unregisters the provider; removal depopulates first.
Pinned OF helper source skips unavailable/already-populated children and registers
managed cleanup. The actual MT8163 AFE child is disabled. Native ASan/UBSan tests
compile/execute the actual wrapper bodies with RAM callbacks for probe failure,
populate rollback and remove ordering. They do not emulate kernel devres internals,
create real devices or qualify physical rollback. GNU AArch64 object compilation
is separately recorded. The C driver and build inputs remain unchanged from the
actual bd288c7/run40828537870 provider compile/Image; current input equivalence,
resolved AUDSYS=y and CC marker are pinned. No individual audsys.o hash was emitted
by that run; none is invented. No new kernel/Image build is needed for this schema
and source-DTB guard scope.

The existing common AUDSYS schema routes most children to the MT2701 sound schema.
Applying that unrelated child contract to MT8163 would introduce false validation.
The new MT8163 branch retains the pre-existing parent object/child-placement rule,
requires reg, and leaves child matching to its independent compatible. **No empty
or fabricated child schema is added.** Both full runs still report the disabled
mediatek,mt8163-afe-pcm child as unmatched. Accepting parent metadata therefore does
not claim that child properties, its driver/build, ALSA or audio work. All older
SoC branches are structurally identical after removing only the MT8163 addition.

Thirty actual decoded parent controls cover tuple/resource/cell/property errors,
optional-child parent operation and older-SoC policy. Full matched5186-YAML runs:

- canonical proposed context34→33:21 unmatched/12 validation;
- isolated USB resource context28→27:18 unmatched/9 validation.

Exactly one unmatched parent diagnostic disappears, no diagnostic is added, and
the unsupported child diagnostic is unchanged. Existing Gunyah mk-schema warning
is retained. Wrapper exit1/passedfalse remains visible despite dt-validate exit0;
these are not full validation passes. Canonical b837e6cb and isolated4480f085 DTB
bytes/disabled states are unchanged. Prior receipts remain historical artifacts.

Reproduce with canonical-command.json/isolated-command.json, the pinned cached
archive and tools; no new kernel archive is required. Run actual decoded controls:
`work/dtb-tool/venv/bin/python3 evidence/audsys-binding/check-controls.py --check`.
Fresh-source CI compiles each candidate DTB, runs validate_audsys_dependencies.py
and keeps unrelated diagnostics visible. No device/firmware/helper execution.

The queue still has real independent board prerequisites: silergy,sym827 is an
unmatched regulator. Cached ACK fan53555 source supports syr827, not that spelling;
that is a lead, not proof of the actual bound driver. Next establish exact driver/
legacy variant ownership, selector and probe/voltage constraints before any alias
or binding change. Never treat SYM as SYR by guess or execute regulator operations.

Clean-CI dependency correction: the DTC setup alone does not install dtschema.
setup_binding_tools.py now explicitly verifies16 package artifacts/4,031,591bytes
for Linux x86_64/Python3.12, installs only hash-checked local artifacts into the
existing work venv and builds actual pylibfdt with pinned SWIG4.4.1. No online
resolver/build isolation or skipped schema checks. The original full-corpus local
receipts remain unchanged; replacement exact-head CI must execute the controls.
Other local platforms retain their existing pinned schema environment; this new
bootstrap does not claim cross-platform support.
