# Transport-neutral acquisition integrity contract

Pinned [source review](https://github.com/bkerler/mtkclient/blob/7cb40e727727dfe3faa065eefb29b16ed29bbdf1/mtkclient/Library/DA/legacy/dalegacy_lib.py#L1193) found additional completion gaps beyond region selection:
legacy readflash's in-memory loop assigns len(buffer)-length at line1229. For a
2MiB request after a full1MiB packet, the resulting negative value exits the
positive-remaining loop early. Its file path advances requested size at1209
without directly checking returned chunk length; join(60) at1219 is followed by
success without an explicit thread-liveness check. The writer catches I/O errors
locally. Geometry helpers can clip a requested length. These are source facts
and conditional failure paths, not observed tablet failures. Source digests and
arithmetic example are in source-findings.json. No checksum algorithm is inferred
or claimed verified from the reader's debug checksum output.

`offline_escrow_capture.capture_region` implements our host-side contract with
injected callbacks; it has no USB/native/helper imports, device binding or CLI.
Only synthetic callbacks have been executed. It requires an explicit user,
boot1 or boot2 region, positive bounded expected length, host disk budget and an
exact True region-selection acknowledgement before reads. Each callback request
is at most1MiB and each response must be immutable bytes of exactly that length.
It never silently clips the declared capture extent or advances by missing data.
A future binding must separately establish trusted raw geometry, offset/region
semantics, bounded callback timeouts and protocol integrity; this module does not
make arbitrary callbacks safe or read-only.

Writes go to a unique private host temporary file. Only exact complete output,
a successful flush/fsync and matching host file length permit exclusive publish.
Existing outputs, including a publish-time race, are never replaced. Failures
remove the temporary output and do not publish a nominal completed file. File
contents are SHA256-streamed; normal capture memory uses one bounded chunk.
This is not a guarantee against power loss or hostile concurrent directory
replacement. Output directories must be trusted. Callback stalls require an
external qualified timeout/transport lifecycle; this function cannot interrupt
arbitrary Python callbacks.

Successful results still leave collection-region identity, protocol checksum,
callback binding, restoration and physical-test readiness false. Host integrity
is distinct from proving the device supplied the requested region. Use the
existing offline escrow verifier after acquisition, then separately compare
independent acquisitions and recovery prerequisites. This captures one host
file, not a complete qualified escrow set. No device commands are exposed.

Tests cover exact extents/hash, short/empty/oversized/exception responses, failed
selection with no reads, forbidden region, low disk, existing output preservation
and exclusive-publish races. Run
`python3 -m unittest discover -s tests -p test_escrow_capture_contract.py -v`.
They use temporary host files and fake callbacks only; no acquisition has run
against upstream or a tablet.

Before any future full acquisition, report exact raw geometry and disk needed
for user+boot regions and independent repeats. A16GB model label/12.33GB usable
filesystem reading is not raw geometry. This function gates each individual file
with expected bytes plus64MiB free-space margin; set-level capacity and callback
throughput/RAM/time still need a measured plan. No large read/download began here.
Next binding work must reject silent backend clipping and demonstrate offsets,
completion and error propagation offline before proposing physical operation.
