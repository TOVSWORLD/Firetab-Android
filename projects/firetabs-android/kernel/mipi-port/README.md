# Isolated MT8163 MIPI-TX kernel port (#27)

This patch implements the source intent established in PR429. It is a separate
`mediatek,mt8163-mipi-tx` descriptor/clock-ops path, not an MT8173 alias. Existing
SoC prepare/unprepare/rate/signal functions and descriptors remain byte-identical.
The shared probe adds conditional MT8163 checks; actual original-versus-patched
probe C is compared on the old match across success/error callback paths.

MT8163 probe rejects absent/reversed/unaligned/short resource0, absent reset, and
unqualified nvmem/drive properties before mapping. It checks the reference is
26MHz, propagates mandatory reset failure before provider registration, and skips
the inapplicable generic calibration read. Generic old matches retain their probe
behavior, including optional calibration and absence of this reset operation.
The kernel frameworks own managed resource cleanup; RAM mocks do not emulate
devres, real reset completion, PLL lock or electrical rollback.

New rate ops check both the actual CCF parent and supplied parent rate. Invalid
rate/reference leaves the cache unchanged. Prepare rechecks the actual parent and
cached50..1250MHz range before any MMIO. Round-rate clamps valid-reference requests
and rejects missing/wrong reference. Fractional-Hz PCW uses the donor's64-bit
formula; equality to legacy byte arithmetic is tested at1201 whole-MHz inputs,
not asserted for a legacy fractional-rate interface that does not exist.

Prepare sets fixed lane RT8, uses the legacy declared preserve field bits7..14
(value2),1ms settle lower bounds, and donor PCW-change0→1. Specialized unprepare
clears exactly bits7..14 while preserving outside state. SSC is initially disabled;
legacy SSC was parameter-dependent. No whole electrical, panel/lane or timing
qualification follows. The immutable variant-definition.json remains the historical
source-intent receipt; this patch/inputs.json records its actual implementation.

`apply_mipi_port.py` checks ACK revision, all three original sources, patch target
set, helper/definition and pinned Kconfig/Makefile; it shadow-applies and verifies
all outputs before any real patch write. Wrong second/header/helper/definition/
output/build input and reapplication controls retain target bytes. Use a disposable
checkout without concurrent writers; interrupted filesystem persistence is not a
qualified transaction mechanism.

Actual patched C RAM controls run with ASan/UBSan:65536 field/cleanup states,
1201 PCWs, boundary/64-bit out-of-range and wrong/missing-parent errors, no I/O on
rejected prepare, cache preservation, all nine probe failure stages and ordered
reset/provider calls, resource/override errors, power-on failure with no signal
commit, and differential old-probe paths. Tests compile the patched functions,
not rewritten implementation models; MMIO, CCF, OF, reset, devm and delays are
RAM callbacks. No device operations execute.

New explicit `mipi-provider` mode stages the accepted diagnostic/SYM build, then
applies MIPI, resolves PHY_MTK_MIPI_DSI and dependencies builtin, compiles the three
real translation units with W1, and rebuilds final Image/vmlinux. The flattened
`phy-mtk-mipi-dsi-drv.o` aggregate is not a standalone probe target. Prior staged
Image hashes and gzip predate MIPI; only the final
`MT8163_MIPI_PROVIDER_IMAGE_COMPLETE_RUNTIME_UNQUALIFIED` marker and final hashes
qualify this source build. W1 object hashes are pre-Image probes, not assertions
about final linked object bytes. This scope runs no QEMU or device USB/display.

A new exact-head Linux object/config/Image result is required before merge or
matching bindings. Current DTBs, disabled PHY/display states and failed full
contexts32/26 remain unchanged. Physical clock/reset/PLL/analog/panel/lane and
loading/independent-return/retained-log/beta gates remain unqualified.
