# Douglas handoff coverage and remaining admission evidence — #347

This closes the bounded coverage-inventory scope across nine pinned exact-OTA LK
receipts. It does not close #347, R1/R2, experimental boot, hardware or beta QA.
The cached exact-OTA artifact is not an installed LK3 readback. All nine receipts
refer to SHA256
4ca0cca7ae9af6e959dc848b9ca002624c62e1bb93c83c0ecc89bae8d2186b08.

[Machine-readable manifest](../../evidence/lk-handoff-coverage/manifest.json)
pins each receipt hash, its selected source result, unresolved conditions and five
runtime gates. Run `python3 scripts/validate_lk_handoff_coverage.py` to check the
packet. A successful check means nine consistent source receipts and **zero
qualified runtime gates**. It rejects source-only loading/beta promotion.

## Finite source coverage

- Entry/header: selected ARM/Thumb wrapper and SMC register shuffle, header+0xc
  kernel destination, staging and decompression limits. Entry r4 bootargs are
  saved at a linked address; the local384-byte magic-copy path is pinned. The
  absolute store precedes relocation, so arbitrary placement is not qualified.
- DT selection/address: root version comparison; current candidate lacks the
  required version for the checked route. Header+0x20 supplies FDT destination,
  with fallback0x40000100. The suffix copy precedes in-place open capacity checks.
  Neither a guessed version nor a DTB hash establishes compatible final placement.
- Late contents: chosen bootargs overwrite, memory tuples and original-DRAM/LCA/
  TEE/framebuffer metadata, alternate rank arithmetic, CPU-node removal and
  downward clock-frequency caps. Optional conditional IDME writes mean raw final
  DTB may contain identifiers. Publish normalized allowlisted facts only.

These are selected source paths. Remaining source limits include dispatcher setup
selection/context, all subsequent GOT/global writers, complete FDT lineage and
remaining mutation/trust checks. No CPU-start/PSCI behavior follows merely from
CPU-node edits; no reserved-memory ownership follows merely from tuple decoding.
The manifest links all nine receipts instead of repeating their disassembly.

## Five evidence gates before loading qualification

1. **Installed identity.** A privately retained installed-artifact identity/readback
   or independently authenticated equivalent, tied to the selected route. The
   string LK3 alone does not establish byte/source equivalence. More disassembly
   of the same exact-OTA LK cannot supply this missing identity.
2. **Bounded entry.** Exact reviewed route/artifact, entry register/CPU contract,
   actual placement, extents, overlap and pre-copy bounds, persistent effects and
   return mechanism. Generic Image/QEMU compilation does not qualify this route.
3. **Matching final DTB.** Observed selected post-fixup driver ABI, effective
   command line, RAM/reservations and CPU contract. Stock MFG70/MM67 differ from
   candidate54/51; input-DTB properties may change after selection. Raw capture
   stays private because of IDME. Do not add guessed version/properties to claim
   this gate passed.
4. **Independent failure return.** Observed exit after the intended experimental
   failure via a mechanism independent of the failed payload. Ordinary stock
   recovery before a trial and package reconstruction are not this observation.
5. **Attributable retained failure log.** Defined failure markers, session identity,
   reset/return lifecycle and quantified coverage/truncation. Demonstrated stock
   SYSTEM_RECOVERY_KMSG export is capped at320KiB and does not prove this gate.

Every gate remains unqualified. The [rehearsal](LOADER-RETURN-REHEARSAL.md) retains
R0 as the executable stock observation baseline; this inventory schedules no
firmware/helper execution, mode change or persistent mutation.

## Next executable source acceptance

Compare the existing cached loading/trust alternatives against these gates and
identify one viable nonpersistent bounded entry candidate, or rule them out with
specific blockers. Reuse earlier route reviews rather than repeating cable/log
captures or generating further isolated function scopes. Record the exact
artifact, first persistent effect (if any), supported PL7/LK3/TEE262 evidence,
independent failure exit and missing proof. If no route meets that source
acceptance, identify the single concrete external evidence/action needed before
requesting anything from the owner. No new owner action is needed for this review.
