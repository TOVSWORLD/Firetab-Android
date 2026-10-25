# Local MT8163 UART binding proposal — issues #27 and #22

The pinned donor DT declares four UARTs with the exact compatible pair
`mediatek,mt8163-uart`, `mediatek,mt6577-uart`. The retained ACK 8250_mtk.c
matches the second string and supplies an OF early console. The driver compiled
in the earlier full Image. See [console/storage evidence](DOUGLAS-CONSOLE-STORAGE.md)
and its pinned driver, binding and DT sources. This motivates a narrow local
binding proposal; driver matching is not proof of hardware compatibility.

The proposal adds MT8163 to the existing enum of first strings requiring the
MT6577 fallback. It retains every other constraint, including clocks, DMA,
interrupts, required properties and unevaluatedProperties=false. No DT compatible
is removed, no wildcard or additionalProperties relaxation is added. It is not
an upstream accepted binding. Runtime baud rates, DMA, clock and pin wiring
remain unverified; the separate UART DMA controller schema still lacks MT8163.

The proposal patch and original/proposed schema hashes are pinned under
projects/firetabs-android/kernel/dtb/bindings. Validation uses a fresh extraction
of the exact original ACK corpus and checks its original schema hash, patch hash
and patched schema hash before running dt-doc-validate and full corpus tools.
The default `ack` profile keeps the original corpus unchanged.

```sh
python3 scripts/validate_douglas_bindings.py \
  --experiment sysirq-node-name --binding-profile mt8163-uart-proposed
```

Existing locked corpus/tool dependencies are reused; this adds no download.
The schema meta-validation exits zero with no diagnostics. With the identical
26,279-byte DTB, full-context results change from 33 errors/61 unmatched to
29 errors/57 unmatched. Four UART compatible errors and four corresponding
unmatched entries disappear; no diagnostic signatures are added. These are
schema-selection/conformance results for this proposal, not hardware results.

The upstream Gunyah YAML parsing failure and remaining coverage/validation errors
persist. The overall command exits 1 and reports passed=false. Logs, structured
delta and exact hashes are retained under evidence/uart-binding. No kernel build,
firmware packing, tablet access or physical changes occur.

## Opt-in full-corpus YAML lexical repair (#62)

`validate_douglas_bindings.py --experiment sysirq-node-name --binding-profile
mt8163-uart-proposed --repair-gunyah-yaml` applies a separate hash-locked local
repair to the extracted corpus: exactly three tab indentation characters become
six spaces. Default ACK input and schema semantics remain unchanged. Input/output
hashes and ACK revision are locked in bindings/gunyah-yaml-repair.json; changed
inputs are refused. No diagnostics or schemas are suppressed.

Actual local full-corpus run retained under `evidence/gunyah-binding` now gets
past YAML lexical parsing. Gunyah remains ignored by dt-mk-schema for an invalid
compatible schema, explicitly recorded in stderr. Separate meta-validation
exposes compatible list type, memory-region constraints, singular example key
and missing additional/unevaluatedProperties issues. Indentation repair does
not qualify that schema or the full corpus. Tools still return0 despite those
errors; wrapper correctly returns1/passed=false. DT results remain29 validation
errors plus57 unmatched entries (86 diagnostics), unchanged by this unrelated
schema's lexical repair. The opt-in UART schema itself remains meta-clean.

Next task under#27: source-backed semantic correction of the Gunyah schema and
example, preserving compatible/memory-region behavior, then rerun full corpus;
alternatively independently resolve the PMIC shutdown/generic-domain selector
overlap. No hardware/device/compiler build or download occurred here. This closes
only the bounded lexical-repair implementation scope, not#27 validation.

## Exact MT6323 sys-off selection correction (#64)

Add `--repair-pmic-selector` to the preceding repaired-corpus command to apply
an independent opt-in, input/output/patch-hash-locked proposal to
power/power-domain.yaml. The generic domain schema auto-selects by node name;
the MFD binding names its sys-off child power-controller, despite the actual
mt6323-poweroff driver registering sys-off rather than genpd. The proposal makes
that name selection explicit and excludes only nodes whose compatible contains
mediatek,mt6323-pwrc. It changes no domain property constraints, MFD schema, DT
properties, hardware driver or node name, and does not invent domain cells.
The MFD binding continues constraining that exact child.

Actual local meta-validation of the proposed schema is clean. Negative controls
run with `work/dtb-tool/venv/bin/python evidence/pmic-domain-selector/check-controls.py`
verify that a generic domain missing cells still fails, nodes without compatible
still select by domain name, and MFD sys-off nodes still reject unknown properties
and wrong compatibles. Exact original domain constraints are preserved. Unit tests
verify locked patch application, byte-for-byte preservation outside select and
refusal of changed upstream input. Hashes/profiles and local logs/results are
retained in `evidence/pmic-domain-selector`.

Full-context diagnostic delta removes exactly one required-cells error at
/soc/pwrap@1000d000/mt6323/power-controller and adds none:28 validation errors plus
57 unmatched entries remain, overall passed=false/exit1. Gunyah structural schema
error is still explicitly reported. This is a local source-backed selector
proposal, not upstream acceptance or a full-schema/hardware pass. Next#27 task:
map and resolve remaining errors by binding/node with negative controls, beginning
with Gunyah structural invalidity or a board-relevant mismatch. No device access.

## Strict storage and UART-DMA compatible coverage (#72)

The unchanged donor's three MMC controllers declare MT8163 followed by MT2701;
its UART APDMA declares MT8163 followed by MT6577. Pinned ACK mtk-sd.c and
mtk-uart-apdma.c match those fallbacks. Source hashes/snapshot provenance are in
evidence/storage-console-bindings. No claim is made that the fallback's timing,
DMA addressing or tuning is qualified on douglas.

Two new independent opt-in profiles, --extra-binding mt8163-mmc and
--extra-binding mt8163-uart-dma, add only these exact compatible pairs. For MMC,
the existing MT7623+MT2701 tuple becomes a first-string enum of MT7623/MT8163;
UART-DMA adds MT8163 to its first-string enum. Required fallbacks and all clock,
register, interrupt, DMA, pinctrl and power constraints remain unchanged. Default
corpus and DT/driver inputs do not change. Append both profiles to the preceding
rdma-node-name full-context command including prior proposal flags.

Actual meta-validation of both proposals is clean. Processed-schema controls
accept exact pairs and existing supported SoCs, reject missing/wrong/extra
fallbacks, and compare all other YAML constraints with original. Reproduce with
`work/dtb-tool/venv/bin/python evidence/storage-console-bindings/check-controls.py`.
Locked patch tests reject changed input and prove all other constraint bytes
preserved.89 unit tests pass. Full-context delta removes4 validation errors and
4 unmatched entries (three MMC nodes and one DMA node), adds none:21 validation
errors/51 unmatched remain,72 diagnostics, overallpassed=false/exit1. Exact
source/patch/input/processed/control hashes, local logs/results and delta retained.
This is binding coverage only, not storage access, UART DMA operation or a
boot-ready image. Next#27 remaining I2C/SPI/ADC/RNG fallback coverage, or display
binding gaps with the same negative-control discipline. No tablet accessed.
