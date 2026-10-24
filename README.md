# FireTabs: douglas development investigation

Status, 24 October 2026: source investigation and initial Android 11 bring-up work.
No ROM was compiled, booted, flashed, or represented as working. No device commands were run.

The agreed direction is to make these devices useful as general-purpose Android tablets
through maintainable ports of current Android releases and a current, maintained Android
kernel appropriate to each release. Crestron Home is one application requirement, not the
product scope. Hardware-absent features may be unavailable and must be documented.

The existing Android 10 ROM and 3.18/4.9 kernel sources are reference material for hardware
support and regression diagnosis. Extending those old kernels or building intermediate
Android releases is not the selected maintenance strategy. Android 17 is the initial
platform target under investigation; its feasibility remains unproven.

- [Evidence and feasibility](docs/FEASIBILITY.md)
- [Continuation, resources, and build recipes](docs/CONTINUE.md)
- [Work log and validation](docs/WORKLOG.md)
- [Maintenance objective and kernel strategy](docs/MAINTENANCE.md)
- [Pinned source inventory](evidence/sources.lock.json)
- [Actual Android 11 patch failures](evidence/android11-patch-probe.json)

The workspace branch is `port/douglas-bringup`; the device checkout branch is
`port/android11-bringup`. Source clones are intentionally ignored by the outer repository.
Patches, source pins, manifests, and tools are tracked instead. Nothing has been pushed.
