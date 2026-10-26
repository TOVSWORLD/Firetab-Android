# Offline host adapter safeguards (#127, child of #106)

Our AST-only transformer now prepares two changes against exact hash-pinned
MTKClient7cb40e727727dfe3faa065eefb29b16ed29bbdf1 source modules:

- The Darwin native-library finder selects the explicitly pinned private libusb
  candidate path. Linux/FreeBSD retain their existing branch result; Windows
  lookup is untouched. No global symlink or loader/security setting changes.
- The legacy eMMC read's existing region-selector call must return exactly True;
  otherwise it raises before the following read. False/None/truthy non-Boolean
  values all fail closed. This addresses the discarded Boolean at the audited
  readflash site, not every possible acquisition failure.

Original source sites:
[usblib.py:135](https://github.com/bkerler/mtkclient/blob/7cb40e727727dfe3faa065eefb29b16ed29bbdf1/mtkclient/Library/Connection/usblib.py#L135),
[dalegacy_lib.py:1141](https://github.com/bkerler/mtkclient/blob/7cb40e727727dfe3faa065eefb29b16ed29bbdf1/mtkclient/Library/DA/legacy/dalegacy_lib.py#L1141).

The actual original module hashes and native-library hash are checked before
transformation. Source is parsed/unparsed as syntax only. Original caches remain
unchanged. Modified upstream source is written only as ignored .review.txt files
in a fresh out/ directory, not as importable replacements or an installed helper.
The public report contains digests and qualification flags, no copied helper code
or private absolute library path. The transformed USB text digest depends on the
private workspace path and is not a cross-host reproducible byte identity.

Run `python3 scripts/prepare_offline_readback_adapter.py --output out/FRESH_NAME`
using the already pinned private caches to reproduce review artifacts. It does
not download anything, import/execute upstream code, load a native library,
instantiate a USB backend, enumerate a device or modify firmware. Output outside
ignored out/ and already-existing output directories are rejected. Source drift
or an unexpected number of transformation sites fails instead of guessing.

Three tests execute **only synthetic fixture classes/functions**, never upstream
code. They verify failed selection prevents subsequent fake reads, exact True
continues, Darwin changes while Linux remains unchanged, and source drift is
rejected. The actual upstream outputs are AST-validated, not runtime-tested.

This completes the bounded offline source-hardening task. It does not qualify
libusb loading, actual region selection, short-read/geometry handling, security
bootstrap side effects, uploaded agent identity or a recoverable diagnostic boot.
No original security payload/agent bytes were patched or executed. Parent106
and physical logging/restore gates remain open.

Next source task: define a read-only invocation allowlist and acquisition
preconditions independently of upstream's broad command dispatcher. Keep every
runtime/device operation blocked in automatic runs; a future owner-operated test
needs the complete entry, backup, restoration and log procedure first.
