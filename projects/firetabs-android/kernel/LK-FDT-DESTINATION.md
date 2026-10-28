# Cached LK FDT destination and selected late writes — #347

This extends LK-DTB-SELECTION.md using the same exact-OTA LK SHA256
4ca0cca7ae9af6e959dc848b9ca002624c62e1bb93c83c0ecc89bae8d2186b08.
It establishes selected static paths, not installed LK3 equivalence or a safe
experimental loading/return procedure. No firmware or helper was executed.

## Address producer

With a nonnull header pointer, payload0x3ed84 reads header+0x20 into r5;
0x3ed90 passes it as r1. Wrapper0x3eb84 forwards r0–r3 to0x3de1c, where
0x3de2a saves incoming r1 in r5. This is distinct from header+0xc, which supplies
the kernel entry/decompression destination in the prior header-producer trace.
The header-absent branch constructs r1=0x40000100 at0x3edc0/0x3edce and calls
the same wrapper. Neither path proves the actual current runtime destination.

At0x3dee6 a byte-copy helper writes the rounded selected suffix into r5.
Only afterward does0x3df08 call the in-place open helper with source=destination
and capacity limited to MIN(global-boundary minus r5, 1MiB). That limit does not
establish pre-copy capacity, underflow safety, physical mapping or non-overlap.
No vulnerability or exploitability conclusion follows from this selected trace.

## Late mutation boundaries

The `/memory` lookup at0x3e0a4 is followed by a `reg` update at0x3e0bc,
using a stack tuple buffer and runtime count shifted left4 as byte length.
Candidate memory properties cannot be assumed preserved. The tuple producer,
its runtime count/contents and all reservation changes remain to be qualified.
The `/chosen` lookup at0x3e0e2 precedes selected atag,boot and atag,mem property
writes at0x3e262/0x3e284. The existing LK bootargs trace separately establishes
overwrite behavior. These selected writes are not a complete fixup inventory.

At the K64 call site0x3e73e, r1 is again r5. The existing handoff trace checks
the wrapper/SMC register shuffle; all intervening r5 branches/callbacks and the
secure monitor's final behavior remain unproved. An input-DTB hash is therefore
insufficient proof of the exact final DTB consumed by the kernel.

## Reproduction and acceptance

```sh
python3 scripts/trace_lk_fdt_destination.py \
  --lk out/ota-loader-inspection-659664620/lk.bin \
  --output out/lk-fdt-destination-fresh
python3 -m unittest discover -s tests -p test_lk_fdt_destination.py -v
```

`evidence/lk-fdt-destination/report.json` records exact instruction anchors,
call targets, literal references, bounded disassembly hashes and unresolved
conditions. windows.json supplies sparse technical byte windows for independent
CI replay without distributing the raw firmware. Controls reject changed address,
copy-capacity, call and property references, and truncated input. The host analysis
object is ET_REL without entry/program headers and is never executed.

Next executable #347 source scope: trace the runtime memory-tuple producer and
reservation/PSCI mutation callbacks, then complete selected r5 lineage and trust
checks before defining any loading trial. Keep actual matching DTB handoff,
independent failure return and retained failure logs blocked until observed.
