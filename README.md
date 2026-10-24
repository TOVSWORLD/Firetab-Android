# FireTabs: douglas development investigation

Status, 24 October 2026: source investigation and initial Android 11 bring-up work.
No ROM was compiled, booted, flashed, or represented as working. No device commands were run.

The existing Android 10 port is the only douglas ROM verified here as having published releases.
Android 11 is a credible next bring-up target. A newer 4.9.337 kernel already contains douglas
board support; investigate it before attempting a 3.18 BPF backport. Android 15 is a plausible
longer-term target with that kernel and extensive compatibility work, not a demonstrated port.
Android 17 requires substantially more kernel/platform and graphics work.

- [Evidence and feasibility](docs/FEASIBILITY.md)
- [Continuation, resources, and build recipes](docs/CONTINUE.md)
- [Work log and validation](docs/WORKLOG.md)
- [Maintenance objective and kernel strategy](docs/MAINTENANCE.md)
- [Pinned source inventory](evidence/sources.lock.json)
- [Actual Android 11 patch failures](evidence/android11-patch-probe.json)

The workspace branch is `port/douglas-bringup`; the device checkout branch is
`port/android11-bringup`. Source clones are intentionally ignored by the outer repository.
Patches, source pins, manifests, and tools are tracked instead. Nothing has been pushed.
