# Full ACK binding-context diagnostic — issue #27

This experiment is **not a schema pass**. It uses the entire binding archive
from the selected ACK revision, rather than only dtschema's built-in schemas.
Donor-specific binding coverage remains incomplete, and one upstream YAML file
fails parsing. A full corpus download is not a complete matched schema set.

## Inputs and reproduction

`projects/firetabs-android/kernel/dtb/bindings.lock.json` pins ACK revision,
archive URL, byte count, SHA-256, 5,186 YAML files and dtschema 2026.9. The archive
is 3,275,172 bytes and expands under ignored work/; no full kernel/AOSP download
is needed. The helper allows at most 20 MiB for this explicit fetch and verifies
size/hash before extraction with Python's data filter.

First reproduce the locked DTB and isolated tooling as documented in
[DOUGLAS-DTB-EXPERIMENT.md](DOUGLAS-DTB-EXPERIMENT.md). The existing schema-tool
environment additionally needs the recorded dtschema/pylibfdt dependencies; the
helper checks dtschema version but does not provision or claim a hermetic Python
environment. In the prepared environment run:

```sh
python3 scripts/validate_douglas_bindings.py --download
```

Later runs use the verified cached archive without --download. Fresh source
extraction occurs for each run. Input DTB must match the existing 26,283-byte
DT-only experiment hash; outputs go under work/binding-validation/result.
The tool runs full-context dt-mk-schema, then dt-validate with unmatched-node
reporting; no compatible-only or warning-suppression filters are applied.

## Actual outcome

Captured report, structured diagnostics and stderr are under
[evidence/binding-validation](../../evidence/binding-validation). Both underlying
tools returned zero, but the wrapper exits **1** and sets passed=false:

- dt-mk-schema ignored firmware/gunyah-cma-mem.yaml after a YAML tab parsing error
  at line 45. The unmodified source file is preserved; it was not deleted or
  edited to make the run green. The remaining corpus is therefore provisional.
- dt-validate reported **36 validation errors and 61 unmatched-schema diagnostics**
  (97 entries total). Multiple diagnostics may describe a single node; these are
  not counts of distinct broken hardware components.
- Missing MT8163 coverage includes clock, power and board bindings. Existing
  fallback-compatible schemas also reject several donor compatible lists.
- Structural issues include old PMIC child-node naming/required regulator node,
  missing power-domain cell declaration and an interrupt-controller node name.
  Driver matching and a DTB compile do not establish binding conformance.

## Next work

Separate source-schema parsing failures, missing compatible coverage and genuine
DT structural/property mismatches. Add/adapt real MT8163 bindings with provenance
and constraints grounded in the actual drivers; validate schema documents before
revalidating the DT. Preserve phandles/voltages and investigate runtime implications
before changing board data. Do not remove device identifiers or add permissive
schemas merely to suppress diagnostics.

The wrapper treats diagnostics or subprocess failures as failure regardless of
upstream return codes. Ordinary repository CI may check the source and evidence;
this known-failing diagnostic must not be advertised as a passing hardware/schema
gate. None of this accesses the tablet or promotes boot/runtime validation.
