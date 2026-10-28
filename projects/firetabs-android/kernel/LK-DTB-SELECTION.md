# Cached LK DTB version selection — #347

This is static evidence from the exact-OTA LK, not installed LK3 equivalence,
experimental loading, or a qualified return path. No firmware was executed.

The pinned loader SHA256 and candidate DTB SHA256 are in
`evidence/lk-dtb-selection/report.json`. Payload offsets exclude the 512-byte MTK
container header. The analysis object is ET_REL with no entry/program headers.

At payload0x3de38 the loader obtains a selector from0x20984 and saves it at
stack+0x1c. After a backwards FDT-magic scan,0x3dee6 copies the rounded suffix
into the incoming r1 destination; header/open checks follow the copy. This trace
has not established that all destination/copy bounds are safe.

The root property lookup at0x3df26 uses the literal `version`. Missing property
branches0x3df2e→0x3e174→0x3deb4, resuming the scan. Present property data at+12
is compared at0x3df62 by the byte/string helper0x45cc0 against the saved selector.
Equal compares branch0x3df68→0x3e162→0x3df9e; the selected suffix is subtracted
from the saved header input length. Exhaustion prints the version-specific
no-valid-DT diagnostic. The helper excerpt includes the NUL comparison behavior.

The exact candidate DTB queried with fdtget reports FDT_ERR_NOTFOUND for root
version. The cached stock-DTB report independently contains pre_evt and hvt.
Therefore this candidate lacks a selection prerequisite for this cached route.
The selector helper references the key `board_id`, compares up to seven fixed
17-byte records, caches a selected index and uses index*17 into a version table.
The pinned relocated table at payload0x70540 contains pre_evt, six hvt records,
and invalid. Failure/unmatched paths return invalid. This establishes the static
mapping, not the actual runtime board_id, storage-reader semantics or installed
selector state. Adding a guessed version is not a qualified fix: installed LK3
selection/fixups have not been demonstrated.

Reproduce with the cached inputs:

```sh
python3 scripts/trace_lk_dtb_selection.py \
  --lk out/ota-loader-inspection-659664620/lk.bin \
  --dtb work/dtb-compile/pwrap-pmic-node-name/douglas.dtb \
  --fdtget work/dtb-tool/build/fdtget \
  --output out/lk-dtb-selection-fresh
```

The command checks both input hashes, anchored BL targets/branches, wide literal
references, and the actual candidate property query; it emits bounded normalized
excerpts with hashes. Raw binaries remain ignored. Next source acceptance: trace
the selector's runtime provenance, destination address producer, late fixups and
final handoff, distinguishing original-route evidence from installed LK3.
Recovery/failure-log/runtime gates remain open.
