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
