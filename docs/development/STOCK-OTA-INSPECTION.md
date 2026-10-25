# Bounded stock OTA inspection — issue #46 / #21

A stock OTA candidate can provide file-layout evidence without device access.
It cannot establish the current tablet's firmware handoff, memory fixups or
recovery. The tool downloads no complete OTA, installs nothing and executes no
archive entry. Binary outputs stay in ignored local out/, not public firmware.

## Candidate identity and discovery trap

The [community index](https://github.com/fireos-archive/fireos-archive/blob/main/README.md)
labels two 5.7.1.0 HD8/HD10 links incorrectly. Its HD8 entry points to a filename
marked HD10; CRC-checked target.build.prop identifies KFSUWI/suez/MT8173. The
HD10-labelled entry points to an HD8 filename whose internal properties identify
KFDOWI/douglas/MT8163. Do not choose packages from those labels alone. Exact
README blob/hash, candidate URLs, response metadata, range hashes and identities
are in evidence/stock-ota-probe/index-mismatch.json. The index is discovery data;
the model evidence comes from bytes served at the linked package URLs.

The correct-hardware candidate has incremental build
50.6.5.9_user_659664620 and fingerprint
Amazon/douglas/douglas:5.1.1/LVY48F/50.6.5.9_user_659664620:user/release-keys.
Its embedded ro.build.version.fireos says 5.3.7.3, despite the index's 5.7.1.0
label. The relationship to the user-visible version is unresolved. It must not
be described as an exact match to the user's installed Fire OS 5.7.1.0 until
actual build facts are supplied. Amazon's manual-update help page returned 503
in this investigation; no current official-page endorsement was inferred.

## Reproduce bounded extraction

```sh
python3 scripts/probe_stock_ota.py --download --boot-image \
  --url 'https://fireos-tablet-updates.s3.us-west-2.amazonaws.com/0ddfeap1GXdqCPab39o1Yn1dWv/update-kindle-Fire_HD8_7th_Gen-50.6.5.9_user_659664620.bin' \
  --output out/stock-ota-douglas-659664620
python3 scripts/inspect_boot_image.py out/stock-ota-douglas-659664620/boot.img
```

Use a fresh output path; existing output is refused. Omit --boot-image for
metadata-only inspection. --download is required before any network request.
HEAD provides archive size/ranges/ETag; subsequent requests use If-Match and
require exact 206 Content-Range, unchanged ETag, URL and identity encoding before
reading a bounded body. A 200 fallback is rejected before body reads. The tool
limits cumulative response-body reads to 20 MiB and each compressed/uncompressed
entry to 16 MiB. This is a response-body budget, not an assertion about HTTP/TLS
wire overhead. ZIP64, split/encrypted archives, duplicates, invalid bounds,
unsupported compression, local/central inconsistencies and size/CRC failures
are rejected. Only the fixed property entry and optional boot.img are extracted;
model/manufacturer/device/platform must match before boot-entry extraction.
No arbitrary archive paths are written and no helper/update binary is executed.

The full candidate is 907,705,758 bytes; it was not downloaded. Actual bounded
probe read 8,612,864 response-body bytes and produced an 8,689,664-byte boot.img,
SHA256 8982fa50193acc764be69ee51027ee92e83614cee4b8235b07439d1f9e2db363.
This candidate uses less than 32 MiB of working payload/output memory; generic
Python/process overhead is additional. Initial metadata investigations across
both candidates used another 204,800 response-body bytes. No paid resource,
Android tree or toolchain download was involved. CI exercises synthetic archives
and fake transport only; it never fetches stock firmware or queries devices.

## What the bytes establish

Existing boot-image inspection reports a legacy/v0-compatible layout, 2,048-byte
pages, kernel load-address field 0x40080000, ramdisk 0x44000000 and tags 0x48000000.
These are header fields, not validated addresses for the new kernel. The kernel
component is 7,191,666 bytes; ramdisk 1,492,335 bytes. A 512-byte kernel prefix
starts with little-endian word 0x58881688 and KERNEL name bytes; its size word
matches the remaining component length. Gzip starts after that prefix. Bounded
64-byte decompression finds ARM\x64 at header offset56, matching the official
[AArch64 boot ABI](https://docs.kernel.org/arch/arm64/booting.html). This identifies
an AArch64 Image prefix in this candidate; the generic inspector conservatively
leaves the wrapped payload's full identification unknown.

The image has 2,048 unclassified trailing bytes, with a DER-like prefix. Neither
that observation nor ZIP CRC/ETag validates a signature. No full OTA hash,
certificate chain or boot signature is verified. No partition size was supplied
to the inspector and no fit claim is made. The bounded tool cannot independently
authenticate the whole package from selected entries. It is evidence for further
format/loader review, not recovery firmware or a trusted physical-test package.

Remaining #21 gates include exact installed build/stock facts, runtime RAM and
reservations, CPU/PSCI handoff, wrapper/trailer/authentication requirements,
recoverable loader route and a qualified log channel. No DT/ramdisk integration,
boot-image packing or physical device operation occurs in this work.
