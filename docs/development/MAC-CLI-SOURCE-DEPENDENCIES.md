# Mac read-back CLI: source dependency inventory

This is source analysis, not an installed or device-qualified CLI. No upstream
module was imported/executed, dependency installed or tablet accessed. The
ongoing generic kernel compile is separate (#119/PR121).

At MTKClient7cb40e727727dfe3faa065eefb29b16ed29bbdf1, a conservative syntax walk
from mtk.py visited67 modules. Every cached/downloaded source was checked against
its Git blob identity in the pinned tree, then SHA256 recorded.999718 new source
bytes were fetched under192KiB/file and2MiB aggregate caps. No relative/package
imports were left unresolved in this scan. Dynamic imports, conditional runtime
paths and import-time behavior are not proven complete. Function-local imports
and standalone-module examples are retained as such, not mandatory CLI packages.

Nondeferred imports without an ImportError guard or dependency-module __main__
example branch use these third-party roots: Crypto, Cryptodome, colorama, serial
and usb. A candidate package plan therefore starts with pycryptodome,
pycryptodomex, colorama, pyserial and pyusb, plus a working host USB backend.
The two crypto namespaces both occur through eagerly imported backends, even
when the desired device backend is legacy. Do not remove one just because its
consumer belongs to another backend. Versions/wheel availability/size/host
compatibility remain unverified; this is not a ready requirements lockfile.

The PySide6.QtCore import in config/mtk_config.py:7 is ImportError-guarded and
has a local QObject fallback. Both mfusepy sites are similarly guarded. This
supports a smaller CLI-only investigation without assuming GUI or filesystem
mount support is required. It does not prove a CLI run works without them:
QObject's fallback translation method returns None, and other runtime paths may
have additional assumptions. An installed but broken library can raise an
exception other than ImportError. No reduced-security setting, MacFUSE extension
or GUI package install is justified solely by the upstream general install guide.
Capstone/keystone and other conditional/deferred feature dependencies require a
separate invocation-specific review; syntactic presence is not blanket necessity.

The inventory also sees a bare hwcrypto import under seccfg.py's standalone
__main__ example. It is not treated as a package to install for the CLI. The AST
analyzer records ImportError guards, function scopes and __main__ branches,
without evaluating any upstream code. These annotations are conservative source
facts, not a complete Python import/runtime safety model.

Reproduce using `python3 scripts/inventory_mtkclient_cli_imports.py` from the
existing ignored pinned cache. `--fetch-source` only fills missing source files
under the caps; it never installs anything or downloads binary payloads. It
requires the previously pinned Git-tree metadata. Public evidence contains only
source paths/hashes, import-site metadata and findings; raw upstream code stays
ignored. Source acquisition byte total is retained separately from a cache-only
reproduction's zero newly downloaded bytes.

Next independent task is a pinned candidate wheel/backend resource plan using
metadata only, before proposing installs. Explicitly identify which native USB
library is required on this Mac and what an offline-only validation could test
without importing/instantiating the firmware helper or enumerating the tablet.
Entry/bootstrap, selected-agent effects, region identity, restoration and logs
remain separately unqualified. Do not run the CLI as a dependency test.

## Candidate resource plan and native discovery gap

Version-specific official PyPI metadata now pins five candidate wheels totaling
5,126,579 bytes (~4.89MiB): pycryptodome3.24.1, pycryptodomex3.24.1,
colorama0.4.6, pyserial3.5 and pyusb1.3.1. Each filename, byte count, download URL
and advertised SHA256 is retained in evidence/mac-cli-resources/package-plan.json.
No wheel was downloaded, installed or imported. Metadata consumed115387 bytes;
an initial full-history response exceeded a1MiB cap and was stopped, then
replaced with capped version-specific queries. No full-history metadata retained.

[PyCryptodome's current documentation](https://pypi.org/project/pycryptodome/)
states that4.x uses Crypto only and no longer releases pycryptodomex. This
candidate deliberately keeps the matched3.24.1 pair for the helper's two existing
namespaces, rather than assuming a major-version API migration is covered.
[PyCryptodomex3.24.1](https://pypi.org/project/pycryptodomex/3.24.1/) supplies
Cryptodome; this is a compatibility investigation pin, not a recommendation to
ignore future maintenance/security changes. Dependency adoption needs a review.

Local pip26.2.2's wheel-tag calculation accepts all five candidate tags for this
GIL-enabled Darwin arm64 Python3.15.1. That establishes tag compatibility only,
not package runtime/API compatibility. No resolver install or package execution
was used. The base metadata lists only pyserial's optional cp2110/hidapi extra;
that extra is not selected by this plan. Expanded installation space and native
USB backend download requirements are still unmeasured; this is not a complete
installation budget or a ready lockfile.

[PyUSB](https://pypi.org/project/pyusb/1.3.1/) separately requires a native USB
backend. The pinned helper's Connection/usblib.py:135 groups Darwin with Linux
and supplies a fixed Linux-style libusb-1.0.so name to libusb1's finder. A normal
Darwin dylib path therefore is not automatically established by this source
branch. An alias or other installation might resolve it; no runtime failure is
claimed without testing. The two standard Homebrew libusb dylib paths checked
here were absent. That narrow file check is not a whole-host library inventory.
No native library was loaded and no USB backend or device was instantiated.

Next implement a pure host-side library-path/architecture preflight that can be
tested on synthetic Mach-O headers without loading native code or enumerating
USB. It should establish an explicit usable candidate path before any future
helper adapter or install. Do not change global loader/security settings or
install MacFUSE as a workaround. The helper itself remains unexecuted and
unqualified for acquisition, entry, restoration and log capture.

## Static native-library preflight implemented

`python3 scripts/preflight_mac_usb_library.py` now checks only the two explicit
standard Homebrew candidate files; it does not search devices or enumerate USB.
Neither candidate exists on this host observation. That is a narrow filesystem
result, not proof no native library exists elsewhere. An explicit `--library`
argument can inspect another already available file. No library was installed
or loaded by the implementation or tests.

The parser accepts a generic arm64 Mach-O64 dylib slice, including FAT32/FAT64
containers, and checks architecture table/slice bounds, alignment, overlaps,
load-command bounds and one valid dylib identity command. The Apple SDK
mach-o/loader.h, mach-o/fat.h and mach/machine.h constants/structures were read;
header hashes are in evidence/mac-usb-preflight. x86-only/ELF/executable/truncated
or structurally inconsistent candidates fail. This is a strict format subset,
not a dynamic linker, code-signature checker, dependency validator or proof of
libusb exports/API behavior. Other architectures in a fat file are not executed
or semantically validated. A file can pass structure and still be unusable.

Installation symlinks resolve to a final regular file before opening; device
nodes/nonregular files are rejected. Inputs are capped at64MiB and their bytes
are read/hash-checked only, never passed to a native loader. Trusted local
directories are assumed; hostile concurrent replacement is outside scope.
Output omits selected private paths and emits hashes/structural facts with all
native-loading/USB/runtime readiness flags false. Three synthetic tests bring
the suite to178 passing, including format rejection and symlink resolution.

The next bounded dependency step is provenance/resource metadata for a native
libusb artifact that could be kept in an isolated workspace rather than changing
global Mac library/security state. Do not execute a firmware helper or instantiate
a USB backend to test it. A later helper adapter must use an explicit reviewed
library path instead of assuming a Linux-style filename. Actual libusb loading,
USB reconnect, safe tablet entry and restoration remain separate unqualified gates.

A subsequent transport-source review fetched only the pinned58465-byte PyUSB
wheel as a ZIP for static API inspection; it was not installed/imported. Other
candidate wheels remain undownloaded. See evidence/transport-deadline-contract.
