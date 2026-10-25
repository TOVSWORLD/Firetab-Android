# Local boot-image inspection — issue #32

`scripts/inspect_boot_image.py` reads a regular local file. It does not connect to
the tablet, invoke adb/fastboot, extract components, build firmware, decompress
payloads or write its input. Device nodes and pipes are refused. Input is capped
at 256 MiB. It supports an Android header at offset zero with the v0 layout (or
indistinguishable legacy layout with a zero DT-size word), not OTA/wrapped images.
See the [AOSP header documentation](https://source.android.com/docs/core/architecture/bootloader/boot-image-header).

For a matching boot-image file obtained later, run locally:

```sh
python3 scripts/inspect_boot_image.py /path/to/boot-image-file
```

Only after the actual partition size is established, add
`--partition-bytes SIZE_IN_BYTES`. The old device-tree 16 MiB value is a reference,
not a measurement of this tablet's current layout. Header page size is distinct
from the kernel's memory page size.

Output contains the file/component SHA-256 hashes, declared load addresses,
component offsets/sizes/padded bounds, simple kernel signatures and trailing
bytes that the tool does not classify. A gzip signature does not establish its
contents or appended-DTB layout. Nonzero version/legacy-DT-size words are refused
rather than guessed. Invalid alignment, empty kernel and truncated components
or padding are rejected. A supplied partition overflow exits nonzero.

A fit result is a byte-count comparison only. The tool does not validate firmware
identity, cryptographic signatures, memory overlap, loader compatibility, correct
DT or successful execution. Unknown tail bytes can include metadata/signatures;
they are counted in file size and are not silently stripped. No inspected real
stock image or valid firmware test result exists yet.

Ten synthetic tests cover valid layout recognition and rejection/limitation
paths through `python3 -m unittest discover -s tests -v`. Synthetic fixture bytes
are generated in memory; no firmware or compiled binaries are committed.
