# Offline legacy read binding contract

This own adapter maps the transport-neutral capture interface to the reviewed
legacy readflash API signature. It imports no upstream helper, opens no native
library and exposes no device CLI/bootstrap. Tests bind synthetic callbacks only.
It is not a tested live acquisition package.

The source contract requires non-IoT legacy eMMC and explicit expected raw
user/boot1/boot2 byte counts, independently compared with a supplied observed
geometry callback. Geometry is rechecked before selection and every chunk.
The source's region translation must preserve requested length exactly and map
to the expected region ID; clipping or different IDs fail before readflash.
Offsets/counts must be aligned to the supplied512/4096 logical sector size,
within the declared region and no larger than1MiB. The sector size is explicit;
a DA record's page size is not used as raw geometry evidence.

The adapter passes addr=byte_offset, length=exact_count, filename='', the explicit
parttype and display=False to the read callback. Memory mode avoids the upstream
file-writer thread, and bounded requests avoid relying on its erroneous
multi-packet in-memory loop. Returned type/length are checked again. Any exception
invalidates the acknowledged active-region state; reuse requires fresh selection.
The host capture layer propagates failure and does not publish completed output.
No arbitrary upstream command dispatcher is exposed by this interface.

**Internal selection is still a separate mandatory condition:** readflash calls
the region selector again. The source-hardening guard from127/PR128 must be
integrated and validated before any future real binding; the outer successful
selection cannot prove the internal one succeeded. The adapter does not attest
callback source or effects, and it cannot interrupt a blocked arbitrary callback.
Protocol checksum verification, transport timeouts/reconnect and agent behavior
remain unqualified. No actual backend instance was constructed or called here.

Four tests exercise exact byte offsets/API kwargs through host-file capture,
clipping/wrong IDs, mismatched or changing geometry, unsupported backend/storage,
unselected/unaligned/out-of-bounds reads, failed internal reselection, short data
and selection failure. All callbacks are own fake functions; no upstream source
is executed. Source files/IDs are pinned in contract.json for continued review.

Run `python3 -m unittest discover -s tests -p test_offline_legacy_binding.py -v`.
A passing test establishes the offline binding contract only. Actual collection
origin, protocol integrity, native helper, safe entry, restore and physical logs
remain open under106. Next qualify the source-level checksum/transport error path
and timeout behavior independently before considering an owner-operated read.
