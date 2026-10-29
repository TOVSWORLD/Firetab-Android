# Active work queue — ordered delivery

Owner priority correction,29 October2026. Read the
[ordered roadmap](ORDERED-ROADMAP.md), [stable task/dependency contract](ordered-roadmap.json)
and [Project4](https://github.com/users/TOVSWORLD/projects/4) before selecting work.
The board is the source of live state. Do not resume historical peripheral queues.

## Current selection

- Administrative task#438/PR448 is complete; ordered board readback passed.
- Existing-work exception#440/PR436 is source-accepted after six exact-head checks
  at8ff8731 and actual PWM object/config/final Image run40881461603. No new PWM
  binding/peripheral scope follows. The source receipt is in
  evidence/pwm-kernel-integration/build-result.json; hardware remains unqualified.
- **Next execution task: #439**, exact-build diagnostic entry/go-no-go decision.
  Its [decision package](FIRST-BOOT-DECISION.md) records NO-GO, pending exact-head
  PR acceptance. Next is selected conditional#345's exact-board mechanical
  inspection/independent recovery-log proposal within authorized planning;
  physical approval waits for its concrete reviewable procedure.
  No cached nonpersistent trial route is qualified on observed PL7/LK3/TEE262.

The decision must identify one operational route or state why none is safely
available, the minimum diagnostic package and entry/memory/CPU/transport contract,
pretrial recovery/log/power/thermal provisions, stop criteria and one concrete
reviewable next action/owner decision. Do not repeat stock/cable/photo captures,
LK microtraces or synthetic readiness wrappers. A closed NO-GO does not admit entry.

## Required sequence

1. #439 decision → explicit GO → #347 bounded entry/trial → #346 independent
   failed-load stock return → #348 useful retained diagnostic logs.
2. #22 diagnostic memory/UART/internal storage → #18 clocks/reset → #19 pinctrl/EINT
   → #20 PMIC/domains.
3. #329 display/backlight → #330 touch → #331 GPU/composition → #333 Android candidate.
4. #334 Wi-Fi → #442 audio → #335 charging/thermal → #443 suspend/wake → #336 USB
   → #444 SD → #446 video → #441 Bluetooth → #445 sensors → #447 cameras.
5. #27 final DT/dependency validation → #353/#354 licensing/distribution → #340 exact
   beta/recovery handoff → #341 actual QA admission review.

Issue#345 is a conditional inspection prerequisite only if selected by the route
decision. Historical phase#106 has100 sub-issues; preserve its source evidence and
open runtime exit, but put operational work under#344. Do not create more source
micro-scopes there or mistake completed child counts for recovery qualification.

## Execution contract

One primary Task issue per PR; one implementation task Active at a time. Use an
issue-numbered branch and Updates #N; Fixes #N only after actual acceptance. Every
required check must pass at the exact head before merge to development; main only
through releases. Source/build completion is distinct from device qualification.

Follow the recorded predecessor gate. If blocked, record the condition and work
only inside that issue or on a documented necessary prerequisite inserted ahead
of it. Update order/dependencies before coding. Never bounce to an unrelated
peripheral. Owner-approved scope exclusions remain explicit and do not become
hardware passes. Parent rollups do not themselves authorize forward execution.

Synchronize/read back Status=Delivery state, labels, native parent, execution order,
dependency, acceptance gate, primary PR, latest result, next action and blocker at
selection, PR changes, merge and acceptance. Preserve completed scopes in the
unfiltered default view. No continuous background-agent claims or rough-percentage
updates; report measured entry/boot/log/return milestones.

Standing low-risk read-only lab authorization remains valid. High-brick-risk
unlock/downgrade/bootloader/security writes/electrical actions require explicit
approval of a concrete reviewed procedure. Do not weaken SELinux/security for logs.
No large/paid resource without the existing gate. Raw logs/selectors/identifiers
stay private in ignored out/; publish sanitized exact revision/artifact receipts.

## Actual qualification boundary

Stock recovery entry/ordinary return and a capped320KiB Android USB export are
observed. Experimental loading, independent failed-return, retained first-kernel
logs and the14 hardware groups on the new kernel remain unqualified. Current full
DT contexts30/24 still fail; DSI/PHY source nodes stay disabled and PWM source status
is okay, unchanged. All seven PID1/host-serial admission gates remain denied.
Source/build successes are real groundwork, not first-boot or beta admission.

The previous detailed source queue is retained as
[historical evidence](history/ACTIVE-WORK-QUEUE-2026-10-29-pre-roadmap.md), not a list
of next actions. Old pre-CI sentences there are historical. The ordered live board
and current entry decision take precedence.
