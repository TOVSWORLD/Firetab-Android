# Development setup

## Lightweight contribution environment

Git and Python 3.10+ are sufficient for repository checks; no Python packages, Android
sync or physical tablet are needed. CI uses Ubuntu 24.04 and its system Python.
Use a fork and feature branch based on development; commands are in CONTRIBUTING.md.

Run all three `scripts/ci.py` project modes, `scripts/check_community.py`, and unittest
discovery from the repository root. Repository checks inspect tracked files, so stage new files before the final local
check. `git diff --check` catches whitespace errors. CI also runs the committed change
guard against the exact PR base. Never replace a failed check with a skip.

## Source research

`python3 scripts/restore_sources.py` restores pinned shallow inspection checkouts into
ignored sources/. Read its lock inventory and resource estimates in CONTINUE.md before
running it; this is not an AOSP platform sync. Existing checkouts are preserved and a
wrong revision is refused. Apply documented patches explicitly. `check_sources.py`
expects those checkouts and the documented device patch; ordinary PR CI does not.

`probe_android11_patches.py` retrieves small pinned raw source fixtures to reproduce
historical patch behavior. It can update evidence files; review every change. It does
not build Android 11 or select it as the maintenance target.

## Static vendor-package inspection

`inspect_crestron_apps.py` needs Android SDK apkanalyzer and compatible Java. Without
`--download`, missing local inputs fail rather than trigger downloads. Its explicit
download mode retrieves roughly 79 MiB of pinned archives. It verifies hashes and
extracts/inspects without executing applications or native libraries. Keep those binary
inputs outside Git. A matching hash is not a verified publisher signature.

## Full builds

No complete Android 17 build recipe exists yet. Use a separately provisioned Linux
x86_64 host and a case-sensitive volume; budget at least 400 GiB free disk and preferably
64 GiB RAM before a full AOSP sync. Download size and build duration depend on the
selected pinned platform/toolchain; publish estimates before new large transfers.
No paid host or unusually large download is implied by contributing.

The checked-in Dockerfile is a historical, unbuilt recipe with unpinned apt dependencies.
Do not call it a reproducible current-platform environment. Reproducibility requires
complete source manifests, toolchain/container digests, commands, logs and output hashes.
