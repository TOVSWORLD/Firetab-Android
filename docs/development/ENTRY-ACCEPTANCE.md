# Current-device entry acceptance — #347

Review,30 October2026. **Accepted for the selected persistent software route and
interim Android endpoint only.** This is not maintained-kernel, independent
failed-load return, retained-failure-log, security or public-release acceptance.

## Reviewed outcome

Issue347 requires exact installed-route applicability and observed bounded
entry/exit, rather than compilation or the existence of a command. The selected
route was the original external-brick → FULL BootROM → hacked fastboot → pinned
TWRP sequence admitted by the completed GO decision439/PR451. Owner explicitly
approved its persistent writes and destructive lab-host/device work. The later
working Android baseline was owner-authorized and is measured separately.

## Actual acceptance evidence

- **Exact starting generation:** recorded Douglas/API22 and PL7/LK3/TEE262. The
  approved package hashes and script pairing are retained in the source proposal
  and runtime receipt. The case remained closed; no electrical short was applied.
- **Full-stage endpoint:** original FULL script, not minimal, exited0 at
  2026-10-29T16:31:27UTC. Post-stage fastboot identified Douglas. The recovery_x
  capacity was corroborated against decoded GPT before the pinned TWRP write.
- **Actual recovery entry:** original recovery stage exited0 at16:34:13UTC;
  ADB observed recovery/douglas/TWRP3.3.1-0 and kernel3.18.19. Actual recovery and
  current-kernel logs were retrieved, with exact hashes and private raw receipts.
- **Observed exit and later endpoint:** recovery restarted successfully before
  installation. The ROM and Google-services installers reported actual updaterRC0
  and returned to the recovery menu; empty CLI output was never accepted as an
  installation pass. Android11 subsequently reached setup/home and authorized
  ADB reported boot_completed1, setup_complete1 and provisioned1.
- **Error/stop accounting:** the brick client's status-read failure followed the
  owner-directed unplug after its on-screen All-good instruction. It was not
  retried. An unaccepted recovery CLI request was distinguished from a write;
  recovery was restarted only after confirming no ROM installer had started.
  No repeated unlock, automatic reboot retry or alternate minimal branch occurred.
- **Exact limits retained:** script output is not independent readback of every
  partition. Original security state was not restored. Android reports encryption
  unsupported and SELinux Permissive; device-policy enrollment failed. These facts
  disqualify this baseline as the finished stable updated ValethonOS public OS.

Receipts:

- [Original route/recovery runtime](../../evidence/approved-lab-entry/runtime-result.json)
- [ROM/GApps installation](../../evidence/approved-lab-entry/qa-install-result.json)
- [Observed Android runtime](../../evidence/approved-lab-entry/android-runtime-result.json)

The older receipts preserve their observation-time fields; later Android runtime
supersedes the earlier not-yet-booted snapshot without rewriting historical evidence.
Raw logs, host selectors and account identifiers remain private. No account content
or PIN was read. Temporary installers and tablet installer copies were removed after
boot verification; stock rollback files and small receipts remain available.

## Handoff without implied gate completion

The entry task can close on these actual outcomes. Phase344 remains open: normal
stock return and normal log acquisition do not prove independent failed-load return
or retention after an experimental failure. Issue346 was already closed completed;
its closed state is not used as failure-test proof. The phase must reconcile that
remaining release criterion and the retained-failure-log scope in348 before exit.
The next bounded work is a concrete independent return/log qualification proposal
using the existing recovery/stock assets and current privacy/safety constraints.
No new device action is admitted by this review, and no existing install is repeated.

Maintained-kernel boot and hardware gates remain unqualified. Stable supported
updates, enforcing security, stability and ValethonOS branding remain333/platform
release requirements. Connect/passkey/feature QA remains deferred until340/341
release/admission gates pass. Completed347 is an entry milestone, not final OS QA.
