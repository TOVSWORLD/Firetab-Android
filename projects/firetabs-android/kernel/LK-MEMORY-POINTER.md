# Cached LK entry-r4 and local boot-argument buffer — #347

This extends LK-MEMORY-FIXUPS.md with the selected pointer writer, not a complete
lifetime or installed LK3 qualification. Exact-OTA LK SHA256:
4ca0cca7ae9af6e959dc848b9ca002624c62e1bb93c83c0ecc89bae8d2186b08.
No firmware/helper execution, device access or new download was used.

## Selected provenance

ARM startup branches to payload0x24. The literal at0x70 is0x4bd00020; the store
at0x28 writes incoming **r4** there. This register is an entry contract of the
checked artifact; it is not inferred from a normal C argument in r0.

Initializer0x23230 resolves GOT payload0x761f4 slots0x12c/0x98/0x21c to
0x4bd874c0 (pointer global),0x4bd87340 (local buffer) and0x4bd00020 (saved entry
pointer). At0x23248 it assigns the local buffer to the pointer global before
loading the incoming pointer and testing its first word against0x504c504c.
On equality,0x233a4 supplies copy length0x180 and0x233a8 calls the byte-copy
routine0x45a58 with the local destination and saved incoming source pointer.
The384-byte local buffer ends exactly at the pointer global. Both are outside
the file-backed relocation range ending0x4bd765ac. A selected caller at0x2347e
invokes this initializer. The full init/reset order is not established here.

The nonmatching branch parses alternate tags into the local buffer; complete
conversion, bounds and resulting mblock fields remain unqualified. Therefore
the selected memory helper's input is not established merely by seeing a
candidate DTB or finding its count offset. Actual r4 pointer accessibility,
source extent/magic, initializer success and later writes still matter.

## Relocation caveat

The absolute linked-address r4 store happens **before** startup checks its
current base and conditionally copies the image to linked base0x4bd00000. The
file-backed payload's pointer slot at+0x20 is zero. This ordering does not prove
that the saved pointer survives loading/relocation from an arbitrary address.
No alternate-load fix is proposed and no unsafe runtime outcome is asserted.
Any route using this artifact must explicitly qualify placement and preservation
of this entry state, or supply independently reviewed equivalent behavior.
Installed LK3 may differ and has not been proven equivalent by these excerpts.

## Reproduction and remaining acceptance

```sh
python3 scripts/trace_lk_memory_pointer.py \
  --lk out/ota-loader-inspection-659664620/lk.bin \
  --output out/lk-memory-pointer-fresh
python3 -m unittest discover -s tests -p test_lk_memory_pointer.py -v
```

Evidence/lk-memory-pointer pins instruction-window hashes, linked-pointer slots,
call targets, bounded disassembly and sparse byte replay. Controls reject changed
entry-register stores, relocation instructions, magic branch/copy and pointer
slots. The host analysis object is ET_REL without entry/program headers.

Next executable #347 source acceptance: qualify the alternate tuple branch at
0x3e17c and remaining PSCI/reservation callbacks, then complete selected FDT r5
lineage and trust checks. All subsequent writers/reset lifetime, actual entry r4,
installed LK3, physical DTB placement and independent failure return/log retention
remain open. This source result does not authorize a loading trial.
