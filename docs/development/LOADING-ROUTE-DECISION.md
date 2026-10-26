# Douglas diagnostic loading route decision

Decision2026-10-26: continue developing an observation-first, separately reviewed
RAM-bootstrap route. No physical loading route is qualified. This decision
selects the engineering investigation; it does not select a working exploit,
agent, load address or owner test. Parent106 remains open.

## Route ranking from retained evidence

**First: minimal observation, then a constrained RAM bootstrap.** The owned host
adapter has fake-device transfer/cleanup tests and process supervision. The exact
Mac libusb candidate loads and returns its version without a context. Actual
backend initialization scans devices, so it was not executed. These host pieces
can support a future observation test after entry/return effects are qualified.
Observation must establish fresh mode/version/security facts before agent
selection; it does not itself load a kernel or acquire escrow.

A RAM bootstrap remains plausible source-level work because the pinned candidate
has agent/stage upload paths and matching current-stock EMI data is available.
No persistence-free guarantee follows: bootstrap firmware, MMIO/security effects,
placement, agent acceptance and interruption handling still need review. A tool's
stage2 is its protocol environment, not the Linux kernel or a proven ARM64 boot
trampoline. The next scope is the smallest stage path's actual effects and exit,
not the complete archived unlock script.

**Second: stock fastboot as an observation/return candidate.** Exact-stock LK
registers download/continue/reboot operations in the selected region, but not a
boot command there. Continue reaches a boot-labelled named-record/device-callback
image path with combined16MiB and later verification constraints. Download plus
continue is not an established RAM-boot route. Static registration also does not
prove the current command filter permits the operation. Keep it as a candidate
for a separately reviewed stock-return test, without claiming it loads diagnostics.

**Defer: persistent boot-chain/recovery changes.** The archived software route
intentionally bricks and subsequently modifies boot/security-related storage.
The minimal path assumes prior changes and touches GPT, boot headers, RPMB and
other areas. It lacks the qualified original-state escrow and independent restore
needed here. Modified recovery/fastboot can be useful later, but cannot be assumed
as the current starting state. No downgrade or persistent change is selected now.

## Storage and logging implications

Any route changing boot-chain storage must first preserve original user and both
hardware boot regions with independently verified selection/geometry. The record
store mapping gives a specific reason to include the second boot area; generic
firmware is not a substitute. RPMB/key/counter/fuse state is a separate boundary,
not covered by ordinary image files. A RAM-first route reduces intended writes
but must still establish its actual effects and failure return.

Usable first-kernel logs remain a parallel physical prerequisite. UART routing
source is known, but accessible pads/electrical levels are not qualified; pstore
retention/readout is also not established. Host observation protocol reports are
not kernel boot logs. No package is ready merely because host tests pass.

## Next bounded implementation/research scope

Trace the pinned stage/preloader-stage path from entry through memory writes,
execution transfer and its shutdown/reboot handling. Record exact source hashes,
external firmware dependencies, whether code can restrict itself to observation
and RAM loading, and which failure exits require reboot or persistent changes.
Do not execute it, include payload bytes or patch firmware. Reuse existing source
caches. If the path cannot support a recoverable minimal test, document the exact
reason and compare another path instead of expanding host-policy wrappers.

Sources: [route inventory](../../evidence/recovery-material/sequence-gates.json),
[bootstrap audit](../../evidence/recovery-bootstrap/report.json),
[entry audit](../../evidence/entry-transition-source-audit/report.json),
[current-stock analysis](CURRENT-STOCK-ENTRY-RETURN.md),
[host binding limits](OBSERVATION-BINDING-DESIGN.md),
[pinned stage usage](https://github.com/bkerler/mtkclient/blob/7cb40e727727dfe3faa065eefb29b16ed29bbdf1/README-USAGE.md#L363-L406).

## Pinned stage/plstage review: unmodified helper is not a qualified RAM loader

At the pinned revision, [cmd_stage](https://github.com/bkerler/mtkclient/blob/7cb40e727727dfe3faa065eefb29b16ed29bbdf1/mtkclient/Library/mtk_main.py#L193-L291)
calls the monolithic initializer and crasher before uploading its first payload.
Its second-stage write loop advances only when a write succeeds, without a total
deadline or abort after failed writes. A bad transfer marker is logged; optional
read-back mismatch writes a host file and logs an error but does not return before
the later execution-transfer request. Therefore requesting verification does not
make this exact helper fail closed. These are conditional source findings, not
observed failures or executed transitions on the tablet.

[plstage](https://github.com/bkerler/mtkclient/blob/7cb40e727727dfe3faa065eefb29b16ed29bbdf1/mtkclient/Library/mtk_main.py#L537-L660)
can invoke security bypass, watchdog handling, preloader extraction/patching and
RAM execution depending on configuration. A custom preloader path can be patched
in memory. This is distinct from writing it to flash, but the resulting executed
firmware's indirect effects remain unreviewed. No persistence-free claim follows.
The code's USB close/host exit is not an established return to stock operation.

The [metadata receipt](../../evidence/ram-stage-effects/report.json) verifies
exact cached source identity. Required stage payload code/effects are not reviewed
by this host-method analysis. No payload was downloaded or executed, no helper was
imported, and no firmware patch was produced. Keep the route as an investigation,
not a drop-in test procedure. A Linux/ARM64 handoff is still a separate contract.

Next locate pinned payload source/build provenance for generic stage1, stage2 and
preloader-stage before deciding which can form a minimal RAM-only trampoline.
Audit memory/storage/MMIO/reboot handlers and entry prerequisites together. If
payload source is unavailable, record that exact dependency rather than assuming
that a RAM upload implies no persistent effects. Fixing the host transfer loop
alone would not resolve these firmware and recovery gates.
