# Native libusb candidate privately staged

Official Homebrew formula metadata identifies libusb1.0.30 and immutable
arm64_golden_gate bottle digest
b462926c2314b5bb7d1a6721f9a3cf7336a4166ba67024b4bbd0226de457132a.
The source formula tap revision/path/checksum and API response digest are retained.
The target matches this Mac's observed major release27/arm64; other hosts need
their own compatibility review. Source: [Homebrew libusb](https://formulae.brew.sh/formula/libusb).

HEAD established191568 compressed bytes before the download. The exact public
artifact was fetched into ignored out/libusb-artifact only and its advertised
SHA256 matched. Archive declared file contents total619827 bytes. Only the
regular162720-byte dylib was selected for static inspection; no archive scripts,
installer or helper were executed. The reproducible extractor separately caps
expanded tar bytes at16MiB, members256 and selected dylib4MiB, verifies both
bottle and extracted-library digests, and never extracts arbitrary paths.

The library SHA256 is
95c5d6ec5e955b5fb83253963805a0e25a6b1253e9c4e217eaad68e31bb04f4a.
It passes the own static arm64 dylib header/load-command checks. /usr/bin/nm
confirms the seven listed libusb export names in static bytes. That is stronger
than checking a filename but is not complete ABI/runtime/signature validation.
No native loader, libusb initializer, backend, USB enumeration or tablet transport
was invoked. Binary/native library bytes remain ignored and are not redistributed
by this evidence.

Static otool metadata lists Apple system libraries/frameworks and a dylib identity
containing Homebrew's unrelocated @@HOMEBREW_PREFIX@@ placeholder. Homebrew reports
no additional formula runtime dependencies, but no dependency was dynamically
resolved or tested. No relocation, global symlink, loader path or Mac security
setting was changed. Do not assume a workspace copy is a qualified installation
or that it fixes the helper's forced .so finder name automatically.

Reproduce from the ignored cache with
`python3 scripts/stage_libusb_static_candidate.py`. `--download` retrieves only
this digest-pinned191568-byte bottle using public anonymous OCI pull access;
ephemeral authorization is never printed or persisted. The script stages the
single verified library privately and uses static nm inspection. It does not
install/load native code or create a tablet-ready helper. Mac command-line tools
are required for nm; CI unit tests only use synthetic rejection paths.

Combined candidate wheel + bottle compressed budget is5,318,147 bytes. Wheel
expansion/installation and runtime verification remain unperformed. Next prepare
an own host-side adapter contract for explicit pinned library selection and
fail-closed read-region acknowledgement. Review it offline on synthetic source
before any future separately authorized helper/device test. Native artifact
identity is now resolved for this candidate; safe tablet entry, agent effects,
restoration and usable physical logging remain open.
