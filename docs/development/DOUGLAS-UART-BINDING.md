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
