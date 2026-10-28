# Cached LK alternate memory and optional fixup boundary — #347

Exact-OTA LK SHA256:
4ca0cca7ae9af6e959dc848b9ca002624c62e1bb93c83c0ecc89bae8d2186b08.
This extends LK-MEMORY-FIXUPS.md and LK-MEMORY-POINTER.md using selected static
paths only. No firmware/helper execution, device access or runtime data read.

## Function-presence guard

Payload0x3e07e loads GOT+0x380; that slot contains Thumb function pointer
0x4bd25ac5, the pinned mblock helper. The comparison/branch at0x3e082/0x3e084
reaches alternate block0x3e17c only when the pointer is zero. Thus the unchanged
pinned artifact takes the helper path. This is not evidence that a runtime mode
flag selects alternate memory. All later GOT writes/relocations remain outside
this bounded proof; installed LK3 may differ.

The alternate block reads rank count0x4bd874e4 and pairs from0x4bd874c4, plus
last-rank adjustment0x4bd874e8. It emits16-byte tuples with zero high cells and
32-bit start/size, subtracting the adjustment only from the last rank's size.
The subtraction uses32-bit arithmetic; the host model reports wrap explicitly
and does not declare wrapped geometry valid. The block saves FDT r5 atstack+0x2c
before temporarily using r5 and restores it at0x3e228 before the common reg write.
The model restricts count to the initializer's reviewed1..4 rank limit (also
accepting zero as the selected non-loop case); this is not a new runtime bound.

## Optional dispatcher and identity-data boundary

The dispatcher at0x140 reads callback/context storage at linked-base plus
payload0x7c010/0x7c014. If the callback is null it returns zero; otherwise it calls
through r3 with FDT r0 and context r1. One conditional setup path at0x51c/0x520
copies GOT+0xdc, Thumb pointer0x4bd00d85, into callback storage. This pins one
possible target, not proof that this setup branch runs on the installed device.

That target atpayload0xd84 looks up `/idme`; selected later calls write `value`
and `permission` properties from runtime records. It is an IDME mutation path,
not evidence that the optional dispatcher is itself a PSCI fixup. Full record
enumeration, context contents, setup selection and all other writers remain open.
No identifier values were decoded or published by this investigation.

A future post-fixup DTB capture may contain device/household identifiers. Keep the
raw capture private under ignored out/ and publish only normalized allowlisted
technical facts. This extends the existing evidence privacy rule to the final DTB;
an input candidate hash cannot establish final contents or safe publication.

## Reproduce and continue

```sh
python3 scripts/trace_lk_alternate_memory.py \
  --lk out/ota-loader-inspection-659664620/lk.bin \
  --output out/lk-alternate-memory-fresh
python3 -m unittest discover -s tests -p test_lk_alternate_memory.py -v
```

Evidence/lk-alternate-memory contains bounded disassembly, exact selected-window
hashes, pointer/literal receipts and sparse replay data. Five controls cover
reference drift, zero-high-cell encoding, last-rank arithmetic and model limits.
The analysis object is non-loadable ET_REL without entry/program headers.

Next executable source acceptance: identify the selected dispatcher setup source
and remaining PSCI/reservation edits, then finish FDT r5 lineage and handoff trust
inventory. Actual GOT/context values, installed LK3, physical placement and
independent failed-boot return/log retention remain Blocked.
