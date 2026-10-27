# Beta 1 QA matrix (#339)

This defines tests and admission evidence. **Every device/runtime case is NOT RUN.**
It authorizes no installation, reboot, connection, firmware/helper execution,
flashing, downgrade, wipe or hardware inspection. Start only after the relevant
owner-approved procedure, resource limits and recovery prerequisites exist.

## Admission versus QA completion

Beta **ready for QA** (#341) requires a reproducible candidate, reviewed recovery/
capture procedure, successful owner-authorized boot and essential hardware smoke,
known-issue triage, permitted distribution and the evidence manifest below. It does
not mean the full QA campaign passed or the platform is production ready.

Mandatory admission cases are A01–A07. Campaign cases Q01–Q04 exercise the admitted
candidate more deeply. If a mandatory capability is unavailable, admission fails
unless the owner explicitly revises the beta scope and documents the excluded
case before testing. Never relabel a failed mandatory case as optional afterward.
Crestron runs under #7/#350 separately; native panel parity is not an Android pass.

## Preconditions and stop rule

Identify model/revision privately, with a sanitized unit alias in shared reports.
Record the candidate commit, manifest/config/toolchain, artifact SHA256 values,
security-patch provenance, supported features, environment and test procedure
revision. Verify the actual recovery entry/exit, original-state escrow coverage,
region identity/protection and readback requirements under #346–#347. Determine
what RTC/RPMB/security state is outside that coverage; no generic image substitutes
for original state. Qualify actual captured logs under #348 before loading.

If the approved procedure lacks a bounded failure exit, do not start. Stop on
unexpected storage/security writes, loss of the approved recovery/capture path,
battery damage, unsafe temperature/charging behavior, data corruption or uncertain
unit identity. Use only the already-qualified exit; do not improvise resets,
connector actions, shorts, permission changes or reflashing. Preserve sanitized
failure evidence and open/update a defect against the active task.

## Mandatory admission cases

1. **A01 — Candidate integrity and build reproducibility.** Independently verify
   all distributed hashes against the approved manifest and reproduce the complete
   candidate using pinned inputs. Pass only with a successful full Android/kernel
   build and complete provenance/license review (#333/#354), rather than a generic
   kernel compile. Missing proprietary dependencies or distribution rights block.
2. **A02 — Recoverable loading and original-state return.** Execute only the
   separately approved exact-device procedure. Demonstrate the qualified entry,
   failure exit and restoration/readback checks on the specified original regions.
   Pass only with actual results and documented uncovered security state. If the
   procedure is not qualified, record BLOCKED; do not use QA to discover whether
   recovery might work. This case does not prescribe any write or failure injection.
3. **A03 — Fresh boot logs and memory contract.** Capture attributable logs from
   the approved attempt, retain start/end/timeout context and decode actual usable
   RAM/reservations. Verify ownership/exclusion of all loader/logging regions.
   Fixed UART text, black screen, queued bytes, a filename or an initialized-node
   message alone does not pass. Missing first useful checkpoint or retrieval blocks.
4. **A04 — Complete Android setup and security configuration.** Boot through setup
   to usable home UI; record resolved ABI, Binder/security policy and SELinux
   enforcing state. Exercise settings and normal app lifecycle without security
   bypasses. Pass only with real userspace evidence; kernel entry alone fails.
5. **A05 — Display/input smoke.** Confirm orientation, all screen areas and touch
   coordinates using a non-sensitive grid; exercise brightness endpoints and ten
   screen-off/wake cycles under the approved procedure. Require no dead areas,
   persistent corruption or loss of input. Record graphics/API limitations (#23).
6. **A06 — Essential connectivity/storage/audio smoke.** Connect to the authorized
   test network, complete a local integrity-checked transfer and three reconnects;
   play and record a short non-sensitive audio sample. Verify internal storage and
   any supported SD/USB route with a disposable checksummed test file. Bluetooth,
   camera/sensors and other features follow the declared beta support list (#334/
   #336); unresolved mandatory capabilities block. Publish no credentials or media.
7. **A07 — Power/thermal and short stability smoke.** Verify battery/charging
   reporting against the approved measurement method; run ten suspend/wake cycles
   and a two-hour mixed UI/network/audio session. Require no unexplained reboot,
   corruption, loss of recovery or charging hazard. Use model-qualified thermal
   limits; do not invent a generic temperature threshold. Unknown safe limits
   block the relevant power test. Counts/duration are proposed beta thresholds,
   subject to owner review, not results already observed (#335).

## QA campaign after admission

1. **Q01 — Repeatability.** Repeat the approved startup/recovery and setup flows
   on the same exact candidate using disposable test data. Proposed campaign:
   three complete recorded repetitions, no unexplained state drift or corruption.
   No wipe, reset or installation is implied until explicitly covered by approval.
2. **Q02 — Everyday applications/browser.** On permitted test packages, exercise
   browser/WebView rendering, app launch/background/resume, keyboard and memory
   pressure for two hours. Record supported ABI/GLES/DRM/GMS limitations separately;
   no licensing or certification claim follows from an app launch. Pass criteria:
   no system crash/data loss and all declared core workflows complete.
3. **Q03 — Extended reliability.** Proposed 24-hour idle/mixed-use campaign with
   approved charging conditions, periodic liveness/log checkpoints and defined
   recovery access. Record crashes, wake failures, memory trend and battery drain;
   agree quantitative drain/performance targets from a measured baseline first.
   Never leave a test running without its approved supervision/stop arrangement.
4. **Q04 — Defect fixes and regression.** Re-run the failed case and its dependent
   smoke cases on each new candidate. Results from old commits are supporting
   history, not a pass for changed binaries. Re-admit if recovery/security/storage
   or other admission-critical behavior changes.

## Result format and defect severity

Each result includes case ID; admission/campaign; NOT_RUN, BLOCKED, PASS or FAIL;
exact candidate/procedure revision and artifact hashes; sanitized unit/environment;
start/end timestamps and repetitions; expected/actual behavior; redacted log path
and SHA256; dependency/defect issue; tester and review decision. A blocked result
names the missing prerequisite. Preserve private raw originals separately; publish
only owner-approved sanitized evidence without identifiers/household/network data.

S0: unsafe power/thermal behavior, corruption, security regression or loss of the
qualified recovery route: stop the campaign and reject admission. S1: unusable
boot, input, essential connectivity/storage or other mandatory flow: reject
admission. S2: non-critical supported-feature defect with a documented workaround:
owner triages before admission. S3: cosmetic/documentation issue: track normally.
Severity depends on actual impact, not how easy a fix seems. No unresolved S0/S1
may pass the beta admission review; accepted lower-severity issues need visible
scope/workaround and an issue owner.

## Handoff review

Task #340 supplies the exact permitted candidate package, procedures, test-data
cleanup plan, limitations and known issues. Task #341 reviews each mandatory case,
open defects, hashes and reviewer sign-off and explicitly records ADMIT or REJECT.
Phase #338 remains open until admission acceptance is met. Completing this matrix
closes only test-definition work #339, never a device test or beta gate.
