# Active work queue toward beta QA

Updated 2026-10-28 at owner request. This is an execution queue under the existing
Epic → Feature → Phase → Task hierarchy, not a replacement issue tracker.

## Execution contract

- Continue useful authorized work within the active turn. The 15-minute heartbeat
  resumes interrupted/idle work; it is not a reason to end a work session.
- Briefly reconcile current issues/PRs/CI, then select the first executable item.
  Give it a bounded outcome and acceptance criteria. Finish checks and publish
  evidence through an issue-linked PR to development where repository work is needed.
- A task blocked on CI, owner observation, equipment or permissions does not block
  the queue. Record the exact condition once and take an independent item below.
- No repeated waiting-only runs while a ready independent item exists. No duplicate
  cable/approval/photo requests, artificial micro-issues, or low-value cleanup to
  inflate progress. Preserve real hardware/runtime gates.
- Before yielding, record completed result, exact revisions/commands/hashes, next
  executable action and unresolved blockers here or in WORKLOG with an issue link.
  Say whether work is active, queued or awaiting external input; never imply a
  continuous background process. If all ready work is exhausted, audit this queue
  and ask for the specific external action rather than silently polling.

## Ordered ready work

1. **#348 — locate the 320KiB collection limit (completed source scope).**
   Exact packaged BootReceiver user LOG_SIZE65536 multiplied by positive5 matches
   both measured327680byte payloads. See stock-recovery-archive-limit.json and
   WORKLOG; installed equivalence/source-file completeness remain open.
   Next executable item is2. Historical investigation acceptance: inspect the exact
   cached framework BootReceiver/DumpBox implementation and recovery log-copy
   paths using bounded static decoding; no firmware execution. Compare with both
   acquired archive boundaries after CRLF normalization. Acceptance: identify the
   truncating stage with pinned byte/source evidence, or explicitly distinguish
   candidate stages and the missing observation. Do not rerun the same transfer
   expecting missing bytes. Raw captures remain private under
   `out/recovery-log-export`; current dump SHA256 is
   `25a703e1315c636794d26a586153d4051f4569bbf008e429eccff197bd3ba256`.
2. **#348 — qualify archive attribution and usable capture coverage (completed
   bounded analysis).** Second entry covers0..29.865148seconds and all photographed
   markers, first entry is not monotonic; collection headers are not boot identity.
   Exact freshness/failure retention remain open. Next executable item is3.
   Historical acceptance: Independently
   compare existing entry headers, kernel/build markers, uptime spans and
   photographed markers; publish sanitized attribution/coverage only. Acceptance:
   define exactly which stock boot evidence is supported and which freshness or
   failure lifecycle is untested. A full log and experimental failure retention
   are not implied by the demonstrated USB archive export.
3. **#346/#347 — make the loading/return gate concrete (source plan complete;
   runtime gates open).** See LOADER-RETURN-REHEARSAL.md. R0 baseline passes;
   R1/R2 are blocked on compatible bounded entry and independent failure return.
   Historical acceptance: Reconcile authenticated
   exact stock package/reconstructed recovery, observed geometry, original loader
   write effects and available log route into one bounded rehearsal plan.
   Acceptance: explicit prerequisites, intended failure, reachable return path,
   persistent effects, stop conditions and high-brick-risk decision boundary.
   Source-complete planning may finish while physical gates remain open; do not
   execute helpers or close runtime gates on the strength of the plan.
4. **#340 — assemble the diagnostic evidence handoff (source-review index
   complete; beta package gate open).** See DIAGNOSTIC-EVIDENCE-INDEX.md.
   Next executable item is5, with live issue acceptance review.
   Historical acceptance: Use existing sanitized
   receipts, exact revisions, hashes and commands. Acceptance: one navigable
   package index differentiating verified stock entry/return/export, generic
   builds, candidate diagnostics and untested experimental recovery. Include
   reproducible bounded capture and private-data handling. Do not label it beta
   ready or close #340/#338 without their broader QA acceptance.
5. **#27/#18/#19/#20/#29 — independent board dependency work.** Current execution:
   #29 real audio-parent source scope is complete via merged PR384; #27 exact provider
   binding proposals proceed from cached source during that wait. Topckgen and
   infracfg scopes merged (#385/#386); apmixedsys scope merged (#387); four gate contracts are in #388. A real MMSYS parent-
   instantiation gap are recorded in #387. #18 next needs matched SoC parent/
   routing/reset integration, not merely a compiled MMSYS clock object.
   If recovery work
   truly awaits external evidence, select one dependency-ready existing board task
   after reading its live acceptance criteria. Investigate or implement its actual
   board relevance, run matched checks and link the PR. Compilation/schema counts
   alone do not qualify device boot or displace executable recovery work.

## Confirmed state and external gates

- Stock recovery entry and ordinary Android return demonstrated; actual recovery
  selector and kernel text photographed. Normal recovery USB unavailable despite
  completed cable reseat. Stop asking for cable reseats.
- Android-side tag-only `SYSTEM_RECOVERY_KMSG` export demonstrated: two entries,
  663874 transport bytes; both normalized payloads stop at320KiB. No current owner
  photo, cable action or return-to-Android confirmation is outstanding.
- Actual stock ATF/consys placement reconciles DT/kernel memory. Console buffer
  initialization observed; old-valid contents/experimental retention untested.
- Experimental loader failure return, complete log retention, installed recovery
  image equivalence and beta QA admission remain open. No hardware action is
  currently scheduled; task1 can proceed entirely offline.

## Authorization and resource boundaries

Owner grants standing permission for lab-unit actions without high brick risk.
Scoped USB/ADB/host reads may proceed without repeated approval; assess the actual
risk before changes. High-brick-risk actions still require explicit approval.
Do not infer that permission for an unreviewed helper, bootloader/preloader write,
downgrade or electrical operation is established. Avoid unattended mode changes
requiring owner menu interaction; do independent work while the owner is absent.
Large/paid resource gates and private-data exclusions remain. Main changes only
through development-to-main releases; merge feature PRs only after required
exact-head checks. Every PR updates/closes an actual issue; physical gates close
only on their acceptance evidence.
