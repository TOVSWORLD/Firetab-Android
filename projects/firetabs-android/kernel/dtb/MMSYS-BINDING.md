# MT8163 MMSYS tuple proposal — #27

The opt-in `mt8163-mmsys` profile adds only the exact
`mediatek,mt8163-mmsys`, `syscon` tuple to the pinned ACK MMSYS schema. It keeps
all register, clock/reset cell, graph, mailbox and power-domain constraints.
Parent integration is PR #389 under #18; this schema alone does not instantiate
its clock child or validate reset IDs. The captured DSI node is disabled.

The full cached corpus and existing proposal context produce46 diagnostics:
34 unmatched and12 validation errors, down from47. The sole removed diagnostic
is the previously unmatched MMSYS tuple; no new diagnostic is introduced. The
wrapper still exits1 and `passed` remains false. Eleven actual processed-node
controls reject malformed tuples, missing/multiple registers, wrong cells and
unknown properties while preserving existing MT8173 behavior. Removing the one
enum addition reproduces the original YAML structure exactly.

Evidence and commands are in `evidence/mmsys-binding/`; rerun controls with
`work/dtb-tool/venv/bin/python evidence/mmsys-binding/check-controls.py`.
The report records the full profile command, pinned corpus/DTB hashes and
schema-tool version. No downloads, kernel packaging or device actions occurred.
Remaining reset/routing/probe and broader schema/runtime gates stay open.
