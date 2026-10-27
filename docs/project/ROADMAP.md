# Beta delivery roadmap

The milestone **Beta 1 — ready for owner QA** has no promised date. It is reached
only when recovery, actual boot, essential hardware and the QA admission review
pass on an exact candidate. We are currently before the first qualified physical
loading gate. Generic compilation and completed source audits are supporting evidence.

## Live delivery hierarchy

- [[Epic] FireTabs Android — beta platform for QA](https://github.com/TOVSWORLD/Firetab-Android/issues/2)
  - [[Feature] Recoverable diagnostic loading and real boot logs](https://github.com/TOVSWORLD/Firetab-Android/issues/327)
    - [[Phase 1] Qualify recovery entry, original-state restore and capture](https://github.com/TOVSWORLD/Firetab-Android/issues/106)
    - [[Phase 1b] Qualify owner recovery procedure and capture on exact board](https://github.com/TOVSWORLD/Firetab-Android/issues/344)
      - [[Task] Source-qualify exact-generation inspection and isolation proposal](https://github.com/TOVSWORLD/Firetab-Android/issues/345)
      - [[Task] Qualify original-state acquisition and reachable restore](https://github.com/TOVSWORLD/Firetab-Android/issues/346)
      - [[Task] Qualify current-device entry and bounded return path](https://github.com/TOVSWORLD/Firetab-Android/issues/347)
      - [[Task] Demonstrate real boot-log capture and retrieval](https://github.com/TOVSWORLD/Firetab-Android/issues/348)
  - [[Feature] Maintained-kernel douglas board enablement](https://github.com/TOVSWORLD/Firetab-Android/issues/4)
    - [[Phase 2] Integrate and validate core board providers](https://github.com/TOVSWORLD/Firetab-Android/issues/328)
      - [[Task] Clock/reset providers](https://github.com/TOVSWORLD/Firetab-Android/issues/18)
      - [[Task] Pinctrl and EINT](https://github.com/TOVSWORLD/Firetab-Android/issues/19)
      - [[Task] PMIC wrapper and power domains](https://github.com/TOVSWORLD/Firetab-Android/issues/20)
      - [[Task] Matched full DT binding validation](https://github.com/TOVSWORLD/Firetab-Android/issues/27)
      - [[Task] Resolve HDMI clock dependency relevance and parents](https://github.com/TOVSWORLD/Firetab-Android/issues/29)
    - [[Phase 3] Boot with memory, UART and storage evidence](https://github.com/TOVSWORLD/Firetab-Android/issues/21)
      - [[Task] Validate UART/MMC diagnostic integration](https://github.com/TOVSWORLD/Firetab-Android/issues/22)
    - [[Phase 4] Make display and input usable](https://github.com/TOVSWORLD/Firetab-Android/issues/23)
      - [[Task] Panel and backlight bring-up](https://github.com/TOVSWORLD/Firetab-Android/issues/329)
      - [[Task] Touch and input integration](https://github.com/TOVSWORLD/Firetab-Android/issues/330)
      - [[Task] Android graphics composition](https://github.com/TOVSWORLD/Firetab-Android/issues/331)
  - [[Feature] Reproducible Android platform and essential hardware](https://github.com/TOVSWORLD/Firetab-Android/issues/332)
    - [[Phase 5] Build integrated Android userspace and kernel](https://github.com/TOVSWORLD/Firetab-Android/issues/24)
      - [[Task] Reproduce complete Android candidate build](https://github.com/TOVSWORLD/Firetab-Android/issues/333)
    - [[Phase 6] Essential hardware and reliability smoke](https://github.com/TOVSWORLD/Firetab-Android/issues/25)
      - [[Task] Connectivity and audio smoke](https://github.com/TOVSWORLD/Firetab-Android/issues/334)
      - [[Task] Power, charging and suspend smoke](https://github.com/TOVSWORLD/Firetab-Android/issues/335)
      - [[Task] Storage and peripheral smoke](https://github.com/TOVSWORLD/Firetab-Android/issues/336)
  - [[Feature] Beta QA admission and reproducible handoff](https://github.com/TOVSWORLD/Firetab-Android/issues/337)
    - [[Phase 7] Admit beta candidate to owner QA](https://github.com/TOVSWORLD/Firetab-Android/issues/338)
      - [[Task] Define beta QA matrix and defect severity](https://github.com/TOVSWORLD/Firetab-Android/issues/339)
      - [[Task] Assemble exact beta package and recovery handoff](https://github.com/TOVSWORLD/Firetab-Android/issues/340)
      - [[Task] Review beta admission evidence](https://github.com/TOVSWORLD/Firetab-Android/issues/341)
  - [[Feature] Delivery traceability and release governance](https://github.com/TOVSWORLD/Firetab-Android/issues/8)
    - [[Phase] Enforce issue-linked delivery workflow](https://github.com/TOVSWORLD/Firetab-Android/issues/342)
      - [[Task] Enforce PR issue linkage and publish beta delivery map](https://github.com/TOVSWORLD/Firetab-Android/issues/343)
    - [[Phase] Resolve beta licensing and distribution prerequisites](https://github.com/TOVSWORLD/Firetab-Android/issues/352)
      - [[Task] Record owner first-party license decision](https://github.com/TOVSWORLD/Firetab-Android/issues/353)
      - [[Task] Review beta artifact redistribution and source obligations](https://github.com/TOVSWORLD/Firetab-Android/issues/354)
- [[Epic] Crestron Panel — supported client beta for QA](https://github.com/TOVSWORLD/Firetab-Android/issues/3)
  - [[Feature] Supported Crestron client qualification](https://github.com/TOVSWORLD/Firetab-Android/issues/6)
    - [[Phase] Prepare supported-client QA qualification](https://github.com/TOVSWORLD/Firetab-Android/issues/7)
      - [[Task] Resolve supported client and processor prerequisites](https://github.com/TOVSWORLD/Firetab-Android/issues/349)
      - [[Task] Execute authorized supported-client QA matrix](https://github.com/TOVSWORLD/Firetab-Android/issues/350)

## Execution order and beta exit

Recovery source qualification and the owner procedure/capture phase are first.
Core-provider source/build tasks and the QA matrix can proceed independently,
but physical boot/storage testing waits for qualified entry, restore and logs.
Display/input follows boot/providers; complete Android integration follows the
resolved platform/ABI contract; essential hardware smoke precedes beta admission.

Beta admission requires reproducible candidate hashes and build instructions,
owner-reviewed recovery/test procedures, real boot and essential hardware results,
security/license/provenance review, triaged known limitations, zero critical
recovery/data-loss/safety defects and a complete QA handoff. The admission task
must explicitly accept or reject evidence; it is not passed by a green host CI run.

The Crestron epic has separate supported-client and processor QA acceptance.
Native panel parity remains unproven and outside Android beta admission.

## Board and working rules

Use native Parent issue plus Level and Delivery state on the
[Android board](https://github.com/users/TOVSWORLD/projects/4) and
[Crestron board](https://github.com/users/TOVSWORLD/projects/5). Closed historical
cards are archived from active delivery views; their issues/receipts are preserved.
Current labels/statuses and dependencies live on issues; this checked-in map is
the baseline, not an automatically asserted runtime progress report.

Every PR updates or closes a real issue. Follow the
[delivery workflow](DELIVERY-WORKFLOW.md). Do not create one micro-issue per run.
A blocked task records its exact missing input and moves out of the active lane.
Hardware planning is acceptable; no specific tablet action is authorized by this
roadmap. Main remains development-to-main releases only.
