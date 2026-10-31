# ValethonOS delivery roadmap

Use the [live board](https://github.com/users/TOVSWORLD/projects/4) for current state,
[ordered acceptance contract](../development/ORDERED-ROADMAP.md) for execution rules,
and [current queue](../development/ACTIVE-WORK-QUEUE.md) for the selected task.

Android11 upstream lab boot is measured; final ValethonOS platform is not yet admitted.
Stable supported updates, security/stability, branded identity and recovery precede
Connect/passkey/feature QA. Branding preserves truthful upstream/security attribution.

## Native Epic → Feature → Phase → Task hierarchy

- [Epic #2 — ValethonOS for Android — stable public OS release](https://github.com/TOVSWORLD/ValethonOS-Android/issues/2) · order 0
  - [Feature #8 — Delivery traceability and release governance](https://github.com/TOVSWORLD/ValethonOS-Android/issues/8) · order 0.2
    - [Phase #437 — Ordered roadmap and issue-to-PR execution control](https://github.com/TOVSWORLD/ValethonOS-Android/issues/437) · order 0.5
      - [Task #438 — Ordered roadmap and issue-to-PR workflow](https://github.com/TOVSWORLD/ValethonOS-Android/issues/438) · order 1
    - [Phase #352 — Licensing and distribution prerequisites](https://github.com/TOVSWORLD/ValethonOS-Android/issues/352) · order 409
      - [Task #353 — Owner first-party license decision](https://github.com/TOVSWORLD/ValethonOS-Android/issues/353) · order 410
      - [Task #354 — Distribution and source obligations](https://github.com/TOVSWORLD/ValethonOS-Android/issues/354) · order 420
  - [Feature #327 — Recoverable diagnostic loading and real boot logs](https://github.com/TOVSWORLD/ValethonOS-Android/issues/327) · order 9
    - [Phase #344 — Phase 1 — Operational diagnostic entry, return and logs](https://github.com/TOVSWORLD/ValethonOS-Android/issues/344) · order 9.5
      - [Task #439 — First-boot entry and go/no-go decision](https://github.com/TOVSWORLD/ValethonOS-Android/issues/439) · order 10
      - [Task #345 — Conditional board-inspection proposal](https://github.com/TOVSWORLD/ValethonOS-Android/issues/345) · order 15
      - [Task #347 — Qualified current-device entry and bounded trial](https://github.com/TOVSWORLD/ValethonOS-Android/issues/347) · order 20
      - [Task #346 — Independent stock return and failed-load recovery](https://github.com/TOVSWORLD/ValethonOS-Android/issues/346) · order 30
      - [Task #348 — Usable retained diagnostic boot logs](https://github.com/TOVSWORLD/ValethonOS-Android/issues/348) · order 40
    - [Phase #106 — Historical entry investigation — runtime exit still open](https://github.com/TOVSWORLD/ValethonOS-Android/issues/106) · order 970
  - [Feature #4 — Maintained-kernel douglas board enablement](https://github.com/TOVSWORLD/ValethonOS-Android/issues/4) · order 49
    - [Phase #21 — Phase 2 — Diagnostic memory, UART and internal storage](https://github.com/TOVSWORLD/ValethonOS-Android/issues/21) · order 49.5
      - [Task #22 — Diagnostic memory/UART and internal storage](https://github.com/TOVSWORLD/ValethonOS-Android/issues/22) · order 50
    - [Phase #328 — Phase 3 — Core board provider qualification](https://github.com/TOVSWORLD/ValethonOS-Android/issues/328) · order 59
      - [Task #440 — Finish already-open PWM source PR436](https://github.com/TOVSWORLD/ValethonOS-Android/issues/440) · order 5
      - [Task #18 — Clock/reset provider qualification](https://github.com/TOVSWORLD/ValethonOS-Android/issues/18) · order 60
      - [Task #19 — Pinctrl and EINT qualification](https://github.com/TOVSWORLD/ValethonOS-Android/issues/19) · order 70
      - [Task #20 — PMIC wrapper and power-domain qualification](https://github.com/TOVSWORLD/ValethonOS-Android/issues/20) · order 80
  - [Feature #332 — Reproducible Android platform and essential hardware](https://github.com/TOVSWORLD/ValethonOS-Android/issues/332) · order 99
    - [Phase #23 — Phase 4 — Display, touch and graphics](https://github.com/TOVSWORLD/ValethonOS-Android/issues/23) · order 99.5
      - [Task #329 — Display and backlight](https://github.com/TOVSWORLD/ValethonOS-Android/issues/329) · order 100
      - [Task #330 — Touch and input](https://github.com/TOVSWORLD/ValethonOS-Android/issues/330) · order 110
      - [Task #331 — GPU and Android graphics composition](https://github.com/TOVSWORLD/ValethonOS-Android/issues/331) · order 120
    - [Phase #24 — Phase 5 — Integrated Android candidate](https://github.com/TOVSWORLD/ValethonOS-Android/issues/24) · order 199
      - [Task #333 — Reproducible integrated Android candidate](https://github.com/TOVSWORLD/ValethonOS-Android/issues/333) · order 200
    - [Phase #25 — Phase 6 — Essential hardware and remaining peripherals](https://github.com/TOVSWORLD/ValethonOS-Android/issues/25) · order 299
      - [Task #334 — Wi-Fi integration and reconnect qualification](https://github.com/TOVSWORLD/ValethonOS-Android/issues/334) · order 300
      - [Task #442 — Audio playback and recording](https://github.com/TOVSWORLD/ValethonOS-Android/issues/442) · order 310
      - [Task #335 — Charging, battery and thermal qualification](https://github.com/TOVSWORLD/ValethonOS-Android/issues/335) · order 320
      - [Task #443 — Suspend and wake](https://github.com/TOVSWORLD/ValethonOS-Android/issues/443) · order 330
      - [Task #336 — USB transport and integrity](https://github.com/TOVSWORLD/ValethonOS-Android/issues/336) · order 340
      - [Task #444 — SD integrity and hotplug](https://github.com/TOVSWORLD/ValethonOS-Android/issues/444) · order 350
      - [Task #446 — Video decode and playback](https://github.com/TOVSWORLD/ValethonOS-Android/issues/446) · order 360
      - [Task #441 — Bluetooth integration and qualification](https://github.com/TOVSWORLD/ValethonOS-Android/issues/441) · order 370
      - [Task #445 — Sensors integration and qualification](https://github.com/TOVSWORLD/ValethonOS-Android/issues/445) · order 380
      - [Task #447 — Front/rear camera qualification](https://github.com/TOVSWORLD/ValethonOS-Android/issues/447) · order 390
  - [Feature #337 — Beta QA admission and reproducible handoff](https://github.com/TOVSWORLD/ValethonOS-Android/issues/337) · order 399
    - [Phase #338 — Phase 7 — Candidate validation, packaging and QA admission](https://github.com/TOVSWORLD/ValethonOS-Android/issues/338) · order 399.5
      - [Task #27 — Final candidate DT binding and dependency validation](https://github.com/TOVSWORLD/ValethonOS-Android/issues/27) · order 400
      - [Task #340 — Exact beta package and recovery handoff](https://github.com/TOVSWORLD/ValethonOS-Android/issues/340) · order 500
      - [Task #341 — Beta admission review](https://github.com/TOVSWORLD/ValethonOS-Android/issues/341) · order 510

## Following delivery

Only the earliest admitted implementation Task is Active. Parents are rollups,
not parallel implementation. Open the Task for numbered Work sequence and exact
Acceptance/done gate; follow its Primary PR for the implementation/evidence.
Status and Delivery state agree. Latest result reports measured facts, Next action
the executable step, and Blocker its actual predecessor or missing evidence.

Completed scopes remain visible. There are14 ordered hardware groups; their count
is not a completion percentage. Historical source audits do not replace device gates.
No blocked-task hopping or one-issue-per-run workflow. Main accepts development releases.

Public release requirements are integrated in#333 (platform/branding),#354
(distribution/source/notices),#340 (package/recovery/update handoff),#341 (QA admission).
The interim LineageOS build is not the finished ValethonOS release.

Crestron remains a separate optional workload on the [Crestron board](https://github.com/users/TOVSWORLD/projects/5)
and [Epic3](https://github.com/TOVSWORLD/ValethonOS-Android/issues/3); it does not replace Android platform acceptance.

[Delivery workflow](DELIVERY-WORKFLOW.md) and [QA matrix](../development/BETA-QA-MATRIX.md)
define evidence and admission rules. No roadmap sentence grants new device permissions.
