# Isolated MT8163 DSI controller source

Updates #27. This is a disabled-controller source backend. It adds the exact
MT8163 donor descriptor and DRM component identification, without MMSYS master
match data, pipeline paths, panel data, DT edits or runtime admission.

`mt8163-dsi.patch` changes two pinned ACK files and adds `mtk_dsi_mt8163.h`.
`apply_dsi_port.py` verifies revision, all original sources, protocol/build inputs,
immutable historical intent and patch, then shadow-applies and verifies every
output before real writes. The new header must be absent. This is preflight
against wrong inputs, not crash-atomic filesystem persistence or concurrency proof.
Existing SoC function bodies remain unchanged in legacy helpers; dispatch selects
strict behavior only for the new MT8163 descriptor.

The scoped path validates lanes/format and checked 64-bit rate arithmetic before
power side effects. Successful PHY/clock ownership and references commit only
following successful operations. Cleanup keeps the primary failure, retains
unreleased PHY ownership and latches a fault. Bridge atomic and DDP callers use
these checks; a failed power-on cannot create a reference for later enable.
Probe publishes an initially unready host and requests an initially disabled IRQ.
Mandatory reset precedes encoder creation at bind. Attach rolls back fields and
owned bridge/encoder state on component failure; unresolved power cleanup retains
ownership rather than claiming removal. Detach/remove do not establish physical
rollback or driver-core/devres survival after an error. Reprobe/concurrency and
actual CCF/reset/PHY semantics remain runtime gates.

Packet validation rejects null buffers, unsupported flags/types and overflowing
queue sizes before writes. The historical legacy declaration permits a 508-byte
layout, but actual ACK `CMDQ_SIZE=0x3f` can represent only63 words. This
implementation therefore caps payloads at248 bytes (one header plus62 payload
words), including rejection of249 and508. It does not invent a wider hardware
field. The scoped donor HSTX bit and initial command mode, bypass-RACK and no
VM_DONE policy remain source-variant choices; legacy active IRQ policy differs.
Read responses are bounded, timeouts/interruption latch a fault, and accepted
bytes are not evidence of panel receipt.

`python3 scripts/audit_dsi_port.py` shadow-applies the real patch and compiles its
actual helper and selected legacy/caller bodies under ASan/UBSan with RAM
callbacks. Tests cover power failures/reference/cache state, bridge/DDP callers,
reset-before-encoder, attach rollback, probe failures, queue count boundaries,
packet errors, read copy and IRQ bookkeeping. Callback mocks are not a whole
kernel, electrical or physical cleanup test. Other tests check all original
function bodies/descriptors and preflight failures with no target writes.

`build_dsi_provider.sh` stages the accepted SYM/MIPI source frameworks unchanged,
then enables builtin DRM/DSI dependencies, compiles real `mtk_dsi.o` and
`mtk_drm_drv.o` translation units W=1, and links a final Image/vmlinux. Only the
final `MT8163_DSI_PROVIDER_IMAGE_COMPLETE_RUNTIME_UNQUALIFIED` marker and final
hashes qualify this build scope. Earlier staged Images and gzip files are pre-DSI;
explicit W=1 object hashes are pre-Image probes, not final linked-object hashes.
Actual exact-head Linux build and all PR checks are required before merge.

Current canonical31/isolated25 diagnostics remain failed. Controller and PHY stay
disabled. Thermal calibration/bank lineage, clocks, analog/PLL/lane/reset/panel,
loading, independent failed-return, retained logs and beta QA remain unqualified.
No device, mode, firmware, PHY, panel, reset or electrical action was executed.
