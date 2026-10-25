# Douglas DT compilation experiment — issue #14

Date: 2026-10-25. Initial candidate ACK commit:
`d9318bdb4c34e8b2d997b4f67ced56b120b22b87` (Android 17 / 6.18 family).
MT8163 donor commit: `20951722df6ae1f6fecbfcea0a7d585118a06f3f`.

## Result

The corrected experimental device tree compiles with **dtc 1.8.1 and zero diagnostics**.
The actual DTB is 26,283 bytes, SHA256:

```text
15ee8e58fde850ee571ac607bca5cce480b30c7641265f166edb4b848cda2cf8
```

This is a DTB compilation result, not a kernel build, boot image, boot test, thermal test
or validated board support. No project kernel_compile/boot/hardware stage was promoted.
The physical tablet has not been accessed or modified.

## Real dependencies and compile fixes

The prior audit stopped at a missing MT8163 clock header. This experiment resolved all
transitive literal DTS/header includes, taking actual ACK files where present and pinned
donor files where absent. The [input lock](../../evidence/dtb-compile/sources.lock.json)
records source URLs, commits, bytes, hashes, include relationships and observed 404s.
The 26 files contain roughly 110 KiB of source, including an additional ACK thermal header.
No empty binding files or fabricated macro values were introduced.

Preprocessing those real inputs succeeded. The initial **DTC failed** on unresolved
THERMAL_NO_LIMIT tokens. Patch 1 includes the actual ACK thermal binding. That produced
a DTB, with two structural warnings. Patch 2 renames memory to match its existing base
address and adds two cooling cells to the CPU nodes referenced by cooling maps.
The final compile has no diagnostics; no `-f` or `-Wno-*` flags were used.

The [two patches](../../projects/firetabs-android/kernel/dtb/patches/) retain upstream
source headers and leave inherited memory size, CPU method, regulators and voltages
unchanged. They address syntax/structural declarations, not hardware correctness.
Raw first-failure and intermediate warning logs remain in evidence/dtb-compile.

## Inspecting the compiled binary

The build uses fdtget on the actual generated binary, rather than trusting source text:

- model: Amazon Fire HD 8 (2017)
- compatible: amazon,douglas and mediatek,mt8163
- memory reg: `0 40000000 0 20000000` (512 MiB at the inherited base)
- all four CPU enable-method values: psci
- all four declared cooling-cell counts: 2

Memory size and CPU method are **unvalidated donor assumptions**. The user's hardware
has 1.5 GB; determine bootloader memory fixups/reservations instead of blindly replacing
that size with a nominal number. The old kernel's mt-boot/MTCMOS wrapper must also be
reconciled with the candidate PSCI/firmware contract before assuming SMP or suspend.

The donor common board describes eMMC mux/supplies, a CPU regulator, PMIC interrupt and
a generic PWM backlight. It does not complete the douglas panel/touch endpoint/wiring.
Compare the stock board's LP855x backlight and Goodix configuration before reuse. Correct
phandle references and voltages in a compiled tree do not prove correct physical wiring.
Current integration still lacks the MT8163-specific kernel driver changes identified in
[the source audit](DOUGLAS-KERNEL-AUDIT.md).

## Toolchain and limits

Built official dtc 1.8.1 from the roughly 174 KiB kernel.org source archive. Its hash
matches the publisher's checksum list; PGP signature verification is not claimed.
Meson/Ninja wheels are pinned by URL/bytes/hash for macOS ARM64 and Linux x86_64. The
bootstrap downloads about 1.6 MB on the local host and stays below its 20 MB limit. It
builds only host dtc/fdtget, not a kernel. A C compiler, bison and flex are host dependencies
recorded in logs; a complete immutable container/compiler setup is still outstanding.

The local result used Apple clang 21, DTC 1.8.1 and macOS ARM64. CI repeats preprocessing,
compilation and binary inspection on Ubuntu x86_64 and requires the reviewed DTB hash.
No AOSP sync, whole new kernel checkout, SDK download, paid host or physical tests occur.
Sources/tools/outputs stay under tracked evidence or ignored work/ as documented.

## Schema experiment did not pass

A local dtschema 2026.9/libfdt run was also attempted in an isolated environment. Initial
pylibfdt compilation failed with SWIG 4.5.1 because it removed legacy PyString macros;
using pinned SWIG 4.3.1 compiled the real bindings without C changes or suppressed errors.
The [upstream fix](https://kernel.googlesource.com/pub/scm/utils/dtc/dtc.git/+/5008d1d6a356b8d0a78060da2e1021507d529cff)
describes that tool incompatibility. Exact local schema package inputs are separately
pinned in evidence/dtb-compile/schema-tools.lock.json.

The resulting validator ran with its built-in schemas, **without the complete matching
kernel binding corpus**, and emitted 322 lines of diagnostics. Properties without binding
type context were interpreted as raw bytes. Its exit code was zero; this is deliberately
not treated as validation success. [Schema result](../../evidence/dtb-compile/schema-result.json)
and the raw diagnostic log record the limited attempt. Do not “fix” unknown property
types by deleting real properties. Full ACK/donor bindings, driver integration and board
reconciliation are required before a full schema pass can be claimed.

## Continue

```sh
python3 scripts/setup_dtb_tools.py --download
python3 scripts/build_douglas_dtb.py
```

The setup command only contacts the pinned public tool URLs with explicit --download.
The build is offline. See [experiment guide](../../projects/firetabs-android/kernel/dtb/README.md).
The source-only CI path also runs `build_douglas_dtb.py --verify-only`; the Android job
runs the real compiler. Binary outputs remain ignored and are not release assets.

Next, assemble the actual ACK board/driver integration patch queue and validate against
the matching complete binding schemas. Then use a Linux host for a minimal ARM64 kernel
compile. The earlier 1–3 GiB transfer / 15–25 GiB disk / 8–16 GiB RAM estimates for that
larger experiment remain planning estimates, not measured use in this DT-only task.
Any future owner-run boot test needs an explicit image/recovery/test plan; it is not
implied by a compile success.
