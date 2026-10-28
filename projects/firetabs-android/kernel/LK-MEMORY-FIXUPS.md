# Cached LK memory tuple and reservation metadata — #347

The exact-OTA LK static evidence extends LK-FDT-DESTINATION.md. Input SHA256 is
4ca0cca7ae9af6e959dc848b9ca002624c62e1bb93c83c0ecc89bae8d2186b08.
No input firmware/helper was executed and no device state was read or changed.

## Selected memory branch

At payload0x3e08c the caller passes a stack output buffer and capacity4 into
0x25ac4. The helper resolves GOT payload0x761f4+0x12c to a pointer-global linked
address0x4bd874c0, then dereferences the runtime structure pointer. This global
is beyond the file-backed payload; its value and writer are not established.

The helper reads count at structure+0x30, returns failure if count exceeds the
caller capacity, and returns success without writing records for count0. From
structure+0x38 it consumes records with stride24: little-endian64-bit start at+0,
size at+8, with the remaining8 bytes omitted. It writes start then size in
big-endian64-bit order,16 output bytes per record. At0x3e0bc the selected caller
writes `/memory/reg` from the stack tuple buffer using runtime count<<4 bytes.
The alternative inline tuple branch0x3e17c remains separately unqualified.

`decode_mblocks` is an owned host decoding model of this selected layout. It
checks snapshot size, count<=4 and record completeness. It does not validate
physical memory ownership, overlap or correctness, and is not firmware execution.
Tests cover full64-bit values, zero/four records, omitted metadata, oversized
counts, truncated snapshots and changed instruction/property/pointer evidence.

## Selected memory callback

The call at0x3e0ce conditionally invokes0x25bbc. It looks up `/memory` and copies
runtime structure slices into properties: orig_dram_info from+0x98 for0x48 bytes,
mblock_info from+0x30 for0x68, lca_reserved_mem from+0xe0 for16, and
tee_reserved_mem from+0xf0 for16. These are metadata copies, not proof that the
maintained kernel interprets them or that reserved-memory nodes match them.

It then looks up `/reserved-memory`, adds fb-reserved-memory, assigns compatible
mediatek,fb-reserved-memory and writes16-byte reg from runtime globals. Actual
framebuffer geometry, existing-child/error behavior and reservation ownership
remain unqualified. No generic preservation of input reservations is claimed.

## Reproduce and continue

```sh
python3 scripts/trace_lk_memory_fixups.py \
  --lk out/ota-loader-inspection-659664620/lk.bin \
  --output out/lk-memory-fixups-fresh
python3 -m unittest discover -s tests -p test_lk_memory_fixups.py -v
```

Receipts in evidence/lk-memory-fixups pin complete selected instruction-window
hashes, call targets, strings and sparse byte windows for host CI replay. The
analysis object remains non-loadable ET_REL without entry/program headers.

Next acceptance: identify the writer and lifetime of pointer-global0x4bd874c0,
qualify the alternate tuple branch and remaining reservation/PSCI callbacks,
and complete selected r5 lineage/trust checks. Installed LK3 equivalence, actual
matching-DTB placement, independent failed-boot return and retained logs stay
blocked. A candidate DTB's declared RAM/reservations alone cannot close them.
